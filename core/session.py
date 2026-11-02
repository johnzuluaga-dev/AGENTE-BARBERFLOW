"""Gestión de sesiones: thread_id por usuario e invocación del grafo."""

import re
import uuid

import streamlit as st
from langchain_core.messages import HumanMessage

from core.metricas import MedidorEjecucion
from graph.nodes import texto_de_mensaje
from graph.workflow import crear_grafo_barberia

CLIENTE_INICIAL = {"nombre": "No registrado"}

EJECUCION_INICIAL = {"ruta": "Sin ejecución", "motivo": "", "tools": [], "pasos": []}

LIMITE_RECURSION = 15


@st.cache_resource
def obtener_grafo():
    """Compila el grafo una sola vez; el MemorySaver vive mientras corra la app."""
    return crear_grafo_barberia()


def _config(callbacks: list | None = None) -> dict:
    config = {
        "configurable": {"thread_id": st.session_state.thread_id},
        "recursion_limit": LIMITE_RECURSION,
    }
    if callbacks:
        config["callbacks"] = callbacks
    return config


def inicializar_sesion() -> None:
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "cliente" not in st.session_state:
        st.session_state.cliente = CLIENTE_INICIAL.copy()

    if "ultima_ejecucion" not in st.session_state:
        st.session_state.ultima_ejecucion = EJECUCION_INICIAL.copy()

    if "historial_metricas" not in st.session_state:
        st.session_state.historial_metricas = []


# Palabras que pueden seguir a "soy" / "me llamo" y que no son un nombre.
_NO_NOMBRES = {
    "y", "e", "o", "u", "el", "la", "los", "las", "un", "una", "de", "del",
    "que", "qué", "como", "cómo", "nuevo", "nueva", "cliente", "yo",
}


def actualizar_estado_cliente(texto: str) -> None:
    # Si el cliente pregunta su nombre ("¿cómo me llamo?") no hay nada que guardar.
    if re.search(r"c[oó]mo\s+me\s+llamo", texto, re.IGNORECASE):
        return

    patron_nombre = (
        r"(?:soy|me llamo|mi nombre es|puedes llamarme|llámame|llamame)\s+"
        r"([A-Za-zÁÉÍÓÚáéíóúÑñ]+)"
    )
    coincidencia = re.search(patron_nombre, texto, re.IGNORECASE)

    if coincidencia:
        nombre = coincidencia.group(1)
        if len(nombre) >= 2 and nombre.lower() not in _NO_NOMBRES:
            st.session_state.cliente["nombre"] = nombre.capitalize()


def obtener_historial() -> list[dict]:
    """Lee la conversación desde el checkpoint del thread activo."""
    snapshot = obtener_grafo().get_state(_config())
    historial = []
    for mensaje in snapshot.values.get("messages", []):
        if mensaje.type not in ("human", "ai"):
            continue
        texto = texto_de_mensaje(mensaje)
        if texto:
            rol = "user" if mensaje.type == "human" else "assistant"
            historial.append({"role": rol, "content": texto})
    return historial


def responder(mensaje_usuario: str) -> str:
    """Invoca el grafo en el thread de la sesión y registra la traza."""
    estado_inicial = {
        "messages": [HumanMessage(content=mensaje_usuario)],
        "cliente": st.session_state.cliente,
        "ruta": "",
        "motivo": "",
        "herramientas_usadas": [],
        "pasos_ejecutados": [],
    }

    medidor = MedidorEjecucion(mensaje_usuario)
    try:
        resultado = obtener_grafo().invoke(
            estado_inicial, config=_config([medidor.callback])
        )
    except Exception as error:
        st.session_state.historial_metricas.append(
            medidor.resultado(ruta="error", error=str(error))
        )
        raise

    st.session_state.historial_metricas.append(
        medidor.resultado(ruta=resultado.get("ruta", ""))
    )

    st.session_state.ultima_ejecucion = {
        "ruta": resultado.get("ruta", "Desconocida"),
        "motivo": resultado.get("motivo", ""),
        "tools": resultado.get("herramientas_usadas", []),
        "pasos": resultado.get("pasos_ejecutados", []),
    }

    return texto_de_mensaje(resultado["messages"][-1]) or "No fue posible generar una respuesta."


def diagrama_mermaid() -> str:
    return obtener_grafo().get_graph().draw_mermaid()


def reiniciar_sesion() -> None:
    """Un thread_id nuevo equivale a una conversación nueva en el MemorySaver."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.cliente = CLIENTE_INICIAL.copy()
    st.session_state.ultima_ejecucion = EJECUCION_INICIAL.copy()
    st.session_state.historial_metricas = []
