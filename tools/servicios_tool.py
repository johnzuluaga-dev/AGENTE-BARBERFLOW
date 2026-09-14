import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "servicios.json"
)

def cargar_servicios() -> list[dict]:
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)

def buscar_servicio(nombre: str) -> dict | None:
    criterio = nombre.lower().strip()

    for servicio in cargar_servicios():

        if criterio == servicio["nombre"].lower() or criterio == servicio["id"]:

            return servicio

    return None
