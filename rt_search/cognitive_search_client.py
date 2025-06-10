"""Azure Cognitive Search client module."""
import logging
import os
from typing import Dict, List

from openai import AzureOpenAI
from .search_operations import SearchOperations

logger = logging.getLogger(__name__)

class CognitiveSearchClient(SearchOperations):
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the client
        
        Args:
            endpoint (str): Azure Cognitive Search endpoint
            index_name (str): Name of the search index
            api_key (str): API key for authentication
        """
        # Initialize base client
        super().__init__(endpoint, index_name, api_key)
        
        # Initialize OpenAI client
        logger.info('Initializing OpenAI client...')
        self.openai_client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15'),  # Default to 2023-05-15
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        logger.info('SearchClient initialization complete')

    def search(self, query: str) -> List[Dict]:
        """Execute a search query"""
        # Forward to parent class implementation
        return super().search(query)
