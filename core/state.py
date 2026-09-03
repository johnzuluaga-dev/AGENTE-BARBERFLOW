import re

import streamlit as st

ESTUDIANTE_INICIAL = {
    "nombre": "No registrado",
    "programa": "No registrado",
    "semestre": "No registrado",
}

SEMESTRES = {

    "primer semestre": "1",
    "segundo semestre": "2",
    "tercer semestre": "3",
    "cuarto semestre": "4",
    "quinto semestre": "5",
    "sexto semestre": "6",
    "séptimo semestre": "7",
    "septimo semestre": "7",
    "octavo semestre": "8",
    "noveno semestre": "9",
    "décimo semestre": "10",
    "decimo semestre": "10",

}

CONECTORES_PROGRAMA = {"de", "y"}

def _formatear_programa(texto: str) -> str:

    palabras = texto.strip().split()

    return " ".join(
        palabra.lower()
        if palabra.lower() in CONECTORES_PROGRAMA and indice != 0
        else palabra.capitalize()
        for indice, palabra in enumerate(palabras)
    )

def inicializar_estado() -> None:

    if "estudiante" not in st.session_state:

        st.session_state.estudiante = (
            ESTUDIANTE_INICIAL.copy()
        )

    if "mensajes" not in st.session_state:

        st.session_state.mensajes = []

def actualizar_estado_estudiante(
    texto: str
) -> None:

    texto_lower = texto.lower()

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

        st.session_state.estudiante[
            "nombre"
        ] = coincidencia.group(1).capitalize()

    patron_programa = (
        r"de\s+([A-Za-zÁÉÍÓÚáéíóúÑñ]+"
        r"(?:\s+[A-Za-zÁÉÍÓÚáéíóúÑñ]+)*?)"
        r"\s+de\s+\d{1,2}"
    )

    coincidencia_programa = re.search(
        patron_programa,
        texto,
        re.IGNORECASE
    )

    if coincidencia_programa:

        st.session_state.estudiante[
            "programa"
        ] = _formatear_programa(
            coincidencia_programa.group(1)
        )

    elif (
        "ingeniería de sistemas" in texto_lower
        or "ingenieria de sistemas" in texto_lower
    ):

        st.session_state.estudiante[
            "programa"
        ] = "Ingeniería de Sistemas"

    patron_semestre_numero = (
        r"(\d{1,2})\s*"
        r"(?:er|ro|do|to|vo|mo|no)?\s*"
        r"semestre"
    )

    coincidencia_semestre = re.search(
        patron_semestre_numero,
        texto_lower
    )

    if coincidencia_semestre:

        st.session_state.estudiante[
            "semestre"
        ] = coincidencia_semestre.group(1)

    else:

        for descripcion, numero in SEMESTRES.items():

            if descripcion in texto_lower:

                st.session_state.estudiante[
                    "semestre"
                ] = numero

                break

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

    st.session_state.estudiante = (
        ESTUDIANTE_INICIAL.copy()
    )