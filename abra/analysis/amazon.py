"""
Análisis de datos de Amazon
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



def get_amazon_products(brand, country="es"):
    """
    API: Amazon Organic Results via SerpAPI
    Obtiene productos de Amazon para una marca.
    
    Args:
        brand: Nombre de la marca
        country: es, pt, fr, it, de
        
    Returns:
        dict: Datos de productos Amazon o None
    """
    url = "https://serpapi.com/search.json"
    
    # Mapeo de países a dominios Amazon
    amazon_domains = {
        "ES": "amazon.es",
        "PT": "amazon.es",  # Portugal usa .es
        "FR": "amazon.fr",
        "IT": "amazon.it",
        "DE": "amazon.de"
    }
    
    params = {
        "engine": "amazon",
        "amazon_domain": amazon_domains.get(country.upper(), "amazon.es"),
        "q": brand,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None


def analyze_amazon_data(amazon_data, brand):
    """
    Analiza datos de Amazon para extraer insights.
    
    Returns:
        dict: {
            'total_products': int,
            'avg_rating': float,
            'total_reviews': int,
            'price_range': (min, max),
            'prime_percentage': float,
            'top_products': list
        }
    """
    if not amazon_data or 'organic_results' not in amazon_data:
        return None
    
    products = amazon_data['organic_results']
    
    if not products:
        return None
    
    # Métricas
    total_products = len(products)
    ratings = []
    reviews = []
    prices = []
    prime_count = 0
    
    for product in products:
        # Rating
        if 'rating' in product:
            try:
                ratings.append(float(product['rating']))
            except:
                pass
        
        # Reviews
        if 'reviews_count' in product:
            try:
                reviews.append(int(product['reviews_count']))
            except:
                pass
        
        # Price
        if 'price' in product and product['price']:
            try:
                price_str = product['price'].replace('€', '').replace(',', '.').strip()
                prices.append(float(price_str))
            except:
                pass
        
        # Prime
        if product.get('is_prime', False):
            prime_count += 1
    
    # Calcular promedios
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    total_reviews_count = sum(reviews) if reviews else 0
    price_range = (min(prices), max(prices)) if prices else (0, 0)
    prime_percentage = (prime_count / total_products * 100) if total_products > 0 else 0
    
    # Top 5 productos por reviews
    products_with_reviews = [p for p in products if 'reviews_count' in p]
    top_products = sorted(
        products_with_reviews,
        key=lambda x: int(x.get('reviews_count', 0)),
        reverse=True
    )[:5]
    
    return {
        'total_products': total_products,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews_count,
        'price_range': price_range,
        'prime_percentage': prime_percentage,
        'top_products': top_products,
        'related_searches': amazon_data.get('related_searches', [])
    }


def compare_trends_amazon(trends_change, amazon_products_count, historical_count=None):
    """
    Compara tendencias Google con disponibilidad Amazon.
    
    Returns:
        dict: {
            'status': 'aligned' | 'opportunity' | 'warning',
            'message': str,
            'recommendation': str
        }
    """
    # Si no hay histórico, usar heurística simple
    if historical_count is None:
        if trends_change > 30 and amazon_products_count > 20:
            return {
                'status': 'aligned',
                'icon': '✅',
                'message': f'Tendencia alcista (+{trends_change:.0f}%) respaldada por amplia oferta ({amazon_products_count} productos)',
                'recommendation': 'Aumentar stock - Alta demanda con buena disponibilidad'
            }
        elif trends_change > 30 and amazon_products_count < 10:
            return {
                'status': 'opportunity',
                'icon': '🎯',
                'message': f'Alta demanda (+{trends_change:.0f}%) pero poca oferta ({amazon_products_count} productos)',
                'recommendation': 'OPORTUNIDAD: Baja competencia Amazon - Aumentar catálogo'
            }
        elif trends_change < -20:
            return {
                'status': 'warning',
                'icon': '⚠️',
                'message': f'Demanda bajando ({trends_change:.0f}%) con {amazon_products_count} productos',
                'recommendation': 'Reducir stock - Tendencia descendente'
            }
        else:
            return {
                'status': 'neutral',
                'icon': 'ℹ️',
                'message': f'Tendencia estable con {amazon_products_count} productos disponibles',
                'recommendation': 'Mantener estrategia actual'
            }
    else:
        # Con histórico
        product_change = ((amazon_products_count - historical_count) / historical_count * 100) if historical_count > 0 else 0
        
        if trends_change > 20 and product_change > 15:
            return {
                'status': 'aligned',
                'icon': '✅',
                'message': f'Demanda +{trends_change:.0f}% y oferta +{product_change:.0f}% - Mercado creciendo',
                'recommendation': 'Aumentar stock agresivamente'
            }
        elif trends_change > 20 and product_change < 5:
            return {
                'status': 'opportunity',
                'icon': '🎯',
                'message': f'Demanda +{trends_change:.0f}% pero oferta estancada (+{product_change:.0f}%)',
                'recommendation': 'OPORTUNIDAD: Aumentar antes que competencia'
            }
        else:
            return {
                'status': 'neutral',
                'icon': 'ℹ️',
                'message': f'Demanda {trends_change:+.0f}%, Oferta {product_change:+.0f}%',
                'recommendation': 'Monitorear evolución'
            }


def render_amazon_insights(amazon_analysis, trends_insight):
    """
    Renderiza el panel de insights Amazon vs Google Trends.
    """
    if not amazon_analysis:
        return """
        <div style="background: #f5f5f7; padding: 1rem; border-radius: 12px;">
            <p style="color: #6e6e73; margin: 0;">No hay datos de Amazon disponibles</p>
        </div>
        """
    
    icon = trends_insight.get('icon', 'ℹ️')
    status = trends_insight.get('status', 'neutral')
    message = trends_insight.get('message', '')
    recommendation = trends_insight.get('recommendation', '')
    
    # Color según status
    status_colors = {
        'aligned': '#34C759',
        'opportunity': '#FF9500',
        'warning': '#FF3B30',
        'neutral': '#007AFF'
    }
    
    color = status_colors.get(status, '#007AFF')
    
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
                <h4 style="margin: 0 0 0.5rem 0; color: #1d1d1f;">Amazon vs Google Trends</h4>
                <p style="color: #1d1d1f; margin: 0 0 0.5rem 0; font-weight: 500;">{message}</p>
                <p style="
                    background: {color}25;
                    padding: 0.75rem;
                    border-radius: 8px;
                    margin: 0;
                    color: #1d1d1f;
                    font-weight: 600;
                ">💡 {recommendation}</p>
            </div>
        </div>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid {color}30;
        ">
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Productos Amazon</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {amazon_analysis['total_products']}
                </div>
            </div>
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Rating Promedio</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {amazon_analysis['avg_rating']:.1f} ⭐
                </div>
            </div>
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">% con Prime</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {amazon_analysis['prime_percentage']:.0f}%
                </div>
            </div>
            <div>
                <div style="color: #6e6e73; font-size: 0.85rem;">Total Reviews</div>
                <div style="color: #1d1d1f; font-size: 1.5rem; font-weight: 700;">
                    {amazon_analysis['total_reviews']:,}
                </div>
            </div>
        </div>
    </div>
    """
    
    return html

