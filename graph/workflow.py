"""Topología y compilación del grafo de BarberFlow."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    agente_barberia_node,
    conceptual_node,
    enrutador_node,
    herramientas_node,
)
from graph.state import BarberState


def _decidir_ruta(state: BarberState) -> str:
    if state.get("ruta") == "conceptual":
        return "nodo_conceptual"
    return "agente_barberia"


def _hay_tool_calls(state: BarberState) -> str:
    ultimo = state["messages"][-1]
    if getattr(ultimo, "tool_calls", None):
        return "herramientas"
    return END


def crear_grafo_barberia():
    builder = StateGraph(BarberState)

    builder.add_node("enrutador", enrutador_node)
    builder.add_node("nodo_conceptual", conceptual_node)
    builder.add_node("agente_barberia", agente_barberia_node)
    builder.add_node("herramientas", herramientas_node)

    builder.add_edge(START, "enrutador")
    builder.add_conditional_edges(
        "enrutador",
        _decidir_ruta,
        {"nodo_conceptual": "nodo_conceptual", "agente_barberia": "agente_barberia"},
    )
    builder.add_edge("nodo_conceptual", END)
    builder.add_conditional_edges(
        "agente_barberia",
        _hay_tool_calls,
        {"herramientas": "herramientas", END: END},
    )
    # Arista cíclica: el agente recibe los resultados y responde o vuelve a llamar tools.
    builder.add_edge("herramientas", "agente_barberia")

    return builder.compile(checkpointer=MemorySaver())
