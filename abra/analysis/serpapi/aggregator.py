"""
SerpAPI Aggregator
Combina inteligentemente datos de múltiples APIs
"""
from typing import Dict, Optional
from .client import SerpAPIClient, get_serpapi_client
from .brands import extract_related_brands, render_related_brands_serpapi
from .searches import extract_related_searches, render_related_searches
from .insights import extract_top_insights, render_top_insights, render_insights_mini_widget
from .shopping import extract_shopping_results, analyze_shopping_results, render_shopping_results, render_shopping_mini_widget
from .questions import extract_related_questions, analyze_question_intent, render_related_questions, render_questions_mini_widget
from .stories import extract_top_stories, analyze_story_sentiment, render_top_stories, render_stories_mini_widget

class SerpAPIAggregator:
    """
    Agrega datos de múltiples endpoints SerpAPI de forma eficiente
    """
    
    def __init__(self, api_key: str):
        self.client = SerpAPIClient(api_key)
    
    def analyze_brand(self, brand_name: str, country: str = 'es') -> Dict:
        """
        Análisis completo de marca usando múltiples APIs
        
        Args:
            brand_name: Nombre de marca
            country: Código de país
        
        Returns:
            Dict con todos los datos agregados
        """
        # Búsqueda base (incluye related searches, brands, insights, questions)
        base_search = self.client.search('google', {
            'q': brand_name,
            'gl': country
        })
        
        # Related brands y searches
        related_brands = extract_related_brands(base_search, brand_name)
        related_searches = extract_related_searches(base_search)
        
        # Top insights (knowledge graph)
        insights = extract_top_insights(base_search)
        
        # Related questions
        questions = extract_related_questions(base_search)
        question_intent = analyze_question_intent(questions)
        
        # Noticias
        news = self.client.google_news(brand_name, country)
        
        # Top stories
        stories_search = self.client.top_stories(brand_name, country)
        stories = extract_top_stories(stories_search)
        story_sentiment = analyze_story_sentiment(stories)
        
        # Shopping (productos de la marca)
        shopping_query = f"{brand_name} products"
        shopping = self.client.shopping_results(shopping_query, country)
        products = extract_shopping_results(shopping)
        shopping_analysis = analyze_shopping_results(products)
        
        return {
            'brand_name': brand_name,
            'country': country,
            'related_brands': related_brands,
            'related_searches': related_searches,
            'insights': insights,
            'questions': {
                'items': questions,
                'intent_analysis': question_intent
            },
            'news': news,
            'stories': {
                'items': stories,
                'sentiment_analysis': story_sentiment
            },
            'shopping': {
                'products': products,
                'analysis': shopping_analysis
            },
            'request_count': self.client.request_count
        }
    
    def get_light_analysis(self, brand_name: str, country: str = 'es') -> Dict:
        """
        Análisis ligero (solo 3 requests) para dashboard
        
        Args:
            brand_name: Nombre de marca
            country: Código de país
        
        Returns:
            Dict con datos esenciales
        """
        # Request 1: Base search (brands, searches, insights, questions)
        base_search = self.client.search('google', {
            'q': brand_name,
            'gl': country
        })
        
        insights = extract_top_insights(base_search)
        questions = extract_related_questions(base_search)
        
        # Request 2: Shopping
        shopping = self.client.shopping_results(f"{brand_name} products", country)
        products = extract_shopping_results(shopping)
        
        # Request 3: Stories
        stories_search = self.client.top_stories(brand_name, country)
        stories = extract_top_stories(stories_search)
        
        return {
            'insights': insights,
            'questions': questions[:3],  # Top 3
            'products': products[:3],  # Top 3
            'stories': stories[:3],  # Top 3
            'request_count': self.client.request_count
        }


def get_brand_intelligence(brand_name: str, country: str = 'es', 
                          api_key: Optional[str] = None,
                          mode: str = 'full') -> Optional[Dict]:
    """
    Función helper para obtener intelligence de marca
    
    Args:
        brand_name: Nombre de marca
        country: Código de país
        api_key: SerpAPI key
        mode: 'full' o 'light'
    
    Returns:
        Dict con análisis completo o None si no hay API key
    """
    client = get_serpapi_client(api_key)
    
    if not client:
        return None
    
    aggregator = SerpAPIAggregator(client.api_key)
    
    if mode == 'light':
        return aggregator.get_light_analysis(brand_name, country)
    else:
        return aggregator.analyze_brand(brand_name, country)
