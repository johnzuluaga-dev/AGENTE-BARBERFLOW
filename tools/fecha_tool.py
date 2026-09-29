"""Tool para obtener fecha y día actual."""

from datetime import datetime

from langchain.tools import tool

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


@tool
def obtener_fecha() -> dict:
    """Obtiene la fecha actual (YYYY-MM-DD), el día de la semana y la hora."""
    ahora = datetime.now()
    return {
        "fecha": ahora.strftime("%Y-%m-%d"),
        "dia": DIAS[ahora.weekday()],
        "hora": ahora.strftime("%H:%M"),
    }