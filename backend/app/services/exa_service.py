import logging
from typing import List, Dict, Any, Optional
from exa_py import Exa

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ExaSearchService:
    
    def __init__(self):
        self._client: Optional[Exa] = None
    
    @property
    def client(self) -> Exa:
        if self._client is None:
            if not settings.EXA_API_KEY:
                raise ValueError("EXA_API_KEY not configured")
            self._client = Exa(api_key=settings.EXA_API_KEY)
            logger.info("Exa client initialized")
        return self._client
    
    def search_legal_templates(
        self,
        query: str,
        doc_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            search_query = self._build_search_query(query, doc_type, jurisdiction)
            
            logger.info(f"Searching Exa for: {search_query}")
            
            results = self.client.search_and_contents(
                query=search_query,
                num_results=num_results,
                text={"max_characters": 1000},
                highlights=True,
                use_autoprompt=True
            )
            
            formatted_results = []
            for result in results.results:
                formatted_results.append({
                    "url": result.url,
                    "title": result.title,
                    "snippet": result.text[:300] if result.text else "",
                    "score": getattr(result, 'score', 0.0),
                    "highlights": getattr(result, 'highlights', []),
                    "published_date": getattr(result, 'published_date', None)
                })
            
            logger.info(f"Found {len(formatted_results)} results from Exa")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Exa search failed: {e}")
            return []
    
    def _build_search_query(
        self,
        query: str,
        doc_type: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> str:
        search_parts = [query]
        
        search_parts.append("legal template")
        search_parts.append("document template")
        
        if doc_type:
            search_parts.append(doc_type)
        
        if jurisdiction and jurisdiction.lower() != "general":
            search_parts.append(jurisdiction)
        
        search_parts.append("fillable OR variable OR customizable")
        
        search_query = " ".join(search_parts)
        return search_query
    
    def get_template_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Fetching template from URL: {url}")
            
            result = self.client.get_contents([url])
            
            if result.results:
                content = result.results[0]
                return {
                    "url": url,
                    "title": content.title,
                    "text": content.text,
                    "published_date": getattr(content, 'published_date', None)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None

exa_service = ExaSearchService()
