"""Tool de RAG: busca en la información de la barbería y devuelve los
fragmentos más parecidos a la pregunta del cliente.

Pasos:
1. Lee data/conocimiento/barberia.md y lo parte en fragmentos (uno por sección).
2. Convierte cada fragmento en un vector con el modelo de embeddings de Gemini
   y los guarda en un almacén de vectores en memoria (se hace una sola vez).
3. Ante cada pregunta, busca los fragmentos más parecidos y se los entrega al
   agente para que responda solo con esa información.

Si los embeddings fallan (por ejemplo, sin cupo en la API), se usa una búsqueda
simple por palabras para que el agente no se quede sin respuesta.
"""

import logging
import re
import unicodedata
from pathlib import Path

from langchain.tools import tool
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config.settings import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

ARCHIVO_CONOCIMIENTO = (
    Path(__file__).resolve().parents[1] / "data" / "conocimiento" / "barberia.md"
)
CANTIDAD_FRAGMENTOS = 3

logger = logging.getLogger("barberflow.rag")

_almacen: InMemoryVectorStore | None = None


def cargar_fragmentos() -> list[Document]:
    """Parte el documento en fragmentos: uno por cada sección '## '."""
    texto = ARCHIVO_CONOCIMIENTO.read_text(encoding="utf-8")
    fragmentos = []
    for bloque in re.split(r"^## ", texto, flags=re.MULTILINE)[1:]:
        titulo, _, contenido = bloque.partition("\n")
        fragmentos.append(
            Document(
                page_content=f"{titulo.strip()}\n{' '.join(contenido.split())}",
                metadata={"titulo": titulo.strip()},
            )
        )
    return fragmentos


def _obtener_almacen() -> InMemoryVectorStore:
    """Crea el almacén de vectores la primera vez y luego lo reutiliza."""
    global _almacen
    if _almacen is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,
        )
        almacen = InMemoryVectorStore(embeddings)
        almacen.add_documents(cargar_fragmentos())
        _almacen = almacen
    return _almacen


def _palabras(texto: str) -> set[str]:
    sin_tildes = unicodedata.normalize("NFKD", texto.lower())
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return {p for p in re.findall(r"[a-zñ]+", sin_tildes) if len(p) > 3}


def _buscar_por_palabras(pregunta: str) -> list[tuple[Document, float]]:
    """Respaldo: ordena los fragmentos por palabras en común con la pregunta."""
    palabras_pregunta = _palabras(pregunta)
    puntajes = []
    for fragmento in cargar_fragmentos():
        comunes = palabras_pregunta & _palabras(fragmento.page_content)
        if comunes:
            puntajes.append((fragmento, float(len(comunes))))
    puntajes.sort(key=lambda par: par[1], reverse=True)
    return puntajes[:CANTIDAD_FRAGMENTOS]


@tool
def consultar_informacion_barberia(pregunta: str) -> dict:
    """Busca en la información oficial de la barbería (RAG): horario, formas
    de pago, puntualidad, cancelaciones, qué incluye cada servicio, corte
    infantil, cuidados del cabello y la barba, higiene y cómo reservar.
    Pasa la pregunta del cliente tal cual."""
    try:
        resultados = _obtener_almacen().similarity_search_with_score(
            pregunta, k=CANTIDAD_FRAGMENTOS
        )
        metodo = "embeddings"
    except Exception as error:  # noqa: BLE001 - se informa y se usa el respaldo
        logger.warning("RAG: falló la búsqueda con embeddings (%s); se usa búsqueda por palabras.", error)
        resultados = _buscar_por_palabras(pregunta)
        metodo = "palabras clave (respaldo)"

    fragmentos = [
        {
            "titulo": documento.metadata.get("titulo", ""),
            "texto": documento.page_content,
            "puntaje": round(float(puntaje), 3),
        }
        for documento, puntaje in resultados
    ]
    return {
        "pregunta": pregunta,
        "metodo_busqueda": metodo,
        "fragmentos": fragmentos,
        "cantidad": len(fragmentos),
    }
