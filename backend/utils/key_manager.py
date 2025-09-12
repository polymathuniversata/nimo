"""
Unified Key Management System for Nimo Platform
Handles all cryptographic keys and secrets securely using environment variables.
"""
import os
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

logger = logging.getLogger(__name__)

class KeyManager:
    """
    Centralized key management service that handles all cryptographic keys and secrets.
    Uses environment variables for secure key storage and provides encryption capabilities.
    """
    
    def __init__(self):
        """Initialize the key manager with environment-based configuration."""
        self._keys_cache: Dict[str, str] = {}
        self._encryption_key: Optional[bytes] = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption capabilities for sensitive data."""
        try:
            # Use a master key from environment or generate one
            master_key = os.environ.get('NIMO_MASTER_KEY')
            if not master_key:
                logger.error("NIMO_MASTER_KEY environment variable not set. Generating temporary key for development.")
                # Generate a secure random key for development only
                import secrets
                master_key = secrets.token_hex(32)
                logger.warning("Using auto-generated master key. Set NIMO_MASTER_KEY in production.")
            
            # Derive encryption key from master key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'nimo_platform_salt',
                iterations=100000,
            )
            self._encryption_key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self._encryption_key = None
    
    def get_cardano_service_key(self) -> Optional[str]:
        """
        Get Cardano service private key from environment.
        Returns the private key hex string or None if not found.
        """
        # First try to get from direct environment variable
        private_key = os.environ.get('CARDANO_SERVICE_PRIVATE_KEY')
        if private_key and private_key != 'your_cardano_private_key_here':
            return private_key
        
        # Try to load from key file path
        key_file_path = os.environ.get('CARDANO_SERVICE_KEY_FILE')
        if key_file_path:
            full_path = os.path.join(os.getcwd(), 'contracts', 'cardano', key_file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        key_data = json.load(f)
                        return key_data.get('cborHex')
                except Exception as e:
                    logger.error(f"Failed to load key file {full_path}: {e}")
        
        logger.warning("No Cardano service key found. Please set CARDANO_SERVICE_PRIVATE_KEY environment variable.")
        return None
    
    def get_blockfrost_api_key(self, network: str = 'preview') -> Optional[str]:
        """
        Get Blockfrost API key for the specified network.
        
        Args:
            network: Cardano network (preview, preprod, mainnet)
            
        Returns:
            API key string or None if not found
        """
        env_key = f'BLOCKFROST_PROJECT_ID_{network.upper()}'
        api_key = os.environ.get(env_key)
        
        if api_key and not api_key.startswith('your_'):
            return api_key
        
        logger.warning(f"No valid Blockfrost API key found for {network}. Please set {env_key}.")
        return None
    
    def get_jwt_secret(self) -> str:
        """Get JWT secret key from environment with secure fallback."""
        secret = os.environ.get('JWT_SECRET_KEY')
        if not secret:
            logger.error("JWT_SECRET_KEY environment variable not set. Generating temporary key for development.")
            # Generate a secure random key for development only
            import secrets
            secret = secrets.token_hex(32)
            logger.warning("Using auto-generated JWT secret. Set JWT_SECRET_KEY in production.")
        return secret
    
    def get_flask_secret(self) -> str:
        """Get Flask secret key from environment with secure fallback."""
        secret = os.environ.get('SECRET_KEY')
        if not secret:
            logger.error("SECRET_KEY environment variable not set. Generating temporary key for development.")
            # Generate a secure random key for development only
            import secrets
            secret = secrets.token_hex(32)
            logger.warning("Using auto-generated Flask secret. Set SECRET_KEY in production.")
        return secret
    
    def get_database_url(self) -> str:
        """Get database URL from environment with fallback."""
        return os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration from environment."""
        return {
            'url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'password': os.environ.get('REDIS_PASSWORD'),
            'ssl': os.environ.get('REDIS_SSL', 'false').lower() == 'true',
            'max_connections': int(os.environ.get('REDIS_MAX_CONNECTIONS', '20')),
            'socket_connect_timeout': int(os.environ.get('REDIS_SOCKET_CONNECT_TIMEOUT', '5'))
        }
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email service configuration from environment."""
        return {
            'server': os.environ.get('MAIL_SERVER'),
            'port': int(os.environ.get('MAIL_PORT', 587)),
            'use_tls': os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true',
            'username': os.environ.get('MAIL_USERNAME'),
            'password': os.environ.get('MAIL_PASSWORD')
        }
    
    def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """
        Encrypt sensitive data for storage.
        
        Args:
            data: String data to encrypt
            
        Returns:
            Encrypted data as base64 string or None if encryption fails
        """
        if not self._encryption_key:
            logger.error("Encryption not available")
            return None
        
        try:
            f = Fernet(self._encryption_key)
            encrypted_data = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt sensitive data from storage.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string data or None if decryption fails
        """
        if not self._encryption_key:
            logger.error("Decryption not available")
            return None
        
        try:
            f = Fernet(self._encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return None
    
    def validate_key_security(self) -> Dict[str, bool]:
        """
        Validate that all keys meet security requirements.
        
        Returns:
            Dictionary with validation results for each key type
        """
        results = {}
        
        # Check Cardano service key
        cardano_key = self.get_cardano_service_key()
        results['cardano_service_key'] = bool(cardano_key and len(cardano_key) >= 64)
        
        # Check Blockfrost API keys
        for network in ['preview', 'preprod', 'mainnet']:
            api_key = self.get_blockfrost_api_key(network)
            results[f'blockfrost_{network}'] = bool(api_key and len(api_key) >= 20)
        
        # Check JWT secret
        jwt_secret = self.get_jwt_secret()
        results['jwt_secret'] = jwt_secret != 'jwt-dev-key-change-in-production' and len(jwt_secret) >= 32
        
        # Check Flask secret
        flask_secret = self.get_flask_secret()
        results['flask_secret'] = flask_secret != 'dev-key-please-change-in-production' and len(flask_secret) >= 32
        
        return results
    
    def generate_secure_key(self, length: int = 32) -> str:
        """
        Generate a cryptographically secure random key.
        
        Args:
            length: Length of key to generate
            
        Returns:
            Base64 encoded secure key
        """
        import secrets
        key_bytes = secrets.token_bytes(length)
        return base64.urlsafe_b64encode(key_bytes).decode()
    
    def audit_security_configuration(self) -> Dict[str, Any]:
        """
        Perform a comprehensive security audit of key configuration.
        
        Returns:
            Dictionary with audit results and recommendations
        """
        validation_results = self.validate_key_security()
        
        audit_result = {
            'timestamp': os.environ.get('AUDIT_TIMESTAMP', ''),
            'security_level': 'HIGH' if all(validation_results.values()) else 'MEDIUM',
            'key_validation': validation_results,
            'recommendations': [],
            'critical_issues': [],
            'warnings': []
        }
        
        # Check for critical issues
        if not validation_results.get('cardano_service_key'):
            audit_result['critical_issues'].append("Missing or invalid Cardano service key")
        
        if not any(validation_results.get(f'blockfrost_{net}') for net in ['preview', 'preprod', 'mainnet']):
            audit_result['critical_issues'].append("No valid Blockfrost API keys configured")
        
        # Check for warnings
        if not validation_results.get('jwt_secret'):
            audit_result['warnings'].append("Using default or weak JWT secret")
        
        if not validation_results.get('flask_secret'):
            audit_result['warnings'].append("Using default or weak Flask secret")
        
        # Add recommendations
        if audit_result['critical_issues']:
            audit_result['recommendations'].append("Set all required API keys and service keys")
        
        if audit_result['warnings']:
            audit_result['recommendations'].append("Replace default secrets with strong, randomly generated keys")
        
        audit_result['recommendations'].append("Regularly rotate API keys and service keys")
        audit_result['recommendations'].append("Use hardware security modules (HSM) in production")
        
        return audit_result


# Global key manager instance
key_manager = KeyManager()

# Convenience functions for backward compatibility
def get_cardano_service_key() -> Optional[str]:
    """Get Cardano service private key."""
    return key_manager.get_cardano_service_key()

def get_blockfrost_api_key(network: str = 'preview') -> Optional[str]:
    """Get Blockfrost API key for network."""
    return key_manager.get_blockfrost_api_key(network)

def get_jwt_secret() -> str:
    """Get JWT secret key."""
    return key_manager.get_jwt_secret()

def validate_keys() -> bool:
    """Quick validation of critical keys."""
    validation_results = key_manager.validate_key_security()
    return validation_results.get('cardano_service_key', False)