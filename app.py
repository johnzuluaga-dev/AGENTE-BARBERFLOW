import streamlit as st

from config.settings import (
    validar_configuracion
)

from core.agent import responder

from core.state import (
    agregar_mensaje,
    actualizar_estado_cliente,
    inicializar_estado,
    obtener_memoria,
    reiniciar_estado,
)

# ----------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------

st.set_page_config(
    page_title="BarberFlow",
    page_icon="💈",
)

try:

    validar_configuracion()

except ValueError as error:

    st.error(str(error))

    st.stop()

inicializar_estado()

# ----------------------------------------------
# INTERFAZ
# ----------------------------------------------

st.title(
    "💈 BarberFlow"
)

st.caption(
    "Agenda tu cita conversando con nuestro asistente"
)

st.write(
    "Cuéntame qué servicio quieres, para qué día y "
    "hora, y te confirmo la cita según la "
    "disponibilidad real del barbero."
)

# ----------------------------------------------
# HISTORIAL
# ----------------------------------------------

for mensaje in (
    st.session_state.mensajes
):

    with st.chat_message(
        mensaje["role"]
    ):

        st.markdown(
            mensaje["content"]
        )

# ----------------------------------------------
# MENSAJE DEL USUARIO
# ----------------------------------------------

prompt = st.chat_input(
    "Escribe tu mensaje..."
)

if prompt:

    with st.chat_message("user"):

        st.markdown(prompt)

    actualizar_estado_cliente(
        prompt
    )

    agregar_mensaje(
        "user",
        prompt
    )

    try:

        respuesta = responder(

            mensaje_usuario=prompt,

            cliente=(
                st.session_state.cliente
            ),

            memoria=obtener_memoria(),

        )

    except Exception as error:

        respuesta = (
            "Ocurrió un error al consultar "
            f"Gemini: {error}"
        )

    with st.chat_message(
        "assistant"
    ):

        st.markdown(
            respuesta
        )

    agregar_mensaje(
        "assistant",
        respuesta
    )

# ----------------------------------------------
# ESTADO DEL CLIENTE
# ----------------------------------------------

with st.sidebar:

    st.subheader(
        "Tus datos"
    )

    cliente = (
        st.session_state.cliente
    )

    st.write(
        "Nombre:",
        cliente["nombre"]
    )

    st.divider()

    if st.button(
        "Reiniciar conversación"
    ):

        reiniciar_estado()

        st.rerun()
