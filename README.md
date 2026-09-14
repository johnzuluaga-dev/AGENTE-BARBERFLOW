# BarberFlow

Agente de agendamiento de citas para una barbería, construido con Streamlit
y Gemini (function calling).

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

Configura `GEMINI_API_KEY` en un archivo `.env` en la raíz del proyecto.
