"""Interfaz Streamlit de BarberFlow v3 con LangGraph."""

import streamlit as st

from config.settings import validar_configuracion
from core.session import (
    actualizar_estado_cliente,
    diagrama_mermaid,
    inicializar_sesion,
    obtener_historial,
    reiniciar_sesion,
    responder,
)

st.set_page_config(page_title="BarberFlow", page_icon="💈")

try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()

inicializar_sesion()

st.title("💈 BarberFlow")
st.caption("Agenda tu cita conversando con nuestro asistente")
st.write(
    "Cuéntame qué servicio quieres, para qué día y hora, y te confirmo la "
    "cita según la disponibilidad real del barbero."
)

with st.sidebar:
    st.subheader("Tus datos")
    st.write("Nombre:", st.session_state.cliente["nombre"])

    st.divider()
    st.subheader("Sesión")
    st.caption(f"Thread ID: `{st.session_state.thread_id}`")

    st.divider()
    st.subheader("Última ejecución")

    ejecucion = st.session_state.ultima_ejecucion
    st.write("Ruta:", ejecucion["ruta"])

    if ejecucion["motivo"]:
        st.caption(ejecucion["motivo"])

    if ejecucion["pasos"]:
        st.write("Nodos recorridos:")
        st.code(" → ".join(ejecucion["pasos"]), language=None)

    if ejecucion["tools"]:
        st.write("Tools utilizadas:")
        for nombre in ejecucion["tools"]:
            st.write(f"- {nombre}")
    else:
        st.write("Tools utilizadas: ninguna")

    with st.expander("Diagrama del grafo (Mermaid)"):
        st.code(diagrama_mermaid(), language="mermaid")

    st.divider()

    if st.button("Reiniciar conversación"):
        reiniciar_sesion()
        st.rerun()

for mensaje in obtener_historial():
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

prompt = st.chat_input("Escribe tu mensaje...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_estado_cliente(prompt)

    try:
        responder(prompt)
    except Exception as error:
        # El error no queda en el checkpoint, así que se muestra sin rerun.
        with st.chat_message("assistant"):
            st.markdown(f"Ocurrió un error al procesar la solicitud: {error}")
    else:
        st.rerun()
