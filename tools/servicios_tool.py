"""Tool para consultar el catálogo de servicios."""

import json
from pathlib import Path

from langchain.tools import tool

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "servicios.json"


def cargar_servicios() -> list[dict]:
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def buscar_servicio(nombre: str) -> dict | None:
    """Busca por id o nombre exacto y, si no hay, por coincidencia parcial."""
    criterio = nombre.lower().strip()
    servicios = cargar_servicios()

    for servicio in servicios:
        if criterio == servicio["nombre"].lower() or criterio == servicio["id"]:
            return servicio

    parciales = [
        s for s in servicios
        if criterio and (criterio in s["nombre"].lower() or criterio in s["id"])
    ]
    return parciales[0] if len(parciales) == 1 else None


@tool
def consultar_servicios(consulta: str = "todos") -> dict:
    """Consulta el catálogo real de servicios (nombre, duración y precio).
    Usa 'todos' para listar todo o una palabra clave como 'barba'."""
    servicios = cargar_servicios()
    criterio = consulta.lower().strip()

    if criterio in {"", "todos", "todo", "*"}:
        resultados = servicios
    else:
        resultados = [
            s for s in servicios
            if criterio in s["nombre"].lower() or criterio in s["id"]
        ]

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }