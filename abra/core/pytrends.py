"""
Funciones para interactuar con Google Trends API
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import json
import html

from pytrends.request import TrendReq
from abra.config.secrets import SERPAPI_KEY



def get_interest_over_time(brand, geo="ES", gprop=""):
    """
    SPRINT 5: Añadido soporte multi-canal con parámetro gprop.
    BUGFIX: Añadido cache para optimizar performance.
    gprop: "" (web), "images", "news", "youtube", "froogle" (shopping)
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "TIMESERIES",
        "date": "today 5-y",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    # SPRINT 5: Añadir gprop si no es web search (default)
    if gprop:
        params["gprop"] = gprop
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)


def get_related_queries(brand, geo="ES", gprop=""):
    """
    Obtiene búsquedas relacionadas (TOP + RISING)
    SPRINT 5: Añadido gprop para multi-canal
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "RELATED_QUERIES",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    # SPRINT 5: Añadir gprop
    if gprop:
        params["gprop"] = gprop
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)


def get_related_topics(brand, geo="ES", gprop=""):
    """
    Obtiene temas relacionados (TOP + RISING)
    SPRINT 5: Añadido gprop para multi-canal
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "RELATED_TOPICS",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    # SPRINT 5: Añadir gprop
    if gprop:
        params["gprop"] = gprop
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def get_interest_by_region(brand, geo="ES", gprop=""):
    """
    API: Interest by Region (GEO_MAP_0)
    Obtiene el interés por región/provincia para una marca.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends",
        "q": brand,
        "data_type": "GEO_MAP_0",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    if gprop:
        params["gprop"] = gprop
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)


def get_compared_breakdown(brands_list, geo="ES", gprop=""):
    """
    API: Compared Breakdown by Region (GEO_MAP)
    Compara múltiples marcas por región.
    """
    url = "https://serpapi.com/search.json"
    
    # Unir marcas con coma
    q_param = ",".join(brands_list)
    
    params = {
        "engine": "google_trends",
        "q": q_param,
        "data_type": "GEO_MAP",
        "geo": geo,
        "api_key": SERPAPI_KEY
    }
    
    if gprop:
        params["gprop"] = gprop
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=1800, show_spinner=False)  # Cache 30 min (más fresco)


def get_related_news(brand):
    """
    API: News API
    Obtiene noticias relacionadas con la marca.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends_news",
        "q": brand,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=600, show_spinner=False)  # Cache 10 min (muy fresco)


def get_trending_now(geo="ES", hours=4, category_id=0):
    """
    API: Trending Now
    Obtiene tendencias del momento.
    
    Args:
        geo: País (ES, PT, etc)
        hours: Rango temporal (1, 4, 24)
        category_id: Categoría (0=todas)
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends_trending_now",
        "geo": geo,
        "hours": hours,
        "api_key": SERPAPI_KEY
    }
    
    if category_id:
        params["category_id"] = category_id
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)


def get_autocomplete(query):
    """
    API: Autocomplete
    Obtiene sugerencias de autocompletado.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends_autocomplete",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)


def get_query_trend(query, geo="ES", timeframe="today 12-m"):
    """
    Obtiene la tendencia temporal de una query específica.
    Usado para mostrar sparklines en cada query.
    
    Args:
        query (str): Query a analizar
        geo (str): País (ES, PT, FR, IT, DE)
        timeframe (str): Período (today 12-m para último año)
    
    Returns:
        list: Lista de valores de tendencia [v1, v2, v3, ...]
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_trends",
        "q": query,
        "geo": geo,
        "data_type": "TIMESERIES",
        "date": timeframe,
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'interest_over_time' in data:
                timeline_data = data['interest_over_time'].get('timeline_data', [])
                # Extraer solo los valores
                values = [item.get('values', [{}])[0].get('extracted_value', 0) 
                         for item in timeline_data]
                # Tomar últimos 12 puntos para sparkline
                return values[-12:] if len(values) > 12 else values
        return None
    except Exception as e:
        return None

