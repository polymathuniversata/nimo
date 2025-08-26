import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # MeTTa configuration
    METTA_DB_PATH = os.environ.get('METTA_DB_PATH', 'metta_store.db')
    USE_METTA_REASONING = os.environ.get('USE_METTA_REASONING', 'False').lower() == 'true'
    METTA_CONFIDENCE_THRESHOLD = float(os.environ.get('METTA_CONFIDENCE_THRESHOLD', '0.7'))
    
    # Blockchain configuration
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'base-goerli')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '')
    PROVIDER_URL = os.environ.get('PROVIDER_URL', 'https://goerli.base.org')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///dev.db')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Set the active configuration
active_config = config[os.environ.get('FLASK_ENV', 'default')]