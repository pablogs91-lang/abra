"""
Página de análisis por CSV
Análisis batch de múltiples marcas
"""
import streamlit as st
import pandas as pd
from abra.core.pytrends import *
from abra.analysis.insights import *
from abra.components.render import *

def render_csv_analysis(selected_countries: list, selected_categories: list, relevance_threshold: int):
    """
    Renderiza el modo de análisis por CSV
    
    Args:
        selected_countries: Lista de códigos de países
        selected_categories: Lista de categorías
        relevance_threshold: Umbral de relevancia
    """
    st.markdown("### 📊 Análisis desde CSV")
    
    uploaded_file = st.file_uploader(
        "Sube un archivo CSV con una columna 'marca'",
        type=['csv']
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        if 'marca' in df.columns or 'Marca' in df.columns:
            brands = df['marca'].tolist() if 'marca' in df.columns else df['Marca'].tolist()
            
            st.info(f"📊 {len(brands)} marcas detectadas")
            
            if st.button("🔍 Analizar todas"):
                results = []
                progress = st.progress(0)
                
                for idx, brand in enumerate(brands):
                    with st.spinner(f"Analizando {brand}..."):
                        # Analizar cada marca
                        # TODO: Implementar análisis batch
                        pass
                    progress.progress((idx + 1) / len(brands))
                
                st.success("✅ Análisis completado")
        else:
            st.error("El CSV debe tener una columna llamada 'marca' o 'Marca'")
