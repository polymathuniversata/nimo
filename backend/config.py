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
    METTA_DATABASE_PATH = os.environ.get('METTA_DATABASE_PATH', 'backend/metta_state/metta_database.json')
    METTA_CORE_RULES_PATH = os.environ.get('METTA_CORE_RULES_PATH', 'backend/rules/core_rules.metta')
    USE_METTA_REASONING = os.environ.get('USE_METTA_REASONING', 'False').lower() == 'true'
    METTA_MODE = os.environ.get('METTA_MODE', 'mock')
    METTA_CONFIDENCE_THRESHOLD = float(os.environ.get('METTA_CONFIDENCE_THRESHOLD', '0.7'))
    
    # Try to detect if hyperon/MeTTa is available
    try:
        import hyperon
        USE_METTA_REASONING = True
    except ImportError:
        pass
    
    # Blockchain configuration
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'base-sepolia')
    WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL', 'https://sepolia.base.org')
    
    # Contract addresses based on network
    if BLOCKCHAIN_NETWORK == 'base-sepolia':
        NIMO_IDENTITY_CONTRACT = os.environ.get('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA', '')
        NIMO_TOKEN_CONTRACT = os.environ.get('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA', '')
        USDC_CONTRACT = os.environ.get('USDC_CONTRACT_BASE_SEPOLIA', '0x036CbD53842c5426634e7929541eC2318f3dCF7e')
    elif BLOCKCHAIN_NETWORK == 'base-mainnet':
        NIMO_IDENTITY_CONTRACT = os.environ.get('NIMO_IDENTITY_CONTRACT_BASE_MAINNET', '')
        NIMO_TOKEN_CONTRACT = os.environ.get('NIMO_TOKEN_CONTRACT_BASE_MAINNET', '')
        USDC_CONTRACT = os.environ.get('USDC_CONTRACT_BASE_MAINNET', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
    else:
        NIMO_IDENTITY_CONTRACT = os.environ.get('NIMO_IDENTITY_CONTRACT', '')
        NIMO_TOKEN_CONTRACT = os.environ.get('NIMO_TOKEN_CONTRACT', '')
        USDC_CONTRACT = os.environ.get('USDC_CONTRACT', '')
    
    # Legacy support
    CONTRACT_ADDRESS = NIMO_IDENTITY_CONTRACT
    PROVIDER_URL = WEB3_PROVIDER_URL


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///app.db')


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