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

st.title("Schermata 4 - Esecuzione completa")

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
        os.remove('token.json')

    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    gc = gspread.authorize(creds)
    sht = gc.open_by_url(st.session_state.urlSS)
    worksheet = sht.get_worksheet(0)

    x = int(st.session_state.get("x", 100))
    y = int(st.session_state.get("y", 100))
    email_mittente = st.session_state.get("email_mittente")
    password = st.session_state.get("password")
    oggetto = st.session_state.get("oggetto")
    corpo = st.session_state.get("corpo")
    input_pdf = st.session_state.get("pdf_path")

    if not all([email_mittente, password, oggetto, corpo, input_pdf]):
        st.error("Dati mancanti!")
        return

    progress = st.progress(0)
    i = 0

    while worksheet.cell(2 + i, 4).value is not None:
        if worksheet.cell(2 + i, 6).value is None:
            nome = worksheet.cell(2+i, 2).value
            cognome = worksheet.cell(2+i, 3).value
            email = worksheet.cell(2+i, 4).value
            data = worksheet.cell(2+i, 5).value
            numero_biglietti = worksheet.cell(2+i, 6).value

            qr = qrcode.make(f"{nome} {cognome} {email} {data} {numero_biglietti}")
            qr_image = qr.convert("RGB")
            n = random.randint(1,9999)
            qr_path = f"/mnt/data/qr_{n}.png"
            qr_image.save(qr_path)

            doc = fitz.open(input_pdf)
            page = doc[0]
            rect = fitz.Rect(x, y, x + qr_image.width, y + qr_image.height)
            page.insert_image(rect, filename=qr_path)
            pdf_output_path = f"/mnt/data/biglietto_{n}.pdf"
            doc.save(pdf_output_path)
            doc.close()

            invia_email_con_allegato(email_mittente, password, email, oggetto, corpo, pdf_output_path)
            worksheet.update_cell(2 + i, 6, 'y')
        i += 1
        progress.progress(min(i * 10, 100))
        time.sleep(0.1)

    st.success("Operazione completata con successo!")

if st.button("Avvia processo completo"):
    process()