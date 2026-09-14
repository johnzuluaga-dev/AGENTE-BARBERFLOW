from datetime import date

from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from tools.disponibilidad_tool import (
    consultar_disponibilidad
)

from tools.cita_tool import (
    agendar_cita
)

from tools.servicios_tool import (
    cargar_servicios
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def _catalogo_servicios_texto() -> str:

    return "\n".join(
        f"- {servicio['nombre']}: "
        f"{servicio['duracion_minutos']} min, "
        f"${servicio['precio']:,}"
        for servicio in cargar_servicios()
    )

def construir_contexto(
    cliente: dict,
    memoria: str
) -> str:

    fecha_actual = date.today().isoformat()

    return f"""
Eres el asistente virtual de agendamiento de
BarberFlow, una barbería.

Ayudas al cliente a agendar su cita de principio
a fin dentro de este mismo chat.

FECHA ACTUAL: {fecha_actual}

ESTADO ACTUAL DEL CLIENTE:

Nombre: {cliente["nombre"]}

MEMORIA RECIENTE:

{memoria}

CATÁLOGO DE SERVICIOS (única fuente válida,
no ofrezcas nada fuera de esta lista):

{_catalogo_servicios_texto()}

Dispones de dos herramientas:

- consultar_disponibilidad(fecha, servicio):
  úsala para revisar los horarios reales del
  barbero en una fecha (formato YYYY-MM-DD),
  antes de proponer o confirmar cualquier hora.

- agendar_cita(cliente, servicio, fecha, hora):
  úsala ÚNICAMENTE después de que el cliente
  haya confirmado explícitamente el servicio,
  la fecha y la hora exactos.

Reglas obligatorias:

- Nunca inventes servicios, precios ni horarios
  que no provengan del catálogo o de
  consultar_disponibilidad.
- Nunca llames a agendar_cita sin una
  confirmación explícita del cliente sobre
  servicio, fecha y hora.
- Si una hora no está disponible, propone
  alternativas reales obtenidas de
  consultar_disponibilidad.
- No puedes cancelar ni modificar citas ya
  agendadas; si el cliente lo pide, indícale
  que debe contactar directamente a la barbería
  para ese cambio.
- Sé breve, claro y cordial.
""".strip()

def responder(
    mensaje_usuario: str,
    cliente: dict,
    memoria: str
) -> str:

    contexto = construir_contexto(
        cliente,
        memoria
    )

    nombre_cliente = cliente["nombre"]

    def agendar_cita_cliente(
        servicio: str,
        fecha: str,
        hora: str,
        cliente: str = "",
    ) -> dict:
        """Agenda la cita del cliente actual una vez que confirmó servicio, fecha y hora."""
        return agendar_cita(
            cliente=cliente or nombre_cliente,
            servicio=servicio,
            fecha=fecha,
            hora=hora,
        )

    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=mensaje_usuario,

        config=types.GenerateContentConfig(

            system_instruction=contexto,

            tools=[
                consultar_disponibilidad,
                agendar_cita_cliente,
            ]

        )
    )

    return (
        response.text
        or "No fue posible generar una respuesta."
    )
