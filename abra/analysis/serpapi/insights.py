"""
Top Insights / Things to Know - SerpAPI
Insights automáticos de Knowledge Graph
"""
from typing import List, Dict, Optional
import html

def extract_top_insights(serpapi_data: Dict) -> Dict:
    """
    Extrae insights del Knowledge Graph y featured snippets
    
    Args:
        serpapi_data: Respuesta de SerpAPI
    
    Returns:
        Dict con insights organizados
    """
    insights = {
        'things_to_know': [],
        'key_facts': [],
        'description': '',
        'type': '',
        'attributes': {}
    }
    
    if not serpapi_data:
        return insights
    
    # Knowledge Graph
    if 'knowledge_graph' in serpapi_data:
        kg = serpapi_data['knowledge_graph']
        
        # Descripción principal
        if 'description' in kg:
            insights['description'] = kg['description']
        
        # Tipo de entidad
        if 'type' in kg:
            insights['type'] = kg['type']
        
        # Atributos clave
        for key in ['founded', 'headquarters', 'ceo', 'founders', 'products', 'subsidiaries']:
            if key in kg:
                insights['attributes'][key] = kg[key]
        
        # Profiles/facts
        if 'profiles' in kg:
            for profile in kg['profiles']:
                if 'facts' in profile:
                    insights['key_facts'].extend(profile['facts'])
    
    # Featured Snippet
    if 'answer_box' in serpapi_data:
        answer = serpapi_data['answer_box']
        
        if 'answer' in answer:
            insights['things_to_know'].append(answer['answer'])
        
        if 'snippet' in answer:
            insights['things_to_know'].append(answer['snippet'])
    
    # People Also Ask
    if 'related_questions' in serpapi_data:
        for question in serpapi_data['related_questions'][:5]:  # Top 5
            q_text = question.get('question', '')
            answer = question.get('snippet', '')
            
            if q_text and answer:
                insights['things_to_know'].append(f"{q_text}: {answer}")
    
    return insights


def render_top_insights(insights: Dict, brand_name: str) -> str:
    """
    Renderiza insights en formato visual
    
    Args:
        insights: Dict de insights
        brand_name: Nombre de marca
    
    Returns:
        HTML string
    """
    if not insights or not any([
        insights.get('description'),
        insights.get('things_to_know'),
        insights.get('key_facts'),
        insights.get('attributes')
    ]):
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>💡 No se encontraron insights automáticos</p>
            <small>Intenta con una marca más conocida</small>
        </div>
        """
    
    html_content = ""
    
    # Descripción principal
    if insights.get('description'):
        safe_desc = html.escape(insights['description'])
        entity_type = html.escape(insights.get('type', 'Brand'))
        
        html_content += f"""
        <div style="
            background: linear-gradient(135deg, #007AFF20 0%, #007AFF10 100%);
            border-left: 4px solid #007AFF;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="
                    font-size: 2rem;
                    line-height: 1;
                ">💡</div>
                <div style="flex: 1;">
                    <div style="
                        font-size: 0.85rem;
                        color: #007AFF;
                        font-weight: 600;
                        margin-bottom: 0.5rem;
                        text-transform: uppercase;
                    ">{entity_type}</div>
                    <div style="
                        color: #1d1d1f;
                        font-size: 1rem;
                        line-height: 1.6;
                    ">{safe_desc}</div>
                </div>
            </div>
        </div>
        """
    
    # Atributos clave
    if insights.get('attributes'):
        html_content += """
        <h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">📋 Datos Clave</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        """
        
        attribute_icons = {
            'founded': '📅',
            'headquarters': '🏢',
            'ceo': '👤',
            'founders': '🎯',
            'products': '📦',
            'subsidiaries': '🏛️'
        }
        
        for key, value in insights['attributes'].items():
            icon = attribute_icons.get(key, '📌')
            key_display = key.replace('_', ' ').title()
            safe_value = html.escape(str(value))
            
            html_content += f"""
            <div style="
                background: white;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 8px;
                padding: 1rem;
            ">
                <div style="
                    font-size: 1.2rem;
                    margin-bottom: 0.5rem;
                ">{icon}</div>
                <div style="
                    font-size: 0.75rem;
                    color: #6e6e73;
                    text-transform: uppercase;
                    margin-bottom: 0.25rem;
                ">{key_display}</div>
                <div style="
                    color: #1d1d1f;
                    font-weight: 600;
                    font-size: 0.9rem;
                ">{safe_value}</div>
            </div>
            """
        
        html_content += "</div>"
    
    # Things to Know
    if insights.get('things_to_know'):
        html_content += """
        <h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">🔍 Things to Know</h4>
        """
        
        for i, insight in enumerate(insights['things_to_know'][:5], 1):
            safe_insight = html.escape(insight[:300] + '...' if len(insight) > 300 else insight)
            
            html_content += f"""
            <div style="
                background: white;
                border: 1px solid rgba(0,0,0,0.08);
                border-left: 4px solid #34C759;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
            ">
                <div style="display: flex; gap: 0.75rem;">
                    <div style="
                        background: #34C759;
                        color: white;
                        width: 24px;
                        height: 24px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 0.75rem;
                        font-weight: 700;
                        flex-shrink: 0;
                    ">{i}</div>
                    <div style="
                        color: #1d1d1f;
                        line-height: 1.6;
                        font-size: 0.95rem;
                    ">{safe_insight}</div>
                </div>
            </div>
            """
    
    # Key Facts
    if insights.get('key_facts'):
        html_content += """
        <h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">⭐ Facts Destacados</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 0.75rem;">
        """
        
        for fact in insights['key_facts'][:6]:
            safe_fact = html.escape(str(fact))
            
            html_content += f"""
            <div style="
                background: linear-gradient(135deg, #5856D620 0%, #5856D610 100%);
                border: 1px solid #5856D640;
                border-radius: 8px;
                padding: 0.75rem;
                font-size: 0.9rem;
                color: #1d1d1f;
            ">
                ✓ {safe_fact}
            </div>
            """
        
        html_content += "</div>"
    
    return html_content


def render_insights_mini_widget(insights: Dict) -> str:
    """
    Widget compacto de insights para dashboard
    
    Args:
        insights: Dict de insights
    
    Returns:
        HTML compacto
    """
    if not insights or not insights.get('things_to_know'):
        return ""
    
    html_content = """
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">💡 Top Insights</h4>
    """
    
    for insight in insights['things_to_know'][:3]:
        safe_insight = html.escape(insight[:150] + '...' if len(insight) > 150 else insight)
        
        html_content += f"""
        <div style="
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid #34C759;
            background: #34C75910;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #1d1d1f;
            line-height: 1.5;
        ">
            {safe_insight}
        </div>
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
                Ver todos los insights →
            </span>
        </div>
    </div>
    """
    
    return html_content
