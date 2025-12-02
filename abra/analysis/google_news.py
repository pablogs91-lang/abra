"""
Google News Integration
Extrae noticias relacionadas con marca/producto
"""
import requests
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus
import html

def get_google_news(query, country='ES', language='es', max_results=10):
    """
    Obtiene noticias de Google News relacionadas con la query
    
    Args:
        query: Marca o producto a buscar
        country: Código de país (ES, US, etc)
        language: Código de idioma (es, en, etc)
        max_results: Número máximo de resultados
    
    Returns:
        Lista de noticias con título, descripción, URL, fecha, fuente
    """
    try:
        # Usar Google News RSS (público y no requiere API key)
        encoded_query = quote_plus(query)
        
        # URL de Google News RSS
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl={language}&gl={country}&ceid={country}:{language}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        # Parsear RSS XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        news_items = []
        
        for item in root.findall('.//item')[:max_results]:
            try:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                source = item.find('source').text if item.find('source') is not None else 'Google News'
                
                # Limpiar descripción HTML
                description_clean = re.sub('<[^<]+?>', '', description) if description else ''
                
                # Parsear fecha
                try:
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    date_formatted = date_obj.strftime('%Y-%m-%d')
                    days_ago = (datetime.now() - date_obj).days
                    date_display = f"Hace {days_ago} días" if days_ago > 0 else "Hoy"
                except:
                    date_formatted = ''
                    date_display = pub_date
                
                news_items.append({
                    'title': title,
                    'description': description_clean,
                    'url': link,
                    'date': date_formatted,
                    'date_display': date_display,
                    'source': source,
                    'relevance': calculate_relevance(title, description_clean, query)
                })
            except:
                continue
        
        # Ordenar por relevancia
        news_items.sort(key=lambda x: x['relevance'], reverse=True)
        
        return news_items
    
    except Exception as e:
        print(f"Error fetching Google News: {e}")
        return []


def calculate_relevance(title, description, query):
    """
    Calcula relevancia de noticia respecto a query
    
    Args:
        title: Título de noticia
        description: Descripción
        query: Query de búsqueda
    
    Returns:
        Score de relevancia (0-100)
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
        if len(word) > 3:  # Ignorar palabras cortas
            if word in title_lower:
                score += 10
            if word in desc_lower:
                score += 5
    
    return min(score, 100)


def analyze_news_sentiment(news_items):
    """
    Análisis simple de sentimiento de noticias
    
    Args:
        news_items: Lista de noticias
    
    Returns:
        Análisis de sentimiento agregado
    """
    if not news_items:
        return {
            'overall_sentiment': 'neutral',
            'positive_count': 0,
            'neutral_count': 0,
            'negative_count': 0
        }
    
    positive_keywords = [
        'éxito', 'lanza', 'innova', 'crece', 'líder', 'mejor', 'mejora',
        'gana', 'premio', 'récord', 'popular', 'demanda', 'estrella',
        'revoluciona', 'destaca', 'triunfa', 'logra'
    ]
    
    negative_keywords = [
        'problema', 'fallo', 'defecto', 'error', 'critica', 'baja',
        'pierde', 'retira', 'crisis', 'escándalo', 'demanda', 'multa',
        'cierra', 'despide', 'recorta'
    ]
    
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    
    for news in news_items:
        text = (news['title'] + ' ' + news['description']).lower()
        
        pos_score = sum(1 for word in positive_keywords if word in text)
        neg_score = sum(1 for word in negative_keywords if word in text)
        
        if pos_score > neg_score:
            positive_count += 1
        elif neg_score > pos_score:
            negative_count += 1
        else:
            neutral_count += 1
    
    total = len(news_items)
    
    # Sentimiento general
    if positive_count > total * 0.5:
        overall = 'positive'
    elif negative_count > total * 0.5:
        overall = 'negative'
    else:
        overall = 'neutral'
    
    return {
        'overall_sentiment': overall,
        'positive_count': positive_count,
        'neutral_count': neutral_count,
        'negative_count': negative_count,
        'positive_pct': (positive_count / total * 100) if total > 0 else 0,
        'negative_pct': (negative_count / total * 100) if total > 0 else 0
    }


def render_news_panel(news_items, sentiment_analysis=None):
    """
    Renderiza panel de noticias en HTML
    
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
    
    html = ""
    
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
        
        html += f"""
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
    
    # Noticias
    for i, news in enumerate(news_items, 1):
        # Escapar HTML
        safe_title = html.escape(news['title'])
        safe_description = html.escape(news['description'][:200] + '...' if len(news['description']) > 200 else news['description'])
        safe_source = html.escape(news['source'])
        
        html += f"""
        <div style="
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        " onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
           onmouseout="this.style.boxShadow='none'">
            
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <div style="flex: 1;">
                    <a href="{news['url']}" target="_blank" style="
                        color: #007AFF;
                        text-decoration: none;
                        font-weight: 600;
                        font-size: 1.05rem;
                    ">
                        {i}. {safe_title}
                    </a>
                </div>
                <div style="
                    background: #F5F5F7;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    color: #6e6e73;
                    white-space: nowrap;
                    margin-left: 1rem;
                ">
                    {news['date_display']}
                </div>
            </div>
            
            <p style="color: #6e6e73; margin: 0.5rem 0; line-height: 1.5;">
                {safe_description}
            </p>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                <div style="font-size: 0.85rem; color: #86868b;">
                    📰 {safe_source}
                </div>
                <div style="
                    background: #007AFF15;
                    color: #007AFF;
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 600;
                ">
                    Relevancia: {news['relevance']}%
                </div>
            </div>
        </div>
        """
    
    return html
