import streamlit as st
import time
import os
import random
import gspread
import qrcode
import fitz
import smtplib
import pandas as pd
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials

import os
import streamlit as st

def git_push_excel(file_path, branch="pec_excel"):
    
    # Costruisci l'URL autenticato per il remote

    auth_repo_url = "https://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@github.com/"


    # Cambia remote temporaneamente
    os.system(f"git remote set-url origin {auth_repo_url}")

    # Aggiungi e committa
    os.system(f'git add "{file_path}"')
    commit_message = f'Aggiornamento automatico {file_path}'
    os.system(f'git commit -m "{commit_message}" || echo "Niente da committare"')

    # Push
    result = os.system(f"git push origin {branch}")
    if result == 0:
        st.success("✅ Push su GitHub effettuato!")
    else:
        st.error("❌ Push fallito! Controlla i log/permessi.")

def download_excel(file_path, sheet_name="Foglio1"):
    try:
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        st.success(f"File pronto per il download! ({len(bytes_data)//1024} KB)")
        st.download_button(
            label="📥 Scarica Excel aggiornato",
            data=bytes_data,
            file_name=f"inviti_data_aggiornato.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except FileNotFoundError:
        st.error(f"Il file '{file_path}' non esiste.")
    except Exception as e:
        st.error(f"Errore durante il download: {e}")


def salva_dati_excel(nome, cognome, email, data, numero_biglietti_prima, numero_biglietti_seconda, file_path="P&C reports.xlsx"):
    """
    Salva i dati nel file Excel (append)
    """
    try:
        
        # Crea nuovo record
        nuovo_record = {
            'NOME': nome,
            'COGNOME': cognome,
            'EMAIL': email,
            'SERATE': data,
            'NUMERO PRIMA': numero_biglietti_prima,
            'NUMERO SECONDA': numero_biglietti_seconda
        }
        sheet_name = "Muto cu sape u jocu"
        if os.path.exists(file_path):
            # Carica i dati esistenti dal foglio richiesto
            df_esistente = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            
            # Crea un DataFrame solo con la nuova riga
            df_nuova = pd.DataFrame([nuovo_record])
           
            # Concatena (append) la nuova riga sotto le esistenti
            df_finale = pd.concat([df_esistente, df_nuova], ignore_index=True)

        else:
            # Se il file non esiste ancora, crea DataFrame direttamente
            df_finale = pd.DataFrame([nuovo_record])
        # Scrivi il DataFrame aggiornato NEL FOGLIO che vuoi, lasciando invariati eventuali altri fogli
        with pd.ExcelWriter(file_path, engine="openpyxl", mode='a' if os.path.exists(file_path) else 'w', if_sheet_exists="replace") as writer:
            df_finale.to_excel(file_path, sheet_name=sheet_name, index=False)
            git_push_excel(file_path)
            download_excel(file_path, sheet_name)
        return True
    except Exception as e:
        st.error(f"Errore nel salvataggio: {str(e)}")
        return False

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
        '''
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            #creds = ServiceAccountCredentials.from_json_keyfile_name('qr-ticket-438612-2e9415800f59.json', SCOPES)
            
        else:
            st.error("token.json non trovato. Generalo in locale e caricalo sul server.")
            return

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        gc = gspread.authorize(creds)
        sht = gc.open_by_url("https://docs.google.com/spreadsheets/d/1JKjWoutLbN3kE1pDxYttduJSkQtPJV9upWqr0uLeQ3Y/edit?resourcekey=&gid=1686242127#gid=1686242127")
        worksheet = sht.get_worksheet(1)
        '''
        x = 2065
        y = 298
        email_mittente = "picciottiecarusi2@gmail.com"
        password = "eaty uqmz nlyf sczi"
        oggetto = "Invito a \'Mutu cu sapi u jocu\'"
        corpo = "Grazie per voler partecipare alla commedia \'Mutu cu sapi u jocu\' della Picciotti&Carusi.\nIn allegato trovi il tuo invito!"
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

        # 1. Salva dati in Excel
        if not salva_dati_excel(nome, cognome, email, data, numero_biglietti_prima, numero_biglietti_seconda):
            st.error("❌ Errore nel salvataggio dati!")
            return
        
            
        '''
        #Salvo statistica inviti
        worksheet.append_row([
            st.session_state["nome"],
            st.session_state["cognome"],
            st.session_state["email"],
            st.session_state["data_scelta"],
            int(st.session_state["n_biglietti_prima"]),
            int(st.session_state["n_biglietti_seconda"])
        ])
        '''
        qr = qrcode.make(f"Nome:{nome} Cognome:{cognome} e-mail:{email} Serata:{data} Numero biglietti prima:{numero_biglietti_prima} Numero biglietti seconda:{numero_biglietti_seconda}",box_size=5, border=4)
        qr_image = qr.convert("RGB")
        n = random.randint(1,9999)
        qr_path = os.path.join("temp", f"qr_{n}.png")
        qr_image.save(qr_path)

        doc = fitz.open(input_pdf)
        page = doc[0]
        rect = fitz.Rect(x, y, x + qr_image.width, y + qr_image.height)
        page.insert_image(rect, filename=qr_path)
        pdf_output_path = os.path.join("temp", f"invito_{n}.pdf")
        doc.save(pdf_output_path)
        doc.close()

        invia_email_con_allegato(email_mittente, password, email, oggetto, corpo, pdf_output_path)

        progress.progress(100)
        time.sleep(0.1)

        st.success("Operazione completata con successo!")

    if st.button("Genera invito"):
        process()
