# Configuration settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    BASE_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, 'base_template.xml')
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    pass

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True

# Set configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Active configuration
active_config = config[os.getenv('FLASK_ENV', 'default')]()