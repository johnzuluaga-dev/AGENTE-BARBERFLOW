"""Interfaz Streamlit de BarberFlow v3 con LangGraph."""

import streamlit as st

from config.settings import validar_configuracion
from core.estilos import aplicar_estilos
from core.session import (
    actualizar_estado_cliente,
    diagrama_mermaid,
    inicializar_sesion,
    obtener_historial,
    reiniciar_sesion,
    responder,
)

st.set_page_config(page_title="BarberFlow", page_icon="💈")

# Solo apariencia visual (CSS); no cambia el funcionamiento.
aplicar_estilos("chat")

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

    st.divider()
    st.subheader("Métricas")

    historial_metricas = st.session_state.historial_metricas
    if historial_metricas:
        ultima = historial_metricas[-1]
        col1, col2 = st.columns(2)
        col1.metric("Tiempo", f"{ultima['tiempo_s']} s")
        col2.metric("Llamadas IA", ultima["llamadas_modelo"])
        col3, col4 = st.columns(2)
        col3.metric("Tokens", ultima["tokens_total"])
        col4.metric("Errores", ultima["errores"])
        st.caption(
            f"Tokens de entrada: {ultima['tokens_entrada']} · "
            f"salida: {ultima['tokens_salida']}"
        )
        for detalle in ultima["detalle_errores"]:
            st.caption(f"⚠️ {detalle}")

        with st.expander(f"Historial de la sesión ({len(historial_metricas)})"):
            tiempos = [m["tiempo_s"] for m in historial_metricas]
            st.caption(
                f"Tiempo promedio: {sum(tiempos) / len(tiempos):.2f} s · "
                f"Tokens totales: {sum(m['tokens_total'] for m in historial_metricas)}"
            )
            st.dataframe(
                [
                    {
                        "Hora": m["hora"],
                        "Mensaje": m["mensaje"],
                        "Ruta": m["ruta"],
                        "Tiempo (s)": m["tiempo_s"],
                        "Llamadas": m["llamadas_modelo"],
                        "Tokens": m["tokens_total"],
                        "Tools": m["tools"],
                        "Errores": m["errores"],
                    }
                    for m in historial_metricas
                ],
                hide_index=True,
            )
    else:
        st.caption("Aún no hay métricas. Envía un mensaje para verlas.")

    st.divider()

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
        with st.spinner("Pensando tu respuesta…"):
            responder(prompt)
    except Exception as error:
        # El error no queda en el checkpoint, así que se muestra sin rerun.
        with st.chat_message("assistant"):
            st.markdown(f"Ocurrió un error al procesar la solicitud: {error}")
    else:
        st.rerun()
