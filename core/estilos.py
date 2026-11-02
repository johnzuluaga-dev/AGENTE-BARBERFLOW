"""Estilos visuales de BarberFlow.

Este archivo solo contiene CSS (apariencia) y un pequeño script que marca la
página en español. No tiene lógica de la app: no lee datos, no cambia el
estado y no llama al agente.
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Estilos comunes a todas las páginas
# ---------------------------------------------------------------------------
_CSS_BASE = """
<style>
:root {
    --bf-cobre: #B4532A;
    --bf-cobre-oscuro: #8F3F1D;
    --bf-cobre-suave: #F6E6DA;
    --bf-laton: #D9A066;
    --bf-crema: #FBF8F3;
    --bf-arena: #F4EEE5;
    --bf-borde: #E6DCCD;
    --bf-texto: #1F1B17;
    --bf-texto-suave: #6E6359;
    --bf-espresso: #1B1714;
    --bf-sombra: 0 1px 2px rgba(31, 27, 23, 0.04), 0 6px 20px rgba(31, 27, 23, 0.06);
    --bf-sombra-hover: 0 2px 4px rgba(31, 27, 23, 0.06), 0 12px 28px rgba(31, 27, 23, 0.10);
    --bf-fuente: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
}

/* ---------- Fondo general ---------- */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1100px 420px at 85% -120px, rgba(217, 160, 102, 0.18), transparent 70%),
        radial-gradient(900px 380px at -10% -80px, rgba(180, 83, 42, 0.10), transparent 70%),
        var(--bf-crema);
}

[data-testid="stHeader"] {
    background: rgba(251, 248, 243, 0.72);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

[data-testid="stMainBlockContainer"] {
    padding-top: 3.5rem;
}

/* ---------- Título principal ---------- */
[data-testid="stMainBlockContainer"] h1 {
    font-size: 2.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.1;
    color: var(--bf-texto);
    padding-bottom: 1rem;
    margin-bottom: 0.6rem;
    position: relative;
}

/* Franja decorativa tipo poste de barbería bajo el título */
[data-testid="stMainBlockContainer"] h1::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: 0;
    width: 72px;
    height: 5px;
    border-radius: 999px;
    background: repeating-linear-gradient(
        -45deg,
        #B4532A 0 8px,
        #FBF8F3 8px 12px,
        #1F2A44 12px 20px,
        #FBF8F3 20px 24px
    );
    box-shadow: 0 0 0 1px rgba(31, 27, 23, 0.06);
}

/* ---------- Textos secundarios ---------- */
[data-testid="stMainBlockContainer"] [data-testid="stCaptionContainer"] {
    color: var(--bf-texto-suave);
    font-size: 0.98rem;
}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(217, 160, 102, 0.07), transparent 240px),
        var(--bf-espresso);
    border-right: 1px solid #2E2620;
}

[data-testid="stSidebar"] h3 {
    font-family: var(--bf-fuente);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--bf-laton);
    padding-bottom: 0.25rem;
}

[data-testid="stSidebar"] hr {
    margin: 1.1rem 0;
    border-color: rgba(237, 229, 216, 0.10);
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: rgba(237, 229, 216, 0.62);
}

[data-testid="stSidebar"] p {
    font-size: 0.92rem;
}

[data-testid="stSidebar"] li::marker {
    color: var(--bf-laton);
}

/* Navegación entre páginas */
[data-testid="stSidebarNavLink"] {
    border-radius: 10px;
    transition: background-color 0.2s ease;
}

[data-testid="stSidebarNavLink"]:hover {
    background-color: rgba(217, 160, 102, 0.10);
}

[data-testid="stSidebarNavLink"][aria-current="page"] {
    background-color: rgba(217, 160, 102, 0.16);
    box-shadow: inset 3px 0 0 var(--bf-laton);
}

[data-testid="stSidebarNavLink"] span {
    font-weight: 500;
}

/* Bloques de código en la barra lateral */
[data-testid="stSidebar"] [data-testid="stCode"] pre {
    border: 1px solid #3A3129;
    border-radius: 10px;
}

[data-testid="stSidebar"] [data-testid="stCode"] code {
    white-space: pre-wrap !important;
    word-break: break-word;
    font-size: 0.8rem;
    line-height: 1.6;
}

[data-testid="stSidebar"] p code {
    font-size: 0.75rem;
    word-break: break-all;
}

/* Expansor de la barra lateral */
[data-testid="stSidebar"] [data-testid="stExpander"] details {
    border-color: #3A3129;
    background-color: rgba(255, 255, 255, 0.02);
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
    color: var(--bf-laton);
}

/* Botón de la barra lateral */
[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border: 1px solid rgba(217, 160, 102, 0.55);
    background: transparent;
    color: var(--bf-laton);
    font-weight: 600;
    letter-spacing: 0.01em;
    transition: background-color 0.2s ease, color 0.2s ease, transform 0.15s ease;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: var(--bf-laton);
    border-color: var(--bf-laton);
    color: var(--bf-espresso);
}

[data-testid="stSidebar"] .stButton button:active {
    transform: scale(0.98);
}

/* Métricas de la barra lateral */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid #3A3129;
    border-radius: 12px;
    padding: 0.55rem 0.7rem;
}

[data-testid="stSidebar"] [data-testid="stMetricLabel"] p {
    font-size: 0.7rem;
    letter-spacing: 0.04em;
    color: rgba(237, 229, 216, 0.65);
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 1.35rem;
    color: #EDE5D8;
}

/* Indicador de "pensando…" */
[data-testid="stSpinner"] {
    color: var(--bf-texto-suave);
    font-style: italic;
}

/* ---------- Avisos ---------- */
[data-testid="stAlert"] {
    border-radius: 14px;
}
</style>
"""

# ---------------------------------------------------------------------------
# Estilos de la página del chat (app.py)
# ---------------------------------------------------------------------------
_CSS_CHAT = """
<style>
/* Texto de bienvenida bajo el subtítulo, presentado como tarjeta */
[data-testid="stMainBlockContainer"]
    [data-testid="stElementContainer"]:has([data-testid="stCaptionContainer"])
    + [data-testid="stElementContainer"]
    [data-testid="stMarkdownContainer"] {
    background: #FFFFFF;
    border: 1px solid var(--bf-borde);
    border-left: 4px solid var(--bf-cobre);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    box-shadow: var(--bf-sombra);
    margin-bottom: 0.75rem;
}

[data-testid="stMainBlockContainer"]
    [data-testid="stElementContainer"]:has([data-testid="stCaptionContainer"])
    + [data-testid="stElementContainer"]
    [data-testid="stMarkdownContainer"] p {
    margin: 0;
    color: #3D352E;
}

/* ---------- Mensajes del chat ---------- */
[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid var(--bf-borde);
    border-radius: 18px;
    border-top-left-radius: 6px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.4rem;
    box-shadow: var(--bf-sombra);
    animation: bf-aparecer 0.35s ease both;
    max-width: 88%;
}

/* Mensajes del usuario: a la derecha y con tono cobre */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
    margin-left: auto;
    background: linear-gradient(135deg, #F8EADF, #F3DFD0);
    border-color: #EBCDB8;
    border-radius: 18px;
    border-top-right-radius: 6px;
    width: fit-content;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
    [data-testid="stChatMessageContent"] {
    margin-left: 0;
    margin-right: 0.6rem;
}

[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li {
    line-height: 1.6;
}

[data-testid="stChatMessageContent"] li::marker {
    color: var(--bf-cobre);
}

/* Avatares */
[data-testid="stChatMessageAvatarUser"] {
    background: linear-gradient(135deg, #C8663A, var(--bf-cobre-oscuro));
    color: #FFFFFF;
    box-shadow: 0 2px 6px rgba(143, 63, 29, 0.30);
}

[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, #2B241F, var(--bf-espresso));
    color: var(--bf-laton);
    box-shadow: 0 2px 6px rgba(27, 23, 20, 0.30);
}

/* ---------- Caja para escribir ---------- */
[data-testid="stBottom"] > div {
    background: linear-gradient(180deg, rgba(251, 248, 243, 0), var(--bf-crema) 35%);
}

[data-testid="stChatInput"] {
    background: #FFFFFF;
    border: 1px solid var(--bf-borde);
    border-radius: 18px;
    box-shadow: var(--bf-sombra);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

[data-testid="stChatInput"] > div {
    background: #FFFFFF;
    border-radius: 18px;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--bf-cobre);
    box-shadow: 0 0 0 4px rgba(180, 83, 42, 0.12), var(--bf-sombra);
}

[data-testid="stChatInputSubmitButton"] {
    border-radius: 12px;
    transition: transform 0.15s ease;
}

[data-testid="stChatInputSubmitButton"]:not(:disabled) {
    background: var(--bf-cobre);
    color: #FFFFFF;
}

[data-testid="stChatInputSubmitButton"]:not(:disabled):hover {
    background: var(--bf-cobre-oscuro);
    transform: translateY(-1px);
}

@keyframes bf-aparecer {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
    [data-testid="stChatMessage"] { animation: none; }
}

@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] h1 { font-size: 2.1rem; }
    [data-testid="stChatMessage"] { max-width: 100%; }
}
</style>
"""

# ---------------------------------------------------------------------------
# Estilos del panel del barbero (pages/1_Panel_Barbero.py)
# ---------------------------------------------------------------------------
_CSS_PANEL = """
<style>
/* Nota de "solo lectura" bajo el título */
[data-testid="stMainBlockContainer"]
    [data-testid="stElementContainer"]:has([data-testid="stHeading"])
    + [data-testid="stElementContainer"]
    [data-testid="stCaptionContainer"] {
    background: rgba(255, 255, 255, 0.7);
    border: 1px dashed #DCCBB6;
    border-radius: 12px;
    padding: 0.65rem 0.95rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
}

[data-testid="stMainBlockContainer"]
    [data-testid="stElementContainer"]:has([data-testid="stHeading"])
    + [data-testid="stElementContainer"]
    [data-testid="stCaptionContainer"] p {
    margin: 0;
}

/* Filtro de fecha */
[data-testid="stSelectbox"] {
    max-width: 360px;
}

[data-testid="stSelectbox"] label p {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--bf-texto-suave);
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #FFFFFF;
    box-shadow: var(--bf-sombra);
}

/* Contador de citas como etiqueta */
[data-testid="stElementContainer"]:has(+ [data-testid="stElementContainer"] [data-testid="stDataFrame"])
    [data-testid="stMarkdownContainer"] p {
    display: inline-block;
    margin: 0.5rem 0 0;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    background: var(--bf-cobre-suave);
    color: var(--bf-cobre-oscuro);
    font-size: 0.88rem;
    border: 1px solid #EBCDB8;
}

/* Tabla de citas */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    box-shadow: var(--bf-sombra);
    transition: box-shadow 0.2s ease;
}

[data-testid="stDataFrame"]:hover {
    box-shadow: var(--bf-sombra-hover);
}

@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] h1 { font-size: 2.1rem; }
    [data-testid="stSelectbox"] { max-width: 100%; }
}
</style>
"""

_CSS_POR_PAGINA = {"chat": _CSS_CHAT, "panel": _CSS_PANEL}


# Streamlit marca la página como inglés (<html lang="en">), así que Chrome
# ofrecía "traducirla" y cambiaba textos ("app" -> "aplicación",
# "solo lectura" -> "lectura en solitario"). Este script marca la página
# como español y desactiva la traducción automática.
_SCRIPT_IDIOMA = """
<script>
  const raiz = window.parent.document.documentElement;
  raiz.lang = "es";
  raiz.setAttribute("translate", "no");
  raiz.classList.add("notranslate");
</script>
"""

_CSS_OCULTAR_SCRIPT = """
<style>
[data-testid="stElementContainer"]:has(iframe[height="0"]) {
    display: none;
}
</style>
"""


@st.cache_resource
def _marcar_index_en_espanol() -> bool:
    """Marca en español el index.html que Streamlit envía al navegador.

    El script de arriba llega tarde para Chrome cuando ya tiene activada la
    traducción automática del inglés: la decide al cargar la página. Por eso,
    una sola vez al arrancar, se cambia lang="en" por lang="es" y se agrega
    la etiqueta que le pide a Google no traducir. Si el archivo no se puede
    modificar, la app sigue igual.
    """
    try:
        index = Path(st.__file__).parent / "static" / "index.html"
        html = index.read_text(encoding="utf-8")
        if 'lang="es"' in html:
            return True
        html = html.replace('<html lang="en">', '<html lang="es" translate="no">', 1)
        html = html.replace(
            "<head>", '<head><meta name="google" content="notranslate" />', 1
        )
        index.write_text(html, encoding="utf-8")
        return True
    except OSError:
        return False


def aplicar_estilos(pagina: str = "chat") -> None:
    """Inyecta el CSS visual de la página indicada ("chat" o "panel")."""
    _marcar_index_en_espanol()
    st.html(_CSS_BASE + _CSS_POR_PAGINA.get(pagina, "") + _CSS_OCULTAR_SCRIPT)
    components.html(_SCRIPT_IDIOMA, height=0)
