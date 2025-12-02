"""
Related Questions / People Also Ask - SerpAPI
FAQ automático y customer intent discovery
"""
from typing import List, Dict, Optional
import html

def extract_related_questions(serpapi_data: Dict) -> List[Dict]:
    """
    Extrae preguntas relacionadas (People Also Ask)
    
    Args:
        serpapi_data: Respuesta de SerpAPI
    
    Returns:
        Lista de preguntas con respuestas
    """
    questions = []
    
    if not serpapi_data:
        return []
    
    # Related questions / People Also Ask
    if 'related_questions' in serpapi_data:
        for item in serpapi_data['related_questions']:
            question = item.get('question', '')
            snippet = item.get('snippet', '')
            title = item.get('title', '')
            link = item.get('link', '')
            
            # Date si disponible
            date = item.get('date', '')
            
            # Source info
            displayed_link = item.get('displayed_link', '')
            
            questions.append({
                'question': question,
                'answer': snippet,
                'source_title': title,
                'source_link': link,
                'source_domain': displayed_link,
                'date': date,
                'category': categorize_question(question)
            })
    
    return questions


def categorize_question(question: str) -> str:
    """
    Categoriza pregunta por intención
    
    Args:
        question: Pregunta
    
    Returns:
        Categoría
    """
    question_lower = question.lower()
    
    # Patterns
    if any(word in question_lower for word in ['qué es', 'what is', 'define', 'significa']):
        return 'Definición'
    
    if any(word in question_lower for word in ['cómo', 'how to', 'como hacer']):
        return 'How-To'
    
    if any(word in question_lower for word in ['cuánto', 'precio', 'cost', 'how much']):
        return 'Precio'
    
    if any(word in question_lower for word in ['mejor', 'best', 'top', 'recomend']):
        return 'Recomendación'
    
    if any(word in question_lower for word in ['por qué', 'why', 'porque']):
        return 'Explicación'
    
    if any(word in question_lower for word in ['cuándo', 'when', 'when to']):
        return 'Timing'
    
    if any(word in question_lower for word in ['dónde', 'where', 'donde comprar']):
        return 'Ubicación'
    
    if any(word in question_lower for word in ['comparar', 'vs', 'versus', 'diferencia']):
        return 'Comparación'
    
    return 'General'


def analyze_question_intent(questions: List[Dict]) -> Dict:
    """
    Analiza intención de preguntas
    
    Args:
        questions: Lista de preguntas
    
    Returns:
        Análisis de intenciones
    """
    if not questions:
        return {}
    
    # Contar por categoría
    category_count = {}
    for q in questions:
        cat = q['category']
        category_count[cat] = category_count.get(cat, 0) + 1
    
    # Top categoría
    top_category = max(category_count.items(), key=lambda x: x[1])
    
    # Customer journey stage
    stages = {
        'Awareness': ['Definición', 'Explicación'],
        'Consideration': ['Comparación', 'Recomendación', 'Precio'],
        'Decision': ['How-To', 'Ubicación', 'Timing']
    }
    
    stage_count = {}
    for stage, cats in stages.items():
        count = sum(category_count.get(cat, 0) for cat in cats)
        if count > 0:
            stage_count[stage] = count
    
    top_stage = max(stage_count.items(), key=lambda x: x[1])[0] if stage_count else 'Unknown'
    
    return {
        'total_questions': len(questions),
        'categories': category_count,
        'top_category': top_category[0],
        'top_stage': top_stage,
        'customer_intent': get_intent_description(top_stage)
    }


def get_intent_description(stage: str) -> str:
    """
    Descripción de intención por stage
    
    Args:
        stage: Customer journey stage
    
    Returns:
        Descripción
    """
    descriptions = {
        'Awareness': 'Los usuarios están descubriendo y aprendiendo sobre el tema',
        'Consideration': 'Los usuarios están comparando opciones y evaluando',
        'Decision': 'Los usuarios están listos para comprar o implementar',
        'Unknown': 'Intención mixta o no clara'
    }
    
    return descriptions.get(stage, descriptions['Unknown'])


def render_related_questions(questions: List[Dict], 
                             intent_analysis: Optional[Dict] = None) -> str:
    """
    Renderiza preguntas relacionadas
    
    Args:
        questions: Lista de preguntas
        intent_analysis: Análisis de intención
    
    Returns:
        HTML string
    """
    if not questions:
        return """
        <div style="text-align: center; padding: 2rem; color: #6e6e73;">
            <p>❓ No se encontraron preguntas relacionadas</p>
            <small>Intenta con un tema más popular</small>
        </div>
        """
    
    html_content = ""
    
    # Intent analysis header
    if intent_analysis:
        top_stage = intent_analysis['top_stage']
        intent_desc = intent_analysis['customer_intent']
        
        stage_colors = {
            'Awareness': '#5856D6',
            'Consideration': '#FF9500',
            'Decision': '#34C759',
            'Unknown': '#6e6e73'
        }
        
        stage_icons = {
            'Awareness': '🔍',
            'Consideration': '⚖️',
            'Decision': '✅',
            'Unknown': '❓'
        }
        
        color = stage_colors.get(top_stage, '#6e6e73')
        icon = stage_icons.get(top_stage, '❓')
        
        html_content += f"""
        <div style="
            background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
            border-left: 4px solid {color};
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="font-size: 2rem;">{icon}</div>
                <div>
                    <div style="
                        font-size: 0.85rem;
                        color: {color};
                        font-weight: 600;
                        margin-bottom: 0.5rem;
                        text-transform: uppercase;
                    ">Customer Intent: {top_stage}</div>
                    <div style="
                        color: #1d1d1f;
                        font-size: 0.95rem;
                        line-height: 1.6;
                    ">{intent_desc}</div>
                </div>
            </div>
        </div>
        """
        
        # Categories breakdown
        if intent_analysis.get('categories'):
            html_content += """
            <div style="margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 0.75rem;">📊 Distribución por Categoría</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
            """
            
            category_colors = {
                'Definición': '#5856D6',
                'How-To': '#007AFF',
                'Precio': '#FF9500',
                'Recomendación': '#34C759',
                'Explicación': '#FF3B30',
                'Comparación': '#FF2D55',
                'Ubicación': '#5AC8FA',
                'Timing': '#FFCC00',
                'General': '#6e6e73'
            }
            
            for cat, count in sorted(intent_analysis['categories'].items(), 
                                    key=lambda x: x[1], reverse=True):
                cat_color = category_colors.get(cat, '#6e6e73')
                
                html_content += f"""
                <div style="
                    background: {cat_color}20;
                    border: 1px solid {cat_color}40;
                    color: {cat_color};
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 600;
                ">
                    {cat} ({count})
                </div>
                """
            
            html_content += """
                </div>
            </div>
            """
    
    # Questions accordion
    html_content += '<div style="margin-top: 1.5rem;">'
    
    for i, q in enumerate(questions, 1):
        safe_question = html.escape(q['question'])
        safe_answer = html.escape(q['answer'][:400] + '...' if len(q['answer']) > 400 else q['answer'])
        safe_source = html.escape(q.get('source_domain', 'Google'))
        
        category = q.get('category', 'General')
        cat_color = {
            'Definición': '#5856D6',
            'How-To': '#007AFF',
            'Precio': '#FF9500',
            'Recomendación': '#34C759',
            'Explicación': '#FF3B30',
            'Comparación': '#FF2D55',
            'Ubicación': '#5AC8FA',
            'Timing': '#FFCC00',
            'General': '#6e6e73'
        }.get(category, '#6e6e73')
        
        html_content += f"""
        <details style="
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-left: 4px solid {cat_color};
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            cursor: pointer;
        ">
            <summary style="
                font-weight: 600;
                color: #1d1d1f;
                font-size: 1rem;
                line-height: 1.4;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            ">
                <span style="
                    background: {cat_color};
                    color: white;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.85rem;
                    font-weight: 700;
                    flex-shrink: 0;
                ">{i}</span>
                <span style="flex: 1;">{safe_question}</span>
                <span style="
                    background: {cat_color}20;
                    color: {cat_color};
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    font-weight: 600;
                ">{category}</span>
            </summary>
            
            <div style="
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(0,0,0,0.05);
            ">
                <div style="
                    color: #1d1d1f;
                    line-height: 1.6;
                    font-size: 0.95rem;
                    margin-bottom: 1rem;
                ">{safe_answer}</div>
                
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.85rem;
                    color: #6e6e73;
                ">
                    <div>📰 Fuente: {safe_source}</div>
                    {f'<div>📅 {html.escape(q["date"])}</div>' if q.get('date') else ''}
                </div>
            </div>
        </details>
        """
    
    html_content += '</div>'
    
    return html_content


def render_questions_mini_widget(questions: List[Dict], max_items: int = 3) -> str:
    """
    Widget compacto de preguntas para dashboard
    
    Args:
        questions: Lista de preguntas
        max_items: Máximo de preguntas
    
    Returns:
        HTML compacto
    """
    if not questions:
        return ""
    
    html_content = """
    <div style="
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1d1d1f;">❓ People Also Ask</h4>
    """
    
    for q in questions[:max_items]:
        safe_question = html.escape(q['question'][:100] + '...' if len(q['question']) > 100 else q['question'])
        
        cat_color = {
            'Definición': '#5856D6',
            'How-To': '#007AFF',
            'Precio': '#FF9500',
            'Recomendación': '#34C759',
            'General': '#6e6e73'
        }.get(q.get('category', 'General'), '#6e6e73')
        
        html_content += f"""
        <div style="
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid {cat_color};
            background: {cat_color}10;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #1d1d1f;
            line-height: 1.5;
        ">
            {safe_question}
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
                Ver todas las preguntas →
            </span>
        </div>
    </div>
    """
    
    return html_content
