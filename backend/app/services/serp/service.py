"""
SERP Service - Search Engine Results Page API Integration
Fetches top ranking URLs for target queries
"""
import os
from typing import Dict, List, Optional
import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SERPService:
    """
    SERP API integration service
    Supports ValueSERP and can be extended for other providers
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "valueserp"
    ):
        """
        Initialize SERP service
        
        Args:
            api_key: API key for SERP provider
            provider: SERP API provider ('valueserp', 'serpapi', etc.)
        """
        self.api_key = api_key or os.getenv("VALUESERP_API_KEY") or os.getenv("SERP_API_KEY")
        self.provider = provider
        
        # Provider configurations
        self.providers = {
            'valueserp': {
                'base_url': 'https://api.valueserp.com/search',
                'requires_key': True
            },
            'serpapi': {
                'base_url': 'https://serpapi.com/search',
                'requires_key': True
            }
        }
        
        if self.provider not in self.providers:
            logger.warning(
                "unknown_serp_provider",
                provider=provider,
                available=list(self.providers.keys())
            )
    
    async def search(
        self,
        query: str,
        location: str = "United States",
        language: str = "en",
        num_results: int = 10,
        device: str = "desktop"
    ) -> Dict:
        """
        Search SERP API for query
        
        Args:
            query: Search query
            location: Geographic location for results
            language: Language code
            num_results: Number of results to return
            device: Device type ('desktop' or 'mobile')
            
        Returns:
            Dict with search results
        """
        if not self.api_key:
            logger.error("serp_api_key_missing")
            return {
                'error': 'SERP API key not configured',
                'query': query
            }
        
        try:
            logger.info(
                "serp_search_starting",
                query=query,
                location=location,
                num_results=num_results
            )
            
            if self.provider == 'valueserp':
                return await self._search_valueserp(
                    query, location, language, num_results, device
                )
            elif self.provider == 'serpapi':
                return await self._search_serpapi(
                    query, location, language, num_results, device
                )
            else:
                return {'error': f'Unsupported provider: {self.provider}'}
                
        except Exception as e:
            logger.error(
                "serp_search_failed",
                query=query,
                error=str(e)
            )
            return {
                'error': str(e),
                'query': query
            }
    
    async def _search_valueserp(
        self,
        query: str,
        location: str,
        language: str,
        num_results: int,
        device: str
    ) -> Dict:
        """Search using ValueSERP API"""
        params = {
            'api_key': self.api_key,
            'q': query,
            'location': location,
            'google_domain': 'google.com',
            'gl': 'us',
            'hl': language,
            'num': min(num_results, 100),  # ValueSERP max is 100
            'device': device,
            'output': 'json'
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.providers['valueserp']['base_url'],
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse ValueSERP response
        results = self._parse_valueserp_response(data, query)
        
        logger.info(
            "valueserp_search_complete",
            query=query,
            results_count=len(results.get('organic_results', []))
        )
        
        return results
    
    async def _search_serpapi(
        self,
        query: str,
        location: str,
        language: str,
        num_results: int,
        device: str
    ) -> Dict:
        """Search using SerpAPI"""
        params = {
            'api_key': self.api_key,
            'q': query,
            'location': location,
            'hl': language,
            'num': num_results,
            'device': device
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.providers['serpapi']['base_url'],
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse SerpAPI response
        results = self._parse_serpapi_response(data, query)
        
        logger.info(
            "serpapi_search_complete",
            query=query,
            results_count=len(results.get('organic_results', []))
        )
        
        return results
    
    def _parse_valueserp_response(self, data: Dict, query: str) -> Dict:
        """Parse ValueSERP API response into standard format"""
        organic_results = []
        
        for result in data.get('organic_results', []):
            organic_results.append({
                'position': result.get('position'),
                'title': result.get('title'),
                'link': result.get('link'),
                'displayed_link': result.get('displayed_link'),
                'snippet': result.get('snippet'),
                'date': result.get('date'),
                'domain': result.get('domain')
            })
        
        return {
            'query': query,
            'search_parameters': data.get('search_parameters', {}),
            'organic_results': organic_results,
            'total_results': len(organic_results),
            'provider': 'valueserp',
            'raw_response': data  # Keep full response for debugging
        }
    
    def _parse_serpapi_response(self, data: Dict, query: str) -> Dict:
        """Parse SerpAPI response into standard format"""
        organic_results = []
        
        for result in data.get('organic_results', []):
            organic_results.append({
                'position': result.get('position'),
                'title': result.get('title'),
                'link': result.get('link'),
                'displayed_link': result.get('displayed_link'),
                'snippet': result.get('snippet'),
                'date': result.get('date')
            })
        
        return {
            'query': query,
            'search_parameters': data.get('search_parameters', {}),
            'organic_results': organic_results,
            'total_results': len(organic_results),
            'provider': 'serpapi',
            'raw_response': data
        }
    
    def extract_urls(self, search_results: Dict, top_n: int = 10) -> List[str]:
        """
        Extract URLs from search results
        
        Args:
            search_results: SERP search results dict
            top_n: Number of top URLs to return
            
        Returns:
            List of URLs
        """
        urls = []
        for result in search_results.get('organic_results', [])[:top_n]:
            url = result.get('link')
            if url:
                urls.append(url)
        
        logger.info(
            "urls_extracted",
            query=search_results.get('query'),
            count=len(urls)
        )
        
        return urls
    
    def get_competitor_data(self, search_results: Dict) -> List[Dict]:
        """
        Extract competitor data from search results
        
        Args:
            search_results: SERP search results dict
            
        Returns:
            List of competitor data dicts
        """
        competitors = []
        
        for result in search_results.get('organic_results', []):
            competitors.append({
                'position': result.get('position'),
                'url': result.get('link'),
                'title': result.get('title'),
                'snippet': result.get('snippet'),
                'domain': result.get('domain') or result.get('displayed_link'),
                'date': result.get('date')
            })
        
        return competitors


# Singleton instance
_serp_service_instance = None


def get_serp_service(api_key: Optional[str] = None) -> SERPService:
    """Get or create singleton SERP service instance"""
    global _serp_service_instance
    
    if _serp_service_instance is None:
        _serp_service_instance = SERPService(api_key=api_key)
    
    return _serp_service_instance

