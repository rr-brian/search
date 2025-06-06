"""Azure Cognitive Search client module."""
import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CognitiveSearchClient:
    """Azure Cognitive Search client"""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the client
        
        Args:
            endpoint (str): Azure Cognitive Search endpoint
            index_name (str): Name of the search index
            api_key (str): API key for authentication
        """
        self.endpoint = endpoint.rstrip('/')
        self.index_name = index_name
        self._auth = api_key
        self.api_version = '2023-07-01-Preview'
        
        # Inspect index on initialization
        self.inspect_index()
        
    def inspect_index(self):
        """Inspect the search index to understand its schema"""
        try:
            # Get index definition
            index_url = f"{self.endpoint}/indexes/{self.index_name}?api-version={self.api_version}"
            response = requests.get(
                index_url,
                headers={
                    'Content-Type': 'application/json',
                    'api-key': self._auth
                }
            )
            
            if response.status_code == 200:
                index_def = response.json()
                logger.info('Index schema:')
                logger.info(f'Index name: {index_def.get("name")}')
                
                # Log field information
                fields = index_def.get('fields', [])
                logger.info(f'Found {len(fields)} fields:')
                for field in fields:
                    logger.info(f'  - {field.get("name")}: {field.get("type")} '
                              f'(searchable: {field.get("searchable", False)}, '
                              f'retrievable: {field.get("retrievable", False)})')
                
                # Store searchable fields for later use
                self.searchable_fields = [f['name'] for f in fields if f.get('searchable', False)]
                logger.info(f'Searchable fields: {self.searchable_fields}')
                
            else:
                logger.error(f'Failed to get index definition: {response.status_code}')
                logger.error(f'Response: {response.text}')
                
        except Exception as e:
            logger.error(f'Error inspecting index: {str(e)}')

    def search(self, query: str) -> List[Dict]:
        """Execute a search query"""
        logger.info(f'Searching for: {query}')
        
        # Prepare search URL
        search_url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version={self.api_version}"
        logger.info(f'Search URL: {search_url}')
        logger.info(f'Index name: {self.index_name}')
        
        # Clean and process the query
        cleaned_query = query.strip()
        logger.info(f'Original query: {query}')
        logger.info(f'Cleaned query: {cleaned_query}')
        
        # Prepare search body with discovered fields
        search_body = {
            'search': cleaned_query,
            'queryType': 'simple',
            'top': 50,
            'select': '*',
            'searchFields': ','.join(self.searchable_fields) if hasattr(self, 'searchable_fields') else 'content',
            'searchMode': 'any',
            'count': True,
            'orderby': 'search.score() desc',
            'highlight': ','.join(self.searchable_fields) if hasattr(self, 'searchable_fields') else 'content',
            'highlightPreTag': '<mark>',
            'highlightPostTag': '</mark>'
        }
        
        # Log search configuration
        logger.info('Search configuration:')
        for key, value in search_body.items():
            logger.info(f'  {key}: {value}')
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
                    
                    # Get highlights if available
                    highlights = item.get('@search.highlights', {})
                    highlighted_content = highlights.get('content', [content])[0] if highlights else content
                    
                    # Get semantic details if available
                    captions = item.get('@search.captions', [])
                    caption = captions[0].get('text') if captions else ''
                    
                    # Log field details
                    logger.info(f'Result {idx + 1} content length: {len(content)}')
                    logger.info(f'Result {idx + 1} context length: {len(context)}')
                    logger.info(f'Result {idx + 1} score: {score}')
                    logger.info(f'Result {idx + 1} has highlights: {bool(highlights)}')
                    logger.info(f'Result {idx + 1} has caption: {bool(caption)}')
                    
                    result = {
                        'content': highlighted_content,
                        'context': context,
                        'relevance': float(score),
                        'summary': caption or context[:200] + '...' if context else ''
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
