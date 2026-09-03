from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from tools.horario_tool import (
    consultar_horario
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def construir_contexto(
    estudiante: dict,
    memoria: str
) -> str:

    return f"""
Eres un asistente académico de la
Universidad Católica Luis Amigó.

Ayudas al estudiante con preguntas
académicas sencillas.

ESTADO ACTUAL DEL ESTUDIANTE:

Nombre: {estudiante["nombre"]}
Programa: {estudiante["programa"]}
Semestre: {estudiante["semestre"]}

MEMORIA RECIENTE:

{memoria}

Dispones de una herramienta llamada
consultar_horario.

Usa consultar_horario cuando el estudiante
pregunte por:

- horarios;
- clases;
- días;
- horas;
- asignaturas;
- aulas.

Si puedes responder utilizando el estado
o la memoria, responde directamente.

No inventes información de horarios.

Sé breve, claro y cordial.
""".strip()

def responder(
    mensaje_usuario: str,
    estudiante: dict,
    memoria: str
) -> str:

    contexto = construir_contexto(
        estudiante,
        memoria
    )

    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=mensaje_usuario,

        config=types.GenerateContentConfig(

            system_instruction=contexto,

            tools=[
                consultar_horario
            ]

        )
    )

    return (
        response.text
        or "No fue posible generar una respuesta."
    )