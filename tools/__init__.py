"""Herramientas de BarberFlow expuestas al ToolNode del grafo."""

from tools.cita_tool import agendar_cita, consultar_citas, priorizar_citas
from tools.disponibilidad_tool import consultar_disponibilidad
from tools.fecha_tool import obtener_fecha
from tools.servicios_tool import consultar_servicios

TOOLS_BARBERIA = [
    obtener_fecha,
    consultar_servicios,
    consultar_disponibilidad,
    agendar_cita,
    consultar_citas,
    priorizar_citas,
]
