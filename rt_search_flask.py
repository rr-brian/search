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
app = Flask(__name__)
CORS(app)

# Load environment variables
load_env()

# Initialize search client
search_client = SearchClient()

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search requests."""
    try:
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
            
        query = data['query']
        if not query or not isinstance(query, str):
            return jsonify({'error': 'Invalid query format'}), 400
            
        # Execute search
        results = search_client.search_contract_language(query)
        
        # Return results
        if isinstance(results, dict) and 'error' in results:
            return jsonify(results), 500
        return jsonify(results)
        
    except Exception as e:
        logger.error(f'Error processing request: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        logger.info('Server shutting down...')
