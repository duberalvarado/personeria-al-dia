
import streamlit as st
import pandas as pd
import unicodedata
import urllib.parse

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

st.markdown("""
<style>
    /* Página */
    .stApp {
        background: #f4f7fa;
    }

    .main .block-container {
        max-width: 1120px;
        padding: 24px 28px 50px 28px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    /* Encabezado */
    .topbar {
        background: #174f7a;
        border-radius: 14px;
        padding: 18px 24px;
        color: white;
        box-shadow: 0 5px 18px rgba(23, 79, 122, .14);
        margin-bottom: 22px;
    }

    .topbar-title {
        font-size: 23px;
        font-weight: 800;
        line-height: 1.1;
    }

    .topbar-subtitle {
        font-size: 13px;
        opacity: .88;
        margin-top: 5px;
    }

    /* Presentación */
    .intro {
        background: white;
        border: 1px solid #e0e7ed;
        border-radius: 14px;
        padding: 30px 32px 25px 32px;
        box-shadow: 0 4px 16px rgba(31, 61, 84, .05);
        margin-bottom: 18px;
    }

    .intro-kicker {
        color: #23844d;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .8px;
        margin-bottom: 8px;
    }

    .intro-title {
        color: #173f61;
        font-size: 32px;
        font-weight: 800;
        margin: 0;
    }

    .intro-text {
        color: #667684;
        font-size: 15px;
        margin-top: 8px;
        line-height: 1.55;
    }

    /* Buscador */
    .search-card {
        background: white;
        border: 1px solid #dfe7ee;
        border-radius: 14px;
        padding: 22px 24px 16px 24px;
        box-shadow: 0 4px 16px rgba(31, 61, 84, .05);
        margin-bottom: 18px;
    }

    .search-title {
        color: #173f61;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .search-help {
        color: #7a8792;
        font-size: 13px;
        margin-bottom: 10px;
    }

    div[data-testid="stTextInput"] input {
        background: #f8fafc !important;
        border: 2px solid #d6e0e8 !important;
        border-radius: 10px !important;
        color: #173f61 !important;
        font-size: 16px !important;
        padding: 13px 15px !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #2877a9 !important;
        box-shadow: 0 0 0 3px rgba(40,119,169,.10) !important;
    }

    /* Aviso */
    .notice {
        background: #fff9e9;
        border: 1px solid #f1dfaa;
        border-left: 5px solid #e0a62a;
        border-radius: 10px;
        padding: 15px 18px;
        color: #695526;
        margin: 18px 0;
        font-size: 13px;
        line-height: 1.5;
    }

    .notice strong {
        color: #7b5b0c;
    }

    /* Resultados */
    .results-head {
        color: #173f61;
        font-size: 18px;
        font-weight: 800;
        margin: 22px 0 5px 0;
    }

    .results-count {
        color: #778692;
        font-size: 13px;
        margin-bottom: 10px;
    }

    .selected-person {
        background: #174f7a;
        color: white;
        border-radius: 12px;
        padding: 18px 22px;
        margin: 20px 0 15px 0;
    }

    .selected-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: .8px;
        opacity: .8;
    }

    .selected-name {
        font-size: 22px;
        font-weight: 800;
        margin-top: 4px;
    }

    /* Métricas */
    .metric {
        background: white;
        border: 1px solid #e0e7ed;
        border-radius: 12px;
        padding: 18px;
        min-height: 112px;
        box-shadow: 0 3px 12px rgba(31, 61, 84, .05);
    }

    .metric-green {
        border-top: 4px solid #23844d;
    }

    .metric-blue {
        border-top: 4px solid #2877a9;
    }

    .metric-orange {
        border-top: 4px solid #e0a62a;
    }

    .metric-label {
        color: #74828d !important;
        background: transparent !important;
        -webkit-text-fill-color: #74828d !important;
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: .4px;
    }

    .metric-value {
        color: #173f61 !important;
        background: transparent !important;
        -webkit-text-fill-color: #173f61 !important;
        font-size: 23px;
        font-weight: 800;
        margin-top: 7px;
    }

    .metric {
        color: #173f61 !important;
        -webkit-text-fill-color: initial;
    }

    /* Secciones */
    .section-title {
        color: #173f61;
        font-size: 18px;
        font-weight: 800;
        margin: 25px 0 5px 0;
    }

    .section-subtitle {
        color: #7a8792;
        font-size: 13px;
        margin-bottom: 10px;
    }

    /* Correo */
    .email-card {
        background: #eef8f2;
        border: 1px solid #cbe5d4;
        border-radius: 12px;
        padding: 20px;
        margin-top: 22px;
    }

    .email-title {
        color: #1e7043;
        font-size: 18px;
        font-weight: 800;
    }

    .email-text {
        color: #63756a;
        font-size: 13px;
        margin-top: 5px;
        line-height: 1.5;
    }

    /* Botón */
    .stLinkButton a {
        border-radius: 9px !important;
        font-weight: 700 !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #87939c;
        font-size: 12px;
        border-top: 1px solid #dfe6ec;
        padding-top: 20px;
        margin-top: 35px;
    }

    /* Móvil */
    @media (max-width: 700px) {
        .main .block-container {
            padding: 15px 14px 35px 14px;
        }

        .intro {
            padding: 24px 20px;
        }

        .intro-title {
            font-size: 27px;
        }

        .topbar {
            padding: 16px 18px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES
# ============================================================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_dashboard_beneficiarios.csv")

    numericas = [
        "VALOR_PAGADO",
        "LO_QUE_DEBIO_COBRAR",
        "DEVOLUCION",
    ]

    for col in numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["NOMBRE", "DIRECCION"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[
        (df["NOMBRE"] != "") &
        (df["NOMBRE"].str.lower() != "nan")
    ].copy()

    return df


def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(texto.split())


def dinero(valor):
    return f"${valor:,.0f}".replace(",", ".")


def coincide_por_palabras(nombre, busqueda):
    """
    Permite buscar:
    DIAZ
    MARCO
    MARCO DIAZ
    MARCO ANTONIO DIAZ
    sin importar mayúsculas, tildes ni el orden de las palabras.
    """
    nombre_norm = normalizar(nombre)
    palabras = [p for p in normalizar(busqueda).split() if p]

    return all(palabra in nombre_norm for palabra in palabras)


# ============================================================
# DATOS
# ============================================================

df = cargar_datos()

# ============================================================
# ENCABEZADO
# ============================================================

logo_col, titulo_col = st.columns([1, 4])

with logo_col:
    try:
        st.image("logo_personeria.png", width=170)
    except Exception:
        st.markdown("### Personería al Día")

with titulo_col:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">Personería al Día</div>
            <div class="topbar-subtitle">
                Personería Municipal de Concepción, Santander
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# INTRODUCCIÓN
# ============================================================

st.markdown(
    """
    <div class="intro">
        <div class="intro-kicker">Impuesto Predial</div>
        <div class="intro-title">Consulta de saldo a favor</div>
        <div class="intro-text">
            Consulte de manera sencilla la información registrada
            sobre el valor pagado, el valor que debía cobrarse y
            el saldo a favor correspondiente a la vigencia 2027.
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
        <div class="search-title">🔎 Busque su nombre o apellido</div>
        <div class="search-help">
            Puede escribir un nombre, un apellido o varias palabras.
            Por ejemplo: <strong>DIAZ</strong>, <strong>MARCO</strong>
            o <strong>MARCO DIAZ</strong>.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

busqueda = st.text_input(
    "Buscar",
    placeholder="Escriba aquí el nombre o apellido...",
    label_visibility="collapsed",
    key="buscador_principal",
)

# ============================================================
# AVISO
# ============================================================

st.markdown(
    """
    <div class="notice">
        📢 <strong>IMPORTANTE:</strong>
        El valor indicado como devolución
        <strong>NO será entregado en efectivo</strong>.
        Este valor será aplicado por la Alcaldía Municipal
        como abono al impuesto predial correspondiente
        a la vigencia 2027.
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PRIVACIDAD
# ============================================================

with st.expander("🔒 Información sobre el tratamiento de datos personales"):
    st.write(
        """
        La información presentada en esta herramienta corresponde
        a registros relacionados con la consulta del impuesto predial.

        El tratamiento de la información deberá realizarse conforme
        a las normas aplicables sobre protección de datos personales
        y acceso a la información pública.

        La información presentada deberá utilizarse únicamente para
        fines relacionados con la consulta del saldo a favor.
        """
    )

# ============================================================
# VARIABLES DE RESULTADO
# ============================================================

nombre_seleccionado = None
coincidencias = []

# ============================================================
# BÚSQUEDA
# ============================================================

if busqueda.strip():

    coincidencias = [
        nombre
        for nombre in sorted(
            df["NOMBRE"].drop_duplicates().tolist(),
            key=lambda x: normalizar(x)
        )
        if coincide_por_palabras(nombre, busqueda)
    ]

    if not coincidencias:
        st.warning(
            "No encontramos personas que coincidan con su búsqueda. "
            "Revise la escritura e intente nuevamente."
        )

    elif len(coincidencias) == 1:
        nombre_seleccionado = coincidencias[0]

    else:
        st.markdown(
            '<div class="results-head">Personas encontradas</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="results-count">'
            f'Se encontraron {len(coincidencias)} coincidencias. '
            f'Seleccione la persona que desea consultar.'
            f'</div>',
            unsafe_allow_html=True,
        )

        nombre_seleccionado = st.selectbox(
            "Seleccione el nombre",
            options=coincidencias,
            index=0,
            key="persona_resultado",
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
        if total_pagado > 0
        else 0
    )

    st.markdown(
        f"""
        <div class="selected-person">
            <div class="selected-label">Resultado de la consulta</div>
            <div class="selected-name">{nombre_seleccionado}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric metric-blue">
                <div class="metric-label">Valor pagado</div>
                <div class="metric-value">{dinero(total_pagado)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric metric-orange">
                <div class="metric-label">Valor que debía cobrarse</div>
                <div class="metric-value">{dinero(total_debio)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric metric-green">
                <div class="metric-label">Saldo a favor para 2027</div>
                <div class="metric-value">{dinero(total_devolucion)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # PORCENTAJE
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #e0e7ed;
            border-radius:12px;
            padding:17px 20px;
            margin-top:16px;
            box-shadow:0 3px 12px rgba(31,61,84,.05);
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:9px;
            ">
                <span style="
                    color:#6f7e89;
                    font-size:12px;
                    font-weight:800;
                    text-transform:uppercase;
                ">
                    Porcentaje de devolución
                </span>
                <strong style="
                    color:#174f7a;
                    font-size:20px;
                ">
                    {porcentaje:.2%}
                </strong>
            </div>
            <div style="
                height:8px;
                background:#e8eef3;
                border-radius:10px;
                overflow:hidden;
            ">
                <div style="
                    width:{min(max(porcentaje * 100, 0), 100):.2f}%;
                    height:100%;
                    background:#23844d;
                    border-radius:10px;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # DETALLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📄 Detalle de la información</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Registros asociados al beneficiario consultado.'
        '</div>',
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
    tabla["Valor que debía cobrarse"] = (
        tabla["Valor que debía cobrarse"].apply(dinero)
    )
    tabla["Saldo a favor"] = tabla["Saldo a favor"].apply(dinero)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # CORREO
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="email-card">
            <div class="email-title">
                📧 ¿Necesita recibir esta información?
            </div>
            <div class="email-text">
                Puede solicitar una copia de la información consultada
                directamente a la Personería Municipal.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    correo_contacto = "personeria@concepcion-santander.gov.co"

    asunto = f"Solicitud de información - {nombre_seleccionado}"

    cuerpo = f"""Buen día,

Solicito una copia de la información consultada en la herramienta de saldo a favor del impuesto predial.

Nombre: {nombre_seleccionado}

Gracias.
"""

    enlace_correo = (
        "mailto:"
        + correo_contacto
        + "?subject="
        + urllib.parse.quote(asunto)
        + "&body="
        + urllib.parse.quote(cuerpo)
    )

    st.link_button(
        "📧 Solicitar información por correo",
        enlace_correo,
        use_container_width=True,
    )

    st.info(
        "ℹ️ El saldo a favor indicado en esta consulta corresponde "
        "al valor registrado y será aplicado como abono al impuesto "
        "predial correspondiente a la vigencia 2027."
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
