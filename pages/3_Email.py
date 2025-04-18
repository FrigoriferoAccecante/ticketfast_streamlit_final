import streamlit as st

def show():
    st.title("Schermata 3 - Dati Email")
    st.text_input("Email mittente", key="email_mittente")
    st.text_input("Password app", type="password", key="password")
    st.text_input("Oggetto email", key="oggetto")
    st.text_area("Corpo email", key="corpo")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀️ Indietro"):
            st.session_state.page = 'pages/2_Coordinate_e_PDF'
    with col2:
        if st.button("Avanti ▶️"):
            st.session_state.page = 'pages/4_Esecuzione'