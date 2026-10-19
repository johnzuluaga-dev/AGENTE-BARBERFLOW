"""Nodos del grafo: reciben el estado y devuelven un diccionario de cambios."""

from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
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


def _crear_modelo(temperature: float) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=temperature,
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


def enrutador_node(state: BarberState) -> dict:
    """Clasifica la consulta como conceptual o de herramientas."""
    modelo = _crear_modelo(0).with_structured_output(RutaConsulta)
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
    respuesta = _crear_modelo(0.2).invoke(
        [SystemMessage(content=CONCEPTUAL_SYSTEM_PROMPT)] + state["messages"]
    )
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["nodo_conceptual"],
    }


def agente_barberia_node(state: BarberState) -> dict:
    """Agente razonador con las tools vinculadas; decide si llamarlas."""
    system_prompt = AGENT_SYSTEM_TEMPLATE.format(nombre=state["cliente"]["nombre"])
    modelo = _crear_modelo(0.1).bind_tools(TOOLS_BARBERIA)
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
