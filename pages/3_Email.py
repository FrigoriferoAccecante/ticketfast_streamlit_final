import streamlit as st

st.title("Schermata 3 - Dati Email")

oggetto = st.text_input("Oggetto email")
corpo = st.text_area("Corpo email")

if st.button("Salva dati email"):
    st.session_state.oggetto = oggetto
    st.session_state.corpo = corpo
    st.success("Dati salvati!")