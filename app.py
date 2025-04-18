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

# Inizializza la pagina corrente
if 'page' not in st.session_state:
    st.session_state.page = 'pages/1_URL'

# Pagine disponibili
pages = {
    'pages/1_URL': 'pages/1_URL',
    'pages/2_Coordinate_e_PDF': 'pages/2_Coordinate_e_PDF',
    'pages/3_Email': 'pages/3_Email',
    'pages/4_Esecuzione': 'pages/4_Esecuzione',
}

# Import dinamico
import importlib.util
spec = importlib.util.spec_from_file_location("modulo", f"{st.session_state.page}.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.show()

st.set_page_config(page_title="TicketFast", layout="centered")
st.title("Benvenuto in TicketFast!")
st.markdown("Usa il menu a sinistra per navigare tra le schermate dell'app.")