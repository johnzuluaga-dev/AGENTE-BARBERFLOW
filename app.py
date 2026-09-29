"""Interfaz Streamlit de BarberFlow v2 con LangChain."""

import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    actualizar_estado_cliente,
    agregar_mensaje,
    inicializar_estado,
    obtener_memoria,
    registrar_ejecucion,
    reiniciar_estado,
)

st.set_page_config(page_title="BarberFlow", page_icon="💈")

try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()

inicializar_estado()

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
    st.subheader("Última ejecución")

    ejecucion = st.session_state.ultima_ejecucion
    st.write("Ruta:", ejecucion["ruta"])

    if ejecucion["motivo"]:
        st.caption(ejecucion["motivo"])

    if ejecucion["tools"]:
        st.write("Tools utilizadas:")
        for nombre in ejecucion["tools"]:
            st.write(f"- {nombre}")
    else:
        st.write("Tools utilizadas: ninguna")

    st.divider()

    if st.button("Reiniciar conversación"):
        reiniciar_estado()
        st.rerun()

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

prompt = st.chat_input("Escribe tu mensaje...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_estado_cliente(prompt)
    agregar_mensaje("user", prompt)

    try:
        resultado = responder(
            mensaje_usuario=prompt,
            cliente=st.session_state.cliente,
            memoria=obtener_memoria(),
        )
        respuesta = resultado["respuesta"]
        registrar_ejecucion(resultado)
    except Exception as error:
        respuesta = f"Ocurrió un error al procesar la solicitud: {error}"

    with st.chat_message("assistant"):
        st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)
    st.rerun()