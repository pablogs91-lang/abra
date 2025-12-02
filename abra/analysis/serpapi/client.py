"""
SerpAPI Unified Client
Base client for all SerpAPI endpoints with intelligent caching
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os

class SerpAPIClient:
    """
    Cliente base unificado para todas las APIs de SerpAPI
    
    Features:
    - Cache inteligente 24h
    - Rate limiting awareness
    - Error handling robusto
    - Logging opcional
    """
    
    def __init__(self, api_key: str, cache_duration_hours: int = 24):
        """
        Inicializa cliente SerpAPI
        
        Args:
            api_key: SerpAPI API key
            cache_duration_hours: Duración del cache (default: 24h)
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.cache = {}
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.request_count = 0
    
    def _get_cache_key(self, engine: str, params: Dict) -> str:
        """Genera key única para cache"""
        # Ordenar params para key consistente
        sorted_params = sorted(params.items())
        params_str = "_".join(f"{k}={v}" for k, v in sorted_params)
        return f"{engine}_{params_str}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica si cache es válido"""
        if cache_key not in self.cache:
            return False
        
        cached_data, cached_time = self.cache[cache_key]
        return datetime.now() - cached_time < self.cache_duration
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Obtiene datos del cache si son válidos"""
        if self._is_cache_valid(cache_key):
            cached_data, _ = self.cache[cache_key]
            return cached_data
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Guarda datos en cache"""
        self.cache[cache_key] = (data, datetime.now())
    
    def search(self, engine: str, params: Dict, use_cache: bool = True) -> Optional[Dict]:
        """
        Búsqueda genérica en SerpAPI
        
        Args:
            engine: Engine name (google, google_news, etc)
            params: Query parameters
            use_cache: Si usar cache (default: True)
        
        Returns:
            Dict con resultados o None si error
        """
        # Check cache
        cache_key = self._get_cache_key(engine, params)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        # Build request params
        request_params = {
            'engine': engine,
            'api_key': self.api_key,
            **params
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=request_params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            self.request_count += 1
            
            # Save to cache
            if use_cache:
                self._save_to_cache(cache_key, data)
            
            return data
        
        except requests.exceptions.Timeout:
            print(f"SerpAPI timeout for engine: {engine}")
            return None
        
        except requests.exceptions.HTTPError as e:
            print(f"SerpAPI HTTP error: {e}")
            return None
        
        except Exception as e:
            print(f"SerpAPI error: {e}")
            return None
    
    def google_news(self, query: str, country: str = 'es', 
                   language: str = 'es', num: int = 15) -> Optional[Dict]:
        """
        Google News API
        
        Args:
            query: Search query
            country: Country code (es, us, etc)
            language: Language code (es, en, etc)
            num: Number of results
        
        Returns:
            News results
        """
        params = {
            'q': query,
            'gl': country,
            'hl': language,
            'num': num
        }
        return self.search('google_news', params)
    
    def related_brands(self, query: str, country: str = 'es') -> Optional[Dict]:
        """
        Related Brands API
        
        Args:
            query: Brand name
            country: Country code
        
        Returns:
            Related brands with similarity scores
        """
        params = {
            'q': query,
            'gl': country
        }
        return self.search('google', params)  # Related brands en results
    
    def related_searches(self, query: str, country: str = 'es') -> Optional[Dict]:
        """
        Related Searches API
        
        Args:
            query: Search query
            country: Country code
        
        Returns:
            Related searches with thumbnails
        """
        params = {
            'q': query,
            'gl': country
        }
        return self.search('google', params)  # Related searches en results
    
    def top_insights(self, query: str, country: str = 'es') -> Optional[Dict]:
        """
        Top Insights / Things to Know API
        
        Args:
            query: Brand/topic query
            country: Country code
        
        Returns:
            Knowledge graph insights
        """
        params = {
            'q': query,
            'gl': country
        }
        return self.search('google', params)  # Knowledge graph en results
    
    def shopping_results(self, query: str, country: str = 'es',
                        num: int = 20) -> Optional[Dict]:
        """
        Shopping Results API
        
        Args:
            query: Product query
            country: Country code
            num: Number of results
        
        Returns:
            Shopping results with prices, ratings
        """
        params = {
            'q': query,
            'gl': country,
            'num': num,
            'tbm': 'shop'  # Shopping tab
        }
        return self.search('google_shopping', params)
    
    def related_questions(self, query: str, country: str = 'es') -> Optional[Dict]:
        """
        Related Questions / People Also Ask API
        
        Args:
            query: Query
            country: Country code
        
        Returns:
            Related questions with answers
        """
        params = {
            'q': query,
            'gl': country
        }
        return self.search('google', params)  # Related questions en results
    
    def top_stories(self, query: str, country: str = 'es') -> Optional[Dict]:
        """
        Top Stories API
        
        Args:
            query: Topic query
            country: Country code
        
        Returns:
            Breaking news stories
        """
        params = {
            'q': query,
            'gl': country,
            'tbm': 'nws'  # News tab
        }
        return self.search('google', params)
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de uso
        
        Returns:
            Dict con stats (requests, cache hits, etc)
        """
        cache_hits = sum(1 for k in self.cache if self._is_cache_valid(k))
        
        return {
            'total_requests': self.request_count,
            'cache_entries': len(self.cache),
            'cache_hits_potential': cache_hits,
            'cache_duration_hours': self.cache_duration.total_seconds() / 3600
        }


def get_serpapi_client(api_key: Optional[str] = None) -> Optional[SerpAPIClient]:
    """
    Factory function para obtener cliente SerpAPI
    
    Args:
        api_key: SerpAPI key (o None para buscar en env)
    
    Returns:
        Cliente SerpAPI o None si no hay key
    """
    if not api_key:
        api_key = os.getenv('SERPAPI_API_KEY')
    
    if not api_key:
        return None
    
    return SerpAPIClient(api_key)
