import sys
import streamlit as st
import subprocess
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from urllib.parse import urlparse
import numpy as np

# Configurazione della pagina
st.set_page_config(
    page_title="Excel GitHub Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Inizializza le variabili del session_state"""
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
    if 'sheet_names' not in st.session_state:
        st.session_state.sheet_names = []
    if 'current_sheet' not in st.session_state:
        st.session_state.current_sheet = None
    if 'url_input' not in st.session_state:
        st.session_state.url_input = ""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'file_info' not in st.session_state:
        st.session_state.file_info = {}
    if 'loading' not in st.session_state:
        st.session_state.loading = False

def convert_github_url_to_raw(github_url):
    """Converte un URL GitHub standard in un URL raw per il download diretto"""
    if "github.com" in github_url and "/blob/" in github_url:
        return github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return github_url

def download_excel_from_github(url):
    """Scarica un file Excel da GitHub"""
    try:
        raw_url = convert_github_url_to_raw(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(raw_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: Il download del file ha richiesto troppo tempo")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Errore di connessione: Impossibile raggiungere l'URL")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error("❌ File non trovato: Verifica che l'URL sia corretto")
        else:
            st.error(f"❌ Errore HTTP {e.response.status_code}: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Errore generico: {str(e)}")
        return None

def load_excel_data(excel_content, url):
    """Carica i dati Excel e li salva nel session_state"""
    try:
        excel_file = pd.ExcelFile(io.BytesIO(excel_content))
        sheet_names = excel_file.sheet_names
        
        # Salva nel session_state
        st.session_state.excel_data = {}
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(io.BytesIO(excel_content), sheet_name=sheet_name)
                st.session_state.excel_data[sheet_name] = df
            except Exception as e:
                st.warning(f"⚠️ Impossibile leggere il sheet '{sheet_name}': {str(e)}")
        
        st.session_state.sheet_names = list(st.session_state.excel_data.keys())
        st.session_state.current_sheet = st.session_state.sheet_names[0] if st.session_state.sheet_names else None
        st.session_state.data_loaded = True
        st.session_state.url_input = url
        st.session_state.file_info = {
            'url': url,
            'sheets_count': len(st.session_state.sheet_names),
            'file_size': len(excel_content)
        }
        return True
    except Exception as e:
        st.error(f"❌ Errore nella lettura del file Excel: {str(e)}")
        return False

def reset_data():
    """Reset completo dei dati"""
    st.session_state.excel_data = None
    st.session_state.sheet_names = []
    st.session_state.current_sheet = None
    st.session_state.data_loaded = False
    st.session_state.file_info = {}
    st.session_state.loading = False

def get_current_dataframe():
    """Ottiene il DataFrame corrente dal sheet selezionato"""
    if st.session_state.excel_data and st.session_state.current_sheet:
        return st.session_state.excel_data.get(st.session_state.current_sheet)
    return None

def display_basic_stats(df):
    """Mostra statistiche di base per il DataFrame"""
    st.subheader("📈 Statistiche di Base")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Righe", len(df))
    with col2:
        st.metric("Colonne", len(df.columns))
    with col3:
        st.metric("Valori Mancanti", df.isnull().sum().sum())
    with col4:
        st.metric("Memoria (KB)", f"{df.memory_usage(deep=True).sum() / 1024:.1f}")

    # Statistiche descrittive per colonne numeriche
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.subheader("📊 Statistiche Descrittive (Colonne Numeriche)")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)

    # Informazioni sui tipi di dati
    st.subheader("🔍 Informazioni sulle Colonne")
    column_info = pd.DataFrame({
        'Colonna': df.columns,
        'Tipo di Dato': df.dtypes.astype(str),
        'Valori Non Nulli': df.count(),
        'Valori Nulli': df.isnull().sum(),
        '% Valori Nulli': (df.isnull().sum() / len(df) * 100).round(2)
    })
    st.dataframe(column_info, use_container_width=True)

def create_plots(df):
    """Crea grafici per le colonne numeriche del DataFrame"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        st.warning("⚠️ Nessuna colonna numerica trovata per creare i grafici")
        return

    st.subheader("📈 Visualizzazioni")
    
    # Selezione delle colonne da visualizzare
    selected_cols = st.multiselect(
        "Seleziona le colonne numeriche da visualizzare:",
        options=list(numeric_cols),
        default=list(numeric_cols[:3])
    )

    if not selected_cols:
        st.info("👆 Seleziona almeno una colonna numerica per visualizzare i grafici")
        return

    # Tipi di grafici
    chart_types = st.multiselect(
        "Seleziona i tipi di grafici:",
        options=["Istogramma", "Box Plot", "Grafico a Linee", "Scatter Plot"],
        default=["Istogramma", "Box Plot"]
    )

    for chart_type in chart_types:
        if chart_type == "Istogramma":
            st.subheader("📊 Istogrammi")
            cols = st.columns(min(len(selected_cols), 3))
            for i, col in enumerate(selected_cols):
                with cols[i % 3]:
                    fig = px.histogram(df, x=col, title=f"Distribuzione di {col}")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Box Plot":
            st.subheader("📦 Box Plot")
            fig = go.Figure()
            for col in selected_cols:
                fig.add_trace(go.Box(y=df[col], name=col))
            fig.update_layout(title="Box Plot delle Colonne Selezionate", height=500)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Grafico a Linee":
            st.subheader("📈 Grafico a Linee")
            fig = go.Figure()
            for col in selected_cols:
                fig.add_trace(go.Scatter(y=df[col], mode='lines', name=col))
            fig.update_layout(title="Andamento delle Colonne Selezionate", height=500)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter Plot" and len(selected_cols) >= 2:
            st.subheader("🎯 Scatter Plot")
            col1_scatter = st.selectbox("Seleziona colonna X:", selected_cols, key="scatter_x")
            col2_scatter = st.selectbox("Seleziona colonna Y:", 
                                      [col for col in selected_cols if col != col1_scatter], 
                                      key="scatter_y")
            fig = px.scatter(df, x=col1_scatter, y=col2_scatter, 
                           title=f"Scatter Plot: {col1_scatter} vs {col2_scatter}")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Inizializza session_state
    initialize_session_state()

    # Titolo
    st.title("📊 Excel GitHub Analyzer")
    st.markdown("Analizza file Excel direttamente da repository GitHub con una semplice URL.")

    # Sidebar per controlli
    with st.sidebar:
        st.header("⚙️ Controlli")
        
        # Pulsanti di controllo
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Reset", use_container_width=True):
                reset_data()
                st.rerun()
        
        with col2:
            if st.button("🔄 Ricarica", use_container_width=True, disabled=not st.session_state.data_loaded):
                if st.session_state.url_input:
                    st.session_state.loading = True
                    st.rerun()

        # URL di esempio
        st.subheader("🔗 URL di Esempio")
        example_url = "https://github.com/plotly/datasets/blob/master/2014_world_gdp_with_codes.xlsx"
        st.code(example_url, language="text")
        
        if st.button("Usa URL di Esempio"):
            st.session_state.url_input = example_url

        # Informazioni file caricato
        if st.session_state.data_loaded:
            st.success("✅ File Caricato!")
            with st.expander("ℹ️ Info File"):
                st.write(f"**URL:** ...{st.session_state.file_info['url'][-30:]}")
                st.write(f"**Sheets:** {st.session_state.file_info['sheets_count']}")
                st.write(f"**Dimensione:** {st.session_state.file_info['file_size']:,} bytes")

    # Area principale
    if not st.session_state.data_loaded:
        # Input URL
        st.header("🌐 Inserisci URL del File Excel da GitHub")
        
        url_input = "https://github.com/FrigoriferoAccecante/ticketfast_streamlit_final/blob/pec_form/P%26C%20reports.xlsx"
        # Pulsante per analizzare
        if st.button("🚀 Analizza File", type="primary", use_container_width=True):
            if not url_input:
                st.warning("⚠️ Per favore inserisci un URL valido")
                return
            
            st.session_state.loading = True
            
            with st.spinner("📥 Scaricando il file da GitHub..."):
                excel_content = download_excel_from_github(url_input)
            
            if excel_content is not None:
                with st.spinner("📖 Caricando i dati Excel..."):
                    if load_excel_data(excel_content, url_input):
                        st.success("✅ File caricato con successo!")
                        st.session_state.loading = False
                        st.rerun()
                    else:
                        st.session_state.loading = False
            else:
                st.session_state.loading = False

        # Istruzioni
        st.markdown("---")
        st.markdown("""
        **Come utilizzare questa app:**
        1. Vai su GitHub e trova il file Excel che vuoi analizzare
        2. Copia l'URL del file (sia l'URL normale che quello raw funzionano)
        3. Incolla l'URL nel campo sopra e clicca "Analizza File"
        4. Esplora i dati utilizzando le diverse sezioni
        
        **Formati supportati:** .xlsx, .xls
        """)

    else:
        # Visualizzazione dati caricati
        st.header("📋 Analisi dei Dati")
        
        # Selezione del sheet se ci sono più sheet
        if len(st.session_state.sheet_names) > 1:
            selected_sheet = st.selectbox(
                "📋 Seleziona il sheet da analizzare:",
                options=st.session_state.sheet_names,
                index=st.session_state.sheet_names.index(st.session_state.current_sheet),
                key="sheet_selector"
            )
            
            if selected_sheet != st.session_state.current_sheet:
                st.session_state.current_sheet = selected_sheet
                st.rerun()
        else:
            st.info(f"📋 Sheet: **{st.session_state.current_sheet}**")

        # Ottieni DataFrame corrente
        df = get_current_dataframe()
        
        if df is not None and not df.empty:
            # Tab per organizzare il contenuto
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Dati", "📈 Statistiche", "🎨 Grafici", "🔍 Filtri & Download"])

            with tab1:
                st.subheader(f"📊 Dati del Sheet: {st.session_state.current_sheet}")
                
                # Controlli per la visualizzazione
                col1, col2 = st.columns(2)
                with col1:
                    show_rows = st.number_input(
                        "Righe da mostrare:",
                        min_value=1,
                        max_value=len(df),
                        value=min(100, len(df))
                    )
                with col2:
                    show_index = st.checkbox("Mostra indice righe", value=False)

                # Mostra DataFrame
                st.dataframe(df.head(int(show_rows)), use_container_width=True, hide_index=not show_index)

            with tab2:
                display_basic_stats(df)

            with tab3:
                create_plots(df)

            with tab4:
                st.subheader("🔍 Filtri e Download")
                
                # Filtro colonne
                if len(df.columns) > 10:
                    selected_columns = st.multiselect(
                        "Seleziona colonne da visualizzare:",
                        options=list(df.columns),
                        default=list(df.columns[:10])
                    )
                    filtered_df = df[selected_columns] if selected_columns else df
                else:
                    filtered_df = df

                # Filtro di ricerca
                search_term = st.text_input("Cerca nei dati:", placeholder="Inserisci termine di ricerca...")
                if search_term:
                    mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    filtered_df = filtered_df[mask]

                # Mostra dati filtrati
                st.dataframe(filtered_df, use_container_width=True)

                # Download
                col1, col2 = st.columns(2)
                with col1:
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Scarica CSV Filtrato",
                        data=csv,
                        file_name=f"{st.session_state.current_sheet}_filtered.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    excel_buffer = io.BytesIO()
                    filtered_df.to_excel(excel_buffer, sheet_name=st.session_state.current_sheet, index=False)
                    excel_data = excel_buffer.getvalue()
                    st.download_button(
                        label="📊 Scarica Excel Filtrato",
                        data=excel_data,
                        file_name=f"{st.session_state.current_sheet}_filtered.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.warning(f"⚠️ Il sheet '{st.session_state.current_sheet}' è vuoto o non leggibile")

    # Gestione ricarica
    if st.session_state.loading and st.session_state.url_input:
        with st.spinner("🔄 Ricaricando il file..."):
            excel_content = download_excel_from_github(st.session_state.url_input)
            if excel_content is not None:
                if load_excel_data(excel_content, st.session_state.url_input):
                    st.success("✅ File ricaricato con successo!")
                    st.session_state.loading = False
                    st.rerun()

if __name__ == "__main__":
    main()