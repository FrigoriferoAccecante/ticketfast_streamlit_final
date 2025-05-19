import streamlit as st
import subprocess
import sys
import os

requirements = """\
streamlit
PyPDF2
pymupdf
pillow
qrcode
gspread
oauth2client
os
PIL
fitz
time
random
smtplib
InstalledAppFlow
"""

# Salva i pacchetti in requirements.txt, se non esiste
if not os.path.exists("requirements.txt"):
    with open("requirements.txt", "w") as f:
        f.write(requirements)

# Esegue pip install -r requirements.txt
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
except subprocess.CalledProcessError as e:
    print("Errore durante l'installazione delle dipendenze:", e)
    sys.exit(1)
st.set_page_config(page_title="TicketFast", layout="centered")
st.title("Benvenuto in TicketFast!")
st.markdown("Clicca \"Avanti\" per procedere.")

col1, col2 = st.columns(2)
with col2:
    if st.button("Avanti ▶️"):
        st.session_state.page = 'pages/1_Modulo_Utente.py'