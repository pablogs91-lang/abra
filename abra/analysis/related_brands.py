"""
Detector de Marcas Relacionadas
Identifica marcas que se buscan junto a la marca principal
"""
import re
from collections import Counter
from typing import List, Dict

def detect_related_brands(queries_data, topics_data, main_brand):
    """
    Detecta marcas que se buscan junto a la marca principal
    
    Args:
        queries_data: Datos de related queries
        topics_data: Datos de related topics  
        main_brand: Marca principal
    
    Returns:
        Lista de marcas relacionadas con métricas
    """
    # Marcas tech conocidas (expandir según necesidad)
    KNOWN_BRANDS = {
        # Periféricos
        'logitech', 'razer', 'corsair', 'steelseries', 'hyperx', 'asus', 'msi',
        'roccat', 'cooler master', 'thermaltake', 'nzxt', 'lian li',
        # Teclados especializados
        'keychron', 'ducky', 'varmilo', 'leopold', 'filco', 'das keyboard',
        'durgod', 'anne pro', 'royal kludge', 'keycult',
        # Switches
        'cherry mx', 'gateron', 'kailh', 'holy panda', 'zealios',
        # Audio
        'sennheiser', 'beyerdynamic', 'audio technica', 'sony', 'bose',
        'akg', 'shure', 'rode', 'blue yeti',
        # Monitores
        'lg', 'samsung', 'dell', 'benq', 'acer', 'viewsonic', 'gigabyte',
        # Componentes
        'nvidia', 'amd', 'intel', 'kingston', 'crucial', 'western digital',
        'seagate', 'sandisk', 'g.skill', 'corsair', 'teamgroup',
        # Sillas
        'secretlab', 'noblechairs', 'herman miller', 'dxracer', 'akracing'
    }
    
    related_brands = []
    brand_counter = Counter()
    
    # Normalizar marca principal
    main_brand_lower = main_brand.lower()
    
    # 1. BUSCAR EN QUERIES
    if queries_data and 'related_queries' in queries_data:
        # Top queries
        if 'top' in queries_data['related_queries']:
            for query_item in queries_data['related_queries']['top']:
                query = query_item.get('query', '').lower()
                
                # Buscar marcas conocidas
                for brand in KNOWN_BRANDS:
                    if brand in query and brand not in main_brand_lower and main_brand_lower not in brand:
                        brand_counter[brand] += query_item.get('value', 1)
        
        # Rising queries
        if 'rising' in queries_data['related_queries']:
            for query_item in queries_data['related_queries']['rising']:
                query = query_item.get('query', '').lower()
                
                for brand in KNOWN_BRANDS:
                    if brand in query and brand not in main_brand_lower and main_brand_lower not in brand:
                        value = query_item.get('value', 'Breakout')
                        # Si es Breakout, dar más peso
                        weight = 200 if isinstance(value, str) and 'breakout' in value.lower() else value if isinstance(value, (int, float)) else 100
                        brand_counter[brand] += weight
    
    # 2. BUSCAR EN TOPICS
    if topics_data and 'related_topics' in topics_data:
        if 'top' in topics_data['related_topics']:
            for topic_item in topics_data['related_topics']['top']:
                topic = topic_item.get('topic', {})
                title = topic.get('title', '').lower()
                topic_type = topic.get('type', '')
                
                # Si es tipo Brand, es más relevante
                weight_multiplier = 2.0 if topic_type == 'Brand' else 1.0
                
                for brand in KNOWN_BRANDS:
                    if brand in title and brand not in main_brand_lower:
                        brand_counter[brand] += topic_item.get('value', 1) * weight_multiplier
    
    # 3. CONSTRUIR LISTA DE MARCAS RELACIONADAS
    for brand, score in brand_counter.most_common(20):
        # Clasificar tipo de relación
        relationship_type = classify_relationship(main_brand_lower, brand)
        
        related_brands.append({
            'brand': brand.title(),
            'co_search_score': int(score),
            'relationship': relationship_type,
            'category': get_brand_category(brand)
        })
    
    return related_brands


def classify_relationship(main_brand, related_brand):
    """
    Clasifica el tipo de relación entre marcas
    
    Args:
        main_brand: Marca principal
        related_brand: Marca relacionada
    
    Returns:
        Tipo de relación
    """
    # Competidores directos (misma categoría principal)
    competitors_map = {
        'logitech': ['razer', 'corsair', 'steelseries', 'hyperx'],
        'razer': ['logitech', 'corsair', 'steelseries', 'hyperx'],
        'corsair': ['logitech', 'razer', 'steelseries', 'hyperx'],
        'keychron': ['ducky', 'varmilo', 'leopold', 'royal kludge'],
        'nvidia': ['amd', 'intel'],
        'amd': ['nvidia', 'intel'],
        'intel': ['amd', 'nvidia'],
    }
    
    # Complementarios (diferentes categorías)
    complementary_map = {
        'logitech': ['keychron', 'ducky', 'secretlab'],  # Mouse + teclado/silla
        'nvidia': ['intel', 'amd', 'corsair', 'kingston'],  # GPU + CPU/RAM
    }
    
    if main_brand in competitors_map:
        if related_brand in competitors_map[main_brand]:
            return 'Competidor Directo'
    
    if main_brand in complementary_map:
        if related_brand in complementary_map[main_brand]:
            return 'Complementario'
    
    return 'Relacionado'


def get_brand_category(brand):
    """
    Obtiene categoría de una marca
    
    Args:
        brand: Nombre de marca
    
    Returns:
        Categoría
    """
    categories = {
        'periféricos': ['logitech', 'razer', 'corsair', 'steelseries', 'hyperx', 'roccat'],
        'teclados': ['keychron', 'ducky', 'varmilo', 'leopold', 'filco', 'das keyboard'],
        'audio': ['sennheiser', 'beyerdynamic', 'audio technica', 'sony', 'bose'],
        'monitores': ['lg', 'samsung', 'dell', 'benq', 'acer'],
        'componentes': ['nvidia', 'amd', 'intel', 'kingston', 'crucial', 'corsair'],
        'sillas': ['secretlab', 'noblechairs', 'herman miller', 'dxracer']
    }
    
    for category, brands in categories.items():
        if brand in brands:
            return category.title()
    
    return 'General'


def render_related_brands(related_brands, main_brand):
    """
    Renderiza panel de marcas relacionadas
    
    Args:
        related_brands: Lista de marcas relacionadas
        main_brand: Marca principal
    
    Returns:
        HTML string
    """
    if not related_brands:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>🔍 No se detectaron marcas relacionadas</p>
            <small>Intenta con una marca más popular</small>
        </div>
        """
    
    # Agrupar por tipo de relación
    competitors = [b for b in related_brands if b['relationship'] == 'Competidor Directo']
    complementary = [b for b in related_brands if b['relationship'] == 'Complementario']
    related = [b for b in related_brands if b['relationship'] == 'Relacionado']
    
    html = f"""
    <div style="margin-bottom: 1.5rem;">
        <p style="color: #6e6e73; font-size: 0.95rem;">
            💡 Usuarios que buscan <strong>{main_brand}</strong> también buscan estas marcas
        </p>
    </div>
    """
    
    # Competidores
    if competitors:
        html += '<h4 style="margin-top: 1.5rem;">🏆 Competidores Directos</h4>'
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem;">'
        
        for brand in competitors[:6]:
            html += f"""
            <div style="
                background: white;
                border: 2px solid #FF9500;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #1d1d1f; font-size: 1.1rem;">
                            {brand['brand']}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73; margin-top: 0.25rem;">
                            {brand['category']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: #FF9500;">
                            {brand['co_search_score']}
                        </div>
                        <div style="font-size: 0.75rem; color: #6e6e73;">
                            Co-búsquedas
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html += '</div>'
    
    # Complementarios
    if complementary:
        html += '<h4 style="margin-top: 1.5rem;">🤝 Marcas Complementarias</h4>'
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem;">'
        
        for brand in complementary[:6]:
            html += f"""
            <div style="
                background: white;
                border: 2px solid #34C759;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #1d1d1f; font-size: 1.1rem;">
                            {brand['brand']}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73; margin-top: 0.25rem;">
                            {brand['category']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: #34C759;">
                            {brand['co_search_score']}
                        </div>
                        <div style="font-size: 0.75rem; color: #6e6e73;">
                            Co-búsquedas
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html += '</div>'
    
    # Otros relacionados
    if related:
        html += '<h4 style="margin-top: 1.5rem;">🔗 Otras Marcas Relacionadas</h4>'
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem;">'
        
        for brand in related[:8]:
            html += f"""
            <div style="
                background: white;
                border: 2px solid #007AFF;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <div style="display: flex; justify-space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #1d1d1f; font-size: 1.1rem;">
                            {brand['brand']}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73; margin-top: 0.25rem;">
                            {brand['category']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: #007AFF;">
                            {brand['co_search_score']}
                        </div>
                        <div style="font-size: 0.75rem; color: #6e6e73;">
                            Co-búsquedas
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html += '</div>'
    
    return html
