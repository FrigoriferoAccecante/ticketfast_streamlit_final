import streamlit as st

def show():
    st.title("📢 Comunicazione importante")

    st.markdown("""
    Grazie per aver compilato il form!
    Prima di ricevere il biglietto, dovrai effettuare il pagamento secondo queste modalità:
    - Paypal: picciottiecarusi2@gmail.com
    - Bonifico bancario: IT72E3608105138267014967017 (intestatario Fabio Ruta)
                
    Una volta effettuato il pagamento, cliccare sulla casellina per procedere.
    """)

    st.markdown("---")

    accettato = st.checkbox("✅ Confermo di aver pagato.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀️ Indietro"):
            st.session_state.page_index -= 1

    with col2:
        if st.button("Avanti ▶️"):
            if not accettato:
                st.warning("Per favore, clicca la casella di conferma.")
            else:
                st.session_state.page_index += 1
