import streamlit as st
import pandas as pd
import hmac
import html
import os
import sqlite3
import unicodedata
import urllib.parse
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Personería al Día | Consulta Predial",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ESTILOS
# ------------------------------------------------------------
# Tema CLARO fijo. Los colores del tema están en .streamlit/config.toml,
# pero aquí se fijan también de forma explícita para que la app se vea
# igual aunque el navegador tenga modo oscuro o un tema oscuro guardado
# en caché (Streamlit guarda la preferencia en localStorage y esta tiene
# prioridad sobre config.toml).
#
# Paleta:
#   Fondo general      #f4f7fa
#   Texto principal    #173f61
#   Azul institucional #174f7a
#   Verde              #23844d
# ============================================================

st.markdown(
    r"""
<style>
/* ---------- 1. Base: esquema claro y color de texto global ---------- */
:root { color-scheme: light; }

html, body, .stApp {
    background-color: #f4f7fa;
    color: #173f61;
}

.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(35,132,77,.09), transparent 27%),
        radial-gradient(circle at 92% 0%, rgba(23,79,122,.12), transparent 30%),
        linear-gradient(180deg, #edf4f8 0%, #f8fafc 48%, #eef4f8 100%);
}

/* Barra superior de Streamlit transparente (en modo oscuro se ve negra) */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Texto de markdown nativo (st.markdown, st.write, contenido de expanders) */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] ol,
[data-testid="stMarkdownContainer"] ul {
    color: #173f61;
}

/* Contenedor principal */
[data-testid="stMainBlockContainer"],
.main .block-container {
    max-width: 1160px;
    padding: 28px 28px 55px 28px;
}

#MainMenu, footer { visibility: hidden; }

/* ---------- 2. Buscador (st.selectbox) ----------
   Se cubren las dos estructuras internas que ha usado Streamlit:
   - versiones recientes: React Aria  ([role="group"], [role="combobox"])
   - versiones anteriores: BaseWeb    ([data-baseweb="select"])           */
div[data-testid="stSelectbox"] [role="group"],
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 2px solid #d5e0e8 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    box-shadow: 0 4px 14px rgba(31,61,84,.05);
}
div[data-testid="stSelectbox"] [role="group"]:focus-within,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
    border-color: #174f7a !important;
    box-shadow: 0 0 0 3px rgba(23,79,122,.12) !important;
}
/* Texto escrito y valor seleccionado */
div[data-testid="stSelectbox"] input,
div[data-testid="stSelectbox"] [role="group"] *,
div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #173f61 !important;
    -webkit-text-fill-color: #173f61 !important;
    background-color: transparent;
}
div[data-testid="stSelectbox"] input {
    font-size: 15px !important;
}
/* Placeholder */
div[data-testid="stSelectbox"] input::placeholder {
    color: #6b7f90 !important;
    -webkit-text-fill-color: #6b7f90 !important;
    opacity: 1 !important;
}
/* Iconos (flecha, borrar) */
div[data-testid="stSelectbox"] svg {
    fill: #174f7a !important;
    color: #174f7a !important;
}

/* Lista desplegable: se dibuja fuera de .stApp (capa flotante) */
[data-testid="stSelectboxVirtualDropdown"],
[data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul[role="listbox"] {
    background-color: #ffffff !important;
    border-color: #d5e0e8 !important;
}
[data-testid="stSelectboxVirtualDropdown"] [role="option"],
div[data-baseweb="popover"] [role="option"] {
    background-color: #ffffff !important;
    color: #173f61 !important;
}
[data-testid="stSelectboxVirtualDropdown"] [role="option"] *,
[data-testid="stSelectboxVirtualDropdown"] *,
div[data-baseweb="popover"] [role="option"] * {
    color: #173f61 !important;
    -webkit-text-fill-color: #173f61 !important;
}
/* Opción resaltada (mouse o teclado) */
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-hovered],
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background-color: #e6eff6 !important;
}

/* ---------- 3. Botones (descarga y enlace de correo) ---------- */
[data-testid="stDownloadButton"] button,
[data-testid="stLinkButton"] a,
.stButton > button {
    background-color: #174f7a !important;
    border: 1px solid #174f7a !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] button *,
[data-testid="stLinkButton"] a,
[data-testid="stLinkButton"] a *,
.stButton > button,
.stButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 750 !important;
}
[data-testid="stDownloadButton"] button:hover,
[data-testid="stLinkButton"] a:hover,
.stButton > button:hover {
    background-color: #123f63 !important;
    border-color: #123f63 !important;
}

/* ---------- 4. Expanders ---------- */
div[data-testid="stExpander"] details {
    background-color: #ffffff !important;
    border: 1px solid #dce5ec !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] summary {
    background-color: #ffffff !important;
    color: #173f61 !important;
    border-radius: 12px;
}
div[data-testid="stExpander"] summary:hover {
    background-color: #f0f5f9 !important;
}
div[data-testid="stExpander"] summary *,
div[data-testid="stExpanderDetails"],
div[data-testid="stExpanderDetails"] * {
    color: #173f61 !important;
}
div[data-testid="stExpander"] summary svg {
    fill: #174f7a !important;
}

/* ---------- 5. Mensajes (st.info, st.warning, st.error) ---------- */
div[data-testid="stAlert"] > div {
    background-color: #e8f1f8 !important;
    border: 1px solid #c8dbe9 !important;
    border-radius: 12px !important;
}
div[data-testid="stAlert"],
div[data-testid="stAlert"] * {
    color: #174f7a !important;
}

/* ---------- 6. Barra de progreso ---------- */
div[data-testid="stProgress"] p,
div[data-testid="stProgress"] [data-testid="stMarkdownContainer"] p {
    color: #173f61 !important;
    font-weight: 700;
}
div[data-testid="stProgress"] [role="progressbar"] > div {
    background-color: #dfe8ef !important;
}
div[data-testid="stProgress"] [role="progressbar"] > div > div {
    background-color: #23844d !important;
}

/* ---------- 7. Tabla ---------- */
div[data-testid="stDataFrame"] {
    border: 1px solid #dfe7ed;
    border-radius: 12px;
    overflow: hidden;
    background-color: #ffffff;
}

/* ---------- 8. Componentes HTML propios ---------- */
.brand-bar {
    background: linear-gradient(115deg, #123f63 0%, #1d638b 68%, #23844d 100%);
    border-radius: 18px;
    padding: 20px 24px;
    color: #ffffff;
    box-shadow: 0 12px 30px rgba(23,79,122,.16);
    margin-bottom: 24px;
}
.brand-title { font-size: 24px; font-weight: 800; line-height: 1.1; color: #ffffff; }
.brand-subtitle { font-size: 13px; margin-top: 5px; color: #e6eef5; }

.hero {
    background: rgba(255,255,255,.92);
    border: 1px solid #dfe8ef;
    border-radius: 18px;
    padding: 28px 30px 24px 30px;
    box-shadow: 0 10px 28px rgba(31,61,84,.06);
    margin-bottom: 18px;
}
.hero-kicker {
    color: #23844d;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.hero-title {
    color: #123f63;
    font-size: 34px;
    font-weight: 850;
    margin-top: 5px;
}
.hero-text {
    color: #50636f;
    font-size: 15px;
    line-height: 1.55;
    margin-top: 7px;
}

.search-card {
    background: #ffffff;
    border: 1px solid #dbe5ec;
    border-radius: 16px;
    padding: 20px 22px 16px 22px;
    box-shadow: 0 8px 22px rgba(31,61,84,.06);
    margin-bottom: 18px;
}
.search-title {
    color: #123f63;
    font-size: 19px;
    font-weight: 800;
}
.search-help {
    color: #5f707c;
    font-size: 13px;
    margin-top: 4px;
}

.notice {
    background: #fff9e9;
    border: 1px solid #f0dfad;
    border-left: 5px solid #e0a62a;
    border-radius: 12px;
    padding: 15px 18px;
    color: #6a5525;
    line-height: 1.5;
    font-size: 13px;
    margin: 18px 0;
}
.notice strong { color: #5a4515; }

.result-banner {
    background: linear-gradient(115deg, #174f7a 0%, #1e648d 100%);
    color: #ffffff;
    border-radius: 16px;
    padding: 19px 22px;
    box-shadow: 0 9px 24px rgba(23,79,122,.15);
    margin: 20px 0 16px 0;
}
.result-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #d6e4ef;
}
.result-name {
    font-size: 23px;
    font-weight: 850;
    margin-top: 4px;
    color: #ffffff;
}

/* Métricas propias (reemplazan st.metric) */
.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
.metric-card {
    background: #174f7a;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 8px 22px rgba(23,79,122,.16);
}
.metric-label {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
}
.metric-value {
    color: #ffffff;
    font-size: 30px;
    font-weight: 850;
    margin-top: 6px;
    line-height: 1.15;
    word-break: break-word;
}

.saldo-card {
    background: linear-gradient(135deg, #eef9f2 0%, #ffffff 100%);
    border: 1px solid #c9e4d2;
    border-top: 5px solid #23844d;
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: 0 8px 22px rgba(35,132,77,.07);
    margin-top: 16px;
}
.saldo-label {
    color: #28704a;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .6px;
}
.saldo-value {
    color: #17633b;
    font-size: 31px;
    font-weight: 850;
    margin-top: 4px;
}
.saldo-note {
    color: #4f6b5c;
    font-size: 12px;
    margin-top: 4px;
}

.section-title {
    color: #123f63;
    font-size: 19px;
    font-weight: 800;
    margin: 27px 0 4px 0;
}
.section-help {
    color: #5f707c;
    font-size: 13px;
    margin-bottom: 10px;
}

.legal-card {
    background: linear-gradient(135deg, #f3f8fc 0%, #ffffff 100%);
    border: 1px solid #d5e2eb;
    border-left: 5px solid #174f7a;
    border-radius: 15px;
    padding: 19px 21px;
    margin-top: 26px;
    margin-bottom: 12px;
    box-shadow: 0 7px 20px rgba(31,61,84,.05);
}
.legal-kicker {
    color: #23844d;
    font-size: 11px;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .8px;
}
.legal-title {
    color: #123f63;
    font-size: 19px;
    font-weight: 850;
    margin-top: 4px;
}
.legal-text {
    color: #50636f;
    font-size: 13px;
    line-height: 1.55;
    margin-top: 7px;
}
.legal-meta {
    color: #5f707c;
    font-size: 12px;
    margin-top: 9px;
}
.legal-meta strong { color: #173f61; }

.email-card {
    background: linear-gradient(135deg, #eef8f2 0%, #f9fcfa 100%);
    border: 1px solid #cbe4d4;
    border-left: 5px solid #23844d;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 24px;
    margin-bottom: 12px;
}
.email-title {
    color: #1e7043;
    font-size: 18px;
    font-weight: 800;
}
.email-text {
    color: #4f6b5c;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 4px;
}

.footer {
    text-align: center;
    color: #5f707c;
    font-size: 12px;
    border-top: 1px solid #dfe6ec;
    padding-top: 20px;
    margin-top: 38px;
}
.footer strong { color: #173f61; }

/* Contador de visitas (pie de página) */
.footer-visits {
    display: inline-block;
    margin-top: 10px;
    padding: 5px 14px;
    background: #e8f1f8;
    border: 1px solid #c8dbe9;
    border-radius: 999px;
    color: #174f7a;
    font-size: 12px;
    font-weight: 700;
}

/* ---------- 9. Móvil ---------- */
@media (max-width: 700px) {
    [data-testid="stMainBlockContainer"],
    .main .block-container { padding: 14px 14px 35px 14px; }
    .hero { padding: 23px 19px 20px 19px; }
    .hero-title { font-size: 28px; }
    .brand-bar { padding: 16px 18px; }
    .metric-grid { grid-template-columns: 1fr; }
    .metric-value { font-size: 26px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# FUNCIONES
# ============================================================

@st.cache_data
def cargar_datos():
    archivo = Path("datos_dashboard_beneficiarios.csv")

    if not archivo.exists():
        return None, "No se encontró 'datos_dashboard_beneficiarios.csv'."

    try:
        df = pd.read_csv(archivo, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(archivo, encoding="latin-1")
        except Exception as error:
            return None, f"No se pudo leer el archivo de datos: {error}"
    except Exception as error:
        return None, f"No se pudo leer el archivo de datos: {error}"

    requeridas = [
        "NOMBRE",
        "DIRECCION",
        "FACTURA",
        "VALOR_PAGADO",
        "LO_QUE_DEBIO_COBRAR",
        "DEVOLUCION",
    ]
    faltantes = [col for col in requeridas if col not in df.columns]

    if faltantes:
        return None, "Faltan columnas requeridas: " + ", ".join(faltantes)

    df["NOMBRE"] = df["NOMBRE"].fillna("").astype(str).str.strip()
    df["DIRECCION"] = df["DIRECCION"].fillna("").astype(str).str.strip()

    df = df[
        (df["NOMBRE"] != "") &
        (df["NOMBRE"].str.lower() != "nan")
    ].copy()

    for col in ["VALOR_PAGADO", "LO_QUE_DEBIO_COBRAR", "DEVOLUCION"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df, None


def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(texto.split())


def dinero(valor):
    return f"${valor:,.0f}".replace(",", ".")



# ============================================================
# CONTADOR DE VISITAS
# ------------------------------------------------------------
# Guarda por día el número de visitas (una por sesión de navegador)
# y de consultas realizadas. NO guarda nombres ni datos personales.
#
# En Render el conteo se guarda en el disco persistente montado en
# /var/data. Sin ese disco, el conteo funciona pero se reinicia en
# cada despliegue.
# ============================================================

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


def _ruta_contador():
    ruta = os.environ.get("CONTADOR_DB")
    if ruta:
        return Path(ruta)
    disco = Path("/var/data")
    if disco.is_dir():
        return disco / "contador.db"
    return Path("contador.db")


RUTA_CONTADOR = _ruta_contador()


def _conexion():
    con = sqlite3.connect(RUTA_CONTADOR, timeout=10)
    con.execute(
        "CREATE TABLE IF NOT EXISTS conteo ("
        "fecha TEXT PRIMARY KEY, "
        "visitas INTEGER NOT NULL DEFAULT 0, "
        "consultas INTEGER NOT NULL DEFAULT 0)"
    )
    return con


def registrar(campo):
    if campo not in ("visitas", "consultas"):
        return
    hoy = datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d")
    try:
        with closing(_conexion()) as con, con:
            con.execute(
                "INSERT INTO conteo (fecha) VALUES (?) "
                "ON CONFLICT(fecha) DO NOTHING",
                (hoy,),
            )
            con.execute(
                f"UPDATE conteo SET {campo} = {campo} + 1 WHERE fecha = ?",
                (hoy,),
            )
    except sqlite3.Error:
        pass


def leer_conteo():
    try:
        with closing(_conexion()) as con:
            return con.execute(
                "SELECT fecha, visitas, consultas FROM conteo "
                "ORDER BY fecha DESC"
            ).fetchall()
    except sqlite3.Error:
        return []


def numero(valor):
    return f"{valor:,.0f}".replace(",", ".")


# ============================================================
# DATOS
# ============================================================

df, error = cargar_datos()

if error:
    st.error(error)
    st.info(
        "Verifique que 'datos_dashboard_beneficiarios.csv' "
        "esté en la misma carpeta que app.py."
    )
    st.stop()

nombres = sorted(
    df["NOMBRE"].drop_duplicates().tolist(),
    key=lambda x: normalizar(x)
)

# ============================================================
# REGISTRO DE VISITA (una vez por sesión)
# ============================================================

if "visita_registrada" not in st.session_state:
    st.session_state["visita_registrada"] = True
    registrar("visitas")

# ============================================================
# ENCABEZADO
# ============================================================

col_logo, col_brand = st.columns([1, 4], vertical_alignment="center")

with col_logo:
    logo = Path("logo_personeria.png")
    if logo.exists():
        st.image(str(logo), width=175)
    else:
        st.subheader("Personería al Día")

with col_brand:
    st.markdown(
        """
<div class="brand-bar">
<div class="brand-title">Personería al Día</div>
<div class="brand-subtitle">Personería Municipal de Concepción, Santander</div>
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="hero">
<div class="hero-kicker">Impuesto Predial · Vigencia 2027</div>
<div class="hero-title">Consulta de saldo a favor</div>
<div class="hero-text">
Consulte de forma sencilla la información registrada sobre el valor
pagado, el valor que debía cobrarse y el saldo a favor.
</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# BUSCADOR ÚNICO
# ============================================================

st.markdown(
    """
<div class="search-card">
<div class="search-title">🔎 Propietario o beneficiario</div>
<div class="search-help">
Escriba un nombre o apellido. El campo permite buscar dentro de la lista de propietarios y beneficiarios.
</div>
</div>
""",
    unsafe_allow_html=True,
)

nombre_seleccionado = st.selectbox(
    "Propietario o beneficiario",
    options=nombres,
    index=None,
    placeholder="Escriba aquí el nombre o apellido...",
    label_visibility="collapsed",
    key="propietario",
)

# ============================================================
# AVISO
# ============================================================

st.markdown(
    """
<div class="notice">
📢 <strong>IMPORTANTE:</strong>
El valor indicado como devolución <strong>NO será entregado en efectivo</strong>.
Este valor será aplicado por la Alcaldía Municipal como abono al impuesto
predial correspondiente a la vigencia 2027.
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# BASE JURÍDICA DE LA MEDIDA
# ============================================================

resolucion = Path("RESOLUCION_146_2026.pdf")

st.markdown(
    """
<div class="legal-card">
<div class="legal-kicker">Documento de respaldo</div>
<div class="legal-title">📄 Resolución No. 146 de 2026</div>
<div class="legal-text">
La consulta se relaciona con la medida administrativa adoptada por la Alcaldía
Municipal de Concepción frente a un error material en la parametrización de la
fórmula de cálculo del Impuesto Predial Unificado para la vigencia fiscal 2026.
La resolución establece la compensación de los valores pagados en exceso mediante
un abono al impuesto predial correspondiente a la vigencia 2027.
</div>
<div class="legal-meta"><strong>Fecha:</strong> 30 de junio de 2026 · <strong>Entidad:</strong> Alcaldía Municipal de Concepción, Santander</div>
</div>
""",
    unsafe_allow_html=True,
)

if resolucion.exists():
    with open(resolucion, "rb") as archivo_pdf:
        st.download_button(
            "📥 Descargar Resolución No. 146 de 2026",
            data=archivo_pdf.read(),
            file_name="Resolucion_146_de_2026.pdf",
            mime="application/pdf",
            width="stretch",
        )
else:
    st.warning("El documento de respaldo no está disponible en este momento.")

with st.expander("📌 ¿Qué establece la Resolución 146 de 2026?"):
    st.markdown(
        """
- Reconoce formalmente un **error material en la parametrización de la fórmula de cálculo** del Impuesto Predial Unificado aplicado en el municipio para la vigencia fiscal 2026.
- Dispone la **compensación de los valores pagados en exceso** mediante su aplicación como abono al impuesto predial de la vigencia 2027.
- Ordena a las dependencias municipales correspondientes identificar los propietarios afectados y adelantar los procedimientos administrativos necesarios.
- El documento contiene, en sus páginas anexas, el listado de predios, propietarios y valores de devolución asociados a la medida.

**Fuente:** Resolución No. 146 de 2026, Alcaldía Municipal de Concepción, Santander.
"""
    )

# ============================================================
# DATOS PERSONALES
# ============================================================

with st.expander("🔒 Información sobre el tratamiento de datos personales"):
    st.write(
        """
La información presentada en esta herramienta corresponde a registros
relacionados con la consulta del impuesto predial.

El tratamiento de la información deberá realizarse conforme a las normas
aplicables sobre protección de datos personales y acceso a la información
pública.

La información presentada deberá utilizarse únicamente para fines
relacionados con la consulta del saldo a favor.
"""
    )

# ============================================================
# RESULTADO
# ============================================================

if nombre_seleccionado:

    if st.session_state.get("ultima_consulta") != nombre_seleccionado:
        st.session_state["ultima_consulta"] = nombre_seleccionado
        registrar("consultas")

    resultados = df[df["NOMBRE"] == nombre_seleccionado].copy()

    total_pagado = resultados["VALOR_PAGADO"].sum()
    total_debio = resultados["LO_QUE_DEBIO_COBRAR"].sum()
    total_devolucion = resultados["DEVOLUCION"].sum()

    porcentaje = (
        total_devolucion / total_pagado
        if total_pagado > 0 else 0
    )

    st.markdown(
        f"""
<div class="result-banner">
<div class="result-label">Resultado de la consulta</div>
<div class="result-name">{html.escape(nombre_seleccionado)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="metric-grid">
<div class="metric-card">
<div class="metric-label">💵 Valor pagado</div>
<div class="metric-value">{dinero(total_pagado)}</div>
</div>
<div class="metric-card">
<div class="metric-label">📋 Valor que debía cobrarse</div>
<div class="metric-value">{dinero(total_debio)}</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="saldo-card">
<div class="saldo-label">💰 Saldo a favor para 2027</div>
<div class="saldo-value">{dinero(total_devolucion)}</div>
<div class="saldo-note">Valor registrado para ser aplicado como abono al impuesto predial de la vigencia 2027.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">📊 Porcentaje de devolución</div>',
        unsafe_allow_html=True,
    )

    st.progress(
        min(max(porcentaje, 0), 1),
        text=f"{porcentaje:.2%}",
    )

    st.markdown(
        '<div class="section-title">📄 Detalle de la información</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-help">Registros asociados al propietario o beneficiario consultado.</div>',
        unsafe_allow_html=True,
    )

    tabla = resultados[
        [
            "NOMBRE",
            "DIRECCION",
            "FACTURA",
            "VALOR_PAGADO",
            "LO_QUE_DEBIO_COBRAR",
            "DEVOLUCION",
        ]
    ].copy()

    tabla = tabla.rename(
        columns={
            "NOMBRE": "Beneficiario",
            "DIRECCION": "Dirección",
            "FACTURA": "Factura",
            "VALOR_PAGADO": "Valor pagado",
            "LO_QUE_DEBIO_COBRAR": "Valor que debía cobrarse",
            "DEVOLUCION": "Saldo a favor",
        }
    )

    tabla["Valor pagado"] = tabla["Valor pagado"].apply(dinero)
    tabla["Valor que debía cobrarse"] = tabla["Valor que debía cobrarse"].apply(dinero)
    tabla["Saldo a favor"] = tabla["Saldo a favor"].apply(dinero)

    st.dataframe(
        tabla,
        width="stretch",
        hide_index=True,
    )

    # ========================================================
    # CORREO
    # ========================================================

    st.markdown(
        """
<div class="email-card">
<div class="email-title">📧 ¿Necesita recibir esta información?</div>
<div class="email-text">
Puede solicitar una copia de la información consultada directamente
a la Personería Municipal.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    correo = "personeria@concepcion-santander.gov.co"
    asunto = f"Solicitud de información - {nombre_seleccionado}"
    cuerpo = f"""Buen día,

Solicito una copia de la información consultada en la herramienta de saldo a favor del impuesto predial.

Nombre: {nombre_seleccionado}

Gracias.
"""

    enlace = (
        "mailto:" + correo
        + "?subject=" + urllib.parse.quote(asunto)
        + "&body=" + urllib.parse.quote(cuerpo)
    )

    st.link_button(
        "📧 Solicitar información por correo",
        enlace,
        width="stretch",
    )

    st.info(
        "ℹ️ El saldo a favor indicado en esta consulta corresponde al valor registrado "
        "y será aplicado como abono al impuesto predial correspondiente a la vigencia 2027."
    )

# ============================================================
# ESTADÍSTICAS PRIVADAS
# ------------------------------------------------------------
# Solo se muestran al abrir la app con ?estadisticas=CLAVE, donde
# CLAVE es la variable de entorno STATS_CLAVE configurada en Render.
# ============================================================

conteo = leer_conteo()
total_visitas = sum(fila[1] for fila in conteo)
total_consultas = sum(fila[2] for fila in conteo)

clave_configurada = os.environ.get("STATS_CLAVE", "")
clave_recibida = st.query_params.get("estadisticas", "")

if clave_configurada and hmac.compare_digest(
    str(clave_recibida), clave_configurada
):
    hoy = datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d")
    visitas_hoy = next((f[1] for f in conteo if f[0] == hoy), 0)
    consultas_hoy = next((f[2] for f in conteo if f[0] == hoy), 0)

    st.markdown(
        '<div class="section-title">📈 Estadísticas de uso</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="metric-grid">
<div class="metric-card">
<div class="metric-label">👁️ Visitas totales</div>
<div class="metric-value">{numero(total_visitas)}</div>
</div>
<div class="metric-card">
<div class="metric-label">🔎 Consultas totales</div>
<div class="metric-value">{numero(total_consultas)}</div>
</div>
<div class="metric-card">
<div class="metric-label">📅 Visitas hoy</div>
<div class="metric-value">{numero(visitas_hoy)}</div>
</div>
<div class="metric-card">
<div class="metric-label">📅 Consultas hoy</div>
<div class="metric-value">{numero(consultas_hoy)}</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if conteo:
        st.markdown(
            '<div class="section-help" style="margin-top:14px;">'
            "Detalle por día (hora de Colombia).</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            pd.DataFrame(conteo, columns=["Fecha", "Visitas", "Consultas"]),
            width="stretch",
            hide_index=True,
        )

    if not str(RUTA_CONTADOR).startswith("/var/data"):
        st.warning(
            "El contador no está usando el disco persistente (/var/data). "
            "Los datos se reiniciarán en el próximo despliegue."
        )

# ============================================================
# PIE
# ============================================================

st.markdown(
    f"""
<div class="footer">
<strong>Personería al Día</strong><br>
Herramienta de consulta ciudadana · Concepción, Santander<br>
<span class="footer-visits">👁️ {numero(total_visitas)} visitas</span>
</div>
""",
    unsafe_allow_html=True,
)
