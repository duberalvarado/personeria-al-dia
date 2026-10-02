"""
Agrega la vista previa para WhatsApp, Facebook, Telegram, X, etc.

Estas redes NO ejecutan JavaScript: solo leen el HTML inicial que entrega
Streamlit (que por defecto dice "Streamlit" y no tiene imagen). Este script
modifica ese HTML inicial dentro de la instalación de Streamlit para incluir
título, descripción e imagen (etiquetas Open Graph).

Se ejecuta en Render como parte del Build Command:
    pip install -r requirements.txt && python vista_previa_social.py

Si cambia el dominio, configure la variable de entorno SITIO_URL en Render
(por ejemplo https://www.personeriaaldia.com) y vuelva a desplegar.
"""

import html
import os
from pathlib import Path

import streamlit

SITIO_URL = os.environ.get(
    "SITIO_URL", "https://personeria-al-dia.onrender.com"
).rstrip("/")

TITULO = "Personería al Día | Consulta Predial"
DESCRIPCION = (
    "Consulte su saldo a favor del impuesto predial de Concepción, Santander, "
    "que será abonado a la vigencia 2027. Personería Municipal de Concepción."
)
IMAGEN = f"{SITIO_URL}/app/static/vista_previa.jpg"

MARCA_INICIO = "<!-- VISTA-PREVIA-SOCIAL:INICIO -->"
MARCA_FIN = "<!-- VISTA-PREVIA-SOCIAL:FIN -->"


def etiquetas():
    t = html.escape(TITULO, quote=True)
    d = html.escape(DESCRIPCION, quote=True)
    return f"""{MARCA_INICIO}
    <title>{t}</title>
    <meta name="description" content="{d}" />
    <meta property="og:type" content="website" />
    <meta property="og:locale" content="es_CO" />
    <meta property="og:site_name" content="Personería al Día" />
    <meta property="og:title" content="{t}" />
    <meta property="og:description" content="{d}" />
    <meta property="og:url" content="{SITIO_URL}/" />
    <meta property="og:image" content="{IMAGEN}" />
    <meta property="og:image:secure_url" content="{IMAGEN}" />
    <meta property="og:image:type" content="image/jpeg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="Personería al Día - Consulta de saldo a favor" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{t}" />
    <meta name="twitter:description" content="{d}" />
    <meta name="twitter:image" content="{IMAGEN}" />
    {MARCA_FIN}"""


def main():
    index = Path(streamlit.__file__).parent / "static" / "index.html"
    contenido = index.read_text(encoding="utf-8")

    # Quitar una versión anterior (permite ejecutar el script varias veces)
    if MARCA_INICIO in contenido:
        inicio = contenido.index(MARCA_INICIO)
        fin = contenido.index(MARCA_FIN) + len(MARCA_FIN)
        contenido = contenido[:inicio] + "<title>Streamlit</title>" + contenido[fin:]

    if "<title>Streamlit</title>" not in contenido:
        raise SystemExit("No se encontró <title>Streamlit</title> en index.html")

    contenido = contenido.replace("<title>Streamlit</title>", etiquetas(), 1)
    contenido = contenido.replace('<html lang="en">', '<html lang="es">', 1)
    index.write_text(contenido, encoding="utf-8")
    print(f"Vista previa social aplicada en {index}")
    print(f"Imagen: {IMAGEN}")


if __name__ == "__main__":
    main()
