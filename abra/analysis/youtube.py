"""
Análisis de datos de YouTube
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import json
import html

import requests
from abra.config.secrets import SERPAPI_KEY



def get_youtube_videos(query, country="ES", max_results=50):
    """
    Obtiene videos de YouTube para análisis de tendencias.
    
    Args:
        query: Búsqueda (marca o producto específico)
        country: ES, PT, FR, IT, DE
        max_results: Cantidad de resultados
    """
    url = "https://serpapi.com/search.json"
    
    params = {
        "engine": "youtube",
        "search_query": query,
        "gl": country.lower(),
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def parse_youtube_date(date_str):
    """
    Parsea fechas de YouTube a días.
    """
    import re
    
    if not date_str:
        return 999
    
    date_str = date_str.lower()
    
    if 'hour' in date_str or 'hora' in date_str:
        return 0
    
    if 'day' in date_str or 'día' in date_str:
        match = re.search(r'(\d+)', date_str)
        if match:
            return int(match.group(1))
        return 1
    
    if 'week' in date_str or 'semana' in date_str:
        match = re.search(r'(\d+)', date_str)
        if match:
            return int(match.group(1)) * 7
        return 7
    
    if 'month' in date_str or 'mes' in date_str:
        match = re.search(r'(\d+)', date_str)
        if match:
            return int(match.group(1)) * 30
        return 30
    
    if 'year' in date_str or 'año' in date_str:
        match = re.search(r'(\d+)', date_str)
        if match:
            return int(match.group(1)) * 365
        return 365
    
    if 'streamed' in date_str:
        return 0
    
    return 999


def analyze_youtube_trending(youtube_data, brand):
    """
    Analiza tendencias de contenido YouTube.
    """
    if not youtube_data or 'video_results' not in youtube_data:
        return None
    
    videos = youtube_data.get('video_results', [])
    
    if not videos:
        return None
    
    videos_7d = 0
    videos_30d = 0
    videos_90d = 0
    
    total_views = 0
    videos_with_views = 0
    
    channels_count = {}
    all_videos_info = []
    
    for video in videos:
        published = video.get('published_date', '')
        days_ago = parse_youtube_date(published)
        
        if days_ago <= 7:
            videos_7d += 1
        if days_ago <= 30:
            videos_30d += 1
        if days_ago <= 90:
            videos_90d += 1
        
        views = video.get('views', 0)
        if views:
            total_views += views
            videos_with_views += 1
        
        channel_name = video.get('channel', {}).get('name', 'Unknown')
        channels_count[channel_name] = channels_count.get(channel_name, 0) + 1
        
        all_videos_info.append({
            'title': video.get('title', ''),
            'link': video.get('link', ''),
            'channel': channel_name,
            'channel_verified': video.get('channel', {}).get('verified', False),
            'views': views,
            'published_date': published,
            'days_ago': days_ago,
            'length': video.get('length', ''),
            'thumbnail': video.get('thumbnail', {}).get('static', ''),
            'extensions': video.get('extensions', [])
        })
    
    top_channels = sorted(channels_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    top_videos = sorted(
        [v for v in all_videos_info if v['views'] > 0],
        key=lambda x: x['views'],
        reverse=True
    )[:10]
    
    avg_views = total_views / videos_with_views if videos_with_views > 0 else 0
    
    related_products = detect_products_in_titles([v['title'] for v in all_videos_info], brand)
    
    videos_4k = sum(1 for v in all_videos_info if '4K' in v.get('extensions', []))
    videos_new = sum(1 for v in all_videos_info if 'New' in v.get('extensions', []))
    verified_channels = sum(1 for v in all_videos_info if v.get('channel_verified', False))
    
    quality_indicators = {
        '4k_percentage': (videos_4k / len(videos) * 100) if videos else 0,
        'new_percentage': (videos_new / len(videos) * 100) if videos else 0,
        'verified_percentage': (verified_channels / len(videos) * 100) if videos else 0
    }
    
    return {
        'total_videos': len(videos),
        'by_period': {
            '7d': videos_7d,
            '30d': videos_30d,
            '90d': videos_90d
        },
        'top_videos': top_videos,
        'top_channels': top_channels,
        'related_products': related_products,
        'engagement_avg': avg_views,
        'quality_indicators': quality_indicators,
        'all_videos': all_videos_info
    }


def create_youtube_timeline_chart(youtube_analysis):
    """
    Gráfico temporal de videos por periodo.
    """
    if not youtube_analysis:
        return None
    
    periods = youtube_analysis['by_period']
    
    labels = ['Última\nSemana', 'Último\nMes', 'Últimos\n3 Meses']
    values = [periods['7d'], periods['30d'], periods['90d']]
    colors = ['#FF6B00', '#FF9500', '#FFBE00']
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            text=[f"{v} videos" for v in values],
            textposition='auto',
            marker=dict(
                color=colors,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{x}</b><br>%{y} videos<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="📊 Evolución Temporal de Contenido",
            font=dict(size=18, color='#1d1d1f', family='Inter')
        ),
        xaxis=dict(title=""),
        yaxis=dict(title="Videos Publicados"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter'),
        height=350,
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig


def render_youtube_insights(youtube_analysis, brand):
    """
    Panel principal YouTube Intelligence.
    """
    if not youtube_analysis:
        return """
        <div style="background: #f5f5f7; padding: 1rem; border-radius: 12px;">
            <p style="color: #6e6e73; margin: 0;">No hay datos de YouTube disponibles</p>
        </div>
        """
    
    total = youtube_analysis['total_videos']
    videos_7d = youtube_analysis['by_period']['7d']
    videos_30d = youtube_analysis['by_period']['30d']
    avg_views = youtube_analysis['engagement_avg']
    
    # Detectar tendencia
    growth_rate = ((videos_7d * 4) / videos_30d * 100 - 100) if videos_30d > 0 else 0
    
    if growth_rate > 50:
        status = 'hot'
        icon = '🔥'
        color = '#FF3B30'
        message = f'Contenido VIRAL: +{growth_rate:.0f}% crecimiento semanal'
    elif growth_rate > 20:
        status = 'trending'
        icon = '📈'
        color = '#FF9500'
        message = f'Tendencia POSITIVA: +{growth_rate:.0f}% crecimiento'
    elif growth_rate > 0:
        status = 'stable'
        icon = '✅'
        color = '#34C759'
        message = f'Contenido ESTABLE: +{growth_rate:.0f}% crecimiento'
    else:
        status = 'declining'
        icon = '📉'
        color = '#007AFF'
        message = f'Tendencia DESCENDENTE: {growth_rate:.0f}%'
    
    html = f"""
    <div style="
        background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
        border-left: 4px solid {color};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1rem;">
            <span style="font-size: 2rem;">{icon}</span>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1d1d1f;">YouTube Content Intelligence</h4>
                <p style="color: #1d1d1f; margin: 0; font-weight: 600; font-size: 1.1rem;">{message}</p>
            </div>
        </div>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid {color}30;
        ">
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Total Videos</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {total}
                </div>
            </div>
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Últimos 7 días</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {videos_7d}
                </div>
            </div>
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Últimos 30 días</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {videos_30d}
                </div>
            </div>
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Views Promedio</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {avg_views:,.0f}
                </div>
            </div>
        </div>
    </div>
    """
    
    return html

