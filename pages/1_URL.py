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


st.title("Inserisci URL Google Sheet")

urlSS = st.text_input("Inserisci l'URL del foglio Google Sheet")

if 'urlSS' not in st.session_state:
    st.session_state.urlSS = ""

if st.button("Salva URL"):
    st.session_state.urlSS = urlSS
    st.success("URL salvato correttamente!")