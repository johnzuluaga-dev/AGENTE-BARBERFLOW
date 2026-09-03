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
consultar_horario, que ya está filtrada
automáticamente por el programa y semestre
del estudiante.

Usa consultar_horario cuando el estudiante
pregunte por:

- horarios;
- clases;
- días;
- horas;
- asignaturas;
- aulas.

Si el estudiante pide "mi horario" completo,
llama a consultar_horario sin argumentos.

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

    programa = estudiante["programa"]
    semestre = estudiante["semestre"]

    programa_filtro = (
        "" if programa == "No registrado" else programa
    )
    semestre_filtro = (
        "" if semestre == "No registrado" else semestre
    )

    def consultar_horario_estudiante(consulta: str = "") -> dict:
        """Busca clases del horario del estudiante actual según un criterio de día o asignatura."""
        return consultar_horario(
            consulta=consulta,
            programa=programa_filtro,
            semestre=semestre_filtro,
        )

    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=mensaje_usuario,

        config=types.GenerateContentConfig(

            system_instruction=contexto,

            tools=[
                consultar_horario_estudiante
            ]

        )
    )

    return (
        response.text
        or "No fue posible generar una respuesta."
    )