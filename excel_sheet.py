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

def convert_github_url_to_raw(github_url):
    """
    Converte un URL GitHub standard in un URL raw per il download diretto del file
    
    Args:
        github_url (str): URL del file su GitHub
        
    Returns:
        str: URL raw per il download diretto
    """
    if "github.com" in github_url and "/blob/" in github_url:
        return github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return github_url

def download_excel_from_github(url):
    """
    Scarica un file Excel da un repository GitHub
    
    Args:
        url (str): URL del file Excel su GitHub
        
    Returns:
        bytes: Contenuto del file Excel come bytes, None se errore
    """
    try:
        # Converte URL GitHub in URL raw se necessario
        raw_url = convert_github_url_to_raw(url)
        
        # Headers per simulare un browser (alcuni repository potrebbero richiedere questo)
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

def load_excel_data(excel_content):
    """
    Carica i dati da un file Excel
    
    Args:
        excel_content (bytes): Contenuto del file Excel
        
    Returns:
        dict: Dizionario con i nomi dei sheet come chiavi e i DataFrame come valori
    """
    try:
        # Legge il file Excel con tutti i sheet
        excel_file = pd.ExcelFile(io.BytesIO(excel_content))
        sheet_names = excel_file.sheet_names
        
        data_dict = {}
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(io.BytesIO(excel_content), sheet_name=sheet_name)
                data_dict[sheet_name] = df
            except Exception as e:
                st.warning(f"⚠️ Impossibile leggere il sheet '{sheet_name}': {str(e)}")
        
        return data_dict
        
    except Exception as e:
        st.error(f"❌ Errore nella lettura del file Excel: {str(e)}")
        return None

def display_basic_stats(df):
    """
    Mostra statistiche di base per il DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame da analizzare
    """
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
    """
    Crea grafici per le colonne numeriche del DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame da visualizzare
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        st.warning("⚠️ Nessuna colonna numerica trovata per creare i grafici")
        return
    
    st.subheader("📈 Visualizzazioni")
    
    # Selezione delle colonne da visualizzare
    selected_cols = st.multiselect(
        "Seleziona le colonne numeriche da visualizzare:",
        options=list(numeric_cols),
        default=list(numeric_cols[:3])  # Seleziona le prime 3 colonne per default
    )
    
    if not selected_cols:
        st.info("👆 Seleziona almeno una colonna numerica per visualizzare i grafici")
        return
    
    # Tipi di grafici disponibili
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
    """
    Funzione principale dell'applicazione Streamlit
    """
    try:
     subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print("Errore durante l'installazione delle dipendenze:", e)
        sys.exit(1)
    # Titolo e descrizione
    st.title("📊 Excel GitHub Analyzer")
    st.markdown("""
    Questa app ti permette di analizzare file Excel direttamente da repository GitHub.
    Inserisci l'URL di un file Excel e ottieni visualizzazioni e statistiche istantanee!
    """)
    
    # Sidebar per i controlli
    with st.sidebar:
        st.header("⚙️ Configurazioni")
        
        # URL di esempio
        st.subheader("🔗 URL di Esempio")
        example_url = "https://github.com/plotly/datasets/blob/master/2014_world_gdp_with_codes.xlsx"
        st.code(example_url, language="text")
        
        if st.button("Usa URL di Esempio"):
            st.session_state.url_input = example_url
    
    # Input URL
    url_input = "https://github.com/FrigoriferoAccecante/ticketfast_streamlit_final/blob/pec_form/P%26C%20reports.xlsx"
    
    # Pulsante per analizzare
    if st.button("🚀 Analizza File", type="primary"):
        if not url_input:
            st.warning("⚠️ Per favore inserisci un URL valido")
            return
        
        with st.spinner("📥 Scaricando il file..."):
            excel_content = download_excel_from_github(url_input)
        
        if excel_content is None:
            return
        
        with st.spinner("📖 Leggendo i dati..."):
            data_dict = load_excel_data(excel_content)
        
        if data_dict is None:
            return
        
        if len(data_dict) == 0:
            st.error("❌ Nessun sheet valido trovato nel file Excel")
            return
        
        st.success(f"✅ File caricato con successo! Trovati {len(data_dict)} sheet.")
        
        # Selezione del sheet
        if len(data_dict) > 1:
            selected_sheet = st.selectbox(
                "📋 Seleziona il sheet da analizzare:",
                options=list(data_dict.keys()),
                index=0
            )
        else:
            selected_sheet = list(data_dict.keys())[0]
            st.info(f"📋 Sheet selezionato: **{selected_sheet}**")
        
        df = data_dict[selected_sheet]
        
        if df.empty:
            st.warning(f"⚠️ Il sheet '{selected_sheet}' è vuoto")
            return
        
        # Tab per organizzare il contenuto
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dati", "📈 Statistiche", "🎨 Grafici", "💾 Download"])
        
        with tab1:
            st.subheader(f"📊 Dati del Sheet: {selected_sheet}")
            
            # Filtri per la visualizzazione
            col1, col2 = st.columns(2)
            with col1:
                show_rows = st.number_input("Numero di righe da mostrare:", 
                                          min_value=10, max_value=len(df), 
                                          value=min(100, len(df)))
            with col2:
                if len(df.columns) > 10:
                    show_all_columns = st.checkbox("Mostra tutte le colonne", value=False)
                    if not show_all_columns:
                        selected_columns = st.multiselect(
                            "Seleziona colonne da visualizzare:",
                            options=list(df.columns),
                            default=list(df.columns[:5])
                        )
                        if selected_columns:
                            df_display = df[selected_columns].head(int(show_rows))
                        else:
                            df_display = df.head(int(show_rows))
                    else:
                        df_display = df.head(int(show_rows))
                else:
                    df_display = df.head(int(show_rows))
            
            st.dataframe(df_display, use_container_width=True)
        
        with tab2:
            display_basic_stats(df)
        
        with tab3:
            create_plots(df)
        
        with tab4:
            st.subheader("💾 Download Dati")
            
            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Scarica come CSV",
                data=csv,
                file_name=f"{selected_sheet}.csv",
                mime="text/csv"
            )
            
            # Download Excel
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, sheet_name=selected_sheet, index=False)
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="📊 Scarica come Excel",
                data=excel_data,
                file_name=f"{selected_sheet}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Come utilizzare questa app:**
    1. Vai su GitHub e trova il file Excel che vuoi analizzare
    2. Copia l'URL del file (sia l'URL normale che quello raw funzionano)
    3. Incolla l'URL nel campo sopra e clicca "Analizza File"
    4. Esplora i dati utilizzando le diverse tab
    
    **Formati supportati:** .xlsx, .xls
    """)

if __name__ == "__main__":
    main()
