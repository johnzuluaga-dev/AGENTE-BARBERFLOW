# BarberFlow

Agente de agendamiento de citas para una barbería, construido con Streamlit,
Gemini y LangGraph (v03).

## documentacion y algunos commits hechos con la IA

## Qué hace

- El **cliente** conversa con el asistente en la página principal para
  agendar su cita: el agente entiende la solicitud, consulta disponibilidad
  real y confirma la cita solo cuando el cliente confirma servicio, fecha y
  hora.
- El **barbero/administrador** revisa la agenda en el panel
  "Panel del barbero" (solo lectura).

## Datos

- `data/servicios.json`: catálogo de servicios y precios.
- `data/horarios.json`: horario laboral del barbero por día de la semana.
- `data/citas.json`: citas ya agendadas.

## Arquitectura (v03 con LangGraph)

```
START → enrutador ─┬─ conceptual ─────────────→ nodo_conceptual → END
                   └─ herramientas → agente_barberia ⇄ herramientas (ToolNode)
                                           └─ sin tool calls → END
```

- `graph/state.py`: `BarberState` (mensajes con el reducer `add_messages`,
  cliente, ruta, motivo, herramientas usadas y traza de nodos).
- `graph/nodes.py`: nodos enrutador, conceptual, agente y herramientas.
- `graph/workflow.py`: topología del grafo y compilación con `MemorySaver`.
- `core/session.py`: un `thread_id` por sesión e invocación del grafo.
- `tools/__init__.py`: lista `TOOLS_BARBERIA` con las 6 tools.

## Herramientas del agente

- `consultar_disponibilidad(fecha, servicio)`: calcula horarios libres
  cruzando el horario laboral con las citas ya agendadas.
- `agendar_cita(cliente, servicio, fecha, hora)`: valida que el servicio y el
  horario sean reales y disponibles, y registra la cita.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Configura `GEMINI_API_KEY` (y opcionalmente `GEMINI_MODEL`) en un archivo
`.env` en la raíz del proyecto.
