"""Azure OpenAI client module."""
import logging
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, endpoint: str, deployment: str, api_key: str):
        """Initialize the OpenAI client"""
        self.endpoint = endpoint
        self.deployment = deployment
        self.api_key = api_key

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version='2024-02-15-preview'
        )

    def get_completion(self, query: str, context: str = '') -> str:
        """Get a completion from Azure OpenAI"""
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": "Find relevant contract language and summarize key points briefly. Focus on exact matches and similarities."
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\nContext: {context}"
                }
            ]
            
            # Get completion
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            
            # Extract and return content
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            else:
                logger.warning("No completion content found")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            return ""
