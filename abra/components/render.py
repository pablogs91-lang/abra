"""
Componentes de renderizado UI
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import json
import html

import plotly.graph_objects as go
import plotly.express as px

from abra.config.constants import PRODUCT_CATEGORIES



def render_query_with_bar(query_text, value, max_value, index, query_type="Query", relevance=0, trend_values=None):
    """
    Renderiza una query con barra visual estilo Glimpse.
    Opcionalmente muestra sparkline si trend_values está disponible.
    
    Args:
        query_text (str): Texto de la query
        value (int/str): Valor/volumen
        max_value (int): Valor máximo para calcular %
        index (int): Índice de la query
        query_type (str): Tipo de query
        relevance (int): Relevancia %
        trend_values (list): Lista de valores para sparkline [v1, v2, ...]
    """
    # Calcular width de la barra (porcentaje del máximo)
    if max_value > 0:
        width_pct = (value / max_value) * 100
    else:
        width_pct = 0
    
    # Formato del valor
    if isinstance(value, str):
        value_display = value
        numeric_value = "N/A"
    elif value >= 1000:
        value_display = f"{value/1000:.1f}K"
        numeric_value = f"{value:,}"
    else:
        value_display = str(int(value))
        numeric_value = f"{value:,}"
    
    # Escapar query_text para HTML
    safe_query_text = html.escape(str(query_text))
    
    # Fix: Use pipe separators instead of newlines in HTML title attribute
    tooltip_text = f"{safe_query_text} | Volumen: {numeric_value} | Tipo: {query_type} | Relevancia: {relevance}%"
    
    # Generar sparkline si hay datos de tendencia
    sparkline_html = ""
    if trend_values and len(trend_values) > 0:
        # Crear mini sparkline inline
        max_trend = max(trend_values) if trend_values else 1
        max_trend = max(max_trend, 1)  # Evitar división por 0
        
        # Calcular tendencia (último vs primero)
        if len(trend_values) >= 2:
            first_val = trend_values[0] if trend_values[0] > 0 else 1
            last_val = trend_values[-1]
            trend_change = ((last_val - first_val) / first_val) * 100
            trend_emoji = "📈" if trend_change > 5 else "📉" if trend_change < -5 else "➡️"
            trend_color = "#34C759" if trend_change > 5 else "#FF3B30" if trend_change < -5 else "#6e6e73"
        else:
            trend_emoji = "➡️"
            trend_color = "#6e6e73"
        
        # Crear puntos del sparkline (mini gráfico)
        sparkline_points = []
        for i, val in enumerate(trend_values):
            height_pct = (val / max_trend) * 100 if max_trend > 0 else 0
            sparkline_points.append(f'<div style="height:{height_pct}%; background:{trend_color}; width:3px; display:inline-block; margin:0 1px; vertical-align:bottom;"></div>')
        
        sparkline_html = f'''
        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.25rem;">
            <span style="font-size:1rem;">{trend_emoji}</span>
            <div style="display:flex; align-items:flex-end; height:20px; gap:1px;">
                {"".join(sparkline_points)}
            </div>
            <span style="font-size:0.75rem; color:{trend_color}; font-weight:600;">
                Tendencia últimos 12 meses
            </span>
        </div>
        '''
    
    return f"""
    <div class="query-bar-container" title="{tooltip_text}">
        <div class="query-text">{index}. {safe_query_text}</div>
        <div class="query-bar-wrapper">
            <div class="query-bar" style="width: {width_pct}%">
                <span class="query-value">{value_display}</span>
            </div>
        </div>
        {sparkline_html}
    </div>
    """


def render_seasonality_chart(monthly_data, overall_avg):
    """Renderiza gráfico de barras de estacionalidad estilo Glimpse"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    html = '<div class="seasonality-container">'
    
    for month in months:
        value = monthly_data.get(month, 0)
        # Calcular altura relativa (max 150px para no romper contenedor)
        if overall_avg > 0:
            height = min((value / overall_avg) * 100, 150)  # FIX: Cap a 150px
        else:
            height = 50
        
        # Determinar si es positivo o negativo
        css_class = 'positive' if value >= overall_avg else 'negative'
        
        # SPRINT 4: Tooltip mejorado con más información
        if overall_avg > 0:
            diff_pct = ((value - overall_avg) / overall_avg) * 100
            diff_sign = "+" if diff_pct > 0 else ""
            status = "Por encima" if diff_pct > 0 else "Por debajo"
            emoji = "📈" if diff_pct > 0 else "📉"
        else:
            diff_pct = 0
            diff_sign = ""
            status = "Normal"
            emoji = "➡️"
        
        # Fix: Use HTML entities and spaces instead of newlines in title attribute
        tooltip = f"{month} - Interés: {value:.0f} | Promedio: {overall_avg:.0f} | Diferencia: {diff_sign}{diff_pct:.1f}% | {emoji} {status} del promedio"
        
        html += f"""
        <div class="seasonality-month">
            <div class="seasonality-bar {css_class}" 
                 style="height: {height}px" 
                 title="{tooltip}">
            </div>
            <div class="month-label">{month}</div>
        </div>
        """
    
    html += '</div>'
    return html


def render_comparison_summary(comparison_data, country):
    """
    Renderiza tabla resumen comparativa.
    
    Args:
        comparison_data (dict): Datos de comparación
        country (str): País
    
    Returns:
        pandas.DataFrame: Tabla de comparación
    """
    summary = []
    
    for brand, brand_data in comparison_data.items():
        if country in brand_data:
            data = brand_data[country]
            
            summary.append({
                'Marca': brand,
                'Promedio 5Y': f"{data['avg_value']:.0f}/100" if data['avg_value'] else "N/A",
                'Cambio Mes': f"{data['month_change']:+.1f}%" if data['month_change'] is not None else "N/A",
                'Cambio Trimestre': f"{data['quarter_change']:+.1f}%" if data['quarter_change'] is not None else "N/A",
                'Cambio Año': f"{data['year_change']:+.1f}%" if data['year_change'] is not None else "N/A"
            })
    
    if summary:
        return pd.DataFrame(summary)
    return None


def render_history_table(history_data, limit=20):
    """
    Renderiza tabla de histórico.
    
    Args:
        history_data (list): Datos históricos
        limit (int): Número máximo de registros
    
    Returns:
        pandas.DataFrame: Tabla formateada
    """
    if not history_data:
        return None
    
    # Limitar y ordenar (más recientes primero)
    recent = sorted(history_data, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    
    # Convertir a tabla
    table_data = []
    for record in recent:
        table_data.append({
            "Fecha": record["timestamp"][:10],
            "Hora": record["timestamp"][11:16],
            "Marca": record["brand"],
            "País": record.get("country_name", "N/A"),
            "Canal": record.get("channel_name", "N/A"),
            "Promedio": f"{record['metrics'].get('avg_value', 0):.0f}/100",
            "Cambio Año": f"{record['metrics'].get('year_change', 0):+.1f}%"
        })
    
    if table_data:
        return pd.DataFrame(table_data)
    return None


def render_alert_card(alert):
    """
    Renderiza una alerta con estilo.
    
    Args:
        alert (dict): Alerta a renderizar
    
    Returns:
        str: HTML de la alerta
    """
    severity_colors = {
        'high': '#FF3B30',
        'medium': '#FF9500',
        'low': '#007AFF'
    }
    
    bg_color = severity_colors.get(alert['severity'], '#6e6e73')
    
    # Escapar contenido del usuario
    safe_icon = html.escape(str(alert.get('icon', '')))
    safe_message = html.escape(str(alert.get('message', '')))
    safe_metric = html.escape(str(alert.get('metric', '')).replace('_', ' ').title())
    
    html_content = f"""
    <div style="
        background: linear-gradient(135deg, {bg_color}15 0%, {bg_color}05 100%);
        border-left: 4px solid {bg_color};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        animation: slideInRight 0.4s ease;
    ">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.5rem;">{safe_icon}</span>
            <div style="flex: 1;">
                <div style="color: #1d1d1f; font-weight: 600; margin-bottom: 0.25rem;">
                    {safe_message}
                </div>
                <div style="color: #6e6e73; font-size: 0.85rem;">
                    Métrica: {safe_metric} | 
                    Valor: {alert.get('value', 0):.1f}
                </div>
            </div>
        </div>
    </div>
    """
    
    return html_content


def render_comparison_card(comparison):
    """
    Renderiza comparación con histórico.
    
    Args:
        comparison (dict): Datos de comparación
    
    Returns:
        str: HTML de comparación
    """
    if not comparison or not comparison.get('changes'):
        return ""
    
    html = f"""
    <div style="
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">
            📊 Comparación con último análisis ({comparison['last_date']})
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
    """
    
    for metric, data in comparison['changes'].items():
        metric_name = {
            'avg_value': 'Promedio 5Y',
            'month_change': 'Cambio Mes',
            'quarter_change': 'Cambio Trim',
            'year_change': 'Cambio Año'
        }.get(metric, metric)
        
        diff = data['diff']
        arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
        color = "#34C759" if diff > 0 else "#FF3B30" if diff < 0 else "#6e6e73"
        
        html += f"""
        <div style="
            background: rgba(0, 0, 0, 0.02);
            padding: 1rem;
            border-radius: 12px;
        ">
            <div style="color: #6e6e73; font-size: 0.85rem; margin-bottom: 0.5rem;">
                {metric_name}
            </div>
            <div style="display: flex; align-items: baseline; gap: 0.5rem;">
                <span style="font-size: 1.5rem; font-weight: 700; color: #1d1d1f;">
                    {data['current']:.1f}
                </span>
                <span style="color: {color}; font-weight: 600;">
                    {arrow} {abs(diff):.1f}
                </span>
            </div>
            <div style="color: #86868b; font-size: 0.75rem; margin-top: 0.25rem;">
                Anterior: {data['last']:.1f}
            </div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html


def render_news_card(news_item):
    """
    Renderiza una tarjeta de noticia.
    """
    title = news_item.get('title', 'Sin título')
    link = news_item.get('link', '#')
    source = news_item.get('source', 'Fuente desconocida')
    date = news_item.get('date', '')
    thumbnail = news_item.get('thumbnail', '')
    
    # Escapar contenido del usuario
    safe_title = html.escape(str(title))
    safe_link = html.escape(str(link))
    safe_source = html.escape(str(source))
    safe_date = html.escape(str(date)) if date else ''
    safe_thumbnail = html.escape(str(thumbnail)) if thumbnail else ''
    
    thumbnail_html = f'<img src="{safe_thumbnail}" alt="Trending search thumbnail" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;">' if thumbnail else ''
    date_html = f' • {safe_date}' if date else ''
    
    html_content = f"""
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    " tabindex="0"
       onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.1)';" 
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';"
       onfocus="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.1)';"
       onblur="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
        <div style="display: flex; gap: 1rem;">
            {thumbnail_html}
            <div style="flex: 1;">
                <a href="{safe_link}" target="_blank" style="
                    color: #1d1d1f;
                    font-weight: 600;
                    font-size: 0.95rem;
                    text-decoration: none;
                    display: block;
                    margin-bottom: 0.5rem;
                ">{safe_title}</a>
                <div style="color: #6e6e73; font-size: 0.85rem;">
                    <span style="font-weight: 500;">{safe_source}</span>
                    {date_html}
                </div>
            </div>
        </div>
    </div>
    """
    
    return html_content


def render_trending_item(trend):
    """
    Renderiza un item de tendencia.
    """
    query = trend.get('query', '')
    traffic = trend.get('search_count', 'N/A')
    percentage = trend.get('percentage_increase', 0)
    
    # Color según porcentaje
    if percentage >= 100:
        color = '#FF3B30'
        icon = '🔥'
    elif percentage >= 50:
        color = '#FF9500'
        icon = '📈'
    else:
        color = '#34C759'
        icon = '↗️'
    
    html = f"""
    <div style="
        background: linear-gradient(135deg, {color}10 0%, {color}05 100%);
        border-left: 3px solid {color};
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                <span style="color: #1d1d1f; font-weight: 600;">{query}</span>
            </div>
            <div style="text-align: right;">
                <div style="color: {color}; font-weight: 700; font-size: 0.9rem;">
                    +{percentage}%
                </div>
                <div style="color: #86868b; font-size: 0.75rem;">
                    {traffic} búsquedas
                </div>
            </div>
        </div>
    </div>
    """
    
    return html


def render_product_detection_table(products_dict):
    """
    Tabla de productos específicos detectados.
    """
    if not products_dict:
        return None
    
    html = """
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        overflow: hidden;
    ">
        <div style="
            background: linear-gradient(135deg, #FF6B0015 0%, #FF6B0005 100%);
            padding: 1rem;
            border-bottom: 1px solid rgba(0,0,0,0.08);
        ">
            <h4 style="margin: 0; color: #1d1d1f;">🎯 Productos Específicos Detectados</h4>
            <p style="margin: 0.5rem 0 0 0; color: #6e6e73; font-size: 0.9rem;">
                Productos mencionados en títulos de videos
            </p>
        </div>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f5f5f7;">
                        <th style="padding: 0.75rem; text-align: left; color: #1d1d1f; font-weight: 600;">Producto</th>
                        <th style="padding: 0.75rem; text-align: center; color: #1d1d1f; font-weight: 600;">Videos</th>
                        <th style="padding: 0.75rem; text-align: center; color: #1d1d1f; font-weight: 600;">Tendencia</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for idx, (product, data) in enumerate(list(products_dict.items())[:10]):
        count = data['count']
        
        # SECURITY: Escape HTML to prevent XSS
        import html as html_escape
        product_safe = html_escape.escape(product.title())
        
        # Indicador de tendencia
        if count >= 10:
            trend_icon = '🔥'
            trend_color = '#FF3B30'
            trend_text = 'HOT'
        elif count >= 5:
            trend_icon = '📈'
            trend_color = '#FF9500'
            trend_text = 'Trending'
        else:
            trend_icon = '↗️'
            trend_color = '#34C759'
            trend_text = 'Emerging'
        
        bg_color = '#ffffff' if idx % 2 == 0 else '#f9f9f9'
        
        html += f"""
        <tr style="background: {bg_color};">
            <td style="padding: 0.75rem; border-top: 1px solid rgba(0,0,0,0.05);">
                <span style="font-weight: 500; color: #1d1d1f;">{product_safe}</span>
            </td>
            <td style="padding: 0.75rem; text-align: center; border-top: 1px solid rgba(0,0,0,0.05);">
                <span style="
                    background: #FF6B0020;
                    color: #FF6B00;
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-weight: 600;
                ">{count}</span>
            </td>
            <td style="padding: 0.75rem; text-align: center; border-top: 1px solid rgba(0,0,0,0.05);">
                <span style="color: {trend_color}; font-weight: 600;">
                    {trend_icon} {trend_text}
                </span>
            </td>
        </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


# SECURITY: Asegurar escapar user input con html.escape()
def render_empty_state(icon, title, message, suggestions=None):
    """
    Renderiza un estado vacío elegante con icono, mensaje y sugerencias opcionales.
    
    Args:
        icon (str): Emoji o icono
        title (str): Título del mensaje
        message (str): Mensaje descriptivo
        suggestions (list): Lista de sugerencias opcionales
    
    Note: Usa st.write con unsafe_allow_html=True para renderizar
    """
    # Construir HTML
    suggestions_html = ""
    if suggestions and len(suggestions) > 0:
        chips_html = ""
        for suggestion in suggestions:
            chips_html += f'<span style="display:inline-block;background:white;padding:0.5rem 1rem;border-radius:20px;font-size:0.9rem;color:#1d1d1f;border:1px solid rgba(0,0,0,0.08);margin:0.25rem;font-weight:500;">{suggestion}</span>'
        
        suggestions_html = f'''
        <div style="margin-top:2rem;">
            <div style="color:#1d1d1f;font-weight:600;margin-bottom:1rem;font-size:0.95rem;">💡 Prueba buscando:</div>
            <div style="display:flex;flex-wrap:wrap;gap:0.75rem;justify-content:center;max-width:600px;margin:0 auto;">
                {chips_html}
            </div>
        </div>
        '''
    
    html_content = f'''
    <div style="text-align:center;padding:4rem 2rem;background:linear-gradient(135deg,#f5f5f7 0%,#ffffff 100%);border-radius:20px;border:2px dashed rgba(0,0,0,0.1);margin:2rem 0;">
        <div style="font-size:4rem;margin-bottom:1.5rem;">{icon}</div>
        <h3 style="color:#1d1d1f;margin-bottom:0.75rem;font-size:1.5rem;font-weight:600;">{title}</h3>
        <p style="color:#6e6e73;margin-bottom:2rem;font-size:1rem;line-height:1.6;max-width:500px;margin-left:auto;margin-right:auto;">{message}</p>
        {suggestions_html}
    </div>
    '''
    
    # Usar solo st.markdown para evitar problemas
    st.markdown(html_content, unsafe_allow_html=True)


def render_no_queries_state():
    """Empty state cuando no hay queries"""
    render_empty_state(
        icon="🔍",
        title="No se encontraron búsquedas",
        message="No hay queries relacionadas con relevancia suficiente. Intenta ajustar los filtros o probar con otra marca.",
        suggestions=["logitech", "razer", "corsair", "keychron", "steelseries"]
    )


def render_no_topics_state():
    """Empty state cuando no hay topics"""
    render_empty_state(
        icon="📊",
        title="No hay temas disponibles",
        message="No se encontraron temas relacionados para esta búsqueda. Prueba con una marca más popular o conocida.",
        suggestions=["apple", "samsung", "sony", "nvidia", "amd"]
    )


def render_no_data_state():
    """Empty state cuando no hay datos en general"""
    render_empty_state(
        icon="🌐",
        title="Sin datos disponibles",
        message="No se encontraron datos para esta búsqueda. Verifica el nombre de la marca o intenta con otro país.",
        suggestions=["microsoft", "google", "amazon", "meta", "tesla"]
    )


def render_low_relevance_state(threshold):
    """Empty state cuando todas las queries tienen baja relevancia"""
    render_empty_state(
        icon="⚠️",
        title=f"Relevancia por debajo del {threshold}%",
        message=f"Todas las búsquedas relacionadas tienen una relevancia menor al {threshold}%. Reduce el umbral de filtrado o prueba con otra marca.",
        suggestions=None
    )


def render_progress_bar(progress, message, submessage=""):
    """
    Renderiza una barra de progreso personalizada con mensajes.
    
    Args:
        progress (int): Porcentaje de progreso (0-100)
        message (str): Mensaje principal
        submessage (str): Mensaje secundario opcional
    
    Returns:
        str: HTML de la barra de progreso
    """
    html = f"""
    <div class="animate-fadeIn" style="
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
        border-radius: 20px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        margin: 2rem 0;
    ">
        <div style="
            font-size: 3rem;
            margin-bottom: 1.5rem;
            animation: pulse 1.5s ease-in-out infinite;
        ">
            🔄
        </div>
        
        <div style="
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        ">
            {message}
        </div>
        
        {f'<div style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.9rem;">{submessage}</div>' if submessage else ''}
        
        <div style="
            width: 100%;
            max-width: 400px;
            height: 8px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 10px;
            overflow: hidden;
            margin: 0 auto;
            position: relative;
        ">
            <div style="
                width: {progress}%;
                height: 100%;
                background: linear-gradient(90deg, #007AFF 0%, #0051D5 100%);
                border-radius: 10px;
                transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
            "></div>
        </div>
        
        <div style="
            margin-top: 0.75rem;
            color: var(--accent-blue);
            font-weight: 600;
            font-size: 0.95rem;
        ">
            {progress}%
        </div>
    </div>
    """
    return html


def render_skeleton_loader(type="card"):
    """
    Renderiza un skeleton loader animado.
    
    Args:
        type (str): Tipo de skeleton ('card', 'line', 'chart')
    
    Returns:
        str: HTML del skeleton
    """
    if type == "card":
        return """
        <div style="
            background: white;
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <div class="skeleton" style="
                height: 20px;
                width: 60%;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
                margin-bottom: 1rem;
            "></div>
            <div class="skeleton" style="
                height: 40px;
                width: 40%;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
                margin-bottom: 0.5rem;
            "></div>
            <div class="skeleton" style="
                height: 16px;
                width: 30%;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
            "></div>
        </div>
        """
    elif type == "line":
        return """
        <div class="skeleton" style="
            height: 12px;
            width: 100%;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 4px;
            margin-bottom: 0.75rem;
        "></div>
        """
    elif type == "chart":
        return """
        <div style="
            background: white;
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 16px;
            padding: 2rem;
            height: 300px;
            display: flex;
            align-items: flex-end;
            gap: 0.5rem;
        ">
            <div class="skeleton" style="
                height: 60%;
                flex: 1;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
            "></div>
            <div class="skeleton" style="
                height: 80%;
                flex: 1;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
            "></div>
            <div class="skeleton" style="
                height: 45%;
                flex: 1;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
            "></div>
            <div class="skeleton" style="
                height: 70%;
                flex: 1;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
            "></div>
            <div class="skeleton" style="
                height: 90%;
                flex: 1;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 4px;
            "></div>
        </div>
        """


def render_loading_state(message="Cargando datos...", show_skeleton=False):
    """
    Renderiza un estado de carga completo con mensaje y opcionalmente skeleton.
    
    Args:
        message (str): Mensaje de carga
        show_skeleton (bool): Mostrar skeleton loaders
    
    Returns:
        str: HTML del loading state
    """
    html = f"""
    <div class="animate-fadeIn" style="
        text-align: center;
        padding: 3rem 2rem;
    ">
        <div style="
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: pulse 1.5s ease-in-out infinite;
        ">
            ⏳
        </div>
        <div style="
            color: var(--text-primary);
            font-weight: 600;
            font-size: 1.1rem;
        ">
            {message}
        </div>
    </div>
    """
    
    if show_skeleton:
        html += "<div style='margin-top: 2rem;'>"
        html += render_skeleton_loader("card")
        html += render_skeleton_loader("chart")
        html += "</div>"
    
    return html


def render_metric_card(label, value, delta=None, delay=0):
    """
    Renderiza una métrica card con animación.
    SPRINT 4: Añadido delay para efecto cascada.
    """
    delta_class = "positive" if delta and delta > 0 else "negative" if delta and delta < 0 else ""
    delta_symbol = "↑" if delta and delta > 0 else "↓" if delta and delta < 0 else ""
    delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {abs(delta):.1f}%</div>' if delta is not None else ""
    
    # SPRINT 4: Añadir clase de animación con delay
    animation_class = f"animate-fadeInUp delay-{delay}" if delay > 0 else "animate-fadeInUp"
    
    return f"""
    <div class="metric-card {animation_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """


# SECURITY: Asegurar escapar user input con html.escape()
def render_multi_channel_results(brand, geo, country_data, categories, threshold):
    """
    Renderiza resultados de análisis multi-canal de forma estructurada.
    
    Args:
        brand (str): Marca analizada
        geo (str): Código del país
        country_data (dict): Datos consolidados del país
        categories (list): Categorías
        threshold (int): Umbral de relevancia
    """
    country_name = country_data['country']
    channels = country_data['channels']
    consolidated = country_data['consolidated']
    
    # Header del país
    st.markdown(f"## 🌍 {country_name}")
    
    # ========== RESUMEN EJECUTIVO ==========
    st.markdown("### 📊 Resumen Multi-Canal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Canales Analizados",
            consolidated['total_channels'],
            f"{consolidated['channels_with_data']} con datos"
        )
    
    with col2:
        dominant = consolidated.get('dominant_channel')
        if dominant:
            st.metric(
                "Canal Dominante",
                dominant['name'],
                f"{dominant['percentage']:.1f}%"
            )
        else:
            st.metric("Canal Dominante", "N/A")
    
    with col3:
        total_queries = len(consolidated['all_queries'])
        st.metric("Queries Totales", total_queries)
    
    with col4:
        total_topics = len(consolidated['all_topics'])
        st.metric("Topics Totales", total_topics)
    
    # ========== INSIGHTS CROSS-CHANNEL ==========
    if consolidated['insights']:
        st.markdown("### 💡 Insights Multi-Canal")
        
        for insight in consolidated['insights']:
            severity_colors = {
                'success': '#34C759',
                'warning': '#FF9500',
                'info': '#007AFF'
            }
            color = severity_colors.get(insight.get('severity', 'info'), '#007AFF')
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem;">{insight['icon']}</span>
                    <div>
                        <div style="color: #1d1d1f; font-weight: 600; margin-bottom: 0.25rem;">
                            {insight['title']}
                        </div>
                        <div style="color: #6e6e73; font-size: 0.9rem;">
                            {insight['description']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== GRÁFICO COMPARATIVO DE VOLUMEN POR CANAL ==========
    st.markdown("### 📊 Volumen por Canal")
    
    if consolidated['channel_volumes']:
        import plotly.graph_objects as go
        
        channel_names = []
        channel_values = []
        channel_colors = {
            'web': '#FF6B00',
            'images': '#34C759',
            'news': '#FF3B30',
            'youtube': '#FF0000',
            'shopping': '#007AFF'
        }
        
        for channel_key, volume in consolidated['channel_volumes'].items():
            channel_names.append(channels[channel_key]['name'])
            channel_values.append(volume)
        
        fig = go.Figure(data=[
            go.Bar(
                x=channel_names,
                y=channel_values,
                marker_color=[channel_colors.get(k, '#6e6e73') for k in consolidated['channel_volumes'].keys()],
                text=channel_values,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Interés Promedio por Canal - {brand}",
            xaxis_title="Canal",
            yaxis_title="Interés (0-100)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ========== DATOS POR CANAL (TABS) ==========
    st.markdown("### 📡 Datos Detallados por Canal")
    
    # Crear tabs para cada canal
    channel_tabs = st.tabs([
        f"{CHANNELS['web']['icon']} Web",
        f"{CHANNELS['images']['icon']} Images",
        f"{CHANNELS['news']['icon']} News",
        f"{CHANNELS['youtube']['icon']} YouTube",
        f"{CHANNELS['shopping']['icon']} Shopping"
    ])
    
    channel_keys = ['web', 'images', 'news', 'youtube', 'shopping']
    
    for idx, channel_key in enumerate(channel_keys):
        with channel_tabs[idx]:
            channel_data = channels[channel_key]
            
            if 'error' in channel_data:
                st.error(f"❌ Error obteniendo datos: {channel_data['error']}")
                continue
            
            # Métricas del canal
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Interés Promedio",
                    f"{channel_data['avg_value']:.1f}"
                )
            
            with col2:
                st.metric(
                    "Cambio Mensual",
                    f"{channel_data['month_change']:+.1f}%"
                )
            
            with col3:
                st.metric(
                    "Cambio Trimestral",
                    f"{channel_data['quarter_change']:+.1f}%"
                )
            
            with col4:
                st.metric(
                    "Cambio Anual",
                    f"{channel_data['year_change']:+.1f}%"
                )
            
            # Timeline
            if channel_data.get('timeline'):
                timeline = channel_data['timeline']
                if 'interest_over_time' in timeline:
                    df = timeline['interest_over_time']
                    if not df.empty and brand in df.columns:
                        dates = df.index.strftime('%Y-%m-%d').tolist()
                        values = df[brand].tolist()
                        
                        st.markdown(f"#### 📈 Tendencia Temporal - {channel_data['name']}")
                        fig = create_trend_chart(dates, values, brand)
                        st.plotly_chart(fig, use_container_width=True)
            
            # Queries del canal
            if channel_data.get('queries'):
                st.markdown(f"#### 🔍 Top Queries - {channel_data['name']}")
                
                queries_data = channel_data['queries']
                if 'related_queries' in queries_data and 'top' in queries_data['related_queries']:
                    top_queries = queries_data['related_queries']['top'][:10]
                    
                    for idx_q, q in enumerate(top_queries, 1):
                        query_text = q.get('query', '')
                        value = q.get('value', 0)
                        category = q.get('category', '')
                        relevance = q.get('relevance', 100)
                        
                        # Badge de categoría si existe
                        category_badge = ""
                        if category and category != 'N/A':
                            icon = PRODUCT_CATEGORIES.get(category, {}).get('icon', '🏷️')
                            category_badge = f"""
                            <span style="
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                padding: 0.2rem 0.5rem;
                                border-radius: 4px;
                                font-size: 0.75rem;
                                font-weight: 600;
                                margin-left: 0.5rem;
                            ">
                                {icon} {category}
                            </span>
                            """
                        
                        st.markdown(f"""
                        <div style="
                            background: white;
                            border: 1px solid rgba(0,0,0,0.08);
                            border-radius: 8px;
                            padding: 0.75rem;
                            margin-bottom: 0.5rem;
                        ">
                            <strong>{idx_q}. {query_text}</strong>
                            {category_badge}
                            <span style="float: right; color: #FF6B00; font-weight: 600;">
                                {value}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No hay queries disponibles para {channel_data['name']}")
            
            # Topics del canal
            if channel_data.get('topics'):
                topics_data = channel_data['topics']
                if 'related_topics' in topics_data and 'top' in topics_data['related_topics']:
                    with st.expander(f"📑 Topics - {channel_data['name']}", expanded=False):
                        top_topics = topics_data['related_topics']['top'][:10]
                        
                        topics_list = []
                        for t in top_topics:
                            category = t.get('category', 'N/A')
                            icon = PRODUCT_CATEGORIES.get(category, {}).get('icon', '🏷️') if category != 'N/A' else ''
                            category_display = f"{icon} {category}" if category != 'N/A' else 'N/A'
                            
                            topics_list.append({
                                'Topic': t.get('topic', {}).get('title', 'N/A'),
                                'Categoría': category_display,
                                'Tipo': t.get('topic', {}).get('type', 'N/A'),
                                'Valor': t.get('value', 0)
                            })
                        
                        if topics_list:
                            st.dataframe(pd.DataFrame(topics_list), use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)


def render_related_trends_with_sparklines(topics_data, max_items=6):
    """
    Renderiza tendencias relacionadas con sparklines.
    Estilo Glimpse.
    """
    if not topics_data or 'related_topics' not in topics_data:
        return None
    
    rising_topics = topics_data.get('related_topics', {}).get('rising', [])
    
    if not rising_topics:
        return None
    
    # Limitar a max_items
    topics_to_show = rising_topics[:max_items]
    
    html_content = '<div style="margin-top: 2rem;">'
    html_content += '<h4 style="color: #1d1d1f; margin-bottom: 1rem;">🔗 Tendencias Relacionadas</h4>'
    html_content += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">'
    
    for idx, topic in enumerate(topics_to_show, start=1):
        topic_title = topic.get('topic', {}).get('title', 'N/A')
        topic_type = topic.get('topic', {}).get('type', '')
        value = topic.get('value', 0)
        
        # Fix: Escape HTML to prevent XSS and rendering issues
        topic_title_safe = html.escape(str(topic_title))
        topic_type_safe = html.escape(str(topic_type))
        
        # Generar datos simulados para sparkline (en prod vendría del API)
        # FIX: random ya importado arriba
        spark_values = [random.randint(30, 100) for _ in range(12)]
        
        # SPRINT 4: Añadir clases de animación con delay
        animation_class = f"animate-scaleIn delay-{idx}"
        
        html_content += f"""
        <div class="sparkline-card {animation_class}" style="
            background: white;
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            padding: 1rem;
            cursor: pointer;
        ">
            <div style="font-weight: 600; color: #1d1d1f; font-size: 0.95rem; margin-bottom: 0.5rem;">
                {topic_title_safe}
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.8rem; color: #6e6e73;">{topic_type_safe}</span>
                <span style="font-size: 0.8rem; font-weight: 600; color: #34C759;">
                    {'Breakout' if isinstance(value, str) and 'Breakout' in str(value) else f'+{value}%'}
                </span>
            </div>
        </div>
        """
    
    html_content += '</div>'
    
    # Link para ver todas
    total_topics = len(rising_topics)
    if total_topics > max_items:
        html_content += f'<div style="text-align: center; margin-top: 1rem;">'
        html_content += f'<a href="#" style="color: #007AFF; text-decoration: none; font-weight: 500;">→ Ver todas las {total_topics} tendencias relacionadas</a>'
        html_content += '</div>'
    
    html_content += '</div>'
    
    return html_content

