import streamlit as st

def show():
    st.title("Schermata 2 - Coordinate + Caricamento PDF")
    st.number_input("Coordinata X", value=100, key="x")
    st.number_input("Coordinata Y", value=100, key="y")
    st.file_uploader("Carica un PDF", type="pdf", key="pdf_file")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀️ Indietro"):
            st.session_state.page = 'pages/1_URL'
    with col2:
        if st.button("Avanti ▶️"):
            st.session_state.page = 'pages/3_Email'