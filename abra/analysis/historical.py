"""
Gestión de histórico y evolución
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import json
import html

import os



def save_analysis_to_history(brand, country, channel, results, filename="analysis_history.json"):
    """
    Guarda un análisis en el histórico JSON.
    
    Args:
        brand (str): Nombre de la marca
        country (str): Código del país
        channel (str): Canal usado
        results (dict): Resultados del análisis
        filename (str): Archivo JSON de histórico
    """
    import os
    from datetime import datetime
    
    # Estructura del registro
    record = {
        "timestamp": datetime.now().isoformat(),
        "brand": brand,
        "country": country,
        "country_name": COUNTRIES[country]["name"],
        "channel": channel,
        "channel_name": CHANNELS[channel]["name"],
        "metrics": {
            "avg_value": results.get("avg_value"),
            "month_change": results.get("month_change"),
            "quarter_change": results.get("quarter_change"),
            "year_change": results.get("year_change")
        }
    }
    
    # Cargar histórico existente
    history = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Añadir nuevo registro
    history.append(record)
    
    # Limitar a últimos 100 registros
    if len(history) > 100:
        history = history[-100:]
    
    # Guardar
    try:
        with open(filename, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except:
        return False


def load_analysis_history(filename="analysis_history.json"):
    """
    Carga el histórico de análisis.
    
    Returns:
        list: Lista de registros históricos
    """
    import os
    
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return []


def get_brand_evolution(brand, channel="web", filename="analysis_history.json"):
    """
    Obtiene la evolución histórica de una marca.
    
    Args:
        brand (str): Nombre de la marca
        channel (str): Canal a filtrar
        filename (str): Archivo de histórico
    
    Returns:
        list: Registros filtrados y ordenados por fecha
    """
    history = load_analysis_history(filename)
    
    # Filtrar por marca y canal
    filtered = [
        record for record in history 
        if record.get("brand", "").lower() == brand.lower() 
        and record.get("channel", "") == channel
    ]
    
    # Ordenar por timestamp
    filtered.sort(key=lambda x: x.get("timestamp", ""))
    
    return filtered


def create_evolution_chart(evolution_data, metric="avg_value"):
    """
    Crea gráfico de evolución histórica.
    
    Args:
        evolution_data (list): Datos de evolución
        metric (str): Métrica a graficar
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de evolución
    """
    if not evolution_data:
        return None
    
    fig = go.Figure()
    
    # Extraer datos
    timestamps = [record["timestamp"][:10] for record in evolution_data]  # Solo fecha
    values = [record["metrics"].get(metric, 0) for record in evolution_data]
    
    # Gráfico de línea
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=values,
        mode='lines+markers',
        name=metric.replace("_", " ").title(),
        line=dict(color='#FF6B00', width=3),
        marker=dict(size=8, color='#FF6B00'),
        hovertemplate='<b>%{x}</b><br>Valor: %{y:.1f}<extra></extra>'
    ))
    
    metric_names = {
        "avg_value": "Promedio 5 Años",
        "month_change": "Cambio Mensual (%)",
        "quarter_change": "Cambio Trimestral (%)",
        "year_change": "Cambio Anual (%)"
    }
    
    fig.update_layout(
        title=dict(
            text=f"📈 Evolución: {metric_names.get(metric, metric)}",
            font=dict(size=18, color='#1d1d1f', family='Inter')
        ),
        xaxis=dict(
            title="Fecha de Análisis",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title=metric_names.get(metric, metric),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        hovermode='x',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, -apple-system, sans-serif'),
        height=350,
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig


def compare_with_history(brand, country, channel, current_data, filename="analysis_history.json"):
    """
    Compara análisis actual con histórico para detectar cambios.
    
    Args:
        brand (str): Marca
        country (str): País
        channel (str): Canal
        current_data (dict): Datos actuales
        filename (str): Archivo de histórico
    
    Returns:
        dict: Comparación con último análisis
    """
    history = load_analysis_history(filename)
    
    # Filtrar por marca, país y canal
    relevant = [
        r for r in history
        if r.get('brand', '').lower() == brand.lower()
        and r.get('country', '') == country
        and r.get('channel', '') == channel
    ]
    
    if not relevant:
        return None
    
    # Obtener último registro (más reciente)
    last_record = sorted(relevant, key=lambda x: x.get('timestamp', ''))[-1]
    
    # Calcular diferencias
    comparison = {
        'last_date': last_record['timestamp'][:10],
        'changes': {}
    }
    
    for metric in ['avg_value', 'month_change', 'quarter_change', 'year_change']:
        current_val = current_data.get(metric, 0)
        last_val = last_record['metrics'].get(metric, 0)
        
        if current_val is not None and last_val is not None:
            diff = current_val - last_val
            comparison['changes'][metric] = {
                'current': current_val,
                'last': last_val,
                'diff': diff,
                'diff_pct': (diff / last_val * 100) if last_val != 0 else 0
            }
    
    return comparison


def create_download_button(data, filename, mime_type, button_text):
    """Crea un botón de descarga con el contenido"""
    b64 = b64encode(data.encode() if isinstance(data, str) else data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="text-decoration: none;">' \
           f'<button style="background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%); ' \
           f'color: white; border: none; border-radius: 8px; padding: 0.5rem 1rem; ' \
           f'font-weight: 600; cursor: pointer; font-size: 0.9rem; ' \
           f'transition: all 0.3s ease;">{button_text}</button></a>'
    return href

