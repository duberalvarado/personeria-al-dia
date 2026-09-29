import streamlit as st
import pandas as pd
import unicodedata
import urllib.parse
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
# ============================================================

st.markdown(
r"""
<style>
.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(35,132,77,.09), transparent 27%),
        radial-gradient(circle at 92% 0%, rgba(23,79,122,.12), transparent 30%),
        linear-gradient(180deg, #edf4f8 0%, #f8fafc 48%, #eef4f8 100%);
}
.main .block-container {
    max-width: 1160px;
    padding: 28px 28px 55px 28px;
}
#MainMenu, footer { visibility: hidden; }

.brand-bar {
    background: linear-gradient(115deg, #123f63 0%, #1d638b 68%, #23844d 100%);
    border-radius: 18px;
    padding: 20px 24px;
    color: white;
    box-shadow: 0 12px 30px rgba(23,79,122,.16);
    margin-bottom: 24px;
}
.brand-title { font-size: 24px; font-weight: 800; line-height: 1.1; }
.brand-subtitle { font-size: 13px; opacity: .9; margin-top: 5px; }

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
    color: #647583;
    font-size: 15px;
    line-height: 1.55;
    margin-top: 7px;
}

.search-card {
    background: white;
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
    color: #7a8792;
    font-size: 13px;
    margin-top: 4px;
}

div[data-testid="stSelectbox"] > div > div {
    border-radius: 12px !important;
    border: 2px solid #d5e0e8 !important;
    background: #fbfdff !important;
    min-height: 48px !important;
    box-shadow: 0 4px 14px rgba(31,61,84,.05);
}
div[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #2877a9 !important;
    box-shadow: 0 0 0 3px rgba(40,119,169,.11) !important;
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

.result-banner {
    background: linear-gradient(115deg, #174f7a 0%, #1e648d 100%);
    color: white;
    border-radius: 16px;
    padding: 19px 22px;
    box-shadow: 0 9px 24px rgba(23,79,122,.15);
    margin: 20px 0 16px 0;
}
.result-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: .78;
}
.result-name {
    font-size: 23px;
    font-weight: 850;
    margin-top: 4px;
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
    color: #688073;
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
    color: #7a8792;
    font-size: 13px;
    margin-bottom: 10px;
}

/* Base jurídica */
.legal-card {
    background: linear-gradient(135deg, #f3f8fc 0%, #ffffff 100%);
    border: 1px solid #d5e2eb;
    border-left: 5px solid #174f7a;
    border-radius: 15px;
    padding: 19px 21px;
    margin-top: 26px;
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
    color: #5f707c;
    font-size: 13px;
    line-height: 1.55;
    margin-top: 7px;
}
.legal-meta {
    color: #6e7e89;
    font-size: 12px;
    margin-top: 9px;
}

.email-card {
    background: linear-gradient(135deg, #eef8f2 0%, #f9fcfa 100%);
    border: 1px solid #cbe4d4;
    border-left: 5px solid #23844d;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 24px;
}
.email-title {
    color: #1e7043;
    font-size: 18px;
    font-weight: 800;
}
.email-text {
    color: #63766a;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 4px;
}

.stButton > button, .stLinkButton > a {
    border-radius: 10px !important;
    font-weight: 750 !important;
    min-height: 44px !important;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.94);
    border: 1px solid #dfe7ed;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(31,61,84,.055);
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

div[data-testid="stExpander"] {
    border-radius: 12px !important;
    border-color: #dce5ec !important;
    background: rgba(255,255,255,.78);
}

.footer {
    text-align: center;
    color: #87939c;
    font-size: 12px;
    border-top: 1px solid #dfe6ec;
    padding-top: 20px;
    margin-top: 38px;
}

@media (max-width: 700px) {
    .main .block-container { padding: 14px 14px 35px 14px; }
    .hero { padding: 23px 19px 20px 19px; }
    .hero-title { font-size: 28px; }
    .brand-bar { padding: 16px 18px; }
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
            use_container_width=True,
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
<div class="result-name">{nombre_seleccionado}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric("💵 Valor pagado", dinero(total_pagado))

    with c2:
        st.metric("📋 Valor que debía cobrarse", dinero(total_debio))

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
        use_container_width=True,
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
        use_container_width=True,
    )

    st.info(
        "ℹ️ El saldo a favor indicado en esta consulta corresponde al valor registrado "
        "y será aplicado como abono al impuesto predial correspondiente a la vigencia 2027."
    )

# ============================================================
# PIE
# ============================================================

st.markdown(
    """
<div class="footer">
<strong>Personería al Día</strong><br>
Herramienta de consulta ciudadana · Concepción, Santander
</div>
""",
    unsafe_allow_html=True,
)
