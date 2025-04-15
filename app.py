# Main application entry point
import os
import logging
from flask import Flask

from config import active_config
from controllers.xml_controller import xml_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config or active_config)
    
    # Ensure output directory exists
    os.makedirs(app.config['OUTPUT_DIR'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(xml_bp, url_prefix='/api/xml')
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return {'status': 'healthy'}
    
    logger.info(f"Application created with configuration: {app.config['ENV']}")
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting application on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)