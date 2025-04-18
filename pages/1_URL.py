import streamlit as st

def show():
    st.title("Inserisci URL Google Sheet")

    urlSS = st.text_input("Inserisci l'URL del foglio Google Sheet")

    if 'urlSS' not in st.session_state:
        st.session_state.urlSS = ""

    if st.button("Salva URL"):
        st.session_state.urlSS = urlSS
        st.success("URL salvato correttamente!")

    if st.button("Avanti ▶️"):
            st.session_state.page = 'pages/2_Coordinate_e_PDF'