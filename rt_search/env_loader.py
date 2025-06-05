"""Environment variable loader module."""
import os
import logging
from dotenv import load_dotenv
from typing import Dict

def load_env() -> Dict[str, str]:
    """Load environment variables from .env file or environment
    Returns:
        Dict[str, str]: Dictionary of required variables
    """
    logger = logging.getLogger(__name__)
    logger.info('Loading environment variables...')

    # Define required variables and their descriptions
    required_vars = {
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint",
        "AZURE_OPENAI_DEPLOYMENT": "Azure OpenAI deployment name",
        "AZURE_OPENAI_CREDENTIAL": "Azure OpenAI credential",
        "AZURE_AI_SEARCH_ENDPOINT": "Azure AI Search endpoint",
        "AZURE_AI_SEARCH_INDEX": "Azure AI Search index name",
        "AZURE_AI_SEARCH_CREDENTIAL": "Azure AI Search credential"
    }

    # Check if required variables are already set
    env_vars = {}
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
            # Log securely - don't show actual values for sensitive variables
            if any(s in var.lower() for s in ['key', 'secret', 'password', 'token']):
                logger.info(f'Found {var} in environment [value hidden]')
            else:
                logger.info(f'Found {var} in environment: {value}')
        else:
            missing_vars.append(var)

    # If any variables are missing, try to load from .env file
    if missing_vars:
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
