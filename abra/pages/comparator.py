"""
Página del comparador de marcas
Compara hasta 4 marcas simultáneamente
"""
import streamlit as st
import html
from abra.core.pytrends import *
from abra.analysis.insights import *
from abra.components.render import *
from abra.utils.sanitize import sanitize_query, sanitize_html
from abra.config.constants import COUNTRIES, CHANNELS

def render_comparator(selected_countries: list, selected_categories: list, relevance_threshold: int):
    """
    Renderiza el modo comparador
    
    Args:
        selected_countries: Lista de códigos de países
        selected_categories: Lista de categorías
        relevance_threshold: Umbral de relevancia
    """
    st.markdown("#### ⚖️ Comparar Marcas")
    st.markdown("Compara hasta **4 marcas** en **1 país** simultáneamente")
    
    # RESTRICCIÓN: Solo 1 país para comparador
    col_country, col_spacer = st.columns([2, 8])
    with col_country:
        comparator_country = st.selectbox(
            "🌍 País",
            options=list(COUNTRIES.keys()),
            index=0,  # Default ES
            format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}",
            key="comparator_country",
            help="Solo se puede comparar en 1 país a la vez"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Inputs para marcas (máximo 4)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        marca1 = st.text_input("Marca 1", placeholder="Ej: Logitech", key="comp_m1")
    with col_m2:
        marca2 = st.text_input("Marca 2", placeholder="Ej: Razer", key="comp_m2")
    with col_m3:
        marca3 = st.text_input("Marca 3 (opcional)", placeholder="Ej: Corsair", key="comp_m3")
    with col_m4:
        marca4 = st.text_input("Marca 4 (opcional)", placeholder="Ej: SteelSeries", key="comp_m4")
    
    # Filtrar marcas no vacías
    brands_to_compare = [b.strip() for b in [marca1, marca2, marca3, marca4] if b and b.strip()]
    
    # INFO: Análisis multi-canal automático
    st.info("🌐 **Análisis automático en todos los canales**: Web + Images + News + YouTube + Shopping")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("⚖️ Comparar Marcas", type="primary", use_container_width=True):
        # BUGFIX: Validación mejorada
        if len(brands_to_compare) < 2:
            st.error("❌ Debes introducir al menos 2 marcas para comparar")
        elif len(brands_to_compare) > 4:
            st.error("❌ Máximo 4 marcas permitidas")
        else:
            try:
                # Mostrar marcas a comparar
                country_name = f"{COUNTRIES[comparator_country]['flag']} {COUNTRIES[comparator_country]['name']}"
                
                st.markdown(f"""
                <div class="glass-card">
                    <h2 style="margin: 0; color: #1d1d1f;">⚖️ Comparando {len(brands_to_compare)} marcas</h2>
                    <p style="color: #6e6e73; margin-top: 0.5rem;">{' vs '.join(brands_to_compare)} en {country_name}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Ejecutar comparación con spinner (multi-canal automático)
                with st.spinner(f"🔍 Analizando {len(brands_to_compare)} marcas en todos los canales..."):
                    comparison_results = {}
                    
                    # Comparar cada marca con análisis multi-canal
                    for brand in brands_to_compare:
                        brand_results = analyze_all_channels(
                            brand,
                            [comparator_country],  # Solo 1 país
                            selected_categories,
                            relevance_threshold
                        )
                        comparison_results[brand] = brand_results
                
                # Verificar resultados
                if not comparison_results:
                    st.error("❌ No se pudieron obtener resultados de comparación")
                    st.stop()
                
                # VISTA COMPARATIVA
                st.markdown(f"## 📊 Resultados - {country_name}")
                
                # ========== GRÁFICO COMPARATIVO DE VOLUMEN ==========
                st.markdown("### 📈 Comparación de Interés por Canal")
                
                import plotly.graph_objects as go
                
                # Preparar datos para gráfico
                channels_list = ['web', 'images', 'news', 'youtube', 'shopping']
                channel_names = {
                    'web': 'Web',
                    'images': 'Images',
                    'news': 'News',
                    'youtube': 'YouTube',
                    'shopping': 'Shopping'
                }
                
                fig = go.Figure()
                
                for brand in brands_to_compare:
                    brand_data = comparison_results[brand][comparator_country]
                    volumes = []
                    
                    for channel_key in channels_list:
                        channel_info = brand_data['channels'].get(channel_key, {})
                        avg_value = channel_info.get('avg_value', 0)
                        volumes.append(avg_value)
                    
                    fig.add_trace(go.Bar(
                        name=brand,
                        x=[channel_names[ch] for ch in channels_list],
                        y=volumes,
                        text=volumes,
                        textposition='auto',
                    ))
                
                fig.update_layout(
                    title=f"Interés por Canal - Comparación de Marcas",
                    xaxis_title="Canal",
                    yaxis_title="Interés Promedio (0-100)",
                    barmode='group',
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # ========== TABLA RESUMEN ==========
                st.markdown("### 📊 Tabla Comparativa")
                
                summary_data = []
                for brand in brands_to_compare:
                    brand_data = comparison_results[brand][comparator_country]
                    consolidated = brand_data['consolidated']
                    
                    # Calcular promedios
                    total_volume = sum(consolidated['channel_volumes'].values())
                    avg_volume = total_volume / len(consolidated['channel_volumes']) if consolidated['channel_volumes'] else 0
                    
                    dominant_channel = consolidated.get('dominant_channel', {})
                    
                    summary_data.append({
                        'Marca': brand,
                        'Canales Activos': f"{consolidated['channels_with_data']}/5",
                        'Canal Dominante': dominant_channel.get('name', 'N/A') if dominant_channel else 'N/A',
                        'Volumen Promedio': f"{avg_volume:.1f}",
                        'Total Queries': len(consolidated['all_queries']),
                        'Total Topics': len(consolidated['all_topics'])
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # ========== GANADOR ==========
                summary_df['avg_numeric'] = summary_df['Volumen Promedio'].astype(float)
                winner_idx = summary_df['avg_numeric'].idxmax()
                winner = summary_df.loc[winner_idx, 'Marca']
                winner_avg = summary_df.loc[winner_idx, 'Volumen Promedio']
                
                st.success(f"🏆 **Líder en {country_name}:** {winner} con {winner_avg} de interés promedio")
                
                # ========== DETALLES POR MARCA ==========
                st.markdown("### 📑 Detalles por Marca")
                
                for brand in brands_to_compare:
                    with st.expander(f"**{brand}** - Análisis Detallado", expanded=False):
                        brand_data = comparison_results[brand][comparator_country]
                        
                        # Mostrar insights
                        if brand_data['consolidated']['insights']:
                            st.markdown("**💡 Insights:**")
                            for insight in brand_data['consolidated']['insights']:
                                st.markdown(f"- {insight['icon']} {insight['title']}: {insight['description']}")
                        
                        # Top 5 queries consolidadas
                        if brand_data['consolidated']['all_queries']:
                            st.markdown("**🔍 Top Queries (todas las fuentes):**")
                            top_queries = sorted(
                                brand_data['consolidated']['all_queries'],
                                key=lambda x: x['value'],
                                reverse=True
                            )[:5]
                            
                            for q in top_queries:
                                st.markdown(f"- **{q['query']}** (Valor: {q['value']}, Canal: {q['channel_name']})")
                
            except Exception as e:
                st.error(f"❌ Error en la comparación: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# ================================
# SPRINT 5: HISTÓRICO DE ANÁLISIS
# ================================

