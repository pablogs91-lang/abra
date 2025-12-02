"""
Página de análisis por URL
Extrae marca de URL y analiza
"""
import streamlit as st
import html
from abra.core.pytrends import *
from abra.analysis.insights import extract_brand_from_url
from abra.components.render import *
from abra.utils.sanitize import sanitize_query, sanitize_html

def render_url_analysis(selected_countries: list, selected_categories: list, relevance_threshold: int):
    """
    Renderiza el modo de análisis por URL
    
    Args:
        selected_countries: Lista de códigos de países
        selected_categories: Lista de categorías
        relevance_threshold: Umbral de relevancia
    """
    st.markdown("#### 🔗 Extraer Marca desde URL")
    url_input = st.text_input(
        "URL del producto",
        placeholder="https://www.pccomponentes.com/logitech-g-pro-x-superlight",
        label_visibility="collapsed"
    )
    
    if url_input:
        brand = extract_brand_from_url(url_input)
        if brand:
            st.success(f"✅ Marca detectada: **{brand}**")
            if st.button(f"🔍 Analizar {brand}", type="primary"):
                # TODO: Implementar lógica de análisis
                st.info("Funcionalidad en desarrollo")
        else:
            st.error("❌ No se pudo extraer la marca")
    
    # FOOTER
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #86868b; font-size: 0.85rem; padding: 1.5rem 0; margin-top: 3rem; border-top: 1px solid rgba(0,0,0,0.08);">
        <span style="color: #6e6e73;">🔧 Abra v11 | 🔍 SerpAPI</span>
    </div>
    """, unsafe_allow_html=True)
