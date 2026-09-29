"""Chain para priorizar una lista conocida de citas."""

import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


def crear_priorizacion_chain():
    """Crea una Chain fija: datos -> prompt -> modelo -> salida."""
    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Ordena las citas de la barbería de una jornada usando exclusivamente
                los datos proporcionados. Considera la hora de inicio, la
                duración y el estado de cada cita. No inventes citas.
                Devuelve una lista numerada breve con la hora, el cliente,
                el servicio y una justificación corta del orden.
                """.strip(),
            ),
            (
                "human",
                "Citas disponibles:\n{citas}\n\n"
                "Contexto adicional: {contexto}",
            ),
        ]
    )

    return prompt | model | StrOutputParser()


def serializar_citas(citas) -> str:
    """Convierte las citas a JSON legible para la Chain."""
    return json.dumps(citas, ensure_ascii=False, indent=2)