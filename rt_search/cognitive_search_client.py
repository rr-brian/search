"""Azure Cognitive Search client module."""
import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CognitiveSearchClient:
    def __init__(self, endpoint: str, index_name: str, credential: str):
        """Initialize the search client"""
        self.endpoint = endpoint.rstrip('/')
        self.index_name = index_name
        self._auth = credential
        self.api_version = '2023-07-01-Preview'

    def search(self, query: str) -> List[Dict]:
        """Execute a search query"""
        logger.info(f'Searching for: {query}')
        
        # Prepare search URL
        search_url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version={self.api_version}"
        
        # Prepare search body
        search_body = {
            'search': query,
            'queryType': 'simple',
            'top': 5,
            'select': '*',
            'searchFields': 'content',
            'searchMode': 'all',
            'count': True,
            'orderby': 'search.score() desc'
        }
        
        try:
            # Execute search request
            response = requests.post(
                search_url,
                headers={
                    'Content-Type': 'application/json',
                    'api-key': self._auth,
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                },
                json=search_body
            )
            
            # Check response status
            response.raise_for_status()
            
            # Parse response
            results = response.json()
            if isinstance(results, dict) and 'value' in results:
                logger.info(f'Found {len(results["value"])} results')
                return results['value']
            else:
                logger.warning('Unexpected response format')
                return []
                
        except Exception as e:
            logger.error(f'Search failed: {str(e)}')
            return []
