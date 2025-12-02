"""
Theme centralizado estilo Tailwind CSS para Abra
Colores consistentes en toda la aplicación
"""

# ===================================
# TAILWIND-INSPIRED COLOR PALETTE
# ===================================

# Primary Colors (Blue)
PRIMARY = {
    50: '#EFF6FF',
    100: '#DBEAFE',
    200: '#BFDBFE',
    300: '#93C5FD',
    400: '#60A5FA',
    500: '#3B82F6',  # Main primary
    600: '#2563EB',
    700: '#1D4ED8',
    800: '#1E40AF',
    900: '#1E3A8A',
}

# Success Colors (Green)
SUCCESS = {
    50: '#F0FDF4',
    100: '#DCFCE7',
    200: '#BBF7D0',
    300: '#86EFAC',
    400: '#4ADE80',
    500: '#22C55E',  # Main success
    600: '#16A34A',
    700: '#15803D',
    800: '#166534',
    900: '#14532D',
}

# Warning Colors (Orange/Yellow)
WARNING = {
    50: '#FFFBEB',
    100: '#FEF3C7',
    200: '#FDE68A',
    300: '#FCD34D',
    400: '#FBBF24',
    500: '#F59E0B',  # Main warning
    600: '#D97706',
    700: '#B45309',
    800: '#92400E',
    900: '#78350F',
}

# Danger Colors (Red)
DANGER = {
    50: '#FEF2F2',
    100: '#FEE2E2',
    200: '#FECACA',
    300: '#FCA5A5',
    400: '#F87171',
    500: '#EF4444',  # Main danger
    600: '#DC2626',
    700: '#B91C1C',
    800: '#991B1B',
    900: '#7F1D1D',
}

# Neutral/Gray Colors
NEUTRAL = {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#E5E5E5',
    300: '#D4D4D4',
    400: '#A3A3A3',
    500: '#737373',  # Main neutral
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
}

# Purple Colors (para gradientes)
PURPLE = {
    50: '#FAF5FF',
    100: '#F3E8FF',
    200: '#E9D5FF',
    300: '#D8B4FE',
    400: '#C084FC',
    500: '#A855F7',
    600: '#9333EA',
    700: '#7E22CE',
    800: '#6B21A8',
    900: '#581C87',
}

# Indigo Colors (para gradientes)
INDIGO = {
    50: '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',
    600: '#4F46E5',
    700: '#4338CA',
    800: '#3730A6',
    900: '#312E81',
}

# ===================================
# SEMANTIC COLORS (APPLE-STYLE)
# ===================================

APPLE_COLORS = {
    # Primary
    'primary': '#007AFF',
    'primary_hover': '#0051D5',
    
    # Success
    'success': '#34C759',
    'success_hover': '#248A3D',
    
    # Warning
    'warning': '#FF9500',
    'warning_hover': '#C76A00',
    
    # Danger
    'danger': '#FF3B30',
    'danger_hover': '#D32F2F',
    
    # Neutral
    'neutral': '#6e6e73',
    'neutral_light': '#86868b',
    'neutral_dark': '#1d1d1f',
    
    # Background
    'background': '#FFFFFF',
    'background_secondary': '#F5F5F7',
    'background_tertiary': '#E5E5EA',
    
    # Text
    'text_primary': '#1d1d1f',
    'text_secondary': '#6e6e73',
    'text_tertiary': '#86868b',
    'text_inverse': '#FFFFFF',
    
    # Border
    'border': 'rgba(0, 0, 0, 0.08)',
    'border_hover': 'rgba(0, 0, 0, 0.16)',
    
    # Shadow
    'shadow_sm': '0 2px 8px rgba(0, 0, 0, 0.04)',
    'shadow_md': '0 4px 16px rgba(0, 0, 0, 0.08)',
    'shadow_lg': '0 8px 32px rgba(0, 0, 0, 0.12)',
}

# ===================================
# GRADIENT PRESETS
# ===================================

GRADIENTS = {
    'primary': 'linear-gradient(135deg, #007AFF 0%, #0051D5 100%)',
    'success': 'linear-gradient(135deg, #34C759 0%, #248A3D 100%)',
    'warning': 'linear-gradient(135deg, #FF9500 0%, #C76A00 100%)',
    'danger': 'linear-gradient(135deg, #FF3B30 0%, #D32F2F 100%)',
    'purple': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'blue': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'sunset': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'ocean': 'linear-gradient(135deg, #2E3192 0%, #1BFFFF 100%)',
}

# ===================================
# CHART COLORS
# ===================================

CHART_COLORS = [
    '#007AFF',  # Primary
    '#34C759',  # Success
    '#FF9500',  # Warning
    '#FF3B30',  # Danger
    '#5856D6',  # Purple
    '#FF2D55',  # Pink
    '#5AC8FA',  # Cyan
    '#FFCC00',  # Yellow
    '#FF6482',  # Coral
    '#00C7BE',  # Teal
]

# ===================================
# QUERY TYPE COLORS
# ===================================

QUERY_TYPE_COLORS = {
    'Search term': '#007AFF',
    'Topic': '#34C759',
    'Brand': '#FF9500',
    'Product': '#FF3B30',
    'Category': '#5856D6',
    'Unknown': '#6e6e73',
}

# ===================================
# CHANNEL COLORS
# ===================================

CHANNEL_COLORS = {
    'web': '#007AFF',
    'images': '#34C759',
    'news': '#FF9500',
    'youtube': '#FF3B30',
    'shopping': '#5856D6',
}

# ===================================
# UTILITY FUNCTIONS
# ===================================

def get_color(color_name, shade=500):
    """
    Obtiene un color del tema
    
    Args:
        color_name: primary, success, warning, danger, neutral
        shade: 50-900 (default: 500)
    
    Returns:
        str: Color hex
    
    Example:
        >>> get_color('primary', 600)
        '#2563EB'
    """
    color_maps = {
        'primary': PRIMARY,
        'success': SUCCESS,
        'warning': WARNING,
        'danger': DANGER,
        'neutral': NEUTRAL,
        'purple': PURPLE,
        'indigo': INDIGO,
    }
    
    if color_name in color_maps:
        return color_maps[color_name].get(shade, color_maps[color_name][500])
    
    # Fallback a Apple colors
    return APPLE_COLORS.get(color_name, APPLE_COLORS['neutral'])

def get_gradient(gradient_name):
    """
    Obtiene un gradiente predefinido
    
    Args:
        gradient_name: primary, success, warning, danger, purple, blue, sunset, ocean
    
    Returns:
        str: CSS gradient
    """
    return GRADIENTS.get(gradient_name, GRADIENTS['primary'])

def get_query_color(query_type):
    """
    Obtiene color según tipo de query
    
    Args:
        query_type: Search term, Topic, Brand, Product, Category
    
    Returns:
        str: Color hex
    """
    return QUERY_TYPE_COLORS.get(query_type, QUERY_TYPE_COLORS['Unknown'])

def get_channel_color(channel):
    """
    Obtiene color según canal
    
    Args:
        channel: web, images, news, youtube, shopping
    
    Returns:
        str: Color hex
    """
    return CHANNEL_COLORS.get(channel, APPLE_COLORS['neutral'])

def alpha_color(color, opacity):
    """
    Añade opacidad a un color hex
    
    Args:
        color: Color hex (ej: '#007AFF')
        opacity: Opacidad 0-1
    
    Returns:
        str: Color rgba
    
    Example:
        >>> alpha_color('#007AFF', 0.1)
        'rgba(0, 122, 255, 0.1)'
    """
    # Convertir hex a RGB
    color = color.lstrip('#')
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    return f'rgba({r}, {g}, {b}, {opacity})'
