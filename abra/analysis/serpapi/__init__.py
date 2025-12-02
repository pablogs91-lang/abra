"""
SerpAPI Package
Complete integration of all SerpAPI endpoints
"""

# Client
from .client import SerpAPIClient, get_serpapi_client

# Brands
from .brands import (
    extract_related_brands,
    render_related_brands_serpapi
)

# Searches
from .searches import (
    extract_related_searches,
    render_related_searches
)

# Insights
from .insights import (
    extract_top_insights,
    render_top_insights,
    render_insights_mini_widget
)

# Shopping
from .shopping import (
    extract_shopping_results,
    analyze_shopping_results,
    render_shopping_results,
    render_shopping_mini_widget
)

# Questions (Phase 3)
from .questions import (
    extract_related_questions,
    analyze_question_intent,
    render_related_questions,
    render_questions_mini_widget
)

# Stories (Phase 3)
from .stories import (
    extract_top_stories,
    analyze_story_sentiment,
    render_top_stories,
    render_stories_mini_widget
)

# Aggregator
from .aggregator import (
    SerpAPIAggregator,
    get_brand_intelligence
)

__all__ = [
    # Client
    'SerpAPIClient',
    'get_serpapi_client',
    
    # Brands
    'extract_related_brands',
    'render_related_brands_serpapi',
    
    # Searches
    'extract_related_searches',
    'render_related_searches',
    
    # Insights
    'extract_top_insights',
    'render_top_insights',
    'render_insights_mini_widget',
    
    # Shopping
    'extract_shopping_results',
    'analyze_shopping_results',
    'render_shopping_results',
    'render_shopping_mini_widget',
    
    # Questions
    'extract_related_questions',
    'analyze_question_intent',
    'render_related_questions',
    'render_questions_mini_widget',
    
    # Stories
    'extract_top_stories',
    'analyze_story_sentiment',
    'render_top_stories',
    'render_stories_mini_widget',
    
    # Aggregator
    'SerpAPIAggregator',
    'get_brand_intelligence'
]
