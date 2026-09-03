import streamlit as st

from config.settings import (
    validar_configuracion
)

from core.agent import responder

from core.state import (
    agregar_mensaje,
    actualizar_estado_estudiante,
    inicializar_estado,
    obtener_memoria,
    reiniciar_estado,
)

# ----------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------

st.set_page_config(
    page_title="Agente Académico",
    page_icon="🎓",
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
    "🎓 Agente Académico"
)

st.caption(
    "Universidad Católica Luis Amigó"
)

st.write(
    "MVP con Gemini, contexto, memoria, "
    "estado y una herramienta."
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
    "Escribe tu pregunta académica..."
)

if prompt:

    with st.chat_message("user"):

        st.markdown(prompt)

    actualizar_estado_estudiante(
        prompt
    )

    agregar_mensaje(
        "user",
        prompt
    )

    try:

        respuesta = responder(

            mensaje_usuario=prompt,

            estudiante=(
                st.session_state.estudiante
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
# ESTADO DEL ESTUDIANTE
# ----------------------------------------------

with st.sidebar:

    st.subheader(
        "Estado del estudiante"
    )

    estudiante = (
        st.session_state.estudiante
    )

    st.write(
        "Nombre:",
        estudiante["nombre"]
    )

    st.write(
        "Programa:",
        estudiante["programa"]
    )

    st.write(
        "Semestre:",
        estudiante["semestre"]
    )

    st.divider()

    if st.button(
        "Reiniciar conversación"
    ):

        reiniciar_estado()

        st.rerun()