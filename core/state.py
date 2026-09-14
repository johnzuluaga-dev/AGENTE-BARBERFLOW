import re

import streamlit as st

CLIENTE_INICIAL = {
    "nombre": "No registrado",
}

def inicializar_estado() -> None:

    if "cliente" not in st.session_state:

        st.session_state.cliente = (
            CLIENTE_INICIAL.copy()
        )

    if "mensajes" not in st.session_state:

        st.session_state.mensajes = []

def actualizar_estado_cliente(
    texto: str
) -> None:

    patron_nombre = (
        r"(?:soy|me llamo)\s+"
        r"([A-Za-zÁÉÍÓÚáéíóúÑñ]+)"
    )

    coincidencia = re.search(
        patron_nombre,
        texto,
        re.IGNORECASE
    )

    if coincidencia:

        st.session_state.cliente[
            "nombre"
        ] = coincidencia.group(1).capitalize()

def agregar_mensaje(
    role: str,
    content: str
) -> None:

    st.session_state.mensajes.append(
        {
            "role": role,
            "content": content
        }
    )

def obtener_memoria(
    limite: int = 6
) -> str:

    mensajes = (
        st.session_state.mensajes[-limite:]
    )

    return "\n".join(
        f"{mensaje['role']}: "
        f"{mensaje['content']}"
        for mensaje in mensajes
    )

def reiniciar_estado() -> None:

    st.session_state.mensajes = []

    st.session_state.cliente = (
        CLIENTE_INICIAL.copy()
    )
