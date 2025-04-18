import streamlit as st


st.title("Schermata 3 - Dati Email")
st.text_input("Email mittente", key="email_mittente")
st.text_input("Password app", type="password", key="password")
st.text_input("Oggetto email", key="oggetto")
st.text_area("Corpo email", key="corpo")
