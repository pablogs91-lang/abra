"""
Top Stories - SerpAPI
Breaking news y trending topics
"""
from typing import List, Dict, Optional
import html
from datetime import datetime, timedelta

def extract_top_stories(serpapi_data: Dict) -> List[Dict]:
    """
    Extrae top stories (breaking news)
    
    Args:
        serpapi_data: Respuesta de SerpAPI (news search)
    
    Returns:
        Lista de stories
    """
    stories = []
    
    if not serpapi_data:
        return []
    
    # Top stories carousel
    if 'top_stories' in serpapi_data:
        for item in serpapi_data['top_stories']:
            story = {
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'source': item.get('source', ''),
                'date': item.get('date', ''),
                'thumbnail': item.get('thumbnail', ''),
                'type': 'top_story'
            }
            stories.append(story)
    
    # News results
    if 'news_results' in serpapi_data:
        for item in serpapi_data['news_results']:
            story = {
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'source': item.get('source', ''),
                'date': item.get('date', ''),
                'snippet': item.get('snippet', ''),
                'thumbnail': item.get('thumbnail', ''),
                'type': 'news'
            }
            stories.append(story)
    
    return stories


def classify_story_urgency(story: Dict) -> str:
    """
    Clasifica urgencia de noticia
    
    Args:
        story: Dict de story
    
    Returns:
        Nivel de urgencia
    """
    date_str = story.get('date', '').lower()
    title = story.get('title', '').lower()
    
    # Breaking keywords
    breaking_keywords = ['breaking', 'urgente', 'última hora', 'just in', 'ahora']
    
    if any(kw in title or kw in date_str for kw in breaking_keywords):
        return 'Breaking'
    
    # Recent (horas)
    time_keywords = ['ago', 'hour', 'hours', 'hace', 'hora', 'horas', 'min']
    
    if any(kw in date_str for kw in time_keywords):
        return 'Recent'
    
    # Today/yesterday
    today_keywords = ['today', 'hoy', 'yesterday', 'ayer']
    
    if any(kw in date_str for kw in today_keywords):
        return 'Today'
    
    return 'Older'


def analyze_story_sentiment(stories: List[Dict]) -> Dict:
    """
    Analiza sentimiento de stories
    
    Args:
        stories: Lista de stories
    
    Returns:
        Análisis de sentimiento
    """
    if not stories:
        return {}
    
    positive_keywords = [
        'lanza', 'presenta', 'innova', 'crece', 'líder', 'mejor', 'éxito',
        'gana', 'premio', 'récord', 'destaca', 'revoluciona'
    ]
    
    negative_keywords = [
        'problema', 'fallo', 'error', 'critica', 'baja', 'pierde',
        'crisis', 'escándalo', 'multa', 'cierra', 'despide'
    ]
    
    neutral_keywords = [
        'anuncia', 'dice', 'informa', 'reporta', 'confirma', 'declara'
    ]
    
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for story in stories:
        text = (story.get('title', '') + ' ' + story.get('snippet', '')).lower()
        
        pos_score = sum(1 for kw in positive_keywords if kw in text)
        neg_score = sum(1 for kw in negative_keywords if kw in text)
        neu_score = sum(1 for kw in neutral_keywords if kw in text)
        
        if pos_score > neg_score and pos_score > neu_score:
            positive_count += 1
        elif neg_score > pos_score and neg_score > neu_score:
            negative_count += 1
        else:
            neutral_count += 1
    
    total = len(stories)
    
    if positive_count > total * 0.5:
        overall = 'positive'
    elif negative_count > total * 0.5:
        overall = 'negative'
    else:
        overall = 'neutral'
    
    return {
        'overall_sentiment': overall,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'positive_pct': (positive_count / total * 100) if total > 0 else 0,
        'negative_pct': (negative_count / total * 100) if total > 0 else 0
    }


def render_top_stories(stories: List[Dict], 
                       sentiment_analysis: Optional[Dict] = None) -> str:
    """
    Renderiza top stories
    
    Args:
        stories: Lista de stories
        sentiment_analysis: Análisis de sentimiento
    
    Returns:
        HTML string
    """
    if not stories:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>📰 No se encontraron breaking news</p>
            <small>Intenta con un tema más activo</small>
        </div>
        """
    
    html_content = ""
    
    # Sentiment header
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
        
        sentiment = sentiment_analysis['overall_sentiment']
        color = sentiment_colors[sentiment]
        icon = sentiment_icons[sentiment]
        
        html_content += f"""
        <div style="
            background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
            border-left: 4px solid {color};
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <div>
                    <strong>Buzz General: {sentiment.title()}</strong>
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
    
    # Group by urgency
    breaking = [s for s in stories if classify_story_urgency(s) == 'Breaking']
    recent = [s for s in stories if classify_story_urgency(s) == 'Recent']
    today = [s for s in stories if classify_story_urgency(s) == 'Today']
    older = [s for s in stories if classify_story_urgency(s) == 'Older']
    
    # Breaking stories
    if breaking:
        html_content += """
        <div style="margin-bottom: 1.5rem;">
            <h4 style="
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: #FF3B30;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
                animation: pulse 2s infinite;
            ">
                🚨 BREAKING NEWS
            </h4>
        </div>
        <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        </style>
        """
        
        html_content += render_story_grid(breaking, urgency='breaking')
    
    # Recent stories
    if recent:
        html_content += '<h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">⚡ Últimas Horas</h4>'
        html_content += render_story_grid(recent, urgency='recent')
    
    # Today stories
    if today:
        html_content += '<h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">📅 Hoy</h4>'
        html_content += render_story_grid(today, urgency='today')
    
    # Older stories
    if older and len(breaking + recent + today) < 10:
        html_content += '<h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">📰 Anteriores</h4>'
        html_content += render_story_grid(older[:5], urgency='older')
    
    return html_content


def render_story_grid(stories: List[Dict], urgency: str = 'normal') -> str:
    """
    Renderiza grid de stories
    
    Args:
        stories: Lista de stories
        urgency: Nivel de urgencia
    
    Returns:
        HTML grid
    """
    urgency_colors = {
        'breaking': '#FF3B30',
        'recent': '#FF9500',
        'today': '#007AFF',
        'older': '#6e6e73'
    }
    
    border_color = urgency_colors.get(urgency, '#6e6e73')
    
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">'
    
    for story in stories:
        safe_title = html.escape(story['title'])
        safe_source = html.escape(story.get('source', 'Unknown'))
        safe_snippet = html.escape(story.get('snippet', '')[:150] + '...' if len(story.get('snippet', '')) > 150 else story.get('snippet', ''))
        
        # Thumbnail
        thumbnail_html = ""
        if story.get('thumbnail'):
            thumbnail_html = f"""
            <div style="
                width: 100%;
                height: 160px;
                border-radius: 8px;
                overflow: hidden;
                background: #f5f5f7;
                margin-bottom: 1rem;
            ">
                <img src="{story['thumbnail']}" 
                     style="width: 100%; height: 100%; object-fit: cover;"
                     onerror="this.parentElement.style.display='none'">
            </div>
            """
        
        html += f"""
        <a href="{story.get('link', '#')}" target="_blank" style="text-decoration: none;">
            <div style="
                background: white;
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
                height: 100%;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                
                {thumbnail_html}
                
                <div style="
                    font-weight: 700;
                    color: #1d1d1f;
                    font-size: 1.05rem;
                    line-height: 1.3;
                    margin-bottom: 0.75rem;
                ">{safe_title}</div>
                
                {f'<div style="color: #6e6e73; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.75rem;">{safe_snippet}</div>' if safe_snippet else ''}
                
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.85rem;
                    color: #6e6e73;
                    margin-top: auto;
                    padding-top: 0.75rem;
                    border-top: 1px solid rgba(0,0,0,0.05);
                ">
                    <div>📰 {safe_source}</div>
                    <div>{html.escape(story.get('date', ''))}</div>
                </div>
            </div>
        </a>
        """
    
    html += '</div>'
    
    return html


def render_stories_mini_widget(stories: List[Dict], max_items: int = 3) -> str:
    """
    Widget compacto de stories para dashboard
    
    Args:
        stories: Lista de stories
        max_items: Máximo de stories
    
    Returns:
        HTML compacto
    """
    if not stories:
        return ""
    
    # Priorizar breaking > recent > today
    sorted_stories = sorted(
        stories,
        key=lambda s: {'Breaking': 0, 'Recent': 1, 'Today': 2, 'Older': 3}.get(
            classify_story_urgency(s), 3
        )
    )[:max_items]
    
    html_content = """
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">🚨 Breaking Stories</h4>
    """
    
    for story in sorted_stories:
        safe_title = html.escape(story['title'][:80] + '...' if len(story['title']) > 80 else story['title'])
        safe_source = html.escape(story.get('source', 'Unknown'))
        
        urgency = classify_story_urgency(story)
        urgency_colors = {
            'Breaking': '#FF3B30',
            'Recent': '#FF9500',
            'Today': '#007AFF',
            'Older': '#6e6e73'
        }
        urgency_color = urgency_colors.get(urgency, '#6e6e73')
        
        html_content += f"""
        <a href="{story.get('link', '#')}" target="_blank" style="
            display: flex;
            gap: 0.75rem;
            align-items: start;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            text-decoration: none;
            border-left: 3px solid {urgency_color};
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#f5f5f7'" 
           onmouseout="this.style.background='transparent'">
            
            <div style="flex: 1; min-width: 0;">
                <div style="
                    color: #1d1d1f;
                    font-weight: 600;
                    font-size: 0.9rem;
                    line-height: 1.3;
                    margin-bottom: 0.25rem;
                ">
                    {safe_title}
                </div>
                <div style="font-size: 0.8rem; color: #86868b;">
                    {safe_source} · {html.escape(story.get('date', ''))}
                </div>
            </div>
            
            {f'<span style="background: {urgency_color}20; color: {urgency_color}; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 600; white-space: nowrap;">{urgency}</span>' if urgency == 'Breaking' else ''}
        </a>
        """
    
    html_content += """
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
                Ver todas las stories →
            </span>
        </div>
    </div>
    """
    
    return html_content
