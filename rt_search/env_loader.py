"""Environment variable loader module."""
import os
import logging
from dotenv import load_dotenv
from typing import Dict

def load_env() -> Dict[str, str]:
    """Load environment variables."""
    logger = logging.getLogger(__name__)
    logger.info('Loading environment variables...')
    
    # Required environment variables
    required_vars = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI endpoint',
        'AZURE_OPENAI_DEPLOYMENT': 'Azure OpenAI deployment name',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI credential',
        'AZURE_AI_SEARCH_ENDPOINT': 'Azure AI Search endpoint',
        'AZURE_AI_SEARCH_INDEX': 'Azure AI Search index name',
        'AZURE_AI_SEARCH_API_KEY': 'Azure AI Search credential'
    }
    
    # Check for missing variables
    missing = []
    env_vars = {}
    
    # Load each variable
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f'{var} ({desc})')
        else:
            # Log variable found (without revealing sensitive values)
            if 'KEY' in var or 'CREDENTIAL' in var:
                logger.info(f'Found {var} in environment [value hidden]')
                logger.debug(f'{var} length: {len(value)}')
            else:
                logger.info(f'Found {var} in environment: {value}')
            env_vars[var] = value
    
    if missing:
        error = f'Missing required environment variables: {", ".join(missing)}'
        logger.error(error)
        raise ValueError(error)
    
    # Log summary
    logger.info('Environment variables loaded successfully:')
    logger.info(f'OpenAI endpoint: {env_vars.get("AZURE_OPENAI_ENDPOINT", "[missing]")}')
    logger.info(f'OpenAI deployment: {env_vars.get("AZURE_OPENAI_DEPLOYMENT", "[missing]")}')
    logger.info(f'Search endpoint: {env_vars.get("AZURE_AI_SEARCH_ENDPOINT", "[missing]")}')
    logger.info(f'Search index: {env_vars.get("AZURE_AI_SEARCH_INDEX", "[missing]")}')

    # If any variables are missing, try to load from .env file
    if missing:
        logger.info('Some environment variables are missing, attempting to load from .env file...')
        try:
            # Find .env file
            env_path = os.path.join(os.getcwd(), '.env')
            if not os.path.exists(env_path):
                env_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
                if not os.path.exists(env_path):
                    raise FileNotFoundError('Environment variables not set and .env file not found')
            
            load_dotenv(env_path, override=True)
            # Check for variables again after loading .env
            for var in missing_vars:
                value = os.getenv(var)
                if value:
                    env_vars[var] = value
                    if any(s in var.lower() for s in ['key', 'secret', 'password', 'token']):
                        logger.info(f'Loaded {var} from .env file [value hidden]')
                    else:
                        logger.info(f'Loaded {var} from .env file: {value}')
                else:
                    error_msg = f"Missing required environment variable: {var} ({required_vars[var]})"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
        except Exception as e:
            logger.error(f'Error loading .env file: {str(e)}')
            raise

    logger.info('Environment variables loaded successfully')
    return env_vars
