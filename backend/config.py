import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Core Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    
    # API Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    MAX_JSON_SIZE = int(os.environ.get('MAX_JSON_SIZE', 1024 * 1024))  # 1MB
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT = int(os.environ.get('DEFAULT_RATE_LIMIT', 100))
    AUTH_RATE_LIMIT = int(os.environ.get('AUTH_RATE_LIMIT', 10))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 300))
    
    # Security Settings
    SECURITY_HEADERS_ENABLED = os.environ.get('SECURITY_HEADERS_ENABLED', 'true').lower() == 'true'
    CONTENT_SECURITY_POLICY = os.environ.get(
        'CONTENT_SECURITY_POLICY',
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    )
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    ENABLE_FILE_LOGGING = os.environ.get('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
    ENABLE_JSON_LOGGING = os.environ.get('ENABLE_JSON_LOGGING', 'false').lower() == 'true'
    MAX_LOG_SIZE = int(os.environ.get('MAX_LOG_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # Feature Flags
    FEATURE_WALLET_AUTH = os.environ.get('FEATURE_WALLET_AUTH', 'true').lower() == 'true'
    FEATURE_METTA_INTEGRATION = os.environ.get('FEATURE_METTA_INTEGRATION', 'true').lower() == 'true'
    FEATURE_AUTO_REWARDS = os.environ.get('FEATURE_AUTO_REWARDS', 'true').lower() == 'true'
    FEATURE_USDC_REWARDS = os.environ.get('FEATURE_USDC_REWARDS', 'true').lower() == 'true'
    FEATURE_IDENTITY_VERIFICATION = os.environ.get('FEATURE_IDENTITY_VERIFICATION', 'true').lower() == 'true'
    
    # External Services
    REDIS_URL = os.environ.get('REDIS_URL')
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Development Settings
    MOCK_EXTERNAL_SERVICES = os.environ.get('MOCK_EXTERNAL_SERVICES', 'false').lower() == 'true'
    SKIP_AUTH_FOR_TESTING = os.environ.get('SKIP_AUTH_FOR_TESTING', 'false').lower() == 'true'
    DEBUG_SQL_QUERIES = os.environ.get('DEBUG_SQL_QUERIES', 'false').lower() == 'true'
    
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
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'polygon-mumbai')
    WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL', 'https://rpc-mumbai.maticvigil.com')
    
    # Contract addresses based on network
    if BLOCKCHAIN_NETWORK == 'base-sepolia':
        NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA = os.environ.get('NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA', '0x56186c1e64ca8043DEF78d06Aff222212ea5df71')
        NIMO_TOKEN_CONTRACT_BASE_SEPOLIA = os.environ.get('NIMO_TOKEN_CONTRACT_BASE_SEPOLIA', '0x53Eba1e079F885482238EE8bf01C4A9f09DE458f')
        USDC_CONTRACT_BASE_SEPOLIA = os.environ.get('USDC_CONTRACT_BASE_SEPOLIA', '0x036CbD53842c5426634e7929541eC2318f3dCF7e')
        
        # Set the generic contract addresses for current network
        NIMO_IDENTITY_CONTRACT = NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA
        NIMO_TOKEN_CONTRACT = NIMO_TOKEN_CONTRACT_BASE_SEPOLIA
        USDC_CONTRACT = USDC_CONTRACT_BASE_SEPOLIA
    elif BLOCKCHAIN_NETWORK == 'base-mainnet':
        NIMO_IDENTITY_CONTRACT_BASE_MAINNET = os.environ.get('NIMO_IDENTITY_CONTRACT_BASE_MAINNET', '')
        NIMO_TOKEN_CONTRACT_BASE_MAINNET = os.environ.get('NIMO_TOKEN_CONTRACT_BASE_MAINNET', '')
        USDC_CONTRACT_BASE_MAINNET = os.environ.get('USDC_CONTRACT_BASE_MAINNET', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
        
        # Set the generic contract addresses for current network
        NIMO_IDENTITY_CONTRACT = NIMO_IDENTITY_CONTRACT_BASE_MAINNET
        NIMO_TOKEN_CONTRACT = NIMO_TOKEN_CONTRACT_BASE_MAINNET
        USDC_CONTRACT = USDC_CONTRACT_BASE_MAINNET
    elif BLOCKCHAIN_NETWORK == 'polygon-mumbai':
        NIMO_IDENTITY_CONTRACT_POLYGON_MUMBAI = os.environ.get('NIMO_IDENTITY_CONTRACT_POLYGON_MUMBAI', '')
        NIMO_TOKEN_CONTRACT_POLYGON_MUMBAI = os.environ.get('NIMO_TOKEN_CONTRACT_POLYGON_MUMBAI', '')
        USDC_CONTRACT_POLYGON_MUMBAI = os.environ.get('USDC_CONTRACT_POLYGON_MUMBAI', '0x0FA8781a83E46826621b3BC094Ea2A0212e71B23')
        
        # Set the generic contract addresses for current network
        NIMO_IDENTITY_CONTRACT = NIMO_IDENTITY_CONTRACT_POLYGON_MUMBAI
        NIMO_TOKEN_CONTRACT = NIMO_TOKEN_CONTRACT_POLYGON_MUMBAI
        USDC_CONTRACT = USDC_CONTRACT_POLYGON_MUMBAI
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
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Security
    JWT_COOKIE_SECURE = True
    SSL_REDIRECT = os.environ.get('SSL_REDIRECT', 'false').lower() == 'true'
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')
    
    # Server
    SERVER_NAME = os.environ.get('SERVER_NAME')
    TRUSTED_HOSTS = os.environ.get('TRUSTED_HOSTS', '').split(',') if os.environ.get('TRUSTED_HOSTS') else []
    
    # Logging - Production should use structured logging
    ENABLE_JSON_LOGGING = True
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    # Disable development features
    MOCK_EXTERNAL_SERVICES = False
    SKIP_AUTH_FOR_TESTING = False
    DEBUG_SQL_QUERIES = False
    
    # Force real MeTTa service in production (or controlled fallback)
    METTA_MODE = os.environ.get('METTA_MODE', 'mock')  # Allow override for staged rollout


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Set the active configuration
active_config = config[os.environ.get('FLASK_ENV', 'default')]