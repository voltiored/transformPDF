import streamlit as st
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PIL import Image
import tempfile, os

# ----------------------------
# ESTILOS
# ----------------------------
st.set_page_config(page_title="LibroPDF", page_icon="📖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #F5F0E8;
    background-image:
        radial-gradient(circle at 20% 80%, rgba(139,90,43,0.06) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(62,35,18,0.05) 0%, transparent 50%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 680px !important; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    animation: fadeUp 0.8s ease both;
}
.hero-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 0.5rem;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-8px); }
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3.6rem;
    font-weight: 900;
    color: #1E1008;
    letter-spacing: -1px;
    line-height: 1;
    margin: 0 0 0.5rem;
}
.hero h1 span { color: #8B5A2B; }
.hero p {
    font-size: 1.05rem;
    color: #6B5744;
    font-weight: 300;
    margin: 0;
    line-height: 1.6;
}

/* Ornamento */
.ornament {
    text-align: center;
    color: #C4A882;
    font-size: 1.2rem;
    letter-spacing: 0.5rem;
    margin: 1.5rem 0;
}

/* Tarjeta */
.card {
    background: #FFFEF9;
    border: 1.5px solid #E0D5C4;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(62,35,18,0.08), 0 1px 3px rgba(62,35,18,0.05);
    animation: fadeUp 1s ease both;
    margin-bottom: 1rem;
}

/* Uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed #C4A882 !important;
    border-radius: 10px !important;
    background: #FAF7F2 !important;
    padding: 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: #8B5A2B !important; }
[data-testid="stFileUploadDropzone"] { background: transparent !important; }

/* Botón principal */
.stButton > button {
    width: 100%;
    background: #1E1008 !important;
    color: #F5F0E8 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.85rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover {
    background: #8B5A2B !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(139,90,43,0.3) !important;
}

/* Botón descarga */
[data-testid="stDownloadButton"] > button {
    width: 100%;
    background: #8B5A2B !important;
    color: #FFFEF9 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.85rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #6B4420 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(139,90,43,0.4) !important;
}

/* Mensajes */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}

/* Pasos */
.steps {
    display: flex;
    gap: 0.75rem;
    margin: 1.5rem 0 0;
    animation: fadeUp 1.1s ease both;
}
.step {
    flex: 1;
    background: #FFFEF9;
    border: 1px solid #E0D5C4;
    border-radius: 10px;
    padding: 1rem 0.5rem;
    text-align: center;
}
.step-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #C4A882;
    display: block;
}
.step-text {
    font-size: 0.75rem;
    color: #6B5744;
    line-height: 1.4;
    margin-top: 0.25rem;
    display: block;
}

/* Footer */
.footer {
    text-align: center;
    color: #B0A090;
    font-size: 0.8rem;
    padding: 2rem 0 1rem;
    letter-spacing: 0.05em;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# FUNCIÓN PRINCIPAL
# ----------------------------
def hacer_libro_bytes(pdf_bytes):
    try:
        paginas = convert_from_bytes(pdf_bytes, dpi=150)
    except Exception as e:
        raise ValueError("No se pudo leer el PDF. Asegúrate de que el archivo no esté dañado.") from e

    if not paginas:
        raise ValueError("El PDF no contiene páginas.")

    num_paginas = len(paginas)
    faltan = (4 - num_paginas % 4) % 4
    for _ in range(faltan):
        paginas.append(Image.new("RGB", paginas[0].size, "white"))

    ancho, alto = landscape(A4)
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp_out.name, pagesize=landscape(A4))
    temp_files = []

    try:
        for i in range(0, len(paginas), 4):
            pares = [(i, i + 2), (i + 3, i + 1)]
            for izq, der in pares:
                img_izq = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                img_der = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                paginas[izq].save(img_izq, "JPEG")
                paginas[der].save(img_der, "JPEG")
                temp_files.extend([img_izq, img_der])
                c.drawImage(img_izq, 0, 0, ancho / 2, alto)
                c.drawImage(img_der, ancho / 2, 0, ancho / 2, alto)
                c.showPage()
        c.save()
        return tmp_out.name
    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)


# ----------------------------
# INTERFAZ
# ----------------------------
st.markdown("""
<div class="hero">
    <span class="hero-icon">📖</span>
    <h1>Libro<span>PDF</span></h1>
    <p>Transforma cualquier PDF en un cuadernillo listo para imprimir y doblar.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="ornament">— ✦ —</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu PDF aquí", type="pdf", label_visibility="collapsed")

if not archivo:
    st.markdown("""
    <p style="text-align:center; color:#B0A090; font-size:0.85rem; margin-top:0.25rem;">
        📄 Arrastra tu archivo o haz clic para seleccionarlo &nbsp;·&nbsp; Máx. 10 MB
    </p>
    """, unsafe_allow_html=True)

if archivo:
    if archivo.size > 10 * 1024 * 1024:
        st.error("⚠️ El archivo es demasiado grande. Máximo 10 MB.")
    else:
        st.info(f"📄 **{archivo.name}** listo para convertir")

        if st.button("✦ Generar cuadernillo"):
            salida = None
            with st.spinner("Reordenando páginas..."):
                try:
                    salida = hacer_libro_bytes(archivo.read())
                    with open(salida, "rb") as f:
                        st.success("✅ ¡Cuadernillo generado!")
                        nombre_original = os.path.splitext(archivo.name)[0]
                        nombre_salida = f"librito_{nombre_original}.pdf"
                        st.download_button(
                            "⬇️ Descargar cuadernillo",
                            f,
                            file_name=nombre_salida,
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"❌ Error al generar el PDF: {e}")
                finally:
                    if salida and os.path.exists(salida):
                        os.remove(salida)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="steps">
    <div class="step">
        <span class="step-num">①</span>
        <span class="step-text">Sube tu PDF</span>
    </div>
    <div class="step">
        <span class="step-num">②</span>
        <span class="step-text">Genera el cuadernillo</span>
    </div>
    <div class="step">
        <span class="step-num">③</span>
        <span class="step-text">Imprime a doble cara</span>
    </div>
    <div class="step">
        <span class="step-num">④</span>
        <span class="step-text">Dobla y ¡listo!</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    LIBROPDF &nbsp;·&nbsp; Hecho con amor en Python + Streamlit
</div>
""", unsafe_allow_html=True)
