"""
Página de análisis histórico
Visualiza evolución temporal de marcas
"""
import streamlit as st
from abra.analysis.historical import *
from abra.components.render import *
from abra.config.constants import COUNTRIES, CHANNELS

def render_historical():
    """Renderiza el modo histórico"""
    st.markdown("#### 📈 Histórico de Análisis")
    st.markdown("Visualiza y analiza la evolución de tus búsquedas guardadas")
    
    # Cargar histórico
    history = load_analysis_history()
    
    if not history:
        render_empty_state(
            icon="📭",
            title="Sin histórico disponible",
            message="Realiza un análisis y guárdalo usando el botón '💾 Guardar en Histórico' para comenzar a ver evoluciones.",
            suggestions=["logitech", "razer", "corsair"]
        )
    else:
        # Mostrar total de registros
        st.info(f"📊 **{len(history)} análisis guardados** (últimos 100)")
        
        # Tabs: Tabla completa vs Evolución
        tab_table, tab_evolution = st.tabs(["📋 Tabla Completa", "📈 Evolución"])
        
        with tab_table:
            st.markdown("#### 📋 Histórico Completo")
            
            # Filtros
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                # Obtener marcas únicas
                unique_brands = sorted(list(set([r["brand"] for r in history])))
                filter_brand = st.selectbox(
                    "Filtrar por marca",
                    ["Todas"] + unique_brands,
                    key="hist_filter_brand"
                )
            
            with col_filter2:
                # Obtener países únicos
                unique_countries = sorted(list(set([r.get("country_name", "N/A") for r in history])))
                filter_country = st.selectbox(
                    "Filtrar por país",
                    ["Todos"] + unique_countries,
                    key="hist_filter_country"
                )
            
            with col_filter3:
                # Obtener canales únicos
                unique_channels = sorted(list(set([r.get("channel_name", "N/A") for r in history])))
                filter_channel = st.selectbox(
                    "Filtrar por canal",
                    ["Todos"] + unique_channels,
                    key="hist_filter_channel"
                )
            
            # Aplicar filtros
            filtered_history = history
            if filter_brand != "Todas":
                filtered_history = [r for r in filtered_history if r["brand"] == filter_brand]
            if filter_country != "Todos":
                filtered_history = [r for r in filtered_history if r.get("country_name") == filter_country]
            if filter_channel != "Todos":
                filtered_history = [r for r in filtered_history if r.get("channel_name") == filter_channel]
            
            # Mostrar tabla
            if filtered_history:
                st.markdown(f"**Mostrando {len(filtered_history)} registros**")
                history_table = render_history_table(filtered_history, limit=50)
                if history_table is not None:
                    st.dataframe(history_table, use_container_width=True, hide_index=True)
            else:
                st.warning("No hay registros con esos filtros")
        
        with tab_evolution:
            st.markdown("#### 📈 Evolución de Marca")
            
            # Selector de marca y canal para evolución
            col_evo1, col_evo2 = st.columns(2)
            
            with col_evo1:
                unique_brands_evo = sorted(list(set([r["brand"] for r in history])))
                selected_brand_evo = st.selectbox(
                    "Selecciona marca",
                    unique_brands_evo,
                    key="evo_brand"
                )
            
            with col_evo2:
                unique_channels_evo = sorted(list(set([r.get("channel", "web") for r in history])))
                selected_channel_evo = st.selectbox(
                    "Selecciona canal",
                    unique_channels_evo,
                    format_func=lambda x: f"{CHANNELS.get(x, {}).get('icon', '')} {CHANNELS.get(x, {}).get('name', x)}",
                    key="evo_channel"
                )
            
            # Obtener evolución
            if selected_brand_evo:
                evolution = get_brand_evolution(selected_brand_evo, selected_channel_evo)
                
                if not evolution:
                    st.warning(f"No hay datos históricos para '{selected_brand_evo}' en {CHANNELS.get(selected_channel_evo, {}).get('name', selected_channel_evo)}")
                else:
                    st.success(f"📊 {len(evolution)} análisis encontrados")
                    
                    # Selector de métrica
                    metric_to_show = st.selectbox(
                        "Métrica a visualizar",
                        ["avg_value", "month_change", "quarter_change", "year_change"],
                        format_func=lambda x: {
                            "avg_value": "Promedio 5 Años",
                            "month_change": "Cambio Mensual",
                            "quarter_change": "Cambio Trimestral",
                            "year_change": "Cambio Anual"
                        }[x],
                        key="evo_metric"
                    )
                    
                    # Crear y mostrar gráfico
                    evo_chart = create_evolution_chart(evolution, metric_to_show)
                    if evo_chart:
                        st.plotly_chart(evo_chart, use_container_width=True)
                    
                    # Tabla de evolución
                    st.markdown("**📋 Detalle de evolución:**")
                    evo_table = render_history_table(evolution, limit=20)
                    if evo_table is not None:
                        st.dataframe(evo_table, use_container_width=True, hide_index=True)

