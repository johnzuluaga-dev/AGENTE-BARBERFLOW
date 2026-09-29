"""Núcleo de BarberFlow  con LangChain.

Decide si una solicitud se resuelve con una Chain determinista o con un
Agent que dispone de 6 Tools.
"""

from typing import TypedDict

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from chains.response_chain import crear_respuesta_chain
from chains.router_chain import crear_router_chain
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from prompts.Barber_prompt import AGENT_SYSTEM_TEMPLATE
from tools.cita_tool import agendar_cita, consultar_citas, priorizar_citas
from tools.disponibilidad_tool import consultar_disponibilidad
from tools.fecha_tool import obtener_fecha
from tools.servicios_tool import consultar_servicios


class Cliente(TypedDict):
    nombre: str


TOOLS = [
    obtener_fecha,
    consultar_servicios,
    consultar_disponibilidad,
    agendar_cita,
    consultar_citas,
    priorizar_citas,
]


def _crear_modelo() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )


def _construir_system_prompt(cliente: Cliente, memoria: str) -> str:
    return AGENT_SYSTEM_TEMPLATE.format(
        nombre=cliente["nombre"],
        memoria=memoria or "Sin memoria reciente.",
    )


def _extraer_texto_final(result: dict) -> str:
    mensajes = result.get("messages", [])
    if not mensajes:
        return "No fue posible generar una respuesta."

    contenido = mensajes[-1].content

    if isinstance(contenido, str):
        return contenido or "No fue posible generar una respuesta."

    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                partes.append(str(bloque.get("text", "")))
            elif isinstance(bloque, str):
                partes.append(bloque)
        texto = "\n".join(p for p in partes if p).strip()
        return texto or "No fue posible generar una respuesta."

    return str(contenido)


def _detectar_tools_usadas(result: dict) -> list[str]:
    usadas: list[str] = []
    for mensaje in result.get("messages", []):
        for call in getattr(mensaje, "tool_calls", None) or []:
            nombre = call.get("name")
            if nombre and nombre not in usadas:
                usadas.append(nombre)
    return usadas


def responder(mensaje_usuario: str, cliente: Cliente, memoria: str) -> dict:
    """Responde mediante Chain o Agent según la naturaleza de la consulta."""
    entrada = {"pregunta": mensaje_usuario, "memoria": memoria or "Sin memoria."}

    decision = crear_router_chain().invoke(entrada)

    if decision.ruta == "chain":
        texto = crear_respuesta_chain().invoke(entrada)
        return {
            "respuesta": texto,
            "ruta": "Chain",
            "motivo": decision.motivo,
            "tools": [],
        }

    agent = create_agent(
        model=_crear_modelo(),
        tools=TOOLS,
        system_prompt=_construir_system_prompt(cliente, memoria),
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": mensaje_usuario}]}
    )

    return {
        "respuesta": _extraer_texto_final(result),
        "ruta": "Agent",
        "motivo": decision.motivo,
        "tools": _detectar_tools_usadas(result),
    }