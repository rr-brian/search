"""Flask application for the search API."""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from rt_search import SearchClient, load_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

# Disable caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store,no-cache,must-revalidate,post-check=0,pre-check=0,max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def root():
    return app.send_static_file('index.html')

# Load environment variables
load_env()

# Initialize search client
search_client = SearchClient()

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search requests."""
    logger.info('Received search request')
    try:
        # Get query from request
        logger.info(f'Request data: {request.data}')
        data = request.get_json()
        logger.info(f'Parsed JSON data: {data}')
        
        if not data or 'query' not in data:
            logger.error('No query provided in request')
            return jsonify({'error': 'No query provided'}), 400
            
        query = data['query']
        if not query or not isinstance(query, str):
            logger.error(f'Invalid query format: {query}')
            return jsonify({'error': 'Invalid query format'}), 400
            
        # Execute search
        logger.info(f'Executing search with query: {query}')
        results = search_client.search_contract_language(query)
        
        # Log results details
        if isinstance(results, list):
            logger.info(f'Found {len(results)} results')
            for idx, result in enumerate(results):
                logger.info(f'Result {idx + 1}:')
                logger.info(f'  Content length: {len(result.get("content", ""))}')
                logger.info(f'  Relevance score: {result.get("relevance", 0)}')
                if result.get('summary'):
                    logger.info(f'  Has summary: Yes')
        else:
            logger.warning(f'Unexpected results type: {type(results)}')
            if isinstance(results, dict):
                logger.warning(f'Result keys: {list(results.keys())}')
        
        # Return results
        if isinstance(results, dict) and 'error' in results:
            logger.error(f'Search error: {results["error"]}')
            return jsonify({'error': results["error"]}), 500
            
        if not results:
            logger.info('No results found')
            return jsonify([])
            
        logger.info('Returning results successfully')
        return jsonify(results)
        
    except Exception as e:
        logger.error(f'Error processing request: {str(e)}')
        logger.exception('Full traceback:')
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint."""
    logger.info('Test endpoint called')
    return jsonify({'message': 'Test endpoint working'})

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=8000, debug=True)
    except KeyboardInterrupt:
        logger.info('Server shutting down...')
