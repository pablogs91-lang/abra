"""
Detector de Productos Estrella
Identifica productos destacados con alto crecimiento y volumen
"""
import pandas as pd
from typing import List, Dict, Any

def detect_star_products(queries: List[Dict], threshold_volume: int = 50, 
                        threshold_growth: float = 20.0) -> List[Dict]:
    """
    Detecta productos estrella según:
    1. Alto volumen (>threshold_volume)
    2. Crecimiento positivo (>threshold_growth%)
    3. Tipo = Product
    
    Args:
        queries: Lista de queries con clasificación
        threshold_volume: Volumen mínimo
        threshold_growth: Crecimiento mínimo %
    
    Returns:
        Lista de productos estrella ordenados por crecimiento
    """
    stars = []
    
    for query in queries:
        # Extraer datos
        query_text = query.get('query', '')
        query_type = query.get('type', '')
        value = query.get('value', 0)
        
        # Clasificar como producto si contiene indicadores
        is_product = (
            query_type in ['Product', 'Brand'] or
            any(indicator in query_text.lower() for indicator in [
                'pro', 'ultra', 'max', 'mini', 'plus', 'elite',
                'rgb', 'wireless', 'gaming', 'mechanical', 'optical',
                'v2', 'v3', 'gen', 'series', 'edition'
            ])
        )
        
        # Calcular "crecimiento" (si es string "Breakout", considerar 200%)
        if isinstance(value, str):
            if 'breakout' in value.lower():
                growth = 200.0
            else:
                growth = 0.0
        else:
            growth = float(value) if value else 0.0
        
        # Filtrar productos estrella
        if is_product and growth > threshold_growth:
            stars.append({
                'product': query_text,
                'growth': growth,
                'volume': value,
                'type': query_type,
                'category': extract_category(query_text),
                'is_rising': growth >= 100.0
            })
    
    # Ordenar por crecimiento descendente
    return sorted(stars, key=lambda x: x['growth'], reverse=True)


def extract_category(product_name: str) -> str:
    """
    Extrae categoría del nombre del producto
    
    Args:
        product_name: Nombre del producto
    
    Returns:
        Categoría detectada
    """
    product_lower = product_name.lower()
    
    categories = {
        'mouse': ['mouse', 'ratón', 'mice'],
        'keyboard': ['keyboard', 'teclado', 'mechanical'],
        'headset': ['headset', 'auricular', 'headphone'],
        'monitor': ['monitor', 'display', 'screen'],
        'webcam': ['webcam', 'camera', 'cámara'],
        'microphone': ['mic', 'micrófono', 'microphone'],
        'controller': ['controller', 'gamepad', 'joystick'],
        'chair': ['chair', 'silla'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in product_lower for keyword in keywords):
            return category.title()
    
    return 'General'


def render_star_products(star_products: List[Dict]) -> str:
    """
    Renderiza productos estrella en HTML
    
    Args:
        star_products: Lista de productos estrella
    
    Returns:
        HTML string
    """
    if not star_products:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>No se detectaron productos estrella en este análisis.</p>
            <small>Productos con crecimiento >20% aparecerán aquí</small>
        </div>
        """
    
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin: 1rem 0;">'
    
    for i, product in enumerate(star_products[:6], 1):  # Top 6
        # Color según crecimiento
        if product['growth'] >= 200:
            gradient = 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)'
            badge = '🔥 BREAKOUT'
            badge_color = '#EF4444'
        elif product['growth'] >= 100:
            gradient = 'linear-gradient(135deg, #FFA500 0%, #FF8C00 100%)'
            badge = '⭐ RISING'
            badge_color = '#F59E0B'
        else:
            gradient = 'linear-gradient(135deg, #34C759 0%, #248A3D 100%)'
            badge = '📈 GROWING'
            badge_color = '#22C55E'
        
        html += f"""
        <div style="
            background: white;
            border: 2px solid {badge_color};
            border-radius: 12px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                right: 0;
                background: {badge_color};
                color: white;
                padding: 0.25rem 0.75rem;
                border-bottom-left-radius: 8px;
                font-size: 0.75rem;
                font-weight: 700;
            ">
                {badge}
            </div>
            
            <div style="margin-top: 0.5rem;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #1d1d1f; margin-bottom: 0.5rem;">
                    #{i} {product['product']}
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <div>
                        <div style="font-size: 0.85rem; color: #6e6e73;">Crecimiento</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: {badge_color};">
                            +{product['growth']:.0f}%
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.85rem; color: #6e6e73;">Categoría</div>
                        <div style="font-size: 0.9rem; font-weight: 600; color: #1d1d1f;">
                            {product['category']}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    html += '</div>'
    
    return html


def get_star_products_summary(star_products: List[Dict]) -> Dict[str, Any]:
    """
    Genera resumen de productos estrella
    
    Args:
        star_products: Lista de productos estrella
    
    Returns:
        Dict con métricas de resumen
    """
    if not star_products:
        return {
            'total': 0,
            'breakout': 0,
            'rising': 0,
            'avg_growth': 0,
            'top_category': 'N/A'
        }
    
    breakout = sum(1 for p in star_products if p['growth'] >= 200)
    rising = sum(1 for p in star_products if 100 <= p['growth'] < 200)
    avg_growth = sum(p['growth'] for p in star_products) / len(star_products)
    
    # Categoría más común
    categories = [p['category'] for p in star_products]
    top_category = max(set(categories), key=categories.count) if categories else 'N/A'
    
    return {
        'total': len(star_products),
        'breakout': breakout,
        'rising': rising,
        'growing': len(star_products) - breakout - rising,
        'avg_growth': avg_growth,
        'top_category': top_category
    }
