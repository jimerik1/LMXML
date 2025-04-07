# Main application entry point
import os
from flask import Flask

from config import active_config
from controllers.xml_controller import xml_bp

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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)