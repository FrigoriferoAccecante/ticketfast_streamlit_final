import streamlit as st
import time
import os
import random
import gspread
import qrcode
import fitz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

def show():
    st.title("Pagina 2 - Richiedi il tuo invito")

    st.markdown("""
    Cliccare il tasto \"Genera invito\" e una volta completato, controllare che sia arrivata la email.
                
    IMPORTANTE: Controllare sia la POSTA IN ARRIVO che la POSTA INDESIDERATA/SPAM
    """)
    os.makedirs("temp", exist_ok=True)
    def invia_email_con_allegato(email_mittente, password, email_destinatario, oggetto, corpo, percorso_allegato):
        msg = MIMEMultipart()
        msg['From'] = email_mittente
        msg['To'] = email_destinatario
        msg['Subject'] = oggetto
        msg.attach(MIMEText(corpo, 'plain'))

        with open(percorso_allegato, "rb") as allegato:
            parte_allegato = MIMEBase('application', 'octet-stream')
            parte_allegato.set_payload(allegato.read())
            encoders.encode_base64(parte_allegato)
            parte_allegato.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(percorso_allegato)}")
            msg.attach(parte_allegato)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_mittente, password)
            server.sendmail(email_mittente, email_destinatario, msg.as_string())
            server.quit()
            st.success(f"Email inviata a {email_destinatario}")
        except Exception as e:
            st.error(f"Errore durante l'invio dell'email: {e}")

    def process():
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        else:
            st.error("token.json non trovato. Generalo in locale e caricalo sul server.")
            return

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        gc = gspread.authorize(creds)
        sht = gc.open_by_url("https://docs.google.com/spreadsheets/d/1JKjWoutLbN3kE1pDxYttduJSkQtPJV9upWqr0uLeQ3Y/edit?resourcekey=&gid=1686242127#gid=1686242127")
        worksheet = sht.get_worksheet(0)

        x = 1920
        y = 220
        email_mittente = "picciottiecarusi2@gmail.com"
        password = "xthv czht fcxs zwmn"
        oggetto = "Invito a \'Un caso per Caso\'"
        corpo = "Grazie per voler partecipare alla commedia \'Un caso per Caso\' della Picciotti&Carusi.\nIn allegato trovi il tuo invito!"
        input_pdf = os.path.join("moduli", "png2pdf.pdf")

        if not all([email_mittente, password, oggetto, corpo, input_pdf]):
            st.error("Dati mancanti!")
            return

        progress = st.progress(0)
        i = 0


        nome = st.session_state.get("nome")
        cognome = st.session_state.get("cognome")
        email = st.session_state.get("email")
        data = st.session_state.get("data_scelta")
        numero_biglietti_prima = st.session_state.get("n_biglietti_prima")
        numero_biglietti_seconda = st.session_state.get("n_biglietti_seconda")

        #Salvo statistica inviti
        worksheet.append_row([
            st.session_state["nome"],
            st.session_state["cognome"],
            st.session_state["email"],
            st.session_state["data_scelta"],
            st.session_state["n_biglietti_prima"],
            st.session_state["n_biglietti_seconda"]
        ])

        qr = qrcode.make(f"Nome:{nome} Cognome:{cognome} e-mail:{email} Serata:{data} Numero biglietti prima:{numero_biglietti_prima} Numero biglietti seconda:{numero_biglietti_seconda}")
        qr_image = qr.convert("RGB")
        n = random.randint(1,9999)
        qr_path = os.path.join("temp", f"qr_{n}.png")
        qr_image.save(qr_path)

        doc = fitz.open(input_pdf)
        page = doc[0]
        rect = fitz.Rect(x, y, x + qr_image.width, y + qr_image.height)
        page.insert_image(rect, filename=qr_path)
        pdf_output_path = os.path.join("temp", f"biglietto_{n}.pdf")
        doc.save(pdf_output_path)
        doc.close()

        invia_email_con_allegato(email_mittente, password, email, oggetto, corpo, pdf_output_path)

        progress.progress(100)
        time.sleep(0.1)

        st.success("Operazione completata con successo!")

    if st.button("Genera invito"):
        process()
