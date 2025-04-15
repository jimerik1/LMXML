# Configuration settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    ENV = os.getenv('FLASK_ENV', 'development')
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    BASE_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, 'base_template.xml')
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

class ProductionConfig(Config):
    """Production configuration."""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_output')

# Set configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Active configuration
active_config = config[os.getenv('FLASK_ENV', 'default')]()