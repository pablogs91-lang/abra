"""
Abra - Advanced Brand Research & Analysis
Main Streamlit Application

Entry point for the Streamlit web application.
"""
import streamlit as st

# Import from abra package using absolute imports
from abra import __version__
from abra.config.constants import COUNTRIES, PRODUCT_CATEGORIES, CHANNELS
from abra.ui.styles import apply_custom_css
from abra.pages.manual_search import render_manual_search
from abra.pages.comparator import render_comparator
from abra.pages.historical import render_historical
from abra.pages.url_analysis import render_url_analysis

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================

st.set_page_config(
    page_title="Abra",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================
# SESSION STATE INITIALIZATION
# ================================

if 'selected_channel' not in st.session_state:
    st.session_state.selected_channel = 'web'

if 'selected_channel_comp' not in st.session_state:
    st.session_state.selected_channel_comp = 'web'

if 'search_query' not in st.session_state:
    st.session_state.search_query = ''

if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

if 'cache_results' not in st.session_state:
    st.session_state.cache_results = {}

# ================================
# APLICAR ESTILOS CSS
# ================================

apply_custom_css()

# ================================
# HEADER
# ================================

st.markdown("""
<div class="main-header">
    <h1>🔍 Abra</h1>
    <p>Inteligencia Competitiva con Análisis Completo de Google Trends</p>
</div>
""", unsafe_allow_html=True)

# ================================
# TRENDING NOW WIDGET (Demo Mode)
# ================================

with st.expander("🔥 **Tendencias del Momento - Componentes & Periféricos** (Feature deshabilitada para ahorro)", expanded=False):
    st.warning("⚠️ **Feature deshabilitada temporalmente** para optimizar costos de API. Los datos mostrados son ejemplos de demostración.")
    
    col_trend1, col_trend2 = st.columns([1, 3])
    
    with col_trend1:
        trending_geo = st.selectbox(
            "País",
            ["ES", "PT", "FR", "IT", "DE"],
            format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}",
            key="trending_geo"
        )
        
        trending_category = st.selectbox(
            "Categoría",
            ["Ratones", "Teclados", "Monitores", "Auriculares", "Gráficas", "Procesadores", 
             "Placas Base", "RAM", "SSD", "Refrigeración"],
            key="trending_category"
        )
    
    with col_trend2:
        # Datos de demostración
        demo_trends = {
            "Ratones": [
                {"query": "logitech g502 hero", "traffic": "200K+", "growth": "+45%"},
                {"query": "razer deathadder v3", "traffic": "150K+", "growth": "+38%"},
                {"query": "corsair dark core", "traffic": "80K+", "growth": "+22%"},
                {"query": "steelseries rival 3", "traffic": "65K+", "growth": "+15%"},
                {"query": "glorious model o", "traffic": "55K+", "growth": "+12%"}
            ],
            "Teclados": [
                {"query": "keychron k2", "traffic": "180K+", "growth": "+52%"},
                {"query": "corsair k70 rgb", "traffic": "140K+", "growth": "+35%"},
                {"query": "razer blackwidow", "traffic": "120K+", "growth": "+28%"},
                {"query": "logitech g915", "traffic": "90K+", "growth": "+18%"},
                {"query": "ducky one 2", "traffic": "70K+", "growth": "+14%"}
            ],
            # ... otros omitidos por brevedad, están en el monolito
        }
        
        st.markdown(f"**🔍 Tendencias en {trending_category}** (Datos de demostración)")
        st.info("💡 Esta feature funcionaba perfectamente con datos reales de Google Trends, pero se deshabilitó para ahorrar API calls.")
        
        category_trends = demo_trends.get(trending_category, demo_trends["Ratones"])
        
        for idx, trend in enumerate(category_trends, 1):
            growth_color = "#34C759" if "+" in trend["growth"] else "#FF3B30"
            
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid rgba(0,0,0,0.08);
                border-left: 4px solid {growth_color};
                border-radius: 8px;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.2rem; font-weight: 600; color: #6e6e73;">
                        #{idx}
                    </span>
                    <div>
                        <div style="font-weight: 600; color: #1d1d1f; margin-bottom: 0.25rem;">
                            {trend['query']}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73;">
                            {trend['traffic']} búsquedas
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: {growth_color};">
                        {trend['growth']}
                    </div>
                    <div style="font-size: 0.75rem; color: #6e6e73;">
                        vs ayer
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================================
# FLOATING TOOLBAR
# ================================

toolbar_container = st.container()

with toolbar_container:
    st.markdown('<div class="floating-toolbar">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1.2, 2, 2.5, 1.2, 1])
    
    with col1:
        search_mode = st.selectbox(
            "🔎 Modo",
            ["🔍 Manual", "⚖️ Comparador", "📈 Histórico", "🔗 URL"],
            key="search_mode"
        )
    
    with col2:
        selected_countries = st.multiselect(
            "🌍 Países",
            options=list(COUNTRIES.keys()),
            default=["ES"],
            format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}",
            key="countries"
        )
    
    with col3:
        selected_categories = st.multiselect(
            "🎯 Categorías",
            options=list(PRODUCT_CATEGORIES.keys()),
            default=[],  # Sin default - usuario elige lo que necesita
            format_func=lambda x: f"{PRODUCT_CATEGORIES[x]['icon']} {x}",
            key="categories",
            help="Selecciona las categorías de productos que quieres analizar"
        )
    
    with col4:
        relevance_threshold = st.slider(
            "📊 Relevancia",
            min_value=0,
            max_value=100,
            value=30,
            step=10,
            key="threshold"
        )
    
    with col5:
        query_type_filter = st.selectbox(
            "🏷️ Tipo",
            ["Todos", "Preguntas", "Atributos"],
            key="query_type"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================================
# ROUTER DE PÁGINAS
# ================================

if search_mode == "🔍 Manual":
    # Renderizar inputs en la página
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
        <p style="color: white; margin: 0; font-weight: 600; text-align: center;">
            🌐 Análisis Multi-Canal Automático: Web + Images + News + YouTube + Shopping
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "Marca o keyword",
            placeholder="Ej: Logitech, ASUS ROG, Razer...",
            label_visibility="collapsed",
            value=st.session_state.search_query,
            key="app_search_query"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Analizar", type="primary", use_container_width=True, key="app_search_button")
    
    if search_button and search_query and selected_countries:
        render_manual_search(search_query, selected_countries, selected_categories, relevance_threshold)
    elif not search_query or not search_button:
        # Welcome state
        from abra.components.render import render_empty_state
        render_empty_state(
            icon="🚀",
            title="Bienvenido a Abra",
            message="Introduce el nombre de una marca tecnológica para comenzar el análisis de tendencias de búsqueda. Descubre insights de múltiples países simultáneamente.",
            suggestions=["logitech", "razer", "corsair", "keychron", "steelseries"]
        )

elif search_mode == "⚖️ Comparador":
    render_comparator(selected_countries, selected_categories, relevance_threshold)

elif search_mode == "📈 Histórico":
    render_historical()

elif search_mode == "🔗 URL":
    render_url_analysis(selected_countries, selected_categories, relevance_threshold)

# ================================
# FOOTER
# ================================

st.markdown("---")

st.markdown(f"""
<div style="text-align: center; padding: 2rem 0;">
    <p style="color: #6e6e73; font-size: 0.9rem;">
        Generado por Abra v{__version__}
    </p>
    <p style="color: #86868b; font-size: 0.8rem;">
        Professional Architecture | SerpAPI Integration | Powered by Google Trends
    </p>
</div>
""", unsafe_allow_html=True)
