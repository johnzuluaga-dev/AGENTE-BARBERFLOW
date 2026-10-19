"""Tools para agendar, consultar y priorizar citas."""

import json
import uuid
from datetime import date, datetime
from pathlib import Path

from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from prompts.Barber_prompt import PRIORIZACION_SYSTEM_PROMPT
from tools.disponibilidad_tool import consultar_disponibilidad
from tools.servicios_tool import buscar_servicio

CITAS_FILE = Path(__file__).resolve().parents[1] / "data" / "citas.json"


def _crear_priorizacion_chain():
    """Chain fija: datos -> prompt -> modelo -> salida."""
    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PRIORIZACION_SYSTEM_PROMPT),
            ("human", "Citas disponibles:\n{citas}\n\nContexto adicional: {contexto}"),
        ]
    )
    return prompt | model | StrOutputParser()


def listar_citas() -> list[dict]:
    """Función simple (no es tool): la usa el Panel del barbero."""
    if not CITAS_FILE.exists():
        return []
    with CITAS_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def _guardar_citas(citas: list[dict]) -> None:
    with CITAS_FILE.open("w", encoding="utf-8") as archivo:
        json.dump(citas, archivo, ensure_ascii=False, indent=2)


@tool
def agendar_cita(cliente: str, servicio: str, fecha: str, hora: str) -> dict:
    """Agenda una cita. Úsala SOLO tras la confirmación explícita del cliente.
    fecha en formato YYYY-MM-DD y hora en formato HH:MM (24 h)."""
    if not cliente or cliente.strip().lower() == "no registrado":
        return {"error": "Falta el nombre del cliente. Pídeselo antes de agendar."}

    servicio_data = buscar_servicio(servicio)
    if not servicio_data:
        return {"error": f"El servicio '{servicio}' no existe en el catálogo."}

    try:
        momento = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        return {"error": "Fecha u hora inválidas. Usa YYYY-MM-DD y HH:MM."}

    if momento < datetime.now():
        return {"error": "No se pueden agendar citas en el pasado."}

    # Reutiliza la lógica de disponibilidad (horario laboral + citas existentes)
    disponibilidad = consultar_disponibilidad.invoke(
        {"fecha": fecha, "servicio": servicio_data["nombre"]}
    )
    if "error" in disponibilidad:
        return disponibilidad
    if hora not in disponibilidad.get("horarios_disponibles", []):
        return {
            "error": f"La hora {hora} no está disponible.",
            "alternativas": disponibilidad.get("horarios_disponibles", [])[:6],
        }

    cita = {
        "id": str(uuid.uuid4()),
        "cliente": cliente.strip(),
        "servicio": servicio_data["nombre"],
        "precio": servicio_data["precio"],
        "fecha": fecha,
        "hora": hora,
        "duracion_minutos": servicio_data["duracion_minutos"],
        "estado": "confirmada",
        "creado_en": datetime.now().isoformat(timespec="seconds"),
    }

    citas = listar_citas()
    citas.append(cita)
    _guardar_citas(citas)

    return {"ok": True, "cita": cita}


@tool
def consultar_citas(cliente: str = "", fecha: str = "") -> dict:
    """Consulta citas agendadas, filtrando por nombre de cliente y/o fecha
    (YYYY-MM-DD). Sin filtros devuelve todas las no canceladas."""
    resultados = [
        c for c in listar_citas()
        if c.get("estado", "confirmada") != "cancelada"
        and (not cliente or cliente.lower().strip() in c["cliente"].lower())
        and (not fecha or c["fecha"] == fecha)
    ]
    return {"cliente": cliente, "fecha": fecha,
            "resultados": resultados, "cantidad": len(resultados)}


@tool
def priorizar_citas(fecha: str = "", contexto: str = "") -> str:
    """Ordena y prioriza las citas de una fecha (YYYY-MM-DD) usando una
    Chain determinista. Si no se indica fecha usa hoy."""
    fecha = fecha or date.today().isoformat()
    citas = [
        c for c in listar_citas()
        if c["fecha"] == fecha and c.get("estado", "confirmada") != "cancelada"
    ]
    if not citas:
        return f"No hay citas agendadas para {fecha}."

    return _crear_priorizacion_chain().invoke(
        {"citas": json.dumps(citas, ensure_ascii=False, indent=2),
         "contexto": contexto or "Sin contexto adicional."}
    )