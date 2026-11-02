import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Modelo de respaldo: se usa automáticamente si el principal falla
# (por ejemplo 503 "high demand" o sin cupo).
GEMINI_MODEL_RESPALDO = os.getenv("GEMINI_MODEL_RESPALDO", "gemini-3.5-flash-lite")

# Modelo de embeddings para el RAG (búsqueda en la información de la barbería).
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# Límite de espera por cada llamada al modelo (segundos) y número de intentos.
# Antes no había límite de tiempo y la librería hacía hasta 6 intentos, por
# eso la app podía quedarse "cargando" varios minutos sin mostrar nada.
# Ahora se hace 1 solo intento (sin reintentos): si el modelo principal falla
# o tarda más de este tiempo, responde el modelo de respaldo.
TIEMPO_ESPERA_MODELO = int(os.getenv("TIEMPO_ESPERA_MODELO", "20"))
REINTENTOS_MODELO = int(os.getenv("REINTENTOS_MODELO", "1"))  # intentos totales

# Si el modelo principal falla, se deja de usar durante este tiempo (segundos)
# y todas las llamadas van directo al modelo de respaldo.
PAUSA_MODELO_PRINCIPAL = int(os.getenv("PAUSA_MODELO_PRINCIPAL", "600"))


# Zona horaria de la barbería. El servidor de Render trabaja en UTC (5 horas
# adelante de Colombia), así que la hora siempre se calcula con esta zona.
ZONA_HORARIA = os.getenv("ZONA_HORARIA", "America/Bogota")


def ahora() -> datetime:
    """Fecha y hora actuales en la zona horaria de la barbería."""
    return datetime.now(ZoneInfo(ZONA_HORARIA)).replace(tzinfo=None)


def validar_configuracion() -> None:
    """Valida la API Key antes de compilar el grafo."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY_AQUI":
        raise ValueError(
            "Configura una API Key válida en el archivo .env "
            "usando GEMINI_API_KEY."
        )
