import streamlit as st
import importlib.util

if 'page' not in st.session_state:
    st.session_state.page = 'pages/1_URL'

spec = importlib.util.spec_from_file_location("modulo", f"{st.session_state.page}.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.show()