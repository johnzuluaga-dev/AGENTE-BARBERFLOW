import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "horarios.json"
)

def consultar_horario(
    consulta: str = "",
    programa: str = "",
    semestre: str = "",
) -> dict:
    """Busca clases en el horario académico, opcionalmente filtrando por programa y semestre del estudiante."""
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        horarios: list[dict] = json.load(archivo)

    criterio = consulta.lower().strip()
    criterio_programa = programa.lower().strip()
    criterio_semestre = semestre.strip()

    resultados = [
        clase
        for clase in horarios
        if (
            not criterio
            or criterio in clase["dia"].lower()
            or criterio in clase["asignatura"].lower()
        )
        and (
            not criterio_programa
            or criterio_programa in clase["programa"].lower()
        )
        and (
            not criterio_semestre
            or criterio_semestre == clase["semestre"]
        )
    ]

    # Retorno en diccionario estructurado para Gemini Function Calling
    return {
        "consulta": consulta,
        "programa": programa,
        "semestre": semestre,
        "resultados": resultados,
        "cantidad": len(resultados),
    }
