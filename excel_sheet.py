import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Configurazione della pagina
st.set_page_config(
    page_title="Excel Data Manager", 
    page_icon="📊", 
    layout="wide"
)

def initialize_session_state():
    """Inizializza tutte le variabili del session_state"""
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
    
    if 'sheet_names' not in st.session_state:
        st.session_state.sheet_names = []
    
    if 'current_sheet' not in st.session_state:
        st.session_state.current_sheet = None
    
    if 'url_input' not in st.session_state:
        st.session_state.url_input = ""
    
    if 'loading_state' not in st.session_state:
        st.session_state.loading_state = False
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ""
    
    if 'file_info' not in st.session_state:
        st.session_state.file_info = {}

def load_excel_from_url(url):
    """Carica file Excel da URL"""
    try:
        st.session_state.loading_state = True
        st.session_state.error_message = ""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        excel_file = BytesIO(response.content)
        excel_data = pd.ExcelFile(excel_file)
        
        # Salva i dati nel session_state
        st.session_state.excel_data = excel_data
        st.session_state.sheet_names = excel_data.sheet_names
        st.session_state.current_sheet = excel_data.sheet_names[0]
        st.session_state.data_loaded = True
        st.session_state.file_info = {
            'url': url,
            'sheets_count': len(excel_data.sheet_names),
            'file_size': len(response.content)
        }
        
        st.session_state.loading_state = False
        return True
        
    except Exception as e:
        st.session_state.loading_state = False
        st.session_state.error_message = f"Errore nel caricamento: {str(e)}"
        st.session_state.data_loaded = False
        return False

def load_excel_from_file(uploaded_file):
    """Carica file Excel da file caricato"""
    try:
        st.session_state.loading_state = True
        st.session_state.error_message = ""
        
        excel_data = pd.ExcelFile(uploaded_file)
        
        # Salva i dati nel session_state
        st.session_state.excel_data = excel_data
        st.session_state.sheet_names = excel_data.sheet_names
        st.session_state.current_sheet = excel_data.sheet_names[0]
        st.session_state.data_loaded = True
        st.session_state.file_info = {
            'filename': uploaded_file.name,
            'sheets_count': len(excel_data.sheet_names),
            'file_size': uploaded_file.size
        }
        
        st.session_state.loading_state = False
        return True
        
    except Exception as e:
        st.session_state.loading_state = False
        st.session_state.error_message = f"Errore nel caricamento: {str(e)}"
        st.session_state.data_loaded = False
        return False

def reset_data():
    """Reset completo dei dati"""
    st.session_state.excel_data = None
    st.session_state.sheet_names = []
    st.session_state.current_sheet = None
    st.session_state.url_input = ""
    st.session_state.data_loaded = False
    st.session_state.error_message = ""
    st.session_state.file_info = {}

def get_current_dataframe():
    """Ottiene il DataFrame corrente dal sheet selezionato"""
    if st.session_state.excel_data and st.session_state.current_sheet:
        try:
            return pd.read_excel(st.session_state.excel_data, sheet_name=st.session_state.current_sheet)
        except Exception as e:
            st.session_state.error_message = f"Errore nella lettura del sheet: {str(e)}"
            return None
    return None

def main():
    # Inizializza session_state
    initialize_session_state()
    
    st.title("📊 Excel Data Manager")
    st.markdown("Gestione avanzata di file Excel con session state persistente")
    
    # Sidebar per controlli
    with st.sidebar:
        st.header("🔧 Controlli")
        
        # Pulsanti di controllo
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Reset", use_container_width=True):
                reset_data()
                st.rerun()
        
        with col2:
            if st.button("🔄 Ricarica", use_container_width=True, disabled=not st.session_state.data_loaded):
                if 'url' in st.session_state.file_info:
                    load_excel_from_url(st.session_state.file_info['url'])
                st.rerun()
        
        # Informazioni file caricato
        if st.session_state.data_loaded:
            st.success("✅ Dati caricati!")
            with st.expander("ℹ️ Info File"):
                if 'filename' in st.session_state.file_info:
                    st.write(f"**File:** {st.session_state.file_info['filename']}")
                elif 'url' in st.session_state.file_info:
                    st.write(f"**URL:** {st.session_state.file_info['url'][:50]}...")
                
                st.write(f"**Sheets:** {st.session_state.file_info.get('sheets_count', 0)}")
                st.write(f"**Dimensione:** {st.session_state.file_info.get('file_size', 0):,} bytes")
    
    # Area principale
    if not st.session_state.data_loaded:
        # Sezione caricamento dati
        st.header("📁 Carica Dati Excel")
        
        tab1, tab2 = st.tabs(["📎 File Upload", "🌐 Da URL"])
        
        with tab1:
            uploaded_file = st.file_uploader(
                "Scegli un file Excel",
                type=['xlsx', 'xls'],
                key="file_uploader"
            )
            
            if uploaded_file and st.button("Carica File", key="load_file"):
                with st.spinner("Caricamento in corso..."):
                    if load_excel_from_file(uploaded_file):
                        st.success("File caricato con successo!")
                        st.rerun()
        
        with tab2:
            url_input = st.text_input(
                "URL del file Excel",
                value=st.session_state.url_input,
                placeholder="https://esempio.com/file.xlsx"
            )
            
            if url_input != st.session_state.url_input:
                st.session_state.url_input = url_input
            
            if url_input and st.button("Carica da URL", key="load_url"):
                with st.spinner("Caricamento da URL..."):
                    if load_excel_from_url(url_input):
                        st.success("File caricato da URL con successo!")
                        st.rerun()
    
    else:
        # Sezione visualizzazione dati
        st.header("📋 Visualizzazione Dati")
        
        # Selezione sheet
        if len(st.session_state.sheet_names) > 1:
            selected_sheet = st.selectbox(
                "Seleziona Sheet",
                st.session_state.sheet_names,
                index=st.session_state.sheet_names.index(st.session_state.current_sheet),
                key="sheet_selector"
            )
            
            # Aggiorna il sheet corrente solo se cambiato
            if selected_sheet != st.session_state.current_sheet:
                st.session_state.current_sheet = selected_sheet
                st.rerun()
        
        # Ottieni DataFrame corrente
        df = get_current_dataframe()
        
        if df is not None:
            # Tabs per diverse visualizzazioni
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Dati", "📈 Grafici", "📋 Info", "🔍 Filtri"])
            
            with tab1:
                st.subheader(f"Sheet: {st.session_state.current_sheet}")
                
                # Opzioni di visualizzazione
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    show_index = st.checkbox("Mostra Index", value=False)
                
                with col2:
                    rows_to_show = st.number_input("Righe da mostrare", min_value=5, max_value=len(df), value=min(100, len(df)))
                
                with col3:
                    search_term = st.text_input("Cerca nei dati", placeholder="Termine di ricerca...")
                
                # Applica filtro di ricerca se presente
                display_df = df.copy()
                if search_term:
                    mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    display_df = display_df[mask]
                
                # Mostra DataFrame
                st.dataframe(
                    display_df.head(int(rows_to_show)),
                    use_container_width=True,
                    hide_index=not show_index
                )
                
                # Statistiche rapide
                st.subheader("📊 Statistiche Rapide")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Righe Totali", len(df))
                
                with col2:
                    st.metric("Colonne", len(df.columns))
                
                with col3:
                    st.metric("Celle Vuote", df.isnull().sum().sum())
                
                with col4:
                    st.metric("Memoria (KB)", f"{df.memory_usage(deep=True).sum() / 1024:.1f}")
            
            with tab2:
                st.subheader("📈 Visualizzazioni")
                
                numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
                
                if len(numeric_columns) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        chart_type = st.selectbox("Tipo Grafico", ["Istogramma", "Box Plot", "Scatter Plot", "Linea"])
                    
                    with col2:
                        selected_column = st.selectbox("Colonna", numeric_columns)
                    
                    if chart_type == "Istogramma":
                        fig = px.histogram(df, x=selected_column, title=f"Istogramma di {selected_column}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Box Plot":
                        fig = px.box(df, y=selected_column, title=f"Box Plot di {selected_column}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Scatter Plot" and len(numeric_columns) > 1:
                        y_column = st.selectbox("Colonna Y", [col for col in numeric_columns if col != selected_column])
                        fig = px.scatter(df, x=selected_column, y=y_column, title=f"Scatter Plot: {selected_column} vs {y_column}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Linea":
                        fig = px.line(df, y=selected_column, title=f"Grafico a Linea di {selected_column}")
                        st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.info("Nessuna colonna numerica disponibile per i grafici.")
            
            with tab3:
                st.subheader("📋 Informazioni Dettagliate")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Informazioni DataFrame:**")
                    info_data = {
                        "Righe": len(df),
                        "Colonne": len(df.columns),
                        "Memoria (bytes)": df.memory_usage(deep=True).sum(),
                        "Celle Totali": df.size,
                        "Celle Vuote": df.isnull().sum().sum()
                    }
                    
                    for key, value in info_data.items():
                        st.write(f"• **{key}:** {value:,}")
                
                with col2:
                    st.write("**Tipi di Dati:**")
                    dtype_counts = df.dtypes.value_counts()
                    for dtype, count in dtype_counts.items():
                        st.write(f"• **{dtype}:** {count} colonne")
                
                # Anteprima colonne
                st.write("**Anteprima Colonne:**")
                col_info = []
                for col in df.columns[:10]:  # Mostra prime 10 colonne
                    col_info.append({
                        "Colonna": col,
                        "Tipo": str(df[col].dtype),
                        "Non Null": df[col].count(),
                        "% Completezza": f"{(df[col].count() / len(df) * 100):.1f}%"
                    })
                
                st.dataframe(pd.DataFrame(col_info), use_container_width=True, hide_index=True)
            
            with tab4:
                st.subheader("🔍 Filtri Avanzati")
                
                # Filtri per colonne
                filter_columns = st.multiselect("Seleziona Colonne da Mostrare", df.columns.tolist(), default=df.columns.tolist()[:5])
                
                if filter_columns:
                    filtered_df = df[filter_columns]
                    
                    # Filtri per valori
                    for col in filter_columns[:3]:  # Limite a 3 filtri per performance
                        if df[col].dtype == 'object':
                            unique_values = df[col].dropna().unique()
                            if len(unique_values) <= 20:  # Solo se ci sono pochi valori unici
                                selected_values = st.multiselect(
                                    f"Filtra {col}",
                                    unique_values,
                                    key=f"filter_{col}"
                                )
                                if selected_values:
                                    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
                    
                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                    
                    # Pulsante download
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Scarica CSV Filtrato",
                        data=csv,
                        file_name=f"filtered_data_{st.session_state.current_sheet}.csv",
                        mime="text/csv"
                    )
    
    # Mostra errori se presenti
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
    
    # Mostra stato di caricamento
    if st.session_state.loading_state:
        st.info("⏳ Caricamento in corso...")

if __name__ == "__main__":
    main()