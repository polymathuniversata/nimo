import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import key manager after environment is loaded
try:
    from .utils.key_manager import key_manager
    KEY_MANAGER_AVAILABLE = True
except ImportError:
    KEY_MANAGER_AVAILABLE = False
    key_manager = None

class Config:
    """Base configuration."""
    # Core Flask settings - using key manager for secure keys
    SECRET_KEY = key_manager.get_flask_secret() if KEY_MANAGER_AVAILABLE else os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration - using key manager for secure keys
    JWT_SECRET_KEY = key_manager.get_jwt_secret() if KEY_MANAGER_AVAILABLE else os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
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
    
    # Feature Flags - Based on Comprehensive Audit Results
    FEATURE_WALLET_AUTH = os.environ.get('FEATURE_WALLET_AUTH', 'true').lower() == 'true'
    FEATURE_METTA_INTEGRATION = os.environ.get('FEATURE_METTA_INTEGRATION', 'true').lower() == 'true'
    FEATURE_AUTO_REWARDS = os.environ.get('FEATURE_AUTO_REWARDS', 'true').lower() == 'true'
    FEATURE_ADA_REWARDS = os.environ.get('FEATURE_ADA_REWARDS', 'true').lower() == 'true'  # Updated from USDC
    FEATURE_NIMO_REWARDS = os.environ.get('FEATURE_NIMO_REWARDS', 'true').lower() == 'true'  # Native NIMO tokens
    FEATURE_IDENTITY_VERIFICATION = os.environ.get('FEATURE_IDENTITY_VERIFICATION', 'true').lower() == 'true'
    FEATURE_AUTONOMOUS_SYSTEM = os.environ.get('FEATURE_AUTONOMOUS_SYSTEM', 'true').lower() == 'true'
    FEATURE_FRAUD_DETECTION = os.environ.get('FEATURE_FRAUD_DETECTION', 'true').lower() == 'true'
    FEATURE_BATCH_PROCESSING = os.environ.get('FEATURE_BATCH_PROCESSING', 'true').lower() == 'true'
    FEATURE_PERFORMANCE_MONITORING = os.environ.get('FEATURE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
    FEATURE_CACHE_OPTIMIZATION = os.environ.get('FEATURE_CACHE_OPTIMIZATION', 'true').lower() == 'true'
    
    # External Services - Enhanced Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_SSL = os.environ.get('REDIS_SSL', 'false').lower() == 'true'
    REDIS_MAX_CONNECTIONS = int(os.environ.get('REDIS_MAX_CONNECTIONS', '20'))
    REDIS_SOCKET_CONNECT_TIMEOUT = int(os.environ.get('REDIS_SOCKET_CONNECT_TIMEOUT', '5'))
    
    # Monitoring and Alerting
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    PROMETHEUS_METRICS_ENABLED = os.environ.get('PROMETHEUS_METRICS_ENABLED', 'false').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', '60'))  # seconds
    PERFORMANCE_MONITORING_ENABLED = os.environ.get('PERFORMANCE_MONITORING_ENABLED', 'true').lower() == 'true'
    
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
    
    # MeTTa AI Configuration - Enhanced Based on Audit
    METTA_DATABASE_PATH = os.environ.get('METTA_DATABASE_PATH', 'backend/metta_state/metta_database.json')
    METTA_CORE_RULES_PATH = os.environ.get('METTA_CORE_RULES_PATH', 'backend/rules/core_rules.metta')
    USE_METTA_REASONING = os.environ.get('USE_METTA_REASONING', 'True').lower() == 'true'  # Default enabled
    METTA_MODE = os.environ.get('METTA_MODE', 'enhanced')  # enhanced, mock, basic
    METTA_CONFIDENCE_THRESHOLD = float(os.environ.get('METTA_CONFIDENCE_THRESHOLD', '0.7'))
    METTA_FRAUD_DETECTION_THRESHOLD = float(os.environ.get('METTA_FRAUD_DETECTION_THRESHOLD', '0.8'))
    METTA_BATCH_SIZE = int(os.environ.get('METTA_BATCH_SIZE', '100'))
    METTA_CACHE_TTL = int(os.environ.get('METTA_CACHE_TTL', '3600'))  # 1 hour
    METTA_ENABLE_PERFORMANCE_MONITORING = os.environ.get('METTA_ENABLE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
    METTA_QUERY_TIMEOUT = int(os.environ.get('METTA_QUERY_TIMEOUT', '30'))  # seconds
    METTA_ENABLE_CACHE = os.environ.get('METTA_ENABLE_CACHE', 'true').lower() == 'true'
    
    # Autonomous System Configuration
    AUTONOMOUS_SYSTEM_ENABLED = os.environ.get('AUTONOMOUS_SYSTEM_ENABLED', 'true').lower() == 'true'
    AUTONOMOUS_CYCLE_INTERVAL = int(os.environ.get('AUTONOMOUS_CYCLE_INTERVAL', '300'))  # 5 minutes
    AUTONOMOUS_BATCH_SIZE = int(os.environ.get('AUTONOMOUS_BATCH_SIZE', '50'))
    AUTONOMOUS_MAX_CONCURRENT = int(os.environ.get('AUTONOMOUS_MAX_CONCURRENT', '10'))
    AUTONOMOUS_RETRY_ATTEMPTS = int(os.environ.get('AUTONOMOUS_RETRY_ATTEMPTS', '3'))
    AUTONOMOUS_RETRY_DELAY = int(os.environ.get('AUTONOMOUS_RETRY_DELAY', '5'))  # seconds
    
    # Performance Optimization
    QUERY_OPTIMIZER_ENABLED = os.environ.get('QUERY_OPTIMIZER_ENABLED', 'true').lower() == 'true'
    DATABASE_POOL_SIZE = int(os.environ.get('DATABASE_POOL_SIZE', '20'))
    DATABASE_MAX_OVERFLOW = int(os.environ.get('DATABASE_MAX_OVERFLOW', '10'))
    DATABASE_POOL_RECYCLE = int(os.environ.get('DATABASE_POOL_RECYCLE', '3600'))  # 1 hour
    
    # Try to detect if hyperon/MeTTa is available
    try:
        import hyperon
        USE_METTA_REASONING = True
        METTA_MODE = 'enhanced'  # Use enhanced mode if hyperon available
    except ImportError:
        if not os.environ.get('METTA_MODE'):
            METTA_MODE = 'mock'  # Fallback to mock if not specified
    
    # Cardano blockchain configuration
    CARDANO_NETWORK = os.environ.get('CARDANO_NETWORK', 'preview')  # preview, preprod, mainnet
    
    # Blockfrost API configuration - using key manager for secure keys
    BLOCKFROST_PROJECT_ID_MAINNET = key_manager.get_blockfrost_api_key('mainnet') if KEY_MANAGER_AVAILABLE else os.environ.get('BLOCKFROST_PROJECT_ID_MAINNET', '')
    BLOCKFROST_PROJECT_ID_PREVIEW = key_manager.get_blockfrost_api_key('preview') if KEY_MANAGER_AVAILABLE else os.environ.get('BLOCKFROST_PROJECT_ID_PREVIEW', '')
    BLOCKFROST_PROJECT_ID_PREPROD = key_manager.get_blockfrost_api_key('preprod') if KEY_MANAGER_AVAILABLE else os.environ.get('BLOCKFROST_PROJECT_ID_PREPROD', '')
    
    # Cardano service wallet configuration - using key manager for secure keys
    CARDANO_SERVICE_PRIVATE_KEY = key_manager.get_cardano_service_key() if KEY_MANAGER_AVAILABLE else os.environ.get('CARDANO_SERVICE_PRIVATE_KEY', 'your_cardano_private_key_here')
    CARDANO_SERVICE_KEY_FILE = os.environ.get('CARDANO_SERVICE_KEY_FILE', 'service_key.skey')
    
    # NIMO Native Token Configuration - Production Ready
    NIMO_TOKEN_POLICY_ID_MAINNET = os.environ.get('NIMO_TOKEN_POLICY_ID_MAINNET', '')
    NIMO_TOKEN_POLICY_ID_PREVIEW = os.environ.get('NIMO_TOKEN_POLICY_ID_PREVIEW', '')
    NIMO_TOKEN_POLICY_ID_PREPROD = os.environ.get('NIMO_TOKEN_POLICY_ID_PREPROD', '')
    NIMO_TOKEN_ASSET_NAME = os.environ.get('NIMO_TOKEN_ASSET_NAME', 'NIMO')
    ADA_TO_NIMO_RATE = float(os.environ.get('ADA_TO_NIMO_RATE', '100'))  # 1 ADA = 100 NIMO tokens
    NIMO_DECIMAL_PLACES = int(os.environ.get('NIMO_DECIMAL_PLACES', '6'))
    NIMO_MIN_MINT_AMOUNT = int(os.environ.get('NIMO_MIN_MINT_AMOUNT', '1'))
    NIMO_MAX_MINT_AMOUNT = int(os.environ.get('NIMO_MAX_MINT_AMOUNT', '1000000'))
    
    # Reward Configuration
    MIN_ADA_REWARD = int(os.environ.get('MIN_ADA_REWARD', '1000000'))  # 1 ADA in lovelace
    MAX_ADA_REWARD = int(os.environ.get('MAX_ADA_REWARD', '10000000'))  # 10 ADA in lovelace
    MIN_NIMO_REWARD = int(os.environ.get('MIN_NIMO_REWARD', '10'))
    MAX_NIMO_REWARD = int(os.environ.get('MAX_NIMO_REWARD', '1000'))
    CONFIDENCE_REWARD_MULTIPLIER = float(os.environ.get('CONFIDENCE_REWARD_MULTIPLIER', '1.5'))
    
    # Legacy blockchain support (kept for backward compatibility)
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'cardano-preview')
    WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL', 'https://cardano-preview.blockfrost.io/api')
    
    # Legacy contract addresses (deprecated - kept for migration compatibility)
    NIMO_IDENTITY_CONTRACT = os.environ.get('NIMO_IDENTITY_CONTRACT', '')
    NIMO_TOKEN_CONTRACT = os.environ.get('NIMO_TOKEN_CONTRACT', '')
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
    
    # Production MeTTa Configuration
    METTA_MODE = os.environ.get('METTA_MODE', 'enhanced')  # enhanced for production
    METTA_ENABLE_ADA_REWARDS = os.environ.get('METTA_ENABLE_ADA_REWARDS', 'true').lower() == 'true'
    METTA_ENABLE_FRAUD_DETECTION = os.environ.get('METTA_ENABLE_FRAUD_DETECTION', 'true').lower() == 'true'
    
    # Production Performance Settings
    REDIS_CONNECTION_POOL_SIZE = int(os.environ.get('REDIS_CONNECTION_POOL_SIZE', '50'))
    QUERY_CACHE_TTL = int(os.environ.get('QUERY_CACHE_TTL', '300'))  # 5 minutes
    BATCH_PROCESSING_ENABLED = True
    AUTONOMOUS_SYSTEM_ENABLED = True
    
    # Production Monitoring
    PERFORMANCE_MONITORING_ENABLED = True
    PROMETHEUS_METRICS_ENABLED = os.environ.get('PROMETHEUS_METRICS_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', '30'))  # 30 seconds


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Set the active configuration
active_config = config[os.environ.get('FLASK_ENV', 'default')]