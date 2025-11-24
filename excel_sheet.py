import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import io

# ------------- CONFIGURAZIONE PAGINA -------------
st.set_page_config(
    page_title="Excel GitHub Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
plt.style.use('default')
sns.set_palette("husl")

# ------------- UTILS -------------
def convert_github_url_to_raw(github_url):
    """Converte url GitHub in url raw."""
    if "github.com" in github_url and "/blob/" in github_url:
        return github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return github_url

def download_excel_from_github(url):
    """Scarica Excel da GitHub (raw)."""
    try:
        raw_url = convert_github_url_to_raw(url)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(raw_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: Il download ha richiesto troppo tempo.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Errore di connessione: Impossibile raggiungere l'URL.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error("❌ File non trovato: URL errato o file non presente.")
        else:
            st.error(f"❌ Errore HTTP {e.response.status_code}: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Errore generico: {str(e)}")
        return None

def load_excel_data(excel_content):
    """Carica i dati da tutti i fogli Excel."""
    try:
        excel_file = pd.ExcelFile(io.BytesIO(excel_content))
        sheet_names = excel_file.sheet_names
        data_dict = {}
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(io.BytesIO(excel_content), sheet_name=sheet_name)
                data_dict[sheet_name] = df
            except Exception as e:
                st.warning(f"⚠️ Impossibile leggere il foglio '{sheet_name}': {str(e)}")
        return data_dict
    except Exception as e:
        st.error(f"❌ Errore nella lettura Excel: {str(e)}")
        return None

def display_basic_stats(df):
    st.subheader("📈 Statistiche di Base")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Righe", len(df))
    with col2: st.metric("Colonne", len(df.columns))
    with col3: st.metric("Valori Mancanti", df.isnull().sum().sum())
    with col4: st.metric("Memoria (KB)", f"{df.memory_usage(deep=True).sum() / 1024:.1f}")
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        st.subheader("📊 Statistiche Descrittive (Colonne Numeriche)")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    st.subheader("🔍 Info Colonne")
    column_info = pd.DataFrame({
        'Colonna': df.columns,
        'Tipo di Dato': df.dtypes.astype(str),
        'Non Nulli': df.count(),
        'Nulli': df.isnull().sum(),
        '% Nulli': (df.isnull().sum() / len(df) * 100).round(2)
    })
    st.dataframe(column_info, use_container_width=True)

def create_matplotlib_plots(df):
    numeric_cols = df.select_dtypes(include="number").columns
    if not len(numeric_cols):
        st.warning("⚠️ Nessuna colonna numerica trovata.")
        return
    st.subheader("📈 Visualizzazioni")
    selected_cols = st.multiselect("Seleziona colonne numeriche:", list(numeric_cols), default=list(numeric_cols[:3]))
    if not selected_cols:
        st.info("👆 Seleziona almeno una colonna numerica per visualizzare i grafici")
        return
    chart_types = st.multiselect(
        "Tipi di grafici:",
        ["Istogramma", "Box Plot", "Grafico a Linee", "Scatter Plot", "Matrice di Correlazione"],
        default=["Istogramma", "Box Plot"]
    )
    for chart_type in chart_types:
        if chart_type == "Istogramma":
            st.subheader("📊 Istogrammi")
            n_cols = min(len(selected_cols), 3)
            n_rows = (len(selected_cols) + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
            if len(selected_cols) == 1:
                axes = [axes]
            else:
                axes = axes.flatten()
            for i, col in enumerate(selected_cols):
                ax = axes[i]
                data_clean = df[col].dropna()
                ax.hist(data_clean, bins=30, alpha=0.7, color=sns.color_palette()[i % len(sns.color_palette())])
                ax.set_title(f'Distribuzione di {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequenza')
                ax.grid(True, alpha=0.3)
            for i in range(len(selected_cols), len(axes)):
                axes[i].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        elif chart_type == "Box Plot":
            st.subheader("📦 Box Plot")
            fig, ax = plt.subplots(figsize=(12, 6))
            box_data = []
            labels = []
            for col in selected_cols:
                data_clean = df[col].dropna()
                if len(data_clean) > 0:
                    box_data.append(data_clean)
                    labels.append(col)
            if box_data:
                bp = ax.boxplot(box_data, labels=labels, patch_artist=True)
                colors = sns.color_palette("husl", len(box_data))
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                ax.set_title('Box Plot delle Colonne Selezionate')
                ax.set_ylabel('Valori')
                plt.xticks(rotation=45)
                ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        elif chart_type == "Grafico a Linee":
            st.subheader("📈 Grafico a Linee")
            fig, ax = plt.subplots(figsize=(12, 6))
            for i, col in enumerate(selected_cols):
                data_clean = df[col].dropna()
                ax.plot(range(len(data_clean)), data_clean, label=col, linewidth=2,
                        color=sns.color_palette()[i % len(sns.color_palette())])
            ax.set_title('Andamento delle Colonne Selezionate')
            ax.set_xlabel('Indice')
            ax.set_ylabel('Valori')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        elif chart_type == "Scatter Plot" and len(selected_cols) >= 2:
            st.subheader("🎯 Scatter Plot")
            col1_scatter = st.selectbox("Colonna X:", selected_cols, key="scatter_x")
            col2_scatter = st.selectbox("Colonna Y:", [c for c in selected_cols if c != col1_scatter], key="scatter_y")
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter_data = df[[col1_scatter, col2_scatter]].dropna()
            ax.scatter(scatter_data[col1_scatter], scatter_data[col2_scatter],
                       alpha=0.6, s=50, color=sns.color_palette()[0])
            ax.set_xlabel(col1_scatter)
            ax.set_ylabel(col2_scatter)
            ax.set_title(f'Scatter Plot: {col1_scatter} vs {col2_scatter}')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        elif chart_type == "Matrice di Correlazione" and len(selected_cols) >= 2:
            st.subheader("🔥 Matrice di Correlazione")
            corr_matrix = df[selected_cols].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                        square=True, linewidths=0.5, ax=ax)
            ax.set_title('Matrice di Correlazione')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

# ------------- MAIN -------------
def main():
    st.title("📊 Excel GitHub Analyzer")
    st.markdown("""
    App per analizzare file Excel direttamente da GitHub.
    1. Inserisci l'URL del file Excel (normale o raw)
    2. Scarica il file
    3. Scegli lo sheet
    4. Analizza!

    **Formati supportati:** .xlsx, .xls
    """)

    # ------------------------ Workflow fase 1: URL input e download ----------------
    default_url = "https://github.com/plotly/datasets/blob/master/2014_world_gdp_with_codes.xlsx"
    url_input = "https://github.com/FrigoriferoAccecante/ticketfast_streamlit_final/blob/pec_form/P%26C%20reports.xlsx"

    if st.button("📥 Scarica File"):
        if not url_input:
            st.warning("⚠️ Inserire un URL valido")
        else:
            with st.spinner("Download in corso..."):
                excel_content = download_excel_from_github(url_input)
            if excel_content is not None:
                with st.spinner("Lettura fogli Excel..."):
                    data_dict = load_excel_data(excel_content)
                if data_dict and len(data_dict):
                    st.session_state["excel_content"] = excel_content
                    st.session_state["data_dict"] = data_dict
                    st.session_state["sheet_names"] = list(data_dict.keys())
                    st.session_state["url_input"] = url_input
                else:
                    st.error("❌ Nessun sheet valido trovato")
            else:
                st.error("❌ Download non riuscito.")

    # Mostra selectbox fogli solo se dati disponibili (session_state)
    if "data_dict" in st.session_state and "sheet_names" in st.session_state:
        st.success("✅ File Excel caricato correttamente.")
        selected_sheet = st.selectbox(
            "📋 Scegli il foglio da analizzare:",
            st.session_state["sheet_names"],
            key="selected_sheet"
        )
        # Pulsante per analizzare il foglio selezionato
        analyze_btn = st.button("🚀 Analizza Sheet Selezionato")
        if analyze_btn or st.session_state.get("last_analyzed_sheet") == selected_sheet:
            st.session_state["last_analyzed_sheet"] = selected_sheet
            df = st.session_state["data_dict"][selected_sheet]
            if df.empty:
                st.warning(f"⚠️ Il foglio '{selected_sheet}' è vuoto")
                return

            # Tabs organizzative
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Dati", "📈 Statistiche", "🎨 Grafici", "💾 Download"])
            with tab1:
                st.subheader(f"Dati foglio: {selected_sheet}")
                col1, col2 = st.columns(2)
                with col1:
                    show_rows = st.number_input(
                        "Numero di righe da mostrare:",
                        min_value=1,
                        max_value=len(df),
                        value=min(100, len(df))
                    )
                with col2:
                    if len(df.columns) > 10:
                        show_all_columns = st.checkbox("Mostra tutte le colonne", value=False)
                        if not show_all_columns:
                            selected_columns = st.multiselect(
                                "Colonne da visualizzare:",
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
                create_matplotlib_plots(df)
            with tab4:
                st.subheader("💾 Download Dati")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Scarica CSV",
                    data=csv,
                    file_name=f"{selected_sheet}.csv",
                    mime="text/csv"
                )
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, sheet_name=selected_sheet, index=False)
                st.download_button(
                    label="Scarica Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"{selected_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("Premi 'Analizza Sheet Selezionato' per vedere l'analisi!")

    st.markdown("---")
    st.markdown("**Progetto pronto all'uso!**")

if __name__ == "__main__":
    main()