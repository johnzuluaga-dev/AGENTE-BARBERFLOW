import json
import uuid
from datetime import datetime
from pathlib import Path

from tools.disponibilidad_tool import consultar_disponibilidad
from tools.servicios_tool import buscar_servicio

CITAS_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "citas.json"
)

def _cargar_citas() -> list[dict]:
    with CITAS_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)

def _guardar_citas(citas: list[dict]) -> None:
    with CITAS_FILE.open("w", encoding="utf-8") as archivo:
        json.dump(citas, archivo, ensure_ascii=False, indent=2)

def listar_citas() -> list[dict]:
    return _cargar_citas()

def agendar_cita(
    cliente: str,
    servicio: str,
    fecha: str,
    hora: str,
) -> dict:
    """Agenda una cita confirmada por el cliente, validando que el servicio exista y que la fecha/hora estén realmente disponibles antes de registrarla."""

    if not cliente.strip():
        return {"error": "Falta el nombre del cliente para agendar la cita."}

    servicio_encontrado = buscar_servicio(servicio)

    if not servicio_encontrado:
        return {
            "error": (
                f"El servicio '{servicio}' no existe en el catálogo. "
                "No se puede agendar una cita con un servicio inexistente."
            )
        }

    disponibilidad = consultar_disponibilidad(fecha=fecha, servicio=servicio)

    if "error" in disponibilidad:
        return disponibilidad

    if not disponibilidad.get("abierto"):
        return {
            "error": disponibilidad.get(
                "mensaje",
                f"La barbería no atiende el {fecha}.",
            )
        }

    if hora not in disponibilidad["horarios_disponibles"]:
        return {
            "error": (
                f"La hora '{hora}' no está disponible el {fecha} para "
                f"'{servicio_encontrado['nombre']}'. "
                "Consulta consultar_disponibilidad para ver horarios reales."
            ),
            "horarios_disponibles": disponibilidad["horarios_disponibles"],
        }

    citas = _cargar_citas()

    nueva_cita = {
        "id": str(uuid.uuid4()),
        "cliente": cliente.strip(),
        "servicio": servicio_encontrado["nombre"],
        "precio": servicio_encontrado["precio"],
        "fecha": fecha,
        "hora": hora,
        "duracion_minutos": servicio_encontrado["duracion_minutos"],
        "estado": "confirmada",
        "creado_en": datetime.now().isoformat(timespec="seconds"),
    }

    citas.append(nueva_cita)

    _guardar_citas(citas)

    return {
        "confirmada": True,
        "cita": nueva_cita,
        "mensaje": (
            f"Cita confirmada para {nueva_cita['cliente']}: "
            f"{nueva_cita['servicio']} el {fecha} a las {hora}."
        ),
    }
