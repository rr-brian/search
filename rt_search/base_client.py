"""Base client for Azure Cognitive Search."""
import json
import logging

import requests

logger = logging.getLogger(__name__)

class BaseSearchClient:
    """Base client with core functionality."""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the base client.
        
        Args:
            endpoint (str): Azure Cognitive Search endpoint
            index_name (str): Name of the search index
            api_key (str): API key for authentication
        """
        self._endpoint = endpoint.rstrip('/')
        self._index_name = index_name
        self._auth = api_key
        self._api_version = '2023-07-01-Preview'
        self.search_url = f'{self._endpoint}/indexes/{self._index_name}/docs/search?api-version={self._api_version}'
        
        # Initialize by inspecting index
        self.inspect_index()
    
    def inspect_index(self):
        """Inspect the search index to understand its schema."""
        try:
            # Get index definition
            index_url = f"{self._endpoint}/indexes/{self._index_name}?api-version={self._api_version}"
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
                print('\nIndex fields:')
                print(json.dumps(fields, indent=2))
                
                # Log each field's details
                print('\nField details:')
                logger.info('Field details:')
                for field in fields:
                    field_info = {
                        'name': field.get('name'),
                        'type': field.get('type'),
                        'key': field.get('key', False),
                        'searchable': field.get('searchable', False),
                        'filterable': field.get('filterable', False),
                        'sortable': field.get('sortable', False),
                        'facetable': field.get('facetable', False),
                        'retrievable': field.get('retrievable', False)
                    }
                    print(f'Field: {json.dumps(field_info, indent=2)}')
                    logger.info(f'Field: {json.dumps(field_info, indent=2)}')
                
                # Store field information for later use
                self.searchable_fields = [f['name'] for f in fields if f.get('searchable', False)]
                self.retrievable_fields = [f['name'] for f in fields if f.get('retrievable', False)]
                
                # Log available fields
                print('\nSearchable fields:', self.searchable_fields)
                print('Retrievable fields:', self.retrievable_fields)
                logger.info(f'Searchable fields: {self.searchable_fields}')
                logger.info(f'Retrievable fields: {self.retrievable_fields}')
                
                # Print raw index definition for debugging
                print('\nRaw index definition:')
                print(json.dumps(index_def, indent=2))
                
            else:
                logger.error(f'Failed to get index definition: {response.status_code}')
                logger.error(f'Response: {response.text}')
                
        except Exception as e:
            logger.error(f'Error inspecting index: {str(e)}')
