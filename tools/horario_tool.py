import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "horarios.json"
)

def consultar_horario(consulta: str) -> list[dict]:
    """
    Consulta el horario académico ficticio.

    Args:
        consulta: Día de la semana o nombre de la asignatura.

    Returns:
        Lista de clases que coinciden con la consulta.
    """

    with DATA_FILE.open(
        "r",
        encoding="utf-8"
    ) as archivo:

        horarios = json.load(archivo)

    criterio = consulta.lower().strip()

    return [
        clase
        for clase in horarios
        if criterio in clase["dia"].lower()
        or criterio in clase["asignatura"].lower()
    ]