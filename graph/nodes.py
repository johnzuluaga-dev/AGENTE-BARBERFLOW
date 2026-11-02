"""Nodos del grafo: reciben el estado y devuelven un diccionario de cambios."""

import logging
import re
import time
from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MODEL_RESPALDO,
    PAUSA_MODELO_PRINCIPAL,
    REINTENTOS_MODELO,
    TIEMPO_ESPERA_MODELO,
)
from graph.state import BarberState
from prompts.Barber_prompt import (
    AGENT_SYSTEM_TEMPLATE,
    CONCEPTUAL_SYSTEM_PROMPT,
    ROUTER_SYSTEM_PROMPT,
)
from tools import TOOLS_BARBERIA


class RutaConsulta(BaseModel):
    """Ruta seleccionada para atender la solicitud."""

    ruta: Literal["conceptual", "herramientas"] = Field(
        description="Usa 'conceptual' para conversación general sin datos "
        "del negocio y 'herramientas' cuando se requieren tools."
    )
    motivo: str = Field(description="Justificación breve de la selección.")


def _crear_modelo(temperature: float, modelo: str = GEMINI_MODEL) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=modelo,
        api_key=GEMINI_API_KEY,
        temperature=temperature,
        timeout=TIEMPO_ESPERA_MODELO,
        max_retries=REINTENTOS_MODELO,
    )


logger = logging.getLogger("barberflow.modelos")

# Hasta cuándo (segundos de time.time()) se salta el modelo principal.
_principal_en_pausa_hasta = 0.0


def principal_en_pausa() -> bool:
    return time.time() < _principal_en_pausa_hasta


def _pausar_principal(error: Exception) -> None:
    """Tras una falla del modelo principal (sin cupo, saturado o lento), se
    deja de usar por unos minutos para no esperarlo en cada paso."""
    global _principal_en_pausa_hasta
    _principal_en_pausa_hasta = time.time() + PAUSA_MODELO_PRINCIPAL
    logger.warning(
        "Modelo principal %s en pausa %s s por: %s",
        GEMINI_MODEL, PAUSA_MODELO_PRINCIPAL, str(error)[:120],
    )


def _con_respaldo(temperature: float, preparar=lambda modelo: modelo):
    """Modelo principal con un modelo de respaldo (LangChain with_fallbacks).

    `preparar` agrega lo que necesite cada nodo (tools o salida estructurada)
    a los dos modelos por igual. Si el principal falló hace poco, se usa
    directamente el respaldo.
    """
    principal = preparar(_crear_modelo(temperature))
    if not GEMINI_MODEL_RESPALDO or GEMINI_MODEL_RESPALDO == GEMINI_MODEL:
        return principal

    respaldo = preparar(_crear_modelo(temperature, GEMINI_MODEL_RESPALDO))
    if principal_en_pausa():
        return respaldo

    def _invocar_principal(entrada, config):
        try:
            return principal.invoke(entrada, config=config)
        except Exception as error:
            _pausar_principal(error)
            raise

    return RunnableLambda(_invocar_principal, name="modelo_principal").with_fallbacks(
        [respaldo]
    )


def texto_de_mensaje(mensaje: BaseMessage) -> str:
    """Extrae el texto de un mensaje (Gemini puede devolver bloques)."""
    contenido = mensaje.content

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                partes.append(str(bloque.get("text", "")))
            elif isinstance(bloque, str):
                partes.append(bloque)
        return "\n".join(p for p in partes if p).strip()

    return str(contenido)


def _conversacion_reciente(state: BarberState, limite: int = 6) -> str:
    lineas = []
    for mensaje in state["messages"][-limite:]:
        texto = texto_de_mensaje(mensaje)
        if texto and mensaje.type in ("human", "ai"):
            rol = "cliente" if mensaje.type == "human" else "asistente"
            lineas.append(f"{rol}: {texto}")
    return "\n".join(lineas) or "Sin conversación previa."


# Mensajes cortos de cortesía que no necesitan que el modelo decida la ruta.
_SALUDOS = {
    "hola", "holi", "buenas", "buen dia", "buenos dias", "buenas tardes",
    "buenas noches", "gracias", "muchas gracias", "mil gracias", "chao",
    "adios", "hasta luego", "hola como estas", "hola buenas",
}


def _es_saludo(texto: str) -> bool:
    limpio = texto.lower()
    for con_tilde, sin_tilde in zip("áéíóú", "aeiou"):
        limpio = limpio.replace(con_tilde, sin_tilde)
    limpio = re.sub(r"[^a-zñ ]", " ", limpio)
    return " ".join(limpio.split()) in _SALUDOS


def enrutador_node(state: BarberState) -> dict:
    """Clasifica la consulta como conceptual o de herramientas."""
    ultimo = state["messages"][-1]
    if ultimo.type == "human" and _es_saludo(texto_de_mensaje(ultimo)):
        # Atajo: un saludo va directo al nodo conceptual y se ahorra
        # una llamada al modelo (respuesta más rápida).
        return {
            "ruta": "conceptual",
            "motivo": "Saludo o agradecimiento: se responde sin herramientas.",
            "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["enrutador"],
        }

    modelo = _con_respaldo(0, lambda m: m.with_structured_output(RutaConsulta))
    decision = modelo.invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=_conversacion_reciente(state)),
        ]
    )
    return {
        "ruta": decision.ruta,
        "motivo": decision.motivo,
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["enrutador"],
    }


def conceptual_node(state: BarberState) -> dict:
    """Responde sin herramientas usando el historial de mensajes."""
    respuesta = _con_respaldo(0.2).invoke(
        [SystemMessage(content=CONCEPTUAL_SYSTEM_PROMPT)] + state["messages"]
    )
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["nodo_conceptual"],
    }


def agente_barberia_node(state: BarberState) -> dict:
    """Agente razonador con las tools vinculadas; decide si llamarlas."""
    system_prompt = AGENT_SYSTEM_TEMPLATE.format(nombre=state["cliente"]["nombre"])
    modelo = _con_respaldo(0.1, lambda m: m.bind_tools(TOOLS_BARBERIA))
    respuesta = modelo.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["agente_barberia"],
    }


_tool_node = ToolNode(TOOLS_BARBERIA)


def herramientas_node(state: BarberState) -> dict:
    """Ejecuta las tool calls pendientes y registra cuáles se usaron."""
    usadas = list(state.get("herramientas_usadas", []))
    for call in getattr(state["messages"][-1], "tool_calls", None) or []:
        if call["name"] not in usadas:
            usadas.append(call["name"])

    resultado = _tool_node.invoke(state)
    return {
        "messages": resultado["messages"],
        "herramientas_usadas": usadas,
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["herramientas"],
    }
