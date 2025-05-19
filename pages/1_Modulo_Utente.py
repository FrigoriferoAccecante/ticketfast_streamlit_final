import streamlit as st

def show():
    st.title("Pagina 1 - Modulo di Inserimento Dati")

    with st.form("modulo_utente"):
        nome = st.text_input("Nome")
        cognome = st.text_input("Cognome")
        email = st.text_input("Email")
        
        st.title("Modulo - Seleziona una data")

        date_options = [
            "Prima serata - 5 Giugno 2025",
            "Seconda serata - 6 Giugno 2025",
            "Entrambe le serate"
        ]

        data_scelta = st.radio("Scegli una data disponibile:", date_options)

        
        n_biglietti_prima = st.text_input("Numero biglietti prima serata")
        n_biglietti_seconda = st.text_input("Numero biglietti seconda serata")

        submitted = st.form_submit_button("Invia")
        if submitted:
            if not nome or not cognome or not email or not data_scelta or not n_biglietti_prima or not n_biglietti_seconda:
                st.warning("Per favore, completa tutti i campi obbligatori e accetta i termini.")
            else:
                st.session_state.nome = nome
                st.session_state.cognome = cognome
                st.session_state.email = email
                st.session_state.data_scelta = data_scelta
                st.session_state.n_biglietti_prima = n_biglietti_prima
                st.session_state.n_biglietti_seconda = n_biglietti_seconda

                # Puoi aggiungere qui la logica per salvare i dati, ad esempio in un Google Sheet o un database
    st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("◀️ Indietro"):
        st.session_state.page_index -= 1
        st.rerun()

with col2:
    if st.button("Avanti ▶️"):
        if not st.session_state.nome or not st.session_state.cognome or not st.session_state.email or not st.session_state.data_scelta or not st.session_state.n_biglietti_prima or not st.session_state.n_biglietti_seconda:
            st.warning("Per favore, inserisci tutti i dati.")
        else:
            st.session_state.page_index += 1
            st.rerun()
