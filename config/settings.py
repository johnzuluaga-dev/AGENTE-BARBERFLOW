import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Modelo de embeddings para el RAG (búsqueda en la información de la barbería).
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# Límite de espera por cada llamada al modelo (segundos) y reintentos.
# Antes no había límite y la librería reintentaba hasta 6 veces, por eso la
# app podía quedarse "cargando" varios minutos sin mostrar nada.
TIEMPO_ESPERA_MODELO = int(os.getenv("TIEMPO_ESPERA_MODELO", "40"))
REINTENTOS_MODELO = int(os.getenv("REINTENTOS_MODELO", "1"))


def validar_configuracion() -> None:
    """Valida la API Key antes de compilar el grafo."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY_AQUI":
        raise ValueError(
            "Configura una API Key válida en el archivo .env "
            "usando GEMINI_API_KEY."
        )
