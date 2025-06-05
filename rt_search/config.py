"""Configuration module for Azure Cognitive Search and OpenAI."""
import os
from typing import Dict

def get_required_search_vars() -> Dict[str, str]:
    """Get required Azure Cognitive Search and OpenAI variables"""
    vars = {
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'AZURE_OPENAI_CREDENTIAL': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_DEPLOYMENT': os.getenv('AZURE_OPENAI_DEPLOYMENT'),
        'AZURE_AI_SEARCH_ENDPOINT': os.getenv('AZURE_AI_SEARCH_ENDPOINT'),
        'AZURE_AI_SEARCH_INDEX': os.getenv('AZURE_AI_SEARCH_INDEX'),
        'AZURE_AI_SEARCH_CREDENTIAL': os.getenv('AZURE_AI_SEARCH_API_KEY')
    }
    
    # Check for missing variables
    missing = [key for key, value in vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return vars
