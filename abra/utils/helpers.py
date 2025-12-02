"""
Utilidades y funciones auxiliares
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import json
import html



def get_relevance_badge(score):
    if score >= 80:
        return "🟢 Alto", "badge-high"
    elif score >= 50:
        return "🟡 Medio", "badge-medium"
    elif score >= 30:
        return "🟠 Bajo", "badge-low"
    else:
        return "🔴 Dudoso", "badge-doubt"


def extract_brand_from_url(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        known_brands = ["asus", "msi", "gigabyte", "logitech", "razer", "corsair",
                       "hyperx", "steelseries", "roccat", "cooler master", "keychron"]
        
        for brand in known_brands:
            if brand in path:
                return brand.title() if brand not in ["msi", "asus", "hyperx"] else brand.upper()
        
        parts = path.split('/')
        for part in parts:
            if part and len(part) > 2:
                return part.replace('-', ' ').title().split()[0]
        return None
    except:
        return None


def get_seasonality_badge(score):
    """Retorna badge de estacionalidad basado en score"""
    if score >= 60:
        return "🔥 Altamente estacional", "badge-high"
    elif score >= 30:
        return "📊 Moderadamente estacional", "badge-medium"
    else:
        return "➖ Baja estacionalidad", "badge-low"


def paginate_data(data, page_size=20, page=1):
    """Pagina una lista de datos"""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    total_pages = (len(data) + page_size - 1) // page_size
    
    return {
        'data': data[start_idx:end_idx],
        'current_page': page,
        'total_pages': total_pages,
        'total_items': len(data),
        'start_idx': start_idx + 1,
        'end_idx': min(end_idx, len(data))
    }


def sort_queries(queries, sort_by='volume'):
    """
    Ordena queries por diferentes criterios.
    sort_by: 'volume', 'growth', 'alphabetical'
    """
    if not queries:
        return queries
    
    if sort_by == 'volume':
        # Ordenar por valor (desc)
        return sorted(queries, key=lambda x: x.get('value', 0), reverse=True)
    elif sort_by == 'growth':
        # Ordenar por crecimiento (queries con "Breakout" primero)
        def growth_key(q):
            val = q.get('value', 0)
            if isinstance(val, str) and 'Breakout' in val:
                return float('inf')
            return float(val) if isinstance(val, (int, float)) else 0
        return sorted(queries, key=growth_key, reverse=True)
    elif sort_by == 'alphabetical':
        return sorted(queries, key=lambda x: x.get('query', '').lower())
    else:
        return queries


def create_comparison_chart(comparison_data, country):
    """
    Crea gráfico comparativo de múltiples marcas.
    
    Args:
        comparison_data (dict): Datos de comparación {brand: {geo: data}}
        country (str): País a visualizar
    
    Returns:
        plotly.graph_objects.Figure: Gráfico comparativo
    """
    fig = go.Figure()
    
    colors = ['#FF6B00', '#007AFF', '#34C759', '#FF3B30', '#5856D6', '#FF9500']
    
    for idx, (brand, brand_data) in enumerate(comparison_data.items()):
        if country in brand_data:
            data = brand_data[country]
            
            if data['timeline'] and 'interest_over_time' in data['timeline']:
                timeline_data = data['timeline']['interest_over_time'].get('timeline_data', [])
                
                if timeline_data:
                    dates = [item['date'] for item in timeline_data]
                    values = [item.get('values', [{}])[0].get('value', 0) for item in timeline_data]
                    
                    # Color único por marca
                    color = colors[idx % len(colors)]
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=values,
                        mode='lines',
                        name=brand,
                        line=dict(color=color, width=3),
                        hovertemplate=f'<b>{brand}</b><br>%{{x}}<br>Interés: %{{y}}/100<extra></extra>'
                    ))
    
    fig.update_layout(
        title=dict(
            text=f"📊 Comparación Temporal - {COUNTRIES[country]['flag']} {COUNTRIES[country]['name']}",
            font=dict(size=20, color='#1d1d1f', family='Inter')
        ),
        xaxis=dict(
            title="Fecha",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title="Interés (0-100)",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            range=[0, 100]
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, -apple-system, sans-serif'),
        height=450,
        margin=dict(l=60, r=40, t=80, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        )
    )
    
    return fig


def create_region_map(region_data, country_name):
    """
    Crea mapa de calor de interés por región.
    """
    if not region_data or 'interest_by_region' not in region_data:
        return None
    
    regions = region_data['interest_by_region']
    
    # Ordenar por valor
    sorted_regions = sorted(regions, key=lambda x: x.get('extracted_value', 0), reverse=True)
    
    # Top 15 regiones
    top_regions = sorted_regions[:15]
    
    locations = [r['location'] for r in top_regions]
    values = [r.get('extracted_value', 0) for r in top_regions]
    
    fig = go.Figure(data=[
        go.Bar(
            y=locations,
            x=values,
            orientation='h',
            marker=dict(
                color=values,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Interés")
            ),
            text=[f"{v}/100" for v in values],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Interés: %{x}/100<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text=f"📍 Interés por Región - {country_name}",
            font=dict(size=18, color='#1d1d1f', family='Inter')
        ),
        xaxis=dict(title="Interés (0-100)", range=[0, 100]),
        yaxis=dict(title=""),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter'),
        height=500,
        margin=dict(l=150, r=40, t=60, b=60)
    )
    
    return fig


def create_trend_chart(dates, values, brand_name):
    fig = go.Figure()
    
    # SPRINT 4: Calcular tendencia para tooltips mejorados
    trends = []
    for i in range(len(values)):
        if i > 0:
            change = ((values[i] - values[i-1]) / values[i-1] * 100) if values[i-1] != 0 else 0
            trends.append(change)
        else:
            trends.append(0)
    
    # Crear tooltips personalizados
    hover_texts = []
    for i, (date, value, trend) in enumerate(zip(dates, values, trends)):
        # Emoji de tendencia
        trend_emoji = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
        trend_sign = "+" if trend > 0 else ""
        
        tooltip = f"""<b>{brand_name}</b><br>
━━━━━━━━━━━━━━━<br>
<b>Fecha:</b> {date}<br>
<b>Interés:</b> {value}/100<br>
<b>Cambio:</b> {trend_emoji} {trend_sign}{trend:.1f}%<br>
<extra></extra>"""
        hover_texts.append(tooltip)
    
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode='lines',
        name=brand_name,
        line=dict(color='#FF6B00', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 0, 0.08)',
        text=hover_texts,
        hovertemplate='%{text}'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        font=dict(family='Inter', color='#1d1d1f', size=12),
        xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.05)', title=None, color='#6e6e73'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.05)', title=None, 
                  range=[0, max(values) * 1.1] if values else [0, 100], color='#6e6e73'),
        hovermode='x unified',
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        hoverlabel=dict(
            bgcolor='rgba(29, 29, 31, 0.95)',
            font_color='white',
            font_size=13,
            font_family='Inter, -apple-system, sans-serif',
            bordercolor='rgba(255, 255, 255, 0.1)'
        )
    )
    
    return fig


def create_sparkline(values, color='#007AFF'):
    """
    Crea un mini gráfico sparkline estilo Glimpse.
    Para mostrar tendencias relacionadas.
    """
    if not values or len(values) < 2:
        # Si no hay datos, devolver gráfico plano
        values = [50, 50, 50, 50, 50]
    
    fig = go.Figure()
    
    # FIX: Convertir HEX a RGBA de forma clara
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    fillcolor = f'rgba({r}, {g}, {b}, 0.15)'
    
    fig.add_trace(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=2, shape='spline'),
        fill='tozeroy',
        fillcolor=fillcolor,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        height=60,
        width=120,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(visible=False, showgrid=False, range=[0, max(values) * 1.1] if values else [0, 100]),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode=False
    )
    
    return fig


def create_bubble_chart(topics_data, max_topics=30):
    """
    Crea un bubble chart interactivo de temas relacionados.
    Estilo Glimpse - Mapa de temas.
    """
    if not topics_data or 'related_topics' not in topics_data:
        return None
    
    # Obtener topics (top y rising combinados)
    top_topics = topics_data.get('related_topics', {}).get('top', [])[:max_topics]
    rising_topics = topics_data.get('related_topics', {}).get('rising', [])[:10]
    
    # Combinar y eliminar duplicados
    all_topics = []
    seen_titles = set()
    
    # Primero rising (más importantes)
    for topic in rising_topics:
        title = topic.get('topic', {}).get('title', '')
        if title and title not in seen_titles:
            all_topics.append({
                'title': title,
                'type': topic.get('topic', {}).get('type', 'Other'),
                'value': topic.get('value', 0),
                'is_rising': True
            })
            seen_titles.add(title)
    
    # Luego top
    for topic in top_topics:
        title = topic.get('topic', {}).get('title', '')
        if title and title not in seen_titles:
            all_topics.append({
                'title': title,
                'type': topic.get('topic', {}).get('type', 'Other'),
                'value': topic.get('value', 0),
                'is_rising': False
            })
            seen_titles.add(title)
    
    if len(all_topics) < 3:
        return None
    
    # Limitar a max_topics
    all_topics = all_topics[:max_topics]
    
    # Preparar datos para el gráfico
    titles = [t['title'] for t in all_topics]
    values = [t['value'] if isinstance(t['value'], (int, float)) else 100 for t in all_topics]
    types = [t['type'] for t in all_topics]
    is_rising = [t['is_rising'] for t in all_topics]
    
    # Generar posiciones usando algoritmo de empaquetado circular
    import math
    import numpy as np
    
    n = len(titles)
    
    # Usar distribución en espiral
    positions = []
    golden_angle = math.pi * (3 - math.sqrt(5))  # Ángulo dorado
    
    for i in range(n):
        # Radio crece con raíz cuadrada del índice
        radius = 15 * math.sqrt(i + 1)
        # Ángulo usando proporción áurea
        angle = i * golden_angle
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        positions.append((x, y))
    
    x_coords = [p[0] for p in positions]
    y_coords = [p[1] for p in positions]
    
    # Mapeo de tipos a colores
    type_colors = {
        'Search term': '#007AFF',
        'Topic': '#34C759',
        'Brand': '#FF9500',
        'Product': '#FF3B30',
        'Category': '#5856D6',
        'Other': '#8E8E93'
    }
    
    colors = [type_colors.get(t, '#8E8E93') for t in types]
    
    # Normalizar tamaños (entre 20 y 80)
    max_val = max(values) if values else 1
    min_val = min(values) if values else 0
    
    if max_val == min_val:
        sizes = [50] * len(values)
    else:
        sizes = [20 + (60 * (v - min_val) / (max_val - min_val)) for v in values]
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir burbujas
    for i in range(len(titles)):
        # Determinar si es rising
        marker_symbol = 'circle' if not is_rising[i] else 'star'
        border_width = 3 if is_rising[i] else 1
        
        fig.add_trace(go.Scatter(
            x=[x_coords[i]],
            y=[y_coords[i]],
            mode='markers+text',
            marker=dict(
                size=sizes[i],
                color=colors[i],
                opacity=0.8 if not is_rising[i] else 1,
                line=dict(
                    width=border_width,
                    color='white' if not is_rising[i] else '#FFD700'
                ),
                symbol=marker_symbol
            ),
            text=titles[i],
            textposition='middle center',
            textfont=dict(
                size=min(10 + sizes[i] / 8, 14),
                color='white',
                family='Inter, -apple-system, sans-serif'
            ),
            # SPRINT 4: Tooltip mejorado
            hovertemplate=f"""<b>{titles[i]}</b><br>
━━━━━━━━━━━━━━━<br>
<b>Tipo:</b> {types[i]}<br>
<b>Valor:</b> {values[i] if isinstance(values[i], int) else 'Breakout'}<br>
<b>Estado:</b> {"⭐ RISING" if is_rising[i] else "📊 Top"}<br>
<extra></extra>""",
            showlegend=False
        ))
    
    # Layout
    fig.update_layout(
        title={
            'text': '🫧 Mapa de Temas Relacionados',
            'font': {'size': 20, 'color': '#1d1d1f', 'family': 'Inter'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            range=[min(x_coords) - 50, max(x_coords) + 50]
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            range=[min(y_coords) - 50, max(y_coords) + 50],
            scaleanchor='x',
            scaleratio=1
        ),
        height=600,
        plot_bgcolor='rgba(255, 255, 255, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0)',
        hovermode='closest',
        margin=dict(l=20, r=20, t=60, b=20),
        # SPRINT 4: Hoverlabel mejorado
        hoverlabel=dict(
            bgcolor='rgba(29, 29, 31, 0.95)',
            font_color='white',
            font_size=13,
            font_family='Inter, -apple-system, sans-serif',
            bordercolor='rgba(255, 255, 255, 0.1)'
        )
    )
    
    return fig


def export_to_csv(data, brand_name):
    """Exporta datos a CSV"""
    # Preparar datos para export
    export_data = []
    
    # Añadir métricas
    if 'month_change' in data and data['month_change'] is not None:
        export_data.append({
            'Métrica': 'Cambio Mensual',
            'Valor': f"{data['month_change']:.1f}%",
            'Tipo': 'Métrica'
        })
    
    if 'quarter_change' in data and data['quarter_change'] is not None:
        export_data.append({
            'Métrica': 'Cambio Trimestral',
            'Valor': f"{data['quarter_change']:.1f}%",
            'Tipo': 'Métrica'
        })
    
    if 'year_change' in data and data['year_change'] is not None:
        export_data.append({
            'Métrica': 'Cambio Anual',
            'Valor': f"{data['year_change']:.1f}%",
            'Tipo': 'Métrica'
        })
    
    # Añadir queries si existen
    if data.get('queries') and 'related_queries' in data['queries']:
        if 'top' in data['queries']['related_queries']:
            for q in data['queries']['related_queries']['top'][:20]:
                export_data.append({
                    'Métrica': q.get('query', ''),
                    'Valor': q.get('value', 0),
                    'Tipo': 'Query TOP'
                })
    
    df = pd.DataFrame(export_data)
    csv = df.to_csv(index=False)
    return csv


def export_to_excel(data, brand_name):
    """Exporta datos a Excel con formato"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Métricas
        metrics_data = []
        if 'month_change' in data and data['month_change'] is not None:
            metrics_data.append({'Métrica': 'Cambio Mensual', 'Valor': data['month_change']})
        if 'quarter_change' in data and data['quarter_change'] is not None:
            metrics_data.append({'Métrica': 'Cambio Trimestral', 'Valor': data['quarter_change']})
        if 'year_change' in data and data['year_change'] is not None:
            metrics_data.append({'Métrica': 'Cambio Anual', 'Valor': data['year_change']})
        if 'avg_value' in data and data['avg_value'] is not None:
            metrics_data.append({'Métrica': 'Promedio 5 años', 'Valor': data['avg_value']})
        
        if metrics_data:
            pd.DataFrame(metrics_data).to_excel(writer, sheet_name='Métricas', index=False)
        
        # Sheet 2: Queries
        if data.get('queries') and 'related_queries' in data['queries']:
            queries_data = []
            if 'top' in data['queries']['related_queries']:
                for q in data['queries']['related_queries']['top']:
                    queries_data.append({
                        'Query': q.get('query', ''),
                        'Volumen': q.get('value', 0),
                        'Tipo': 'TOP'
                    })
            
            if 'rising' in data['queries']['related_queries']:
                for q in data['queries']['related_queries']['rising']:
                    queries_data.append({
                        'Query': q.get('query', ''),
                        'Volumen': q.get('value', 'Breakout'),
                        'Tipo': 'RISING'
                    })
            
            if queries_data:
                pd.DataFrame(queries_data).to_excel(writer, sheet_name='Queries', index=False)
    
    return output.getvalue()


def export_to_json(data, brand_name):
    """Exporta datos a JSON"""
    export_data = {
        'brand': brand_name,
        'export_date': datetime.now().isoformat(),
        'metrics': {
            'month_change': data.get('month_change'),
            'quarter_change': data.get('quarter_change'),
            'year_change': data.get('year_change'),
            'avg_value': data.get('avg_value')
        },
        'queries': data.get('queries', {}),
        'topics': data.get('topics', {})
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def export_to_pdf(data, brand_name, country_name):
    """
    Exporta datos a PDF profesional con reportlab.
    
    Args:
        data (dict): Datos del análisis
        brand_name (str): Nombre de la marca
        country_name (str): Nombre del país
    
    Returns:
        bytes: PDF generado
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Contenedor de elementos
    story = []
    styles = getSampleStyleSheet()
    
    # ===== HEADER =====
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1d1d1f'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#6e6e73'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    title = Paragraph("📊 TREND HUNTER PRO", title_style)
    story.append(title)
    
    subtitle = Paragraph(
        f"Reporte de Tendencias: <b>{brand_name.upper()}</b><br/>"
        f"País: {country_name}<br/>"
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        subtitle_style
    )
    story.append(subtitle)
    story.append(Spacer(1, 0.3*inch))
    
    # ===== LÍNEA SEPARADORA =====
    line_data = [['', '']]
    line_table = Table(line_data, colWidths=[6.5*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#007AFF')),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ===== MÉTRICAS PRINCIPALES =====
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1d1d1f'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("MÉTRICAS CLAVE", section_style))
    
    metrics_data = [
        ['Métrica', 'Valor'],
    ]
    
    if data.get('month_change') is not None:
        metrics_data.append(['Cambio Mensual', f"{data['month_change']:+.1f}%"])
    if data.get('quarter_change') is not None:
        metrics_data.append(['Cambio Trimestral', f"{data['quarter_change']:+.1f}%"])
    if data.get('year_change') is not None:
        metrics_data.append(['Cambio Anual', f"{data['year_change']:+.1f}%"])
    if data.get('avg_value') is not None:
        metrics_data.append(['Promedio 5 años', f"{data['avg_value']:.1f}"])
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e5e7')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ===== ESTACIONALIDAD =====
    if data.get('timeline'):
        seasonality = calculate_seasonality(data['timeline'])
        if seasonality and seasonality['seasonality_score'] >= 20:
            story.append(Paragraph("ESTACIONALIDAD", section_style))
            
            badge_text, _ = get_seasonality_badge(seasonality['seasonality_score'])
            
            seasonality_info = Paragraph(
                f"<b>Estado:</b> {badge_text}<br/>"
                f"<b>Score:</b> {seasonality['seasonality_score']:.1f}/100<br/>"
                f"<b>Promedio anual:</b> {seasonality['overall_avg']:.1f}",
                styles['Normal']
            )
            story.append(seasonality_info)
            
            # Detectar patrones
            patterns = detect_seasonal_patterns(
                seasonality['monthly_avg'],
                seasonality['overall_avg']
            )
            
            if patterns:
                story.append(Spacer(1, 0.1*inch))
                patterns_text = "<b>Patrones detectados:</b><br/>"
                for i, p in enumerate(patterns[:3], 1):
                    patterns_text += f"{i}. {p['emoji']} {p['name']} ({', '.join(p['months'])}): +{p['increase']:.0f}%<br/>"
                
                story.append(Paragraph(patterns_text, styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
    
    # ===== TOP QUERIES =====
    if data.get('queries') and 'related_queries' in data['queries']:
        story.append(Paragraph("TOP BÚSQUEDAS RELACIONADAS", section_style))
        
        queries_data_table = [['#', 'Query', 'Volumen']]
        
        top_queries = data['queries']['related_queries'].get('top', [])[:20]
        
        for idx, q in enumerate(top_queries, 1):
            query_text = q.get('query', '')
            value = q.get('value', 0)
            
            # Truncar queries muy largas
            if len(query_text) > 50:
                query_text = query_text[:47] + '...'
            
            # Formatear valor
            if value >= 1000:
                value_str = f"{value/1000:.1f}K"
            else:
                value_str = str(value)
            
            queries_data_table.append([str(idx), query_text, value_str])
        
        queries_table = Table(queries_data_table, colWidths=[0.5*inch, 4*inch, 1.5*inch])
        queries_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34C759')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e5e7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f7')]),
        ]))
        
        story.append(queries_table)
        story.append(Spacer(1, 0.3*inch))
    
    # ===== TENDENCIAS RELACIONADAS =====
    if data.get('topics') and 'related_topics' in data['topics']:
        story.append(Paragraph("TENDENCIAS RELACIONADAS", section_style))
        
        rising_topics = data['topics']['related_topics'].get('rising', [])[:10]
        
        if rising_topics:
            topics_data_table = [['Topic', 'Tipo', 'Crecimiento']]
            
            for topic in rising_topics:
                title = topic.get('topic', {}).get('title', 'N/A')
                topic_type = topic.get('topic', {}).get('type', 'N/A')
                value = topic.get('value', 0)
                
                # Truncar títulos largos
                if len(title) > 40:
                    title = title[:37] + '...'
                
                # Formatear valor
                if isinstance(value, str) and 'Breakout' in value:
                    value_str = 'Breakout'
                elif isinstance(value, (int, float)):
                    value_str = f'+{value}%'
                else:
                    value_str = str(value)
                
                topics_data_table.append([title, topic_type, value_str])
            
            topics_table = Table(topics_data_table, colWidths=[3*inch, 2*inch, 1*inch])
            topics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9500')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e5e7')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f7')]),
            ]))
            
            story.append(topics_table)
    
    # ===== FOOTER =====
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#8e8e93'),
        alignment=TA_CENTER
    )
    
    footer = Paragraph(
        f"Generado por Abra | {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>"
        "Powered by Google Trends API",
        footer_style
    )
    story.append(footer)
    
    # Construir PDF
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


# SECURITY: Asegurar escapar user input con html.escape()
def display_queries_filtered(queries_data, categories, threshold, query_type="all", sort_by="volume", page=1):
    """
    Muestra queries filtradas con barras visuales, paginación y ordenamiento.
    SPRINT 1 - Estilo Glimpse
    """
    if not queries_data:
        st.info("No hay datos de queries disponibles")
        return
    
    all_queries = []
    
    # TOP queries
    if 'top' in queries_data.get('related_queries', {}):
        for item in queries_data['related_queries']['top']:
            query = item.get('query', '')
            value = item.get('value', 0)
            score, matches, cat = calculate_relevance(query, categories)
            qtype = classify_query_type(query)
            
            if score >= threshold:
                if query_type == "all" or query_type in qtype:
                    badge, badge_class = get_relevance_badge(score)
                    all_queries.append({
                        'query': query,
                        'type': qtype,
                        'value': value,
                        'numeric_value': value if isinstance(value, (int, float)) else 0,
                        'relevance': score,
                        'badge': badge,
                        'category': cat,
                        'keywords': matches[:3]
                    })
    
    # RISING queries
    if 'rising' in queries_data.get('related_queries', {}):
        for item in queries_data['related_queries']['rising']:
            query = item.get('query', '')
            value = item.get('value', 'Breakout')
            score, matches, cat = calculate_relevance(query, categories)
            qtype = classify_query_type(query)
            
            if score >= threshold:
                if query_type == "all" or query_type in qtype:
                    badge, badge_class = get_relevance_badge(score)
                    # Para rising, si es numérico agregamos +
                    display_value = f'+{value}%' if isinstance(value, int) else value
                    all_queries.append({
                        'query': query,
                        'type': qtype,
                        'value': display_value,
                        'numeric_value': value if isinstance(value, (int, float)) else 10000,  # Breakout = high value
                        'relevance': score,
                        'badge': badge,
                        'category': cat,
                        'keywords': matches[:3]
                    })
    
    if not all_queries:
        # SPRINT 4: Empty state mejorado
        render_low_relevance_state(threshold)
        return
    
    # Ordenar queries PRIMERO (antes de mostrar contador)
    # Mapeo de opciones a valores
    sort_mapping = {
        "Volumen de búsqueda": "volume",
        "Crecimiento": "growth",
        "Alfabético": "alphabetical"
    }
    
    # Determinar sort_by inicial
    sort_by_value = sort_by if sort_by in sort_mapping.values() else "volume"
    
    # Ordenar queries
    sorted_queries = sort_queries(all_queries, sort_by_value)
    
    # Paginar ANTES de mostrar contador
    paginated = paginate_data(sorted_queries, page_size=20, page=page)
    
    # Header con contador y ordenar
    col_sort, col_count = st.columns([3, 1])
    with col_sort:
        st.markdown(f'<div class="sort-container">', unsafe_allow_html=True)
        
        sort_option = st.selectbox(
            "Ordenar por",
            ["Volumen de búsqueda", "Crecimiento", "Alfabético"],
            key=f"sort_{query_type}",
            label_visibility="collapsed"
        )
        
        # CONECTAR: Convertir opción a valor para sort_queries
        sort_by_value = sort_mapping[sort_option]
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_count:
        st.markdown(
            f'<div class="results-counter">{paginated["total_items"]} resultados</div>',
            unsafe_allow_html=True
        )
    
    # Obtener tendencias para top 5 queries (solo primera página para optimizar)
    query_trends = {}
    if paginated['current_page'] == 1:
        with st.spinner("📈 Obteniendo tendencias..."):
            for query_data in paginated['data'][:5]:  # Solo top 5
                query_text = query_data['query']
                # Obtener tendencia de esta query
                trend_values = get_query_trend(query_text, geo="ES", timeframe="today 12-m")
                if trend_values:
                    query_trends[query_text] = trend_values
                time.sleep(0.3)  # Pequeño delay entre llamadas
    
    # Renderizar queries con barras y sparklines
    max_value = max([q['numeric_value'] for q in paginated['data']], default=1)
    max_value = max(max_value, 1)  # FIX: Asegurar mínimo de 1 para evitar división por 0
    
    queries_html = ""
    for idx, query in enumerate(paginated['data'], start=paginated['start_idx']):
        query_text = query['query']
        trend_values = query_trends.get(query_text, None)  # Obtener tendencia si está disponible
        
        queries_html += render_query_with_bar(
            query_text,
            query['numeric_value'],
            max_value,
            idx,
            query_type=query.get('type', 'Query'),
            relevance=query.get('relevance', 0),
            trend_values=trend_values  # Pasar tendencia
        )
    
    st.markdown(queries_html, unsafe_allow_html=True)
    
    # Paginación
    if paginated['total_pages'] > 1:
        st.markdown('<div class="pagination">', unsafe_allow_html=True)
        
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if paginated['current_page'] > 1:
                if st.button("← Anterior", key=f"prev_{query_type}"):
                    st.session_state[f'page_{query_type}'] = paginated['current_page'] - 1
                    st.rerun()
        
        with col_info:
            st.markdown(
                f'<div class="pagination-info">Página {paginated["current_page"]} de {paginated["total_pages"]}</div>',
                unsafe_allow_html=True
            )
        
        with col_next:
            if paginated['current_page'] < paginated['total_pages']:
                if st.button("Siguiente →", key=f"next_{query_type}"):
                    st.session_state[f'page_{query_type}'] = paginated['current_page'] + 1
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

