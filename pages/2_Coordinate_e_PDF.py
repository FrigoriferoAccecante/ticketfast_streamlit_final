import streamlit as st
from PyPDF2 import PdfReader
import fitz
from PIL import Image
import qrcode
import os

st.title("Schermata 2 - Coordinate + Caricamento PDF")
os.makedirs("temp", exist_ok=True)
x = st.number_input("Coordinata X", value=100)
y = st.number_input("Coordinata Y", value=100)

pdf_file = st.file_uploader("Carica un file PDF", type=["pdf"])

def add_qr_code_to_pdf(uploaded_file, x, y):
    qr_data = "QR di test"
    qr = qrcode.make(qr_data)
    qr_image = qr.convert("RGB")
    qr_path = os.path.join("temp", "qr_code_image.png")
    qr_image.save(qr_path)

    input_path = os.path.join("temp", "input.pdf")
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    doc = fitz.open(input_path)
    page = doc[0]
    rect = fitz.Rect(x, y, x + qr_image.width, y + qr_image.height)
    page.insert_image(rect, filename=qr_path)
    output_path = os.path.join("temp", "output.pdf")
    doc.save(output_path)
    doc.close()
    return output_path

if pdf_file and st.button("Carica PDF e genera anteprima con QR"):
    output_path = add_qr_code_to_pdf(pdf_file, x, y)
    st.session_state.pdf_path = output_path
    st.success("PDF aggiornato!")

if "pdf_path" in st.session_state:
    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button("Scarica anteprima PDF aggiornato", data=f, file_name="output.pdf")