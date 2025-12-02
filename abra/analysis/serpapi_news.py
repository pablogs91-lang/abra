"""
Google News via SerpAPI
Implementación profesional con imágenes, metadatos ricos y cache
"""
import requests
import os
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional

class SerpAPINewsClient:
    """
    Cliente para Google News via SerpAPI
    
    Docs: https://serpapi.com/google-news-api
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
    
    def search_news(self, query: str, country: str = 'es', 
                    language: str = 'es', max_results: int = 15) -> List[Dict]:
        """
        Busca noticias relacionadas con query
        
        Args:
            query: Marca o producto a buscar
            country: Código país (es, us, gb, etc)
            language: Idioma (es, en, etc)
            max_results: Número máximo de resultados
        
        Returns:
            Lista de noticias con metadatos completos
        """
        # Check cache
        cache_key = f"{query}_{country}_{language}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data[:max_results]
        
        # Build params
        params = {
            'engine': 'google_news',
            'q': query,
            'gl': country,  # Country
            'hl': language,  # Language
            'api_key': self.api_key,
            'num': max_results
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse results
            news_items = []
            
            if 'news_results' in data:
                for item in data['news_results']:
                    news_items.append(self._parse_news_item(item, query))
            
            # Cache results
            self.cache[cache_key] = (news_items, datetime.now())
            
            return news_items[:max_results]
        
        except Exception as e:
            print(f"SerpAPI Error: {e}")
            return []
    
    def _parse_news_item(self, item: Dict, query: str) -> Dict:
        """
        Parsea item de SerpAPI a formato estándar
        
        Args:
            item: Item raw de SerpAPI
            query: Query original
        
        Returns:
            Dict con formato estandarizado
        """
        # Extract data
        title = item.get('title', '')
        link = item.get('link', '')
        snippet = item.get('snippet', '')
        date = item.get('date', '')
        source = item.get('source', {})
        
        # Source info
        source_name = source.get('name', 'Unknown')
        source_icon = source.get('icon', '')
        
        # Thumbnail image
        thumbnail = item.get('thumbnail', '')
        
        # Parse date
        date_display = self._parse_date(date)
        
        # Calculate relevance
        relevance = self._calculate_relevance(title, snippet, query)
        
        return {
            'title': title,
            'description': snippet,
            'url': link,
            'date': date,
            'date_display': date_display,
            'source': source_name,
            'source_icon': source_icon,
            'thumbnail': thumbnail,
            'relevance': relevance,
            'has_image': bool(thumbnail)
        }
    
    def _parse_date(self, date_str: str) -> str:
        """
        Convierte fecha relativa a display amigable
        
        Args:
            date_str: Fecha de SerpAPI (ej: "2 hours ago", "1 day ago")
        
        Returns:
            Fecha en español
        """
        if not date_str:
            return 'Fecha desconocida'
        
        date_lower = date_str.lower()
        
        # Traducciones comunes
        translations = {
            'ago': '',
            'hour': 'hora',
            'hours': 'horas',
            'minute': 'minuto',
            'minutes': 'minutos',
            'day': 'día',
            'days': 'días',
            'week': 'semana',
            'weeks': 'semanas',
            'month': 'mes',
            'months': 'meses'
        }
        
        result = date_lower
        for eng, esp in translations.items():
            result = result.replace(eng, esp)
        
        return f"Hace {result.strip()}" if result else date_str
    
    def _calculate_relevance(self, title: str, description: str, query: str) -> int:
        """
        Calcula score de relevancia (0-100)
        
        Args:
            title: Título de noticia
            description: Descripción
            query: Query original
        
        Returns:
            Score 0-100
        """
        query_lower = query.lower()
        title_lower = title.lower()
        desc_lower = description.lower()
        
        score = 0
        
        # Query exacta en título: +50
        if query_lower in title_lower:
            score += 50
        
        # Query exacta en descripción: +20
        if query_lower in desc_lower:
            score += 20
        
        # Palabras individuales
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 3:
                if word in title_lower:
                    score += 10
                if word in desc_lower:
                    score += 5
        
        return min(score, 100)


def get_google_news_serpapi(query: str, country: str = 'es', 
                            api_key: Optional[str] = None,
                            max_results: int = 15) -> List[Dict]:
    """
    Función helper para obtener noticias vía SerpAPI
    
    Args:
        query: Marca o producto
        country: Código país
        api_key: SerpAPI key (o None para usar RSS fallback)
        max_results: Max noticias
    
    Returns:
        Lista de noticias
    """
    # Si no hay API key, usar RSS fallback
    if not api_key:
        from .google_news import get_google_news
        return get_google_news(query, country, max_results=max_results)
    
    # Usar SerpAPI
    try:
        client = SerpAPINewsClient(api_key)
        news = client.search_news(query, country, max_results=max_results)
        
        if news:
            return news
        else:
            # Fallback a RSS si SerpAPI falla
            from .google_news import get_google_news
            return get_google_news(query, country, max_results=max_results)
    
    except Exception as e:
        print(f"SerpAPI failed: {e}, falling back to RSS")
        from .google_news import get_google_news
        return get_google_news(query, country, max_results=max_results)


def analyze_news_sentiment_serpapi(news_items: List[Dict]) -> Dict:
    """
    Análisis de sentimiento para noticias de SerpAPI
    (Reutiliza lógica existente)
    """
    from .google_news import analyze_news_sentiment
    return analyze_news_sentiment(news_items)


def render_news_panel_serpapi(news_items: List[Dict], 
                              sentiment_analysis: Optional[Dict] = None) -> str:
    """
    Renderiza noticias de SerpAPI con imágenes
    
    Args:
        news_items: Lista de noticias
        sentiment_analysis: Análisis de sentimiento
    
    Returns:
        HTML string
    """
    if not news_items:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>📰 No se encontraron noticias recientes</p>
            <small>Intenta con otra marca o verifica la conexión</small>
        </div>
        """
    
    import html
    
    html_content = ""
    
    # Sentimiento general
    if sentiment_analysis:
        sentiment_colors = {
            'positive': '#34C759',
            'neutral': '#6e6e73',
            'negative': '#FF3B30'
        }
        sentiment_icons = {
            'positive': '😊',
            'neutral': '😐',
            'negative': '😟'
        }
        
        sentiment_color = sentiment_colors[sentiment_analysis['overall_sentiment']]
        sentiment_icon = sentiment_icons[sentiment_analysis['overall_sentiment']]
        
        html_content += f"""
        <div style="background: linear-gradient(135deg, {sentiment_color}20 0%, {sentiment_color}10 100%);
                    border-left: 4px solid {sentiment_color};
                    padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">{sentiment_icon}</span>
                <div>
                    <strong>Sentimiento General: {sentiment_analysis['overall_sentiment'].title()}</strong>
                    <br>
                    <small style="color: #6e6e73;">
                        Positivas: {sentiment_analysis['positive_count']} | 
                        Neutrales: {sentiment_analysis['neutral_count']} | 
                        Negativas: {sentiment_analysis['negative_count']}
                    </small>
                </div>
            </div>
        </div>
        """
    
    # Noticias con imágenes
    for i, news in enumerate(news_items, 1):
        # Escapar HTML
        safe_title = html.escape(news['title'])
        safe_description = html.escape(news['description'][:200] + '...' if len(news['description']) > 200 else news['description'])
        safe_source = html.escape(news['source'])
        
        # Thumbnail
        thumbnail_html = ""
        if news.get('has_image') and news.get('thumbnail'):
            thumbnail_html = f"""
            <div style="
                width: 120px;
                height: 80px;
                border-radius: 8px;
                overflow: hidden;
                background: #f5f5f7;
                flex-shrink: 0;
            ">
                <img src="{news['thumbnail']}" 
                     style="width: 100%; height: 100%; object-fit: cover;"
                     onerror="this.style.display='none'">
            </div>
            """
        
        # Source icon
        source_icon_html = ""
        if news.get('source_icon'):
            source_icon_html = f"""
            <img src="{news['source_icon']}" 
                 style="width: 16px; height: 16px; border-radius: 2px; margin-right: 0.25rem;"
                 onerror="this.style.display='none'">
            """
        
        html_content += f"""
        <div style="
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            display: flex;
            gap: 1rem;
        " onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
           onmouseout="this.style.boxShadow='none'">
            
            {thumbnail_html}
            
            <div style="flex: 1; min-width: 0;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <a href="{news['url']}" target="_blank" style="
                        color: #007AFF;
                        text-decoration: none;
                        font-weight: 600;
                        font-size: 1.05rem;
                        line-height: 1.4;
                    ">
                        {safe_title}
                    </a>
                </div>
                
                <p style="color: #6e6e73; margin: 0.5rem 0; line-height: 1.5; font-size: 0.9rem;">
                    {safe_description}
                </p>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                    <div style="font-size: 0.85rem; color: #86868b; display: flex; align-items: center;">
                        {source_icon_html}
                        {safe_source} · {news['date_display']}
                    </div>
                    <div style="
                        background: #007AFF15;
                        color: #007AFF;
                        padding: 0.25rem 0.5rem;
                        border-radius: 4px;
                        font-size: 0.75rem;
                        font-weight: 600;
                    ">
                        {news['relevance']}%
                    </div>
                </div>
            </div>
        </div>
        """
    
    return html_content


def render_news_mini_widget(news_items: List[Dict], max_items: int = 3) -> str:
    """
    Renderiza mini widget de noticias para dashboard principal
    
    Args:
        news_items: Lista de noticias
        max_items: Máximo de noticias a mostrar (default: 3)
    
    Returns:
        HTML del widget compacto
    """
    if not news_items:
        return ""
    
    import html
    
    top_news = news_items[:max_items]
    
    html_content = """
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">📰 Últimas Noticias</h4>
    """
    
    for news in top_news:
        safe_title = html.escape(news['title'])
        safe_source = html.escape(news['source'])
        
        thumbnail_html = ""
        if news.get('has_image') and news.get('thumbnail'):
            thumbnail_html = f"""
            <img src="{news['thumbnail']}" 
                 style="width: 50px; height: 50px; border-radius: 6px; object-fit: cover;"
                 onerror="this.style.display='none'">
            """
        
        html_content += f"""
        <a href="{news['url']}" target="_blank" style="
            display: flex;
            gap: 0.75rem;
            align-items: center;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            text-decoration: none;
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#f5f5f7'" 
           onmouseout="this.style.background='transparent'">
            {thumbnail_html}
            <div style="flex: 1; min-width: 0;">
                <div style="
                    color: #1d1d1f;
                    font-weight: 500;
                    font-size: 0.9rem;
                    line-height: 1.3;
                    margin-bottom: 0.25rem;
                ">
                    {safe_title}
                </div>
                <div style="font-size: 0.8rem; color: #86868b;">
                    {safe_source} · {news['date_display']}
                </div>
            </div>
        </a>
        """
    
    total = len(news_items)
    if total > max_items:
        html_content += f"""
        <div style="
            text-align: center;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(0,0,0,0.08);
        ">
            <span style="
                color: #007AFF;
                font-size: 0.9rem;
                font-weight: 500;
            ">
                Ver todas las noticias ({total}) →
            </span>
        </div>
        """
    
    html_content += "</div>"
    
    return html_content
