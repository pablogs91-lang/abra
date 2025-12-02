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
    # Componentes Internos
    "Placas Base": {
        "keywords": ["placa base", "motherboard", "mainboard", "placa madre", "socket", 
                    "chipset", "atx", "micro atx", "mini itx"],
        "icon": "🔌"
    },
    "Tarjetas Gráficas": {
        "keywords": ["tarjeta gráfica", "gpu", "graphics card", "nvidia", "amd", "geforce", 
                    "radeon", "rtx", "gtx", "rx", "vram"],
        "icon": "🎮"
    },
    "Procesadores": {
        "keywords": ["procesador", "cpu", "processor", "intel", "amd", "ryzen", "core i3", 
                    "core i5", "core i7", "core i9", "threadripper", "ghz"],
        "icon": "⚙️"
    },
    "Discos Duros": {
        "keywords": ["disco duro", "hdd", "hard drive", "sata", "rpm", "tb", "almacenamiento"],
        "icon": "💾"
    },
    "SSD": {
        "keywords": ["ssd", "solid state", "nvme", "m.2", "sata ssd", "pcie", "almacenamiento ssd"],
        "icon": "⚡"
    },
    "Memoria RAM": {
        "keywords": ["ram", "memoria", "ddr4", "ddr5", "memoria ram", "dimm", "sodimm", "mhz"],
        "icon": "🧮"
    },
    
    # Refrigeración
    "Refrigeración Líquida": {
        "keywords": ["refrigeración líquida", "watercooling", "aio", "custom loop", 
                    "radiador", "bomba", "bloque"],
        "icon": "💧"
    },
    "Ventiladores": {
        "keywords": ["ventilador", "fan", "cooling fan", "case fan", "rgb fan", "pwm"],
        "icon": "🌀"
    },
    "Ventiladores CPU": {
        "keywords": ["ventilador cpu", "cpu cooler", "disipador", "heatsink", "tower cooler"],
        "icon": "❄️"
    },
    
    # Cajas y Alimentación
    "Torres y Cajas": {
        "keywords": ["torre", "caja", "case", "chasis", "atx case", "full tower", 
                    "mid tower", "mini tower", "gabinete"],
        "icon": "🏢"
    },
    "Fuentes de Alimentación": {
        "keywords": ["fuente", "psu", "power supply", "modular", "watt", "80 plus", 
                    "certificación", "bronze", "gold", "platinum"],
        "icon": "🔋"
    },
    
    # Periféricos de Entrada
    "Teclados": {
        "keywords": ["teclado", "keyboard", "tecla", "switch", "mecánico", "mechanical", 
                    "rgb", "retroiluminado", "gaming keyboard", "wireless keyboard"],
        "icon": "⌨️"
    },
    "Ratones": {
        "keywords": ["ratón", "mouse", "gaming mouse", "wireless mouse", "dpi", "sensor", 
                    "ergonómico", "ambidiestro"],
        "icon": "🖱️"
    },
    "Mandos": {
        "keywords": ["mando", "gamepad", "controller", "joystick", "xbox controller", 
                    "ps5 controller", "nintendo"],
        "icon": "🎮"
    },
    
    # Periféricos de Salida
    "Monitores": {
        "keywords": ["monitor", "pantalla", "display", "4k", "gaming monitor", "hz", 
                    "refresh rate", "panel", "ips", "va", "tn", "ultrawide", "curvo"],
        "icon": "🖥️"
    },
    "Auriculares": {
        "keywords": ["auricular", "headset", "headphone", "gaming headset", "inalámbrico", 
                    "wireless", "sonido surround", "micrófono"],
        "icon": "🎧"
    },
    
    # Mobiliario y Accesorios
    "Sillas Gaming": {
        "keywords": ["silla gaming", "gaming chair", "silla gamer", "ergonómica", 
                    "respaldo", "reposabrazos"],
        "icon": "🪑"
    },
    "Mesas": {
        "keywords": ["mesa", "escritorio", "desk", "gaming desk", "mesa gaming", 
                    "altura ajustable"],
        "icon": "🗄️"
    },
    
    # Otros
    "Otros Componentes": {
        "keywords": ["componente", "cable", "adaptador", "conector", "tornillo", "pasta térmica", 
                    "thermal paste", "bracket"],
        "icon": "🔧"
    },
    "Otros Periféricos": {
        "keywords": ["periférico", "peripheral", "webcam", "micrófono", "altavoz", "speaker", 
                    "hub usb", "lector tarjetas", "alfombrilla"],
        "icon": "🖲️"
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
