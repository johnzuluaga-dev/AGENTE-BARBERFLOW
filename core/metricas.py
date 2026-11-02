"""Observabilidad: mide cada respuesta del agente.

Usa un "callback" de LangChain, que se entera de cada llamada al modelo y de
cada tool que se ejecuta dentro del grafo. Por cada respuesta registra:
tiempo total, llamadas al modelo, tokens (entrada, salida y total), tools
usadas, modelo que respondió y errores. Cada registro también se escribe en los logs del servidor
(en Render se ven en la pestaña "Logs").
"""

import json
import logging
import time

from langchain_core.callbacks import BaseCallbackHandler

from config.settings import ahora

logger = logging.getLogger("barberflow.metricas")
if not logger.handlers:
    _manejador = logging.StreamHandler()
    _manejador.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))
    logger.addHandler(_manejador)
    logger.setLevel(logging.INFO)
    logger.propagate = False


class MetricasCallback(BaseCallbackHandler):
    """Cuenta llamadas al modelo, tokens, tools y errores de una ejecución."""

    def __init__(self) -> None:
        self.llamadas_modelo = 0
        self.tokens_entrada = 0
        self.tokens_salida = 0
        self.tools: list[str] = []
        self.errores: list[str] = []
        self.modelos_ok: list[str] = []
        self._modelo_por_llamada: dict = {}

    # --- Modelo de lenguaje ---
    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
        self.llamadas_modelo += 1
        parametros = kwargs.get("invocation_params") or {}
        nombre = parametros.get("model") or parametros.get("model_name") or "modelo"
        self._modelo_por_llamada[kwargs.get("run_id")] = str(nombre).replace("models/", "")

    def on_llm_end(self, response, **kwargs) -> None:
        nombre = self._modelo_por_llamada.get(kwargs.get("run_id"))
        if nombre and nombre not in self.modelos_ok:
            self.modelos_ok.append(nombre)
        for generaciones in response.generations:
            for generacion in generaciones:
                mensaje = getattr(generacion, "message", None)
                uso = getattr(mensaje, "usage_metadata", None) or {}
                self.tokens_entrada += uso.get("input_tokens", 0) or 0
                self.tokens_salida += uso.get("output_tokens", 0) or 0

    def on_llm_error(self, error, **kwargs) -> None:
        nombre = self._modelo_por_llamada.get(kwargs.get("run_id"), "modelo")
        self.errores.append(f"{nombre}: {str(error)[:200]}")

    # --- Tools ---
    def on_tool_start(self, serialized, input_str, **kwargs) -> None:
        nombre = (serialized or {}).get("name") or kwargs.get("name") or "tool"
        self.tools.append(nombre)

    def on_tool_error(self, error, **kwargs) -> None:
        self.errores.append(f"Tool: {str(error)[:200]}")


class MedidorEjecucion:
    """Toma el tiempo de una respuesta y arma el registro de métricas."""

    def __init__(self, mensaje: str) -> None:
        self.mensaje = mensaje
        self.callback = MetricasCallback()
        self._inicio = time.perf_counter()

    def resultado(self, ruta: str = "", error: str | None = None) -> dict:
        cb = self.callback
        errores = list(cb.errores)
        if error and not any(error[:80] in e for e in errores):
            errores.append(error[:200])

        registro = {
            "hora": ahora().strftime("%H:%M:%S"),
            "mensaje": self.mensaje[:60],
            "ruta": ruta or "-",
            "tiempo_s": round(time.perf_counter() - self._inicio, 2),
            "llamadas_modelo": cb.llamadas_modelo,
            "tokens_entrada": cb.tokens_entrada,
            "tokens_salida": cb.tokens_salida,
            "tokens_total": cb.tokens_entrada + cb.tokens_salida,
            "tools": ", ".join(cb.tools) or "ninguna",
            "modelos": ", ".join(cb.modelos_ok) or "ninguno",
            "errores": len(errores),
            "detalle_errores": errores,
        }
        logger.info("METRICAS %s", json.dumps(registro, ensure_ascii=False))
        return registro
