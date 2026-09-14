from datetime import date

import streamlit as st

from tools.cita_tool import listar_citas

st.set_page_config(
    page_title="BarberFlow · Panel del barbero",
    page_icon="🗓️",
)

st.title("🗓️ Panel del barbero")

st.caption(
    "Consulta de solo lectura. Para cancelar o "
    "modificar una cita, hazlo manualmente en el "
    "archivo de citas."
)

citas = sorted(
    listar_citas(),
    key=lambda cita: (cita["fecha"], cita["hora"]),
)

if not citas:

    st.info("Aún no hay citas agendadas.")

    st.stop()

fechas_disponibles = sorted(
    {cita["fecha"] for cita in citas}
)

filtro_fecha = st.selectbox(
    "Filtrar por fecha",
    options=["Todas"] + fechas_disponibles,
    index=(
        ["Todas"] + fechas_disponibles
    ).index(date.today().isoformat())
    if date.today().isoformat() in fechas_disponibles
    else 0,
)

citas_filtradas = (
    citas
    if filtro_fecha == "Todas"
    else [cita for cita in citas if cita["fecha"] == filtro_fecha]
)

st.write(f"**{len(citas_filtradas)}** cita(s)")

st.dataframe(
    [
        {
            "Fecha": cita["fecha"],
            "Hora": cita["hora"],
            "Cliente": cita["cliente"],
            "Servicio": cita["servicio"],
            "Duración (min)": cita["duracion_minutos"],
            "Precio": cita["precio"],
            "Estado": cita.get("estado", "confirmada"),
        }
        for cita in citas_filtradas
    ],
    use_container_width=True,
    hide_index=True,
)
