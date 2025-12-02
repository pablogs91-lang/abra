"""
Página de búsqueda manual
Análisis multi-canal automático
"""
import streamlit as st
import html
from abra.core.pytrends import *
from abra.analysis.insights import *
from abra.analysis.amazon import *
from abra.analysis.youtube import *
from abra.components.render import *
from abra.config.constants import COUNTRIES, CHANNELS, PRODUCT_CATEGORIES
from abra.analysis.star_products import detect_star_products, render_star_products, get_star_products_summary
from abra.analysis.seasonality_advanced import calculate_seasonality_by_country, compare_seasonality_countries
from abra.analysis.serpapi_news import get_google_news_serpapi, analyze_news_sentiment_serpapi, render_news_panel_serpapi, render_news_mini_widget
from abra.analysis.related_brands import detect_related_brands, render_related_brands

def render_manual_search(search_query: str, selected_countries: list, 
                         selected_categories: list, relevance_threshold: int):
    """
    Renderiza el modo de búsqueda manual
    
    Args:
        search_query: Marca o keyword a buscar
        selected_countries: Lista de códigos de países
        selected_categories: Lista de categorías seleccionadas
        relevance_threshold: Umbral de relevancia
    """
    # Usar nueva función multi-canal
    try:
        # Guardar query en session_state
        st.session_state.search_query = search_query
        
        with st.spinner(f"🌐 Analizando '{search_query}' en todos los canales..."):
            results = analyze_all_channels(search_query, selected_countries, selected_categories, relevance_threshold)
            
            # Verificar si hay resultados
            if not results or all(not data for data in results.values()):
                st.error("❌ No se pudieron obtener datos. Verifica tu API key o intenta más tarde.")
                st.stop()
            
            # NUEVO: Guardar automáticamente en histórico
            from analysis.historical import save_analysis_to_history
            for geo, data in results.items():
                try:
                    save_analysis_to_history(
                        brand=search_query,
                        country=geo,
                        channel='multi-channel',
                        results=data
                    )
                except Exception as e:
                    pass  # Silencioso, no bloquear si falla el guardado
            
            # Sanitizar search_query para HTML
            safe_search_query = sanitize_query(search_query)
            
            st.markdown(f"""
            <div class="glass-card">
                <h2 style="margin: 0; color: #1d1d1f;">📊 {safe_search_query}</h2>
                <p style="color: #6e6e73; margin-top: 0.5rem;">Análisis completo multi-país y multi-canal</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar filtros activos
            if selected_categories:
                categories_display = ", ".join([
                    f"{PRODUCT_CATEGORIES[cat]['icon']} {cat}" 
                    for cat in selected_categories
                ])
                st.info(f"""
                🎯 **Filtrado activo por categorías:** {categories_display}  
                📊 **Umbral de relevancia:** {relevance_threshold}%  
                ℹ️ Solo se muestran queries y topics que coincidan con las categorías seleccionadas
                """)
            else:
                st.info("ℹ️ **Sin filtrado por categorías** - Se muestran todos los resultados")
            
            # NUEVO: Botones de Export
            st.markdown("---")
            st.markdown("### 📥 Exportar Resultados")
            
            col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
            
            with col_exp1:
                # Export CSV
                from utils.helpers import export_to_csv
                try:
                    csv_data = export_to_csv(results, search_query)
                    st.download_button(
                        label="📄 CSV",
                        data=csv_data,
                        file_name=f"{search_query}_analysis.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except:
                    st.button("📄 CSV", disabled=True, use_container_width=True)
            
            with col_exp2:
                # Export JSON
                import json
                json_data = json.dumps(results, indent=2)
                st.download_button(
                    label="📋 JSON",
                    data=json_data,
                    file_name=f"{search_query}_analysis.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_exp3:
                # Export Excel
                from utils.helpers import export_to_excel
                try:
                    excel_data = export_to_excel(results, search_query)
                    st.download_button(
                        label="📊 Excel",
                        data=excel_data,
                        file_name=f"{search_query}_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except:
                    st.button("📊 Excel", disabled=True, use_container_width=True)
            
            with col_exp4:
                # Ver histórico
                st.button("📈 Ver Histórico", use_container_width=True, help="Cambia al modo Histórico para ver todos los análisis guardados")
            
            st.markdown("---")
            
            # NUEVO: DASHBOARD DE PRODUCTOS ESTRELLA
            st.markdown("### ⭐ Productos Estrella Detectados")
            
            # Extraer todas las queries de todos los países
            all_queries = []
            for geo, data in results.items():
                if data.get('queries') and 'related_queries' in data['queries']:
                    if 'top' in data['queries']['related_queries']:
                        all_queries.extend(data['queries']['related_queries']['top'])
                    if 'rising' in data['queries']['related_queries']:
                        all_queries.extend(data['queries']['related_queries']['rising'])
            
            # Detectar productos estrella
            star_products = detect_star_products(all_queries, threshold_volume=30, threshold_growth=15.0)
            
            if star_products:
                # Resumen de métricas
                summary = get_star_products_summary(star_products)
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.metric("Total Productos", summary['total'], "⭐")
                
                with col_s2:
                    st.metric("Breakout", summary['breakout'], "🔥")
                
                with col_s3:
                    st.metric("Rising", summary['rising'], "📈")
                
                with col_s4:
                    st.metric("Promedio Crecimiento", f"{summary['avg_growth']:.0f}%", "↗️")
                
                # Renderizar productos
                st.markdown(render_star_products(star_products), unsafe_allow_html=True)
                
                # Explicación
                st.info(f"💡 **Insight**: La categoría **{summary['top_category']}** lidera en productos estrella. Los productos 'Breakout' 🔥 muestran crecimiento explosivo (>200%).")
            else:
                st.info("ℹ️ No se detectaron productos estrella con los criterios actuales. Ajusta el umbral de relevancia para ver más resultados.")
            
            st.markdown("---")
            
            # NUEVO: MINI WIDGET DE NOTICIAS (3 top en dashboard)
            st.markdown("### 📰 Últimas Noticias")
            
            # Obtener API key desde environment
            import os
            serpapi_key = os.getenv('SERPAPI_API_KEY', '')
            
            with st.spinner(f"Cargando noticias sobre {search_query}..."):
                news_items_preview = get_google_news_serpapi(
                    query=search_query,
                    country=selected_countries[0] if selected_countries else 'es',
                    api_key=serpapi_key if serpapi_key else None,
                    max_results=15
                )
            
            if news_items_preview:
                # Mini widget con top 3
                st.markdown(render_news_mini_widget(news_items_preview, max_items=3), unsafe_allow_html=True)
            else:
                st.info("ℹ️ No se encontraron noticias recientes.")
            
            st.markdown("---")
            
            # NUEVO: TABS ADICIONALES (Noticias + Marcas Relacionadas)
            extra_tabs = st.tabs(["📰 Todas las Noticias", "🔗 Marcas Relacionadas", "📊 Estacionalidad Avanzada"])
            
            with extra_tabs[0]:
                st.markdown("### 📰 Análisis Completo de Noticias")
                st.markdown("""
                <p style="color: #6e6e73; margin-bottom: 1.5rem;">
                    Powered by <strong>SerpAPI</strong> - Noticias con imágenes, fuentes verificadas y análisis de sentimiento.
                </p>
                """, unsafe_allow_html=True)
                
                if news_items_preview:
                    sentiment = analyze_news_sentiment_serpapi(news_items_preview)
                    st.markdown(render_news_panel_serpapi(news_items_preview, sentiment), unsafe_allow_html=True)
                    
                    # Info sobre API
                    if serpapi_key:
                        st.success("✅ Usando SerpAPI - Noticias con imágenes y metadatos completos")
                    else:
                        st.info("💡 Configura `SERPAPI_API_KEY` en .env para noticias con imágenes de alta calidad")
                else:
                    st.info("ℹ️ No se encontraron noticias recientes. Intenta con otra marca.")
            
            with extra_tabs[1]:
                st.markdown("### 🔗 Marcas que se Buscan Junto a Esta")
                st.markdown("""
                <p style="color: #6e6e73; margin-bottom: 1.5rem;">
                    Descubre qué otras marcas buscan los usuarios que están interesados en <strong>{}</strong>.
                    Identifica competidores directos, marcas complementarias y oportunidades de mercado.
                </p>
                """.format(search_query), unsafe_allow_html=True)
                
                # Detectar marcas relacionadas de todos los países
                all_queries = []
                all_topics = []
                for geo, data in results.items():
                    if data.get('queries'):
                        all_queries.append(data['queries'])
                    if data.get('topics'):
                        all_topics.append(data['topics'])
                
                # Consolidar
                combined_queries = all_queries[0] if all_queries else None
                combined_topics = all_topics[0] if all_topics else None
                
                related_brands = detect_related_brands(combined_queries, combined_topics, search_query)
                
                if related_brands:
                    # Métricas resumen
                    col_rb1, col_rb2, col_rb3 = st.columns(3)
                    
                    competitors = [b for b in related_brands if b['relationship'] == 'Competidor Directo']
                    complementary = [b for b in related_brands if b['relationship'] == 'Complementario']
                    
                    with col_rb1:
                        st.metric("Total Marcas", len(related_brands), "🔗")
                    
                    with col_rb2:
                        st.metric("Competidores", len(competitors), "🏆")
                    
                    with col_rb3:
                        st.metric("Complementarias", len(complementary), "🤝")
                    
                    st.markdown(render_related_brands(related_brands, search_query), unsafe_allow_html=True)
                    
                    # Insight
                    if competitors:
                        top_competitor = competitors[0]['brand']
                        st.success(f"💡 **Insight**: {top_competitor} es tu competidor más co-buscado. Los usuarios comparan ambas marcas activamente.")
                else:
                    st.info("ℹ️ No se detectaron marcas relacionadas suficientemente significativas.")
            
            with extra_tabs[2]:
                st.markdown("### 📊 Análisis Avanzado de Estacionalidad por País")
                st.markdown("""
                <p style="color: #6e6e73; margin-bottom: 1.5rem;">
                    Análisis logarítmico, líneas de tendencia (lineal, exponencial, logarítmica) y predicciones por país.
                </p>
                """, unsafe_allow_html=True)
                
                # Calcular estacionalidad avanzada por país
                seasonality_by_country = {}
                for geo, data in results.items():
                    if data.get('timeline'):
                        advanced = calculate_seasonality_by_country(data['timeline'], geo)
                        if advanced:
                            seasonality_by_country[geo] = advanced
                
                if seasonality_by_country:
                    # Comparación entre países
                    comparison = compare_seasonality_countries(seasonality_by_country)
                    
                    # Métricas comparativas
                    st.markdown("#### 🌍 Comparación entre Países")
                    
                    col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)
                    
                    with col_comp1:
                        if comparison['most_seasonal']:
                            st.metric(
                                "Más Estacional",
                                comparison['most_seasonal']['country'],
                                f"{comparison['most_seasonal']['seasonality_score']:.1f}%"
                            )
                    
                    with col_comp2:
                        if comparison['most_volatile']:
                            st.metric(
                                "Más Volátil",
                                comparison['most_volatile']['country'],
                                f"σ={comparison['most_volatile']['volatility']:.2f}"
                            )
                    
                    with col_comp3:
                        if comparison['best_trend']:
                            st.metric(
                                "Mejor Ajuste",
                                comparison['best_trend']['country'],
                                f"R²={comparison['best_trend']['r_squared']:.2f}"
                            )
                    
                    with col_comp4:
                        st.metric(
                            "Países Analizados",
                            len(seasonality_by_country),
                            "🌍"
                        )
                    
                    # Detalles por país
                    st.markdown("---")
                    
                    for geo, season_data in seasonality_by_country.items():
                        country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
                        
                        with st.expander(f"**{country_name}** - Análisis Completo", expanded=False):
                            st.markdown(f"#### 📈 Tendencias y Modelo")
                            
                            # Modelo mejor ajustado
                            best_model = season_data['trends']['best_model']
                            best_r2 = season_data['trends']['best_r_squared']
                            
                            st.info(f"🎯 **Mejor modelo**: {best_model.title()} (R² = {best_r2:.3f})")
                            
                            # Mostrar ecuaciones
                            col_eq1, col_eq2, col_eq3 = st.columns(3)
                            
                            with col_eq1:
                                st.markdown(f"""
                                **Lineal**  
                                R² = {season_data['trends']['linear']['r_squared']:.3f}  
                                `{season_data['trends']['linear']['equation']}`
                                """)
                            
                            with col_eq2:
                                st.markdown(f"""
                                **Exponencial**  
                                R² = {season_data['trends']['exponential']['r_squared']:.3f}  
                                `{season_data['trends']['exponential']['equation']}`
                                """)
                            
                            with col_eq3:
                                st.markdown(f"""
                                **Logarítmica**  
                                R² = {season_data['trends']['logarithmic']['r_squared']:.3f}  
                                `{season_data['trends']['logarithmic']['equation']}`
                                """)
                            
                            # Análisis logarítmico
                            st.markdown("#### 📉 Análisis Logarítmico de Volatilidad")
                            
                            log_analysis = season_data['log_analysis']
                            
                            col_log1, col_log2, col_log3 = st.columns(3)
                            
                            with col_log1:
                                st.metric("Volatilidad (σ)", f"{log_analysis['volatility']:.3f}")
                            
                            with col_log2:
                                st.metric("Retorno Promedio", f"{log_analysis['mean_log_return']:.3f}")
                            
                            with col_log3:
                                risk_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                                risk_icon = risk_colors.get(log_analysis['risk_level'], '⚪')
                                st.metric("Nivel de Riesgo", f"{risk_icon} {log_analysis['risk_level']}")
                            
                            # Predicciones
                            if season_data.get('predictions'):
                                st.markdown("#### 🔮 Predicciones (3 meses)")
                                
                                predictions = season_data['predictions']['next_3_months']
                                confidence = season_data['predictions']['confidence']
                                
                                pred_cols = st.columns(3)
                                for i, pred_val in enumerate(predictions):
                                    with pred_cols[i]:
                                        st.metric(
                                            f"Mes +{i+1}",
                                            f"{pred_val:.1f}",
                                            help=f"Confianza: {confidence:.1%}"
                                        )
                                
                                st.caption(f"💡 Predicciones basadas en modelo {best_model.title()} con confianza del {confidence:.1%}")
                else:
                    st.info("ℹ️ No hay suficientes datos temporales para análisis avanzado de estacionalidad.")
            
            st.markdown("---")
            
            # Renderizar resultados multi-canal
            for geo, country_data in results.items():
                render_multi_channel_results(search_query, geo, country_data, selected_categories, relevance_threshold)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            for geo, data in results.items():
                country_name = f"{COUNTRIES[geo]['flag']} {COUNTRIES[geo]['name']}"
                
                with st.expander(f"**{country_name}**", expanded=True):
                    # MÉTRICAS
                    st.markdown("#### 📈 Métricas Clave")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    val = f"{data['month_change']:.1f}%" if data['month_change'] else "N/A"
                    st.markdown(render_metric_card("Último Mes", val, data['month_change'], delay=1), unsafe_allow_html=True)
                with col2:
                    val = f"{data['quarter_change']:.1f}%" if data['quarter_change'] else "N/A"
                    st.markdown(render_metric_card("Trimestre", val, data['quarter_change'], delay=2), unsafe_allow_html=True)
                with col3:
                    val = f"{data['year_change']:.1f}%" if data['year_change'] else "N/A"
                    st.markdown(render_metric_card("Año", val, data['year_change'], delay=3), unsafe_allow_html=True)
                with col4:
                    val = f"{data['avg_value']:.0f}/100" if data['avg_value'] else "N/A"
                    st.markdown(render_metric_card("Promedio 5Y", val, delay=4), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # SPRINT 5: SISTEMA DE ALERTAS
                st.markdown("#### 🔔 Alertas y Cambios Significativos")
                
                # Detectar alertas
                alerts = detect_alerts(data, threshold_spike=30, threshold_drop=-20)
                
                if alerts:
                    for alert in alerts:
                        st.markdown(render_alert_card(alert), unsafe_allow_html=True)
                else:
                    st.info("✅ Sin alertas. Todos los cambios dentro de rangos normales.")
                
                # Comparación con histórico
                comparison = compare_with_history(search_query, geo, selected_channel, data)
                if comparison:
                    st.markdown(render_comparison_card(comparison), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ESTACIONALIDAD - NUEVO SPRINT 1
                if data['timeline']:
                    seasonality = calculate_seasonality(data['timeline'])
                    if seasonality:
                        st.markdown("#### 📅 Estacionalidad")
                        
                        # Badge de estacionalidad
                        badge_text, badge_class = get_seasonality_badge(seasonality['seasonality_score'])
                        st.markdown(
                            f'<span class="{badge_class}" style="padding: 0.5rem 1rem; border-radius: 20px; display: inline-block; font-weight: 600;">{badge_text}</span>',
                            unsafe_allow_html=True
                        )
                        
                        # Gráfico de barras mensual
                        st.markdown(
                            render_seasonality_chart(seasonality['monthly_avg'], seasonality['overall_avg']),
                            unsafe_allow_html=True
                        )
                        
                        # SPRINT 3: EXPLICACIÓN IA DE PATRONES
                        if seasonality['seasonality_score'] >= 20:  # Solo si hay estacionalidad significativa
                            patterns = detect_seasonal_patterns(
                                seasonality['monthly_avg'], 
                                seasonality['overall_avg']
                            )
                            
                            if patterns:
                                explanation_html = generate_seasonality_explanation(
                                    patterns,
                                    seasonality['monthly_avg'],
                                    seasonality['overall_avg']
                                )
                                st.markdown(explanation_html, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                
                # GRÁFICO CON SELECTOR DE RANGO TEMPORAL
                if data['timeline'] and 'interest_over_time' in data['timeline']:
                    timeline = data['timeline']['interest_over_time']['timeline_data']
                    
                    # Selector de rango temporal
                    col_title, col_range = st.columns([2, 1])
                    
                    with col_title:
                        st.markdown("#### 📊 Tendencia Temporal")
                    
                    with col_range:
                        time_range = st.selectbox(
                            "Período",
                            ["Último mes", "Últimos 3 meses", "Últimos 6 meses", "Último año", "Últimos 2 años", "Todo (5 años)"],
                            index=2,  # Default: Últimos 6 meses
                            key="time_range_selector",
                            label_visibility="collapsed"
                        )
                    
                    # Filtrar datos según el rango seleccionado
                    dates = [p['date'] for p in timeline]
                    values = [p['values'][0]['extracted_value'] if p['values'] else 0 for p in timeline]
                    
                    # Calcular fecha de corte según selección
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    
                    if time_range == "Último mes":
                        cutoff_date = today - timedelta(days=30)
                        months_back = 1
                    elif time_range == "Últimos 3 meses":
                        cutoff_date = today - timedelta(days=90)
                        months_back = 3
                    elif time_range == "Últimos 6 meses":
                        cutoff_date = today - timedelta(days=180)
                        months_back = 6
                    elif time_range == "Último año":
                        cutoff_date = today - timedelta(days=365)
                        months_back = 12
                    elif time_range == "Últimos 2 años":
                        cutoff_date = today - timedelta(days=730)
                        months_back = 24
                    else:  # Todo (5 años)
                        cutoff_date = today - timedelta(days=1825)
                        months_back = 60
                    
                    # Filtrar datos
                    filtered_dates = []
                    filtered_values = []
                    for date_str, value in zip(dates, values):
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            if date_obj >= cutoff_date:
                                filtered_dates.append(date_str)
                                filtered_values.append(value)
                        except:
                            # Si falla el parsing, incluir el dato
                            filtered_dates.append(date_str)
                            filtered_values.append(value)
                    
                    # Crear gráfico con datos filtrados
                    if filtered_dates and filtered_values:
                        fig = create_trend_chart(filtered_dates, filtered_values, search_query)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                        # Info de contexto
                        if len(filtered_dates) < len(dates):
                            st.caption(f"ℹ️ Mostrando {len(filtered_dates)} puntos de datos de los últimos {months_back} meses")
                    else:
                        st.info("No hay datos disponibles para el período seleccionado")
                
                # SPRINT 2: TENDENCIAS RELACIONADAS CON SPARKLINES
                if data.get('topics'):
                    sparklines_html = render_related_trends_with_sparklines(data['topics'], max_items=6)
                    if sparklines_html:
                        st.markdown(sparklines_html, unsafe_allow_html=True)
                
                # SPRINT 2: BOTÓN DE EXPORT
                st.markdown("<br>", unsafe_allow_html=True)
                col_export1, col_export2, col_export3, col_export4 = st.columns(4)
                
                with col_export1:
                    if st.button("📄 Exportar CSV", use_container_width=True):
                        csv_data = export_to_csv(data, search_query)
                        st.download_button(
                            label="⬇️ Descargar CSV",
                            data=csv_data,
                            file_name=f"{search_query}_trends_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with col_export2:
                    if st.button("📗 Exportar Excel", use_container_width=True):
                        excel_data = export_to_excel(data, search_query)
                        st.download_button(
                            label="⬇️ Descargar Excel",
                            data=excel_data,
                            file_name=f"{search_query}_trends_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                
                with col_export3:
                    if st.button("📦 Exportar JSON", use_container_width=True):
                        json_data = export_to_json(data, search_query)
                        st.download_button(
                            label="⬇️ Descargar JSON",
                            data=json_data,
                            file_name=f"{search_query}_trends_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                with col_export4:
                    if REPORTLAB_AVAILABLE:
                        if st.button("📕 Exportar PDF", use_container_width=True):
                            pdf_data = export_to_pdf(data, search_query, COUNTRIES[geo]["name"])
                            if pdf_data:
                                st.download_button(
                                    label="⬇️ Descargar PDF",
                                    data=pdf_data,
                                    file_name=f"{search_query}_trends_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            else:
                                st.error("Error generando PDF")
                    else:
                        st.info("📕 Instalar reportlab para PDF")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # TABS CON SEPARACIÓN POR FUENTE DE DATOS
                st.markdown("### 📊 Análisis por Fuente de Datos")
                st.markdown("""
                <div style="background: #f5f5f7; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0; color: #1d1d1f; font-size: 0.9rem;">
                        💡 <strong>Datos separados por plataforma</strong> para entender el origen de cada insight
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Tabs principales por fuente
                source_tabs = st.tabs([
                    "🌐 Google Trends", 
                    "🛍️ Amazon", 
                    "🎥 YouTube", 
                    "📊 Comparación Multi-plataforma"
                ])
                
                # ========== TAB 1: GOOGLE TRENDS ==========
                with source_tabs[0]:
                    st.markdown("""
                    <div style="display: inline-block; background: #007AFF; color: white; padding: 0.5rem 1rem; border-radius: 20px; margin-bottom: 1rem;">
                        🌐 Fuente: Google Trends
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sub-tabs para Google Trends
                    google_subtabs = st.tabs(["🔍 Queries", "📑 Topics", "🔥 Trending"])
                    
                    with google_subtabs[0]:
                        st.markdown("#### Búsquedas Relacionadas en Google")
                        qtype_map = {
                            "Todos": "all",
                            "Preguntas": "❓ Pregunta",
                            "Atributos": "🏷️ Atributo"
                        }
                        
                        # Inicializar página si no existe
                        if 'page_queries' not in st.session_state:
                            st.session_state.page_queries = 1
                        
                        display_queries_filtered(
                            data['queries'], 
                            selected_categories, 
                            relevance_threshold, 
                            qtype_map[query_type_filter],
                            sort_by="volume",
                            page=st.session_state.get('page_queries', 1)
                        )
                    
                    with google_subtabs[1]:
                        if data['topics'] and 'related_topics' in data['topics']:
                            # SPRINT 3: BUBBLE CHART
                            st.markdown("#### 🫧 Mapa Interactivo de Temas (Google)")
                            
                            bubble_fig = create_bubble_chart(data['topics'], max_topics=30)
                            
                            if bubble_fig:
                                st.plotly_chart(bubble_fig, use_container_width=True, config={
                                    'displayModeBar': True,
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
                                })
                                
                                # Leyenda de colores
                                st.markdown("""
                                <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1rem; flex-wrap: wrap;">
                                    <span style="color: #007AFF;">● Search term</span>
                                    <span style="color: #34C759;">● Topic</span>
                                    <span style="color: #FF9500;">● Brand</span>
                                    <span style="color: #FF3B30;">● Product</span>
                                    <span style="color: #5856D6;">● Category</span>
                                    <span style="color: #FFD700;">⭐ Rising</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Tabla tradicional en expander
                            with st.expander("📋 Ver lista detallada de topics", expanded=False):
                                st.markdown("#### 🔝 Top Topics")
                                if 'top' in data['topics']['related_topics']:
                                    topics_list = []
                                    for t in data['topics']['related_topics']['top'][:20]:
                                        topics_list.append({
                                            'Topic': t.get('topic', {}).get('title', 'N/A'),
                                            'Tipo': t.get('topic', {}).get('type', 'N/A'),
                                            'Valor': t.get('value', 0)
                                        })
                                    if topics_list:
                                        st.dataframe(pd.DataFrame(topics_list), use_container_width=True)
                        else:
                            # SPRINT 4: Empty state para topics
                            render_no_topics_state()
                    
                    with google_subtabs[2]:
                        if data['queries'] and 'related_queries' in data['queries']:
                            if 'rising' in data['queries']['related_queries']:
                                st.markdown("#### 🔥 Queries en Tendencia (Rising)")
                                rising = data['queries']['related_queries']['rising'][:15]
                                rising_list = []
                                for q in rising:
                                    rising_list.append({
                                        'Query': q.get('query', ''),
                                        'Crecimiento': q.get('value', 'Breakout')
                                    })
                                if rising_list:
                                    st.dataframe(pd.DataFrame(rising_list), use_container_width=True)
                        else:
                            st.info("No hay datos de tendencias")
                
                # ========== TAB 2: AMAZON ==========
                with source_tabs[1]:
                    st.markdown("""
                    <div style="display: inline-block; background: #FF9900; color: white; padding: 0.5rem 1rem; border-radius: 20px; margin-bottom: 1rem;">
                        🛍️ Fuente: Amazon
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Obtener datos Amazon
                    amazon_data = get_amazon_products(search_query, geo)
                    
                    if amazon_data:
                        amazon_analysis = analyze_amazon_data(amazon_data, search_query)
                        
                        if amazon_analysis:
                            # Sub-tabs para Amazon
                            amazon_subtabs = st.tabs(["📊 Métricas", "🔍 Búsquedas Amazon", "📦 Top Productos"])
                            
                            with amazon_subtabs[0]:
                                st.markdown("#### 📊 Métricas Generales de Amazon")
                                
                                # Comparar con tendencias Google
                                trends_change = data.get('month_change', 0)
                                amazon_products = amazon_analysis['total_products']
                                
                                trends_insight = compare_trends_amazon(
                                    trends_change,
                                    amazon_products
                                )
                                
                                # Renderizar insights
                                st.markdown(
                                    render_amazon_insights(amazon_analysis, trends_insight),
                                    unsafe_allow_html=True
                                )
                                
                                # Métricas adicionales
                                st.markdown("#### 💰 Análisis de Precios")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    min_price, max_price = amazon_analysis['price_range']
                                    st.metric("Precio Mínimo", f"{min_price:.2f}€")
                                
                                with col2:
                                    st.metric("Precio Máximo", f"{max_price:.2f}€")
                                
                                with col3:
                                    avg_price = (min_price + max_price) / 2 if max_price > 0 else 0
                                    st.metric("Precio Promedio", f"{avg_price:.2f}€")
                            
                            with amazon_subtabs[1]:
                                st.markdown("#### 🔍 Búsquedas Relacionadas en Amazon")
                                
                                if 'related_searches' in amazon_data and amazon_data['related_searches']:
                                    searches = amazon_data['related_searches']
                                    
                                    for idx, search in enumerate(searches[:10], 1):
                                        query = search.get('query', '')
                                        link = search.get('link', '#')
                                        
                                        st.markdown(f"""
                                        <div style="
                                            background: #fff3cd;
                                            border-left: 3px solid #FF9900;
                                            padding: 0.75rem;
                                            margin-bottom: 0.5rem;
                                            border-radius: 4px;
                                        ">
                                            <strong>{idx}. {query}</strong>
                                            <a href="{link}" target="_blank" style="float: right; color: #FF9900; text-decoration: none;">
                                                Ver en Amazon →
                                            </a>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("No hay búsquedas relacionadas disponibles en Amazon")
                            
                            with amazon_subtabs[2]:
                                st.markdown("#### 📦 Top 5 Productos por Reviews")
                                
                                if amazon_analysis['top_products']:
                                    cols_amazon = st.columns(5)
                                    for idx, product in enumerate(amazon_analysis['top_products'][:5]):
                                        with cols_amazon[idx]:
                                            title = product.get('title', 'N/A')
                                            price = product.get('price', 'N/A')
                                            rating = product.get('rating', 0)
                                            reviews = product.get('reviews_count', 0)
                                            
                                            st.markdown(f"""
                                            <div style="
                                                background: white;
                                                border: 1px solid rgba(0,0,0,0.08);
                                                border-radius: 8px;
                                                padding: 0.75rem;
                                                height: 160px;
                                                overflow: hidden;
                                            ">
                                                <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">
                                                    {html.escape(title[:40])}...
                                                </div>
                                                <div style="color: #FF9900; font-weight: 700; margin-bottom: 0.25rem;">
                                                    {price}
                                                </div>
                                                <div style="color: #6e6e73; font-size: 0.8rem;">
                                                    ⭐ {rating} ({reviews:,} reviews)
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                else:
                                    st.info("No hay productos disponibles")
                        else:
                            st.info("No se pudieron analizar los datos de Amazon")
                    else:
                        st.info("No hay datos de Amazon disponibles para esta búsqueda")
                
                # ========== TAB 3: YOUTUBE ==========
                with source_tabs[2]:
                    st.markdown("""
                    <div style="display: inline-block; background: #FF0000; color: white; padding: 0.5rem 1rem; border-radius: 20px; margin-bottom: 1rem;">
                        🎥 Fuente: YouTube
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Obtener datos YouTube
                    youtube_data = get_youtube_videos(search_query, geo)
                    
                    if youtube_data and 'video_results' in youtube_data:
                        videos = youtube_data['video_results']
                        
                        # Sub-tabs para YouTube
                        youtube_subtabs = st.tabs(["📊 Métricas", "📹 Top Videos", "📈 Keywords"])
                        
                        with youtube_subtabs[0]:
                            st.markdown("#### 📊 Métricas de Contenido YouTube")
                            
                            # Calcular métricas
                            total_videos = len(videos)
                            
                            # Extraer views (si están disponibles)
                            total_views = 0
                            videos_with_views = 0
                            for v in videos:
                                views_str = v.get('views', '0')
                                try:
                                    # Limpiar string de views
                                    views_clean = ''.join(filter(str.isdigit, str(views_str)))
                                    if views_clean:
                                        total_views += int(views_clean)
                                        videos_with_views += 1
                                except:
                                    pass
                            
                            avg_views = total_views // videos_with_views if videos_with_views > 0 else 0
                            
                            # Grid de métricas
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("📹 Videos Encontrados", total_videos)
                            
                            with col2:
                                st.metric("👁️ Views Totales", f"{total_views:,}")
                            
                            with col3:
                                st.metric("📊 Views Promedio", f"{avg_views:,}")
                            
                            # Timeline de publicaciones
                            st.markdown("#### 📅 Actividad Reciente")
                            recent_count = sum(1 for v in videos if 'hour' in v.get('published_date', '').lower() or 'day' in v.get('published_date', '').lower())
                            week_count = sum(1 for v in videos if 'week' in v.get('published_date', '').lower() or recent_count > 0)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Última semana", recent_count)
                            with col2:
                                st.metric("Último mes", week_count)
                            with col3:
                                st.metric("Más antiguos", total_videos - week_count)
                        
                        with youtube_subtabs[1]:
                            st.markdown("#### 📹 Top 10 Videos por Views")
                            
                            # Ordenar por views
                            videos_sorted = sorted(
                                videos[:20],
                                key=lambda x: int(''.join(filter(str.isdigit, str(x.get('views', '0'))))),
                                reverse=True
                            )[:10]
                            
                            for idx, video in enumerate(videos_sorted, 1):
                                title = video.get('title', 'N/A')
                                channel = video.get('channel', {}).get('name', 'N/A')
                                views = video.get('views', 'N/A')
                                published = video.get('published_date', 'N/A')
                                link = video.get('link', '#')
                                
                                st.markdown(f"""
                                <div style="
                                    background: white;
                                    border: 1px solid rgba(0,0,0,0.08);
                                    border-radius: 8px;
                                    padding: 1rem;
                                    margin-bottom: 0.75rem;
                                    border-left: 3px solid #FF0000;
                                ">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                        <strong style="color: #1d1d1f; font-size: 1rem;">#{idx} {html.escape(title[:80])}</strong>
                                    </div>
                                    <div style="color: #6e6e73; font-size: 0.85rem; margin-bottom: 0.25rem;">
                                        📺 {html.escape(channel)} | 👁️ {views} views | 📅 {published}
                                    </div>
                                    <a href="{link}" target="_blank" style="color: #FF0000; text-decoration: none; font-size: 0.85rem;">
                                        Ver en YouTube →
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with youtube_subtabs[2]:
                            st.markdown("#### 🔑 Keywords más Mencionadas")
                            
                            # Extraer keywords de títulos
                            from collections import Counter
                            all_words = []
                            
                            for video in videos:
                                title = video.get('title', '').lower()
                                words = title.split()
                                all_words.extend(words)
                            
                            # Contar frecuencia
                            word_counts = Counter(all_words)
                            
                            # Filtrar stopwords
                            stopwords = {'de', 'la', 'el', 'en', 'y', 'a', 'con', 'para', 'por', 'los', 'las', 'del', 'al', 'un', 'una', 'the', 'and', 'or', 'of', 'to', 'in', 'for', 'on', 'with'}
                            filtered = [(w, c) for w, c in word_counts.most_common(50) 
                                        if w not in stopwords and len(w) > 3][:20]
                            
                            if filtered:
                                # Mostrar como tags
                                keywords_html = '<div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">'
                                for word, count in filtered:
                                    keywords_html += f"""
                                    <span style="
                                        background: #ffebee;
                                        color: #FF0000;
                                        padding: 0.5rem 1rem;
                                        border-radius: 20px;
                                        font-weight: 600;
                                        font-size: 0.9rem;
                                    ">
                                        {html.escape(word)} ({count})
                                    </span>
                                    """
                                keywords_html += '</div>'
                                st.markdown(keywords_html, unsafe_allow_html=True)
                            else:
                                st.info("No se pudieron extraer keywords")
                    else:
                        st.info("No hay datos de YouTube disponibles para esta búsqueda")
                
                # ========== TAB 4: COMPARACIÓN MULTI-PLATAFORMA ==========
                with source_tabs[3]:
                    st.markdown("""
                    <div style="display: inline-block; background: #5856D6; color: white; padding: 0.5rem 1rem; border-radius: 20px; margin-bottom: 1rem;">
                        📊 Fuente: Multi-plataforma
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🔀 Comparación de Plataformas")
                    
                    # Recopilar métricas
                    google_queries = 0
                    if data.get('queries') and 'related_queries' in data['queries']:
                        top_queries = data['queries'].get('related_queries', {}).get('top', [])
                        rising_queries = data['queries'].get('related_queries', {}).get('rising', [])
                        google_queries = len(top_queries) + len(rising_queries)
                    
                    amazon_products = 0
                    amazon_data_temp = get_amazon_products(search_query, geo)
                    if amazon_data_temp:
                        amazon_analysis_temp = analyze_amazon_data(amazon_data_temp, search_query)
                        if amazon_analysis_temp:
                            amazon_products = amazon_analysis_temp['total_products']
                    
                    youtube_videos = 0
                    youtube_data_temp = get_youtube_videos(search_query, geo)
                    if youtube_data_temp and 'video_results' in youtube_data_temp:
                        youtube_videos = len(youtube_data_temp['video_results'])
                    
                    # Gráfico comparativo
                    import plotly.graph_objects as go
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Volumen de Contenido',
                            x=['Google Trends', 'Amazon', 'YouTube'],
                            y=[google_queries, amazon_products, youtube_videos],
                            marker_color=['#007AFF', '#FF9900', '#FF0000'],
                            text=[google_queries, amazon_products, youtube_videos],
                            textposition='auto',
                        )
                    ])
                    
                    fig.update_layout(
                        title=f"Volumen de Contenido: {search_query}",
                        yaxis_title="Cantidad de Elementos",
                        showlegend=False,
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabla comparativa
                    st.markdown("#### 📋 Tabla Comparativa")
                    
                    comparison_data = {
                        'Plataforma': ['🌐 Google Trends', '🛍️ Amazon', '🎥 YouTube'],
                        'Elementos': [google_queries, amazon_products, youtube_videos],
                        'Tipo': ['Queries relacionadas', 'Productos', 'Videos'],
                        'Status': [
                            '✅ Alta actividad' if google_queries > 20 else '⚠️ Media actividad' if google_queries > 5 else '❌ Baja actividad',
                            '✅ Alta oferta' if amazon_products > 20 else '⚠️ Media oferta' if amazon_products > 5 else '❌ Baja oferta',
                            '✅ Mucho contenido' if youtube_videos > 20 else '⚠️ Contenido medio' if youtube_videos > 5 else '❌ Poco contenido'
                        ]
                    }
                    
                    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
                    
                    # Insights consolidados
                    st.markdown("#### 💡 Insights Multi-plataforma")
                    
                    # Determinar plataforma dominante
                    platforms = [
                        ('Google Trends', google_queries, '🌐'),
                        ('Amazon', amazon_products, '🛍️'),
                        ('YouTube', youtube_videos, '🎥')
                    ]
                    max_platform = max(platforms, key=lambda x: x[1])
                    
                    # Generar insight personalizado
                    if max_platform[1] > 0:
                        st.success(f"""
                        **{max_platform[2]} Mayor actividad en {max_platform[0]}** con {max_platform[1]} elementos.
                        
                        **Desglose por plataforma:**
                        - 🌐 **Google Trends**: {google_queries} queries relacionadas
                        - 🛍️ **Amazon**: {amazon_products} productos disponibles
                        - 🎥 **YouTube**: {youtube_videos} videos recientes
                        
                        **Recomendación**: 
                        {"La marca tiene fuerte presencia en búsquedas orgánicas. Considera aprovechar esta demanda." if max_platform[0] == 'Google Trends' else
                         "Alta disponibilidad de productos. Mercado establecido con competencia." if max_platform[0] == 'Amazon' else
                         "Mucho contenido generado. La marca tiene engagement en video."}
                        """)
                    else:
                        st.info("No hay suficientes datos para generar insights multi-plataforma")
                    
                    # Análisis de correlación
                    st.markdown("#### 🔗 Análisis de Correlación")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Google vs Amazon**")
                        if google_queries > 20 and amazon_products > 20:
                            st.success("✅ Demanda y oferta correlacionadas")
                        elif google_queries > 20 and amazon_products < 10:
                            st.warning("⚠️ Alta demanda, poca oferta → Oportunidad")
                        elif google_queries < 10 and amazon_products > 20:
                            st.info("ℹ️ Poca demanda, alta oferta → Saturación")
                        else:
                            st.info("ℹ️ Ambos con actividad baja")
                    
                    with col2:
                        st.markdown("**Google vs YouTube**")
                        if google_queries > 20 and youtube_videos > 20:
                            st.success("✅ Búsquedas y contenido correlacionados")
                        elif google_queries > 20 and youtube_videos < 10:
                            st.warning("⚠️ Demanda alta, poco contenido video")
                        elif google_queries < 10 and youtube_videos > 20:
                            st.info("ℹ️ Mucho contenido, pocas búsquedas")
                        else:
                            st.info("ℹ️ Ambos con actividad baja")
                
                # SPRINT 6: INTEREST BY REGION (fuera de tabs, datos Google)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 🗺️ Interés por Región")
                
                region_data = get_interest_by_region(search_query, geo, selected_channel)
                if region_data and 'interest_by_region' in region_data:
                    region_map = create_region_map(region_data, country_name)
                    if region_map:
                        st.plotly_chart(region_map, use_container_width=True)
                    
                    # Tabla top regiones
                    regions = region_data['interest_by_region']
                    top_5 = sorted(regions, key=lambda x: x.get('extracted_value', 0), reverse=True)[:5]
                    
                    st.markdown("**🏆 Top 5 Regiones:**")
                    cols_regions = st.columns(5)
                    for idx, region in enumerate(top_5):
                        with cols_regions[idx]:
                            st.metric(
                                region['location'],
                                f"{region.get('extracted_value', 0)}/100"
                            )
                else:
                    st.info("No hay datos regionales disponibles")
                
                # SPRINT 6: NOTICIAS RELACIONADAS
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📰 Noticias Recientes")
                
                news_data = get_related_news(search_query)
                if news_data and 'news' in news_data:
                    news_items = news_data['news'][:5]  # Top 5 noticias
                    
                    if news_items:
                        for news in news_items:
                            st.markdown(render_news_card(news), unsafe_allow_html=True)
                    else:
                        st.info("No hay noticias recientes disponibles")
                else:
                    st.info("No hay noticias disponibles")
                
                
    except Exception as e:
        st.error(f"❌ Error inesperado al procesar el análisis: {str(e)}")
        st.info("💡 Intenta de nuevo o contacta soporte si el error persiste.")


# ================================
# SPRINT 5: COMPARADOR DE MARCAS
# ================================

