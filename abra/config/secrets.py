"""
Configuración de secrets y variables de entorno
Centraliza el acceso a API keys y configuración sensible
"""
import os
import streamlit as st


def get_serpapi_key():
    """
    Obtiene la API key de SerpAPI desde múltiples fuentes:
    1. Streamlit secrets (producción)
    2. Variables de entorno (desarrollo)
    3. None (modo sin API)
    
    Returns:
        str: API key o None si no está configurada
    """
    # Prioridad 1: Streamlit secrets (Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and 'SERPAPI_API_KEY' in st.secrets:
            return st.secrets['SERPAPI_API_KEY']
    except Exception:
        pass
    
    # Prioridad 2: Variable de entorno (desarrollo local)
    api_key = os.getenv('SERPAPI_API_KEY')
    if api_key:
        return api_key
    
    # Prioridad 3: No configurada
    return None


# Exportar la key globalmente
SERPAPI_KEY = get_serpapi_key()


def is_serpapi_configured():
    """
    Verifica si SerpAPI está configurada
    
    Returns:
        bool: True si hay API key disponible
    """
    return SERPAPI_KEY is not None and SERPAPI_KEY != ""


def get_config_status():
    """
    Obtiene el estado de la configuración
    
    Returns:
        dict: Estado de todas las configuraciones
    """
    return {
        'serpapi_configured': is_serpapi_configured(),
        'serpapi_key_length': len(SERPAPI_KEY) if SERPAPI_KEY else 0,
        'serpapi_source': _get_serpapi_source()
    }


def _get_serpapi_source():
    """Determina de dónde viene la API key"""
    try:
        if hasattr(st, 'secrets') and 'SERPAPI_API_KEY' in st.secrets:
            return 'streamlit_secrets'
    except Exception:
        pass
    
    if os.getenv('SERPAPI_API_KEY'):
        return 'environment'
    
    return 'not_configured'
