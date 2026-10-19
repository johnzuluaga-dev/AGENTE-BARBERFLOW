"""Estado compartido del grafo de BarberFlow (solo estructura y reducers)."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ClienteInfo(TypedDict):
    nombre: str


class BarberState(TypedDict):
    # add_messages acumula el historial en vez de reemplazarlo.
    messages: Annotated[list[BaseMessage], add_messages]
    cliente: ClienteInfo
    ruta: str
    motivo: str
    herramientas_usadas: list[str]
    pasos_ejecutados: list[str]
