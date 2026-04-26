import streamlit as st
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PIL import Image
import tempfile, os

st.set_page_config(page_title="LibroPDF", page_icon="📖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background-color: #F5F0E8;
    background-image:
        radial-gradient(circle at 20% 80%, rgba(139,90,43,0.06) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(62,35,18,0.05) 0%, transparent 50%);
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding-top: 1rem !important;
    max-width: 640px !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.5rem 0 1rem;
    animation: fadeUp 0.7s ease both;
}
.hero-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 0.4rem;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-8px); }
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    font-weight: 900;
    color: #1E1008;
    letter-spacing: -1px;
    line-height: 1;
    margin: 0 0 0.4rem;
}
.hero h1 span { color: #8B5A2B; }
.hero p {
    font-size: 1rem;
    color: #6B5744;
    font-weight: 300;
    margin: 0;
    line-height: 1.6;
}
.ornament {
    text-align: center;
    color: #C4A882;
    font-size: 1.1rem;
    letter-spacing: 0.5rem;
    margin: 0.8rem 0 1.2rem;
}

/* ── Zona upload: estilamos el contenedor nativo ── */
[data-testid="stFileUploader"] {
    background: #FFFEF9 !important;
    border: 1.5px solid #E0D5C4 !important;
    border-radius: 14px !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 4px 24px rgba(62,35,18,0.07) !important;
}
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #C4A882 !important;
    border-radius: 10px !important;
    background: #FAF7F2 !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #8B5A2B !important;
    background: #F5EFE6 !important;
}
/* Label del uploader como hint visual */
[data-testid="stFileUploaderDropzoneInstructions"] p {
    color: #B0A090 !important;
    font-size: 0.85rem !important;
}

/* ── Bloque de info/success/error ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}

/* ── Botón principal: ancho completo ── */
div[data-testid="stButton"] {
    width: 100% !important;
}
div[data-testid="stButton"] > button {
    width: 100% !important;
    background: #1E1008 !important;
    color: #F5F0E8 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.9rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
    margin-top: 0.25rem !important;
}
div[data-testid="stButton"] > button:hover {
    background: #8B5A2B !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(139,90,43,0.28) !important;
}

/* ── Botón descarga: ancho completo ── */
div[data-testid="stDownloadButton"] {
    width: 100% !important;
}
div[data-testid="stDownloadButton"] > button {
    width: 100% !important;
    background: #8B5A2B !important;
    color: #FFFEF9 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.9rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: #6B4420 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(139,90,43,0.35) !important;
}

/* ── Pasos ── */
.steps {
    display: flex;
    gap: 0.6rem;
    margin: 1.4rem 0 0;
    animation: fadeUp 1.1s ease both;
}
.step {
    flex: 1;
    background: #FFFEF9;
    border: 1px solid #E0D5C4;
    border-radius: 12px;
    padding: 0.9rem 0.4rem;
    text-align: center;
}
.step-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #C4A882;
    display: block;
}
.step-text {
    font-size: 0.72rem;
    color: #6B5744;
    line-height: 1.35;
    margin-top: 0.2rem;
    display: block;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #C4A882;
    font-size: 0.75rem;
    padding: 1.5rem 0 0.5rem;
    letter-spacing: 0.08em;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ── FUNCIÓN ──────────────────────────────────────────
def hacer_libro_bytes(pdf_bytes):
    try:
        paginas = convert_from_bytes(pdf_bytes, dpi=150)
    except Exception as e:
        raise ValueError("No se pudo leer el PDF. Asegúrate de que no esté dañado.") from e

    if not paginas:
        raise ValueError("El PDF no contiene páginas.")

    faltan = (4 - len(paginas) % 4) % 4
    for _ in range(faltan):
        paginas.append(Image.new("RGB", paginas[0].size, "white"))

    ancho, alto = landscape(A4)
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp_out.name, pagesize=landscape(A4))
    temp_files = []

    try:
        for i in range(0, len(paginas), 4):
            for izq, der in [(i, i + 2), (i + 3, i + 1)]:
                fi = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                fd = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                paginas[izq].save(fi, "JPEG")
                paginas[der].save(fd, "JPEG")
                temp_files.extend([fi, fd])
                c.drawImage(fi, 0, 0, ancho / 2, alto)
                c.drawImage(fd, ancho / 2, 0, ancho / 2, alto)
                c.showPage()
        c.save()
        return tmp_out.name
    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)


# ── INTERFAZ ─────────────────────────────────────────
st.markdown("""
<div class="hero">
    <span class="hero-icon">📖</span>
    <h1>Libro<span>PDF</span></h1>
    <p>Transforma cualquier PDF en un cuadernillo listo para imprimir y doblar.</p>
</div>
<div class="ornament">— ✦ —</div>
""", unsafe_allow_html=True)

archivo = st.file_uploader(
    "📄 Arrastra tu PDF aquí o haz clic · Máx. 10 MB",
    type="pdf"
)

if archivo:
    if archivo.size > 10 * 1024 * 1024:
        st.error("⚠️ El archivo supera los 200 MB.")
    else:
        st.info(f"📄 **{archivo.name}** listo para convertir")

        if st.button("✦ Generar cuadernillo"):
            salida = None
            with st.spinner("Reordenando páginas..."):
                try:
                    salida = hacer_libro_bytes(archivo.read())
                    with open(salida, "rb") as f:
                        st.success("✅ ¡Cuadernillo generado correctamente!")
                        nombre = f"librito_{os.path.splitext(archivo.name)[0]}.pdf"
                        st.download_button(
                            "⬇️ Descargar cuadernillo",
                            f,
                            file_name=nombre,
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    if salida and os.path.exists(salida):
                        os.remove(salida)

st.markdown("""
<div class="steps">
    <div class="step"><span class="step-num">①</span><span class="step-text">Sube tu PDF</span></div>
    <div class="step"><span class="step-num">②</span><span class="step-text">Genera el cuadernillo</span></div>
    <div class="step"><span class="step-num">③</span><span class="step-text">Imprime a doble cara</span></div>
    <div class="step"><span class="step-num">④</span><span class="step-text">Dobla y ¡listo!</span></div>
</div>
<div class="footer">LIBROPDF &nbsp;·&nbsp; Hecho con amor en Python por VoltioRed</div>
""", unsafe_allow_html=True)
