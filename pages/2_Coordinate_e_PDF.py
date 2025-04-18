import streamlit as st

st.title("Schermata 2 - Coordinate + Caricamento PDF")
st.number_input("Coordinata X", value=100, key="x")
st.number_input("Coordinata Y", value=100, key="y")
st.file_uploader("Carica un PDF", type="pdf", key="pdf_file")
