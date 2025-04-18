import streamlit as st

def show():
    st.title("Schermata 1 - Inserisci URL Google Sheet")
    st.text_input("Inserisci l'URL del foglio", key="urlSS")

    if st.button("Avanti ▶️"):
        st.session_state.page = 'pages/2_Coordinate_e_PDF'