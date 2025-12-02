"""
Constantes de configuración para Abra
"""
from abra.ui.theme import APPLE_COLORS, QUERY_TYPE_COLORS, CHANNEL_COLORS

COUNTRIES = {
    "ES": {"name": "España", "flag": "🇪🇸"},
    "US": {"name": "Estados Unidos", "flag": "🇺🇸"},
    "GB": {"name": "Reino Unido", "flag": "🇬🇧"},
    "FR": {"name": "Francia", "flag": "🇫🇷"},
    "DE": {"name": "Alemania", "flag": "🇩🇪"},
    "IT": {"name": "Italia", "flag": "🇮🇹"},
    "PT": {"name": "Portugal", "flag": "🇵🇹"},
    "MX": {"name": "México", "flag": "🇲🇽"},
    "AR": {"name": "Argentina", "flag": "🇦🇷"},
    "BR": {"name": "Brasil", "flag": "🇧🇷"}
}

CHANNELS = {
    "web": {
        "name": "Web Search", 
        "icon": "🌐",
        "gprop": "",
        "description": "Búsquedas generales en Google"
    },
    "images": {
        "name": "Image Search",
        "icon": "🖼️",
        "gprop": "images",
        "description": "Búsquedas de imágenes"
    },
    "news": {
        "name": "News",
        "icon": "📰",
        "gprop": "news",
        "description": "Búsquedas en noticias"
    },
    "youtube": {
        "name": "YouTube",
        "icon": "📹",
        "gprop": "youtube",
        "description": "Búsquedas en YouTube"
    },
    "shopping": {
        "name": "Shopping",
        "icon": "🛒",
        "gprop": "froogle",
        "description": "Búsquedas de productos"
    }
}

PRODUCT_CATEGORIES = {
    "Teclados": {
        "keywords": ["teclado", "keyboard", "tecla", "switch", "mecánico", "mechanical", 
                    "rgb", "retroiluminado", "gaming keyboard"],
        "icon": "⌨️"
    },
    "Ratones": {
        "keywords": ["ratón", "mouse", "gaming mouse", "wireless mouse"],
        "icon": "🖱️"
    },
    "Auriculares": {
        "keywords": ["auricular", "headset", "headphone", "gaming headset"],
        "icon": "🎧"
    }
}

# Colores Apple-style (desde theme centralizado)
COLORS = APPLE_COLORS

# Colores por tipo de query
QUERY_COLORS = QUERY_TYPE_COLORS

# Colores por canal
COLORS_CHANNEL = CHANNEL_COLORS

# Límites
LIMITS = {
    'max_queries_per_page': 50,
    'max_topics_display': 10,
    'max_countries_comparison': 5,
    'max_brands_comparator': 4,
    'relevance_threshold_default': 10,
    'max_history_entries': 100,
}
