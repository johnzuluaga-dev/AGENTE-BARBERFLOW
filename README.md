# BarberFlow

Agente de agendamiento de citas para una barbería, construido con Streamlit,
Gemini, LangChain y LangGraph.

- **App desplegada:** https://agente-barberflow-1.onrender.com
- **Pruebas, hallazgos y métricas:** [PRUEBAS.md](PRUEBAS.md)

## Qué hace

- El **cliente** conversa con el asistente en la página principal para
  agendar su cita: el agente entiende la solicitud, consulta la
  disponibilidad real y confirma la cita solo cuando el cliente confirma
  servicio, fecha y hora.
- El asistente también responde preguntas sobre la barbería (horario, formas
  de pago, cancelaciones, cuidados, etc.) buscando en su base de
  conocimiento (**RAG**).
- El **barbero/administrador** revisa la agenda en la página
  "Panel del barbero" (solo lectura).
- La barra lateral muestra cómo trabajó el agente en cada respuesta: ruta,
  nodos recorridos, tools usadas y **métricas** (tiempo, llamadas al modelo,
  tokens y errores).

## Datos

- `data/servicios.json`: catálogo de servicios y precios.
- `data/horarios.json`: horario laboral del barbero por día de la semana.
- `data/citas.json`: citas ya agendadas.
- `data/conocimiento/barberia.md`: información de la barbería que usa el RAG.

## Arquitectura (LangGraph)

```
START → enrutador ─┬─ conceptual ─────────────→ nodo_conceptual → END
                   └─ herramientas → agente_barberia ⇄ herramientas (ToolNode)
                                           └─ sin tool calls → END
```

- `graph/state.py`: `BarberState` (mensajes con el reducer `add_messages`,
  cliente, ruta, motivo, herramientas usadas y traza de nodos).
- `graph/nodes.py`: nodos enrutador, conceptual, agente y herramientas. Los
  saludos simples ("hola", "gracias") van directo al nodo conceptual sin
  gastar una llamada al modelo.
- `graph/workflow.py`: conexiones del grafo y compilación con `MemorySaver`
  (memoria de la conversación).
- `core/session.py`: un `thread_id` por sesión, invocación del grafo y
  registro de métricas.
- `core/metricas.py`: mide tiempo, llamadas al modelo, tokens, tools y
  errores de cada respuesta, y los escribe en los logs del servidor.
- `core/estilos.py` y `.streamlit/config.toml`: diseño visual de la interfaz.
- `tools/__init__.py`: lista `TOOLS_BARBERIA` con las 7 tools.

## Herramientas del agente

| Tool | Qué hace |
|---|---|
| `obtener_fecha` | Fecha, día y hora actuales (para entender "mañana", "el viernes"). |
| `consultar_servicios` | Catálogo real de servicios, duración y precios. |
| `consultar_disponibilidad` | Horarios libres de una fecha, cruzando el horario laboral con las citas. |
| `agendar_cita` | Valida y registra la cita (solo tras la confirmación del cliente). |
| `consultar_citas` | Citas ya agendadas por cliente y/o fecha. |
| `priorizar_citas` | Ordena las citas de un día con una chain de LangChain. |
| `consultar_informacion_barberia` | **RAG**: busca en la información de la barbería. |

## RAG (búsqueda en la información de la barbería)

1. `data/conocimiento/barberia.md` se divide en fragmentos (uno por sección).
2. Cada fragmento se convierte en un vector con el modelo de embeddings de
   Gemini (`gemini-embedding-001`) y se guarda en un `InMemoryVectorStore`.
3. Ante una pregunta, la tool busca los 3 fragmentos más parecidos y el
   agente responde solo con esa información.
4. Si los embeddings fallan, se usa una búsqueda por palabras como respaldo.
   La tool informa qué método usó (`metodo_busqueda`).

## Métricas y observabilidad

Cada respuesta registra: tiempo total, llamadas al modelo, tokens de
entrada/salida, tools usadas, modelo que respondió y errores. Se ven en:

- la barra lateral de la app (última respuesta + historial de la sesión);
- los logs del servidor (en Render: pestaña **Logs**), en líneas que
  empiezan por `METRICAS`.

## Modelo de respaldo

Todas las llamadas al modelo usan `with_fallbacks` de LangChain: si
`GEMINI_MODEL` falla (por ejemplo, error 503 por alta demanda o falta de
cupo), la misma petición se repite con `GEMINI_MODEL_RESPALDO`. Después de una
falla, el modelo principal queda **en pausa 10 minutos**
(`PAUSA_MODELO_PRINCIPAL`) y todas las llamadas van directo al respaldo, para
no esperar al modelo que está fallando en cada paso. Las métricas muestran qué
modelo respondió y qué fallos hubo.

## Instalar y ejecutar

1. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # macOS / Linux
   source venv/bin/activate
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Crear un archivo `.env` en la raíz del proyecto:

   ```
   GEMINI_API_KEY=tu_clave
   GEMINI_MODEL=gemini-3.8-flash
   ```

   Variables opcionales: `GEMINI_MODEL_RESPALDO` (por defecto
   `gemini-3.5-flash-lite`), `GEMINI_EMBEDDING_MODEL` (por defecto
   `gemini-embedding-001`), `TIEMPO_ESPERA_MODELO` (segundos de espera por llamada, por defecto 20)
   `REINTENTOS_MODELO` (intentos totales por modelo, por defecto 1) y
   `PAUSA_MODELO_PRINCIPAL` (segundos, por defecto 600).

4. Ejecutar:

   ```bash
   streamlit run app.py
   ```

## Despliegue (Render)

- Comando de construcción: `pip install -r requirements.txt`
- Comando de inicio (ejemplo): `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Variables de entorno en Render → Environment: `GEMINI_API_KEY` y
  `GEMINI_MODEL`.
- En el plan gratis la app se apaga si nadie la usa; la primera visita puede
  tardar cerca de un minuto en abrir.
- La memoria de la conversación y las citas nuevas se guardan en el servidor,
  así que se borran cuando Render reinicia la app.
