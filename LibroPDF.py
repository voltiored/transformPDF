import streamlit as st
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PIL import Image
import tempfile, os

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

    # Asegurar múltiplo de 4
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
        # limpiar imágenes temporales
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)


# ----------------------------
# INTERFAZ DE USUARIO
# ----------------------------

st.set_page_config(page_title="LibroPDF", page_icon="📘", layout="centered")

st.title("📘 LibroPDF")
st.markdown("""
Convierte cualquier PDF en formato **libro/cuadernillo** listo para imprimir y doblar.  
Cada hoja contendrá dos páginas del original.
""")

archivo = st.file_uploader("📄 Sube tu PDF", type="pdf")

if archivo:
    if archivo.size > 10 * 1024 * 1024:
        st.error("⚠️ El archivo es demasiado grande (máximo 10 MB).")
    else:
        st.info("Archivo cargado correctamente ✅")

        if st.button("✨ Generar PDF tipo libro"):
            salida = None  # 👈 clave para evitar el NameError

            with st.spinner("Procesando..."):
                try:
                    salida = hacer_libro_bytes(archivo.read())

                    with open(salida, "rb") as f:
                        st.success("✅ PDF tipo libro generado correctamente")

                        st.download_button(
                            "⬇️ Descargar PDF",
                            f,
                            file_name="LibroPDF.pdf",
                            mime="application/pdf"
                        )

                except Exception as e:
                    st.error(f"❌ Error al generar el PDF: {e}")

                finally:
                    if salida and os.path.exists(salida):
                        os.remove(salida)

st.markdown("---")
st.caption("Hecho con ❤️ en Python + Streamlit")