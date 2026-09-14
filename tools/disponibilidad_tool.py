import json
from datetime import datetime, timedelta
from pathlib import Path

from tools.servicios_tool import buscar_servicio

HORARIOS_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "horarios.json"
)

CITAS_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "citas.json"
)

DIAS_SEMANA = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]

DURACION_POR_DEFECTO_MINUTOS = 30
PASO_MINUTOS = 15

def _cargar_horarios() -> dict:
    with HORARIOS_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)

def _cargar_citas() -> list[dict]:
    with CITAS_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)

def _a_minutos(hora: str) -> int:
    horas, minutos = hora.split(":")
    return int(horas) * 60 + int(minutos)

def _a_hora(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"

def consultar_disponibilidad(
    fecha: str,
    servicio: str = "",
) -> dict:
    """Consulta los horarios disponibles del barbero para una fecha (YYYY-MM-DD), opcionalmente para un servicio específico, revisando el horario laboral y las citas ya agendadas."""

    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return {
            "error": (
                f"La fecha '{fecha}' no tiene un formato válido. "
                "Usa el formato YYYY-MM-DD."
            )
        }

    dia_semana = DIAS_SEMANA[fecha_dt.weekday()]

    horarios = _cargar_horarios()
    jornada = horarios.get(dia_semana)

    if not jornada:
        return {
            "fecha": fecha,
            "dia": dia_semana,
            "abierto": False,
            "mensaje": f"La barbería no atiende los {dia_semana}.",
            "horarios_disponibles": [],
        }

    duracion_minutos = DURACION_POR_DEFECTO_MINUTOS
    servicio_encontrado = None

    if servicio:
        servicio_encontrado = buscar_servicio(servicio)

        if not servicio_encontrado:
            return {
                "error": (
                    f"El servicio '{servicio}' no existe en el catálogo. "
                    "Consulta el catálogo de servicios disponible."
                )
            }

        duracion_minutos = servicio_encontrado["duracion_minutos"]

    inicio_jornada = _a_minutos(jornada["inicio"])
    fin_jornada = _a_minutos(jornada["fin"])

    citas_del_dia = [
        cita
        for cita in _cargar_citas()
        if cita["fecha"] == fecha and cita.get("estado", "confirmada") != "cancelada"
    ]

    ocupados = [
        (
            _a_minutos(cita["hora"]),
            _a_minutos(cita["hora"]) + cita.get("duracion_minutos", DURACION_POR_DEFECTO_MINUTOS),
        )
        for cita in citas_del_dia
    ]

    disponibles = []

    cursor = inicio_jornada

    while cursor + duracion_minutos <= fin_jornada:

        fin_bloque = cursor + duracion_minutos

        hay_cruce = any(
            cursor < ocupado_fin and fin_bloque > ocupado_inicio
            for ocupado_inicio, ocupado_fin in ocupados
        )

        if not hay_cruce:
            disponibles.append(_a_hora(cursor))

        cursor += PASO_MINUTOS

    return {
        "fecha": fecha,
        "dia": dia_semana,
        "abierto": True,
        "horario_laboral": jornada,
        "servicio": servicio_encontrado["nombre"] if servicio_encontrado else "",
        "duracion_minutos": duracion_minutos,
        "horarios_disponibles": disponibles,
        "cantidad_disponible": len(disponibles),
    }
