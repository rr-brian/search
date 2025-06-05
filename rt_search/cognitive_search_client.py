"""Azure Cognitive Search client module."""
import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CognitiveSearchClient:
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the search client"""
        self.endpoint = endpoint.rstrip('/')
        self.index_name = index_name
        self._auth = api_key
        self.api_version = '2023-07-01-Preview'

    def search(self, query: str) -> List[Dict]:
        """Execute a search query"""
        logger.info(f'Searching for: {query}')
        
        # Prepare search URL
        search_url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version={self.api_version}"
        logger.info(f'Search URL: {search_url}')
        logger.info(f'Index name: {self.index_name}')
        
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
        logger.info(f'Search body: {search_body}')
        
        try:
            # Log request details
            headers = {
                'Content-Type': 'application/json',
                'api-key': self._auth[:5] + '...',  # Log first 5 chars of key for debugging
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            logger.info(f'Request headers: {headers}')
            
            # Execute search request
            logger.info('Making search request...')
            response = requests.post(
                search_url,
                headers={'Content-Type': 'application/json',
                         'api-key': self._auth,
                         'Accept': 'application/json',
                         'Cache-Control': 'no-cache',
                         'Pragma': 'no-cache'},
                json=search_body
            )
            
            # Log response details
            logger.info(f'Response status: {response.status_code}')
            logger.info(f'Response headers: {dict(response.headers)}')
            
            try:
                # Parse response
                results = response.json()
                logger.info(f'Raw response type: {type(results)}')
                logger.info(f'Raw response keys: {list(results.keys()) if isinstance(results, dict) else "N/A"}')
                
                if response.status_code != 200:
                    logger.error(f'Search API error: {results}')
                    return []
                
                if not isinstance(results, dict):
                    logger.error(f'Expected dict response, got {type(results)}')
                    return []
                    
                if 'value' not in results:
                    logger.error(f'Response missing "value" key. Keys: {list(results.keys())}')
                    return []
                    
                value = results['value']
                logger.info(f'Value type: {type(value)}')
                logger.info(f'Value length: {len(value) if isinstance(value, (list, dict)) else "N/A"}')
                
                if not isinstance(value, list):
                    logger.error(f'Expected list in "value", got {type(value)}')
                    return []
                    
                # Validate and transform each result
                transformed = []
                for idx, item in enumerate(value):
                    logger.info(f'Processing result {idx + 1}:')
                    if not isinstance(item, dict):
                        logger.warning(f'Skipping non-dict result: {item}')
                        continue
                    
                    logger.info(f'Result {idx + 1} keys: {list(item.keys())}')
                        
                    # Extract required fields with validation
                    content = str(item.get('content', ''))
                    context = str(item.get('context', ''))
                    score = item.get('@search.score', 0)
                    
                    # Log field details
                    logger.info(f'Result {idx + 1} content length: {len(content)}')
                    logger.info(f'Result {idx + 1} context length: {len(context)}')
                    logger.info(f'Result {idx + 1} score: {score}')
                    
                    result = {
                        'content': content,
                        'context': context,
                        'relevance': float(score)
                    }
                    transformed.append(result)
                    
                logger.info(f'Transformed {len(transformed)} valid results')
                if transformed:
                    logger.info(f'First result example: {transformed[0]}')
                return transformed
                        
            except ValueError as e:
                logger.error(f'Failed to parse JSON response: {e}')
                logger.error(f'Raw response text: {response.text[:1000]}')
                return []
                
        except Exception as e:
            logger.error(f'Search failed: {str(e)}')
            logger.error(f'Exception type: {type(e).__name__}')
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
                logger.error(f'Response status: {e.response.status_code}')
                logger.error(f'Response text: {e.response.text[:1000]}')
            return []
