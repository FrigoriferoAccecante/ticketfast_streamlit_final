import streamlit as st
import subprocess
import sys
import os
import importlib.util

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
importlib.util
"""
st.set_page_config(page_title="TicketFast", layout="centered", initial_sidebar_state="collapsed")
st.title("Benvenuto in TicketFast!")
st.markdown("Clicca \"Avanti\" per procedere.")
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
# Elenco delle pagine in ordine
page_order = [
    'moduli/1_Modulo_Utente',
    'moduli/2_Comunicazione pagamento',
    'moduli/3_Esecuzione'
]

# Inizializza l'indice della pagina se non presente
if  not st.session_state.get('page_index'):
    st.session_state.page_index = 0

# Carica e mostra la pagina corrente
spec = importlib.util.spec_from_file_location("modulo", f"{page_order[st.session_state.page_index]}.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.show()




# Pulsanti di navigazione
st.markdown("---")
can_advance = True

if st.session_state.page_index == 0:
    if not st.session_state.get("submitted"):
        can_advance = st.session_state.get("modulo_inviato", False)
col1, col2 = st.columns(2)

if st.session_state.page_index > 0:
    with col1:
        if st.button("◀️ Indietro",key="btn_indietro"):
            st.session_state.page_index -= 1
            st.rerun()

if st.session_state.page_index < len(page_order) - 1:
    with col2:
        if st.button("Avanti ▶️",key="btn_avanti"):
            if can_advance:
                st.session_state.page_index += 1
                st.rerun()
            else:
                st.warning("Devi inviare il modulo prima di proseguire.") 



