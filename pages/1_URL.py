import streamlit as st


st.title("Inserisci URL Google Sheet")

urlSS = st.text_input("Inserisci l'URL del foglio Google Sheet")

if 'urlSS' not in st.session_state:
    st.session_state.urlSS = ""

if st.button("Salva URL"):
    st.session_state.urlSS = urlSS
    st.success("URL salvato correttamente!")