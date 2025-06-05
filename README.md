# Azure Search Integration

This project integrates Azure Cognitive Search with Azure OpenAI to provide intelligent search capabilities for contract language.

## Features

- Azure Cognitive Search integration for document search
- Azure OpenAI integration for query understanding and result summarization
- RESTful API endpoints for search operations
- Secure credential handling
- Comprehensive logging
- Health check endpoint

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   AZURE_OPENAI_ENDPOINT=your_openai_endpoint
   AZURE_OPENAI_DEPLOYMENT=your_openai_deployment
   AZURE_OPENAI_API_KEY=your_openai_key
   AZURE_AI_SEARCH_ENDPOINT=your_search_endpoint
   AZURE_AI_SEARCH_INDEX=your_search_index
   AZURE_AI_SEARCH_API_KEY=your_search_key
   ```

## Usage

Start the Flask server:
```bash
python rt_search_flask.py
```

The server will start on port 8000 by default.

### API Endpoints

#### Search
- **POST** `/api/search`
  - Request body: `{"query": "your search query"}`
  - Returns search results with OpenAI-generated summaries

#### Health Check
- **GET** `/health`
  - Returns server health status

## Security

- Environment variables are securely loaded and validated
- Sensitive values are never logged
- CORS is enabled for web client access
- API keys and credentials are handled securely

## Development

The project uses Python 3.8+ and follows standard Python project structure:
- `rt_search/` - Core package
  - `cognitive_search_client.py` - Azure Cognitive Search client
  - `openai_client.py` - Azure OpenAI client
  - `search_client.py` - Combined search functionality
  - `env_loader.py` - Environment configuration
  - `config.py` - Configuration utilities

## Deployment

The application can be deployed to Azure App Service or any other Python-compatible hosting service.
