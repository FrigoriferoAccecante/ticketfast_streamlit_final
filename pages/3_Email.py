import streamlit as st

st.title("SDati Email")

email_mittente = st.text_input("Email mittente")
password = st.text_input("Password segreta", type="password")
oggetto = st.text_input("Oggetto email")
corpo = st.text_area("Corpo email")

if st.button("Salva dati email"):
    st.session_state.email_mittente = email_mittente
    st.session_state.password = password
    st.session_state.oggetto = oggetto
    st.session_state.corpo = corpo
    st.success("Dati salvati!")