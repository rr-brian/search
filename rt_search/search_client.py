"""Search client module combining Azure Cognitive Search and OpenAI."""
import logging
from typing import Dict, List, Union
from .cognitive_search_client import CognitiveSearchClient
from .openai_client import OpenAIClient
from .config import get_required_search_vars

logger = logging.getLogger(__name__)

class SearchClient:
    def __init__(self):
        """Initialize the search client"""
        logger.info('Initializing SearchClient...')
        
        # Get required variables
        required_vars = get_required_search_vars()
        
        # Initialize Cognitive Search client
        self.search_client = CognitiveSearchClient(
            endpoint=required_vars['AZURE_AI_SEARCH_ENDPOINT'],
            index_name=required_vars['AZURE_AI_SEARCH_INDEX'],
            credential=required_vars['AZURE_AI_SEARCH_CREDENTIAL']
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAIClient(
            endpoint=required_vars['AZURE_OPENAI_ENDPOINT'],
            credential=required_vars['AZURE_OPENAI_CREDENTIAL'],
            deployment=required_vars['AZURE_OPENAI_DEPLOYMENT']
        )
            
    def search_contract_language(self, query: str) -> Union[Dict, List[Dict]]:
        """Search for contract language and get OpenAI completion"""
        try:
            # Execute search
            search_results = self.search_client.search(query)
            
            if not search_results:
                logger.warning('No search results found')
                return {'error': 'No results found'}
            
            # Extract content from results
            content = []
            for result in search_results:
                if isinstance(result, dict) and 'content' in result:
                    content.append(result['content'])
            
            # Get completion from OpenAI
            context = '\n'.join(content)
            completion = self.openai_client.get_completion(query, context)
            
            # Return formatted results
            return [
                {
                    'content': result.get('content', ''),
                    'context': result.get('context', ''),
                    'relevance': result.get('@search.score', 0),
                    'summary': completion if idx == 0 else ''
                }
                for idx, result in enumerate(search_results)
            ]
            
        except Exception as e:
            logger.error(f'Search failed: {str(e)}')
            return {'error': str(e)}
