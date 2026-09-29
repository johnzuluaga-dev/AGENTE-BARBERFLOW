"""Gestión de estado, memoria y trazabilidad en Streamlit."""

import re

import streamlit as st

CLIENTE_INICIAL = {"nombre": "No registrado"}

EJECUCION_INICIAL = {"ruta": "Sin ejecución", "motivo": "", "tools": []}


def inicializar_estado() -> None:
    if "cliente" not in st.session_state:
        st.session_state.cliente = CLIENTE_INICIAL.copy()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if "ultima_ejecucion" not in st.session_state:
        st.session_state.ultima_ejecucion = EJECUCION_INICIAL.copy()


def actualizar_estado_cliente(texto: str) -> None:
    patron_nombre = (
        r"(?:soy|me llamo|mi nombre es|puedes llamarme|llámame|llamame)\s+"
        r"([A-Za-zÁÉÍÓÚáéíóúÑñ]+)"
    )
    coincidencia = re.search(patron_nombre, texto, re.IGNORECASE)

    if coincidencia:
        st.session_state.cliente["nombre"] = coincidencia.group(1).capitalize()


def agregar_mensaje(role: str, content: str) -> None:
    st.session_state.mensajes.append({"role": role, "content": content})


def obtener_memoria(limite: int = 6) -> str:
    mensajes = st.session_state.mensajes[-limite:]
    return "\n".join(f"{m['role']}: {m['content']}" for m in mensajes)


def registrar_ejecucion(resultado: dict) -> None:
    st.session_state.ultima_ejecucion = {
        "ruta": resultado.get("ruta", "Desconocida"),
        "motivo": resultado.get("motivo", ""),
        "tools": resultado.get("tools", []),
    }


def reiniciar_estado() -> None:
    st.session_state.mensajes = []
    st.session_state.cliente = CLIENTE_INICIAL.copy()
    st.session_state.ultima_ejecucion = EJECUCION_INICIAL.copy()