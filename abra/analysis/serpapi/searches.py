"""
Related Searches - SerpAPI
Búsquedas relacionadas con imágenes
"""
from typing import List, Dict
import html

def extract_related_searches(serpapi_data: Dict) -> List[Dict]:
    """
    Extrae búsquedas relacionadas con imágenes
    
    Args:
        serpapi_data: Respuesta de SerpAPI
    
    Returns:
        Lista de búsquedas relacionadas
    """
    searches = []
    
    if not serpapi_data:
        return []
    
    # Related searches
    if 'related_searches' in serpapi_data:
        for item in serpapi_data['related_searches']:
            searches.append({
                'query': item.get('query', ''),
                'thumbnail': item.get('thumbnail'),
                'link': item.get('link'),
                'type': 'related'
            })
    
    # People also search for
    if 'people_also_search_for' in serpapi_data:
        for item in serpapi_data['people_also_search_for']:
            searches.append({
                'query': item.get('title', ''),
                'thumbnail': item.get('thumbnail'),
                'link': item.get('link'),
                'type': 'people_also_search'
            })
    
    return searches


def render_related_searches(searches: List[Dict]) -> str:
    """
    Renderiza búsquedas relacionadas con imágenes
    
    Args:
        searches: Lista de búsquedas
    
    Returns:
        HTML string
    """
    if not searches:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>🔍 No se encontraron búsquedas relacionadas</p>
        </div>
        """
    
    html_content = """
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
    """
    
    for search in searches[:12]:  # Top 12
        safe_query = html.escape(search['query'])
        
        thumbnail_html = ""
        if search.get('thumbnail'):
            thumbnail_html = f"""
            <div style="
                width: 100%;
                height: 120px;
                border-radius: 8px;
                overflow: hidden;
                background: #f5f5f7;
                margin-bottom: 0.75rem;
            ">
                <img src="{search['thumbnail']}" 
                     style="width: 100%; height: 100%; object-fit: cover;"
                     onerror="this.parentElement.style.display='none'">
            </div>
            """
        
        # Badge tipo
        badge_color = '#007AFF' if search['type'] == 'related' else '#5856D6'
        badge_text = 'Related' if search['type'] == 'related' else 'People Search'
        
        html_content += f"""
        <div style="
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 1rem;
            transition: all 0.3s ease;
            cursor: pointer;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            {thumbnail_html}
            
            <div style="
                font-weight: 600;
                color: #1d1d1f;
                font-size: 0.95rem;
                line-height: 1.3;
                margin-bottom: 0.5rem;
            ">
                {safe_query}
            </div>
            
            <div style="
                background: {badge_color}20;
                color: {badge_color};
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                display: inline-block;
            ">
                {badge_text}
            </div>
        </div>
        """
    
    html_content += "</div>"
    
    return html_content
