"""
Related Brands - SerpAPI Official
Detecta marcas relacionadas usando datos oficiales de Google
"""
from typing import List, Dict, Optional
import html

def extract_related_brands(serpapi_data: Dict, main_brand: str) -> List[Dict]:
    """
    Extrae marcas relacionadas de respuesta SerpAPI
    
    Args:
        serpapi_data: Respuesta completa de SerpAPI
        main_brand: Marca principal
    
    Returns:
        Lista de marcas relacionadas con scores
    """
    related_brands = []
    
    if not serpapi_data:
        return []
    
    main_brand_lower = main_brand.lower()
    
    # 1. RELATED SEARCHES (más confiable)
    if 'related_searches' in serpapi_data:
        for item in serpapi_data['related_searches']:
            query = item.get('query', '').lower()
            
            # Detectar si contiene nombre de marca
            brand = extract_brand_name(query, main_brand_lower)
            if brand and brand != main_brand_lower:
                related_brands.append({
                    'brand': brand.title(),
                    'source': 'related_searches',
                    'score': 100,  # Alta confianza
                    'thumbnail': item.get('thumbnail'),
                    'query': item.get('query')
                })
    
    # 2. PEOPLE ALSO SEARCH FOR
    if 'people_also_search_for' in serpapi_data:
        for item in serpapi_data['people_also_search_for']:
            title = item.get('title', '').lower()
            brand = extract_brand_name(title, main_brand_lower)
            
            if brand and brand != main_brand_lower:
                related_brands.append({
                    'brand': brand.title(),
                    'source': 'people_also_search',
                    'score': 90,
                    'thumbnail': item.get('thumbnail'),
                    'link': item.get('link')
                })
    
    # 3. KNOWLEDGE GRAPH RELATED
    if 'knowledge_graph' in serpapi_data:
        kg = serpapi_data['knowledge_graph']
        
        # Related brands en knowledge graph
        if 'related' in kg:
            for item in kg['related']:
                name = item.get('name', '')
                if name and name.lower() != main_brand_lower:
                    related_brands.append({
                        'brand': name.title(),
                        'source': 'knowledge_graph',
                        'score': 95,
                        'thumbnail': item.get('image'),
                        'link': item.get('link')
                    })
    
    # 4. ORGANIC RESULTS (menciones)
    if 'organic_results' in serpapi_data:
        for result in serpapi_data['organic_results'][:10]:  # Top 10
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            brand = extract_brand_name(title + ' ' + snippet, main_brand_lower)
            if brand and brand != main_brand_lower:
                related_brands.append({
                    'brand': brand.title(),
                    'source': 'organic_mention',
                    'score': 70,
                    'link': result.get('link')
                })
    
    # Deduplicar y ordenar
    unique_brands = {}
    for item in related_brands:
        brand_key = item['brand'].lower()
        if brand_key not in unique_brands:
            unique_brands[brand_key] = item
        else:
            # Mantener el de mayor score
            if item['score'] > unique_brands[brand_key]['score']:
                unique_brands[brand_key] = item
    
    # Convertir a lista y ordenar por score
    result = list(unique_brands.values())
    result.sort(key=lambda x: x['score'], reverse=True)
    
    # Clasificar tipo de relación
    for item in result:
        item['relationship'] = classify_relationship(main_brand_lower, item['brand'].lower())
        item['category'] = get_brand_category(item['brand'].lower())
    
    return result


def extract_brand_name(text: str, exclude: str) -> Optional[str]:
    """
    Extrae nombre de marca de texto
    
    Args:
        text: Texto a analizar
        exclude: Marca a excluir
    
    Returns:
        Nombre de marca o None
    """
    # Base de datos de marcas conocidas (expandible)
    KNOWN_BRANDS = {
        # Gaming Peripherals
        'logitech', 'razer', 'corsair', 'steelseries', 'hyperx', 'asus', 'msi',
        'roccat', 'cooler master', 'thermaltake', 'nzxt', 'lian li',
        # Keyboards
        'keychron', 'ducky', 'varmilo', 'leopold', 'filco', 'das keyboard',
        'durgod', 'anne pro', 'royal kludge', 'keycult', 'glorious',
        # Audio
        'sennheiser', 'beyerdynamic', 'audio technica', 'sony', 'bose',
        'akg', 'shure', 'rode', 'blue yeti', 'hyperx', 'astro',
        # Monitors
        'lg', 'samsung', 'dell', 'benq', 'acer', 'viewsonic', 'gigabyte',
        'asus', 'msi', 'alienware', 'hp', 'lenovo',
        # Components
        'nvidia', 'amd', 'intel', 'kingston', 'crucial', 'western digital',
        'seagate', 'sandisk', 'g.skill', 'corsair', 'teamgroup',
        # Chairs
        'secretlab', 'noblechairs', 'herman miller', 'dxracer', 'akracing',
        'autonomous', 'steelcase', 'flexispot',
        # Mice
        'glorious', 'finalmouse', 'zowie', 'vaxee', 'pulsar', 'xtrfy'
    }
    
    text_lower = text.lower()
    
    for brand in KNOWN_BRANDS:
        if brand in text_lower and brand != exclude:
            # Verificar que no es parte de otra palabra
            if brand in text_lower.split() or f" {brand} " in text_lower:
                return brand
    
    return None


def classify_relationship(main_brand: str, related_brand: str) -> str:
    """
    Clasifica relación entre marcas
    
    Args:
        main_brand: Marca principal
        related_brand: Marca relacionada
    
    Returns:
        Tipo de relación
    """
    # Competidores directos
    competitors_map = {
        'logitech': ['razer', 'corsair', 'steelseries', 'hyperx', 'roccat'],
        'razer': ['logitech', 'corsair', 'steelseries', 'hyperx'],
        'corsair': ['logitech', 'razer', 'steelseries', 'hyperx'],
        'keychron': ['ducky', 'varmilo', 'leopold', 'royal kludge', 'glorious'],
        'nvidia': ['amd'],
        'amd': ['nvidia', 'intel'],
        'intel': ['amd'],
        'secretlab': ['noblechairs', 'herman miller', 'dxracer'],
        'glorious': ['finalmouse', 'logitech', 'razer']
    }
    
    # Complementarios
    complementary_map = {
        'logitech': ['keychron', 'ducky', 'secretlab', 'benq', 'lg'],
        'nvidia': ['intel', 'amd', 'corsair', 'kingston'],
        'keychron': ['logitech', 'razer', 'glorious']
    }
    
    if main_brand in competitors_map:
        if related_brand in competitors_map[main_brand]:
            return 'Competidor Directo'
    
    if main_brand in complementary_map:
        if related_brand in complementary_map[main_brand]:
            return 'Complementario'
    
    return 'Relacionado'


def get_brand_category(brand: str) -> str:
    """
    Obtiene categoría de marca
    
    Args:
        brand: Nombre de marca
    
    Returns:
        Categoría
    """
    categories = {
        'Periféricos Gaming': ['logitech', 'razer', 'corsair', 'steelseries', 'hyperx', 'roccat', 'glorious'],
        'Teclados Mecánicos': ['keychron', 'ducky', 'varmilo', 'leopold', 'filco', 'das keyboard', 'royal kludge'],
        'Audio': ['sennheiser', 'beyerdynamic', 'audio technica', 'sony', 'bose', 'shure', 'rode'],
        'Monitores': ['lg', 'samsung', 'dell', 'benq', 'acer', 'viewsonic', 'asus'],
        'Componentes PC': ['nvidia', 'amd', 'intel', 'kingston', 'crucial', 'corsair', 'g.skill'],
        'Sillas Gaming': ['secretlab', 'noblechairs', 'herman miller', 'dxracer', 'akracing'],
        'Ratones Gaming': ['glorious', 'finalmouse', 'zowie', 'vaxee', 'pulsar']
    }
    
    for category, brands in categories.items():
        if brand in brands:
            return category
    
    return 'General'


def render_related_brands_serpapi(related_brands: List[Dict], 
                                   main_brand: str,
                                   show_source: bool = False) -> str:
    """
    Renderiza marcas relacionadas (versión SerpAPI mejorada)
    
    Args:
        related_brands: Lista de marcas
        main_brand: Marca principal
        show_source: Si mostrar fuente de datos
    
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
    
    # Agrupar por relación
    competitors = [b for b in related_brands if b['relationship'] == 'Competidor Directo']
    complementary = [b for b in related_brands if b['relationship'] == 'Complementario']
    related = [b for b in related_brands if b['relationship'] == 'Relacionado']
    
    html_content = f"""
    <div style="margin-bottom: 1.5rem;">
        <p style="color: #6e6e73; font-size: 0.95rem;">
            💡 Usuarios que buscan <strong>{main_brand}</strong> también buscan estas marcas
            {' <span style="color: #007AFF; font-size: 0.85rem;">(Datos oficiales de Google via SerpAPI)</span>' if show_source else ''}
        </p>
    </div>
    """
    
    # Competidores
    if competitors:
        html_content += '<h4 style="margin-top: 1.5rem;">🏆 Competidores Directos</h4>'
        html_content += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">'
        
        for brand in competitors[:6]:
            thumbnail_html = ""
            if brand.get('thumbnail'):
                thumbnail_html = f"""
                <img src="{brand['thumbnail']}" 
                     style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;"
                     onerror="this.style.display='none'">
                """
            
            html_content += f"""
            <div style="
                background: white;
                border: 2px solid #FF9500;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <div style="display: flex; gap: 1rem; align-items: center;">
                    {thumbnail_html}
                    <div style="flex: 1;">
                        <div style="font-weight: 700; color: #1d1d1f; font-size: 1.1rem;">
                            {html.escape(brand['brand'])}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73; margin-top: 0.25rem;">
                            {html.escape(brand['category'])}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span style="
                                background: #FF950020;
                                color: #FF9500;
                                padding: 0.25rem 0.5rem;
                                border-radius: 4px;
                                font-size: 0.75rem;
                                font-weight: 600;
                            ">
                                Score: {brand['score']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html_content += '</div>'
    
    # Complementarios
    if complementary:
        html_content += '<h4 style="margin-top: 1.5rem;">🤝 Marcas Complementarias</h4>'
        html_content += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">'
        
        for brand in complementary[:6]:
            thumbnail_html = ""
            if brand.get('thumbnail'):
                thumbnail_html = f"""
                <img src="{brand['thumbnail']}" 
                     style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;"
                     onerror="this.style.display='none'">
                """
            
            html_content += f"""
            <div style="
                background: white;
                border: 2px solid #34C759;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <div style="display: flex; gap: 1rem; align-items: center;">
                    {thumbnail_html}
                    <div style="flex: 1;">
                        <div style="font-weight: 700; color: #1d1d1f; font-size: 1.1rem;">
                            {html.escape(brand['brand'])}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73; margin-top: 0.25rem;">
                            {html.escape(brand['category'])}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span style="
                                background: #34C75920;
                                color: #34C759;
                                padding: 0.25rem 0.5rem;
                                border-radius: 4px;
                                font-size: 0.75rem;
                                font-weight: 600;
                            ">
                                Score: {brand['score']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html_content += '</div>'
    
    # Otros relacionados
    if related:
        html_content += '<h4 style="margin-top: 1.5rem;">🔗 Otras Marcas Relacionadas</h4>'
        html_content += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">'
        
        for brand in related[:8]:
            thumbnail_html = ""
            if brand.get('thumbnail'):
                thumbnail_html = f"""
                <img src="{brand['thumbnail']}" 
                     style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;"
                     onerror="this.style.display='none'">
                """
            
            html_content += f"""
            <div style="
                background: white;
                border: 2px solid #007AFF;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <div style="display: flex; gap: 1rem; align-items: center;">
                    {thumbnail_html}
                    <div style="flex: 1;">
                        <div style="font-weight: 700; color: #1d1d1f; font-size: 1.1rem;">
                            {html.escape(brand['brand'])}
                        </div>
                        <div style="font-size: 0.85rem; color: #6e6e73; margin-top: 0.25rem;">
                            {html.escape(brand['category'])}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span style="
                                background: #007AFF20;
                                color: #007AFF;
                                padding: 0.25rem 0.5rem;
                                border-radius: 4px;
                                font-size: 0.75rem;
                                font-weight: 600;
                            ">
                                Score: {brand['score']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html_content += '</div>'
    
    return html_content
