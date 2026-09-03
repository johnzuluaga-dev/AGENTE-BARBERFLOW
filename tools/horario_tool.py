import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "horarios.json"
)

def consultar_horario(consulta: str) -> dict:
    """Busca clases en el horario académico según un criterio de consulta."""
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        horarios: list[dict] = json.load(archivo)

    criterio = consulta.lower().strip()

    resultados = [
        clase
        for clase in horarios
        if criterio in clase["dia"].lower()
        or criterio in clase["asignatura"].lower()
    ]

    # Retorno en diccionario estructurado para Gemini Function Calling
    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }