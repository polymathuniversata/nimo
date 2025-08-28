"""
Ethereum signature verification service for wallet authentication.
"""
import re
import time
import hashlib
import secrets
from typing import Optional, Dict, Any
from eth_account.messages import encode_defunct
from eth_account import Account
from flask import current_app

class SignatureVerificationService:
    """Service for verifying Ethereum wallet signatures"""
    
    # Nonce cache to prevent replay attacks (in production, use Redis)
    _nonce_cache = {}
    NONCE_EXPIRY = 300  # 5 minutes
    
    @classmethod
    def generate_nonce(cls) -> str:
        """Generate a cryptographically secure nonce"""
        return secrets.token_hex(16)
    
    @classmethod
    def _cleanup_expired_nonces(cls):
        """Clean up expired nonces from cache"""
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in cls._nonce_cache.items()
            if current_time - timestamp > cls.NONCE_EXPIRY
        ]
        for nonce in expired_nonces:
            del cls._nonce_cache[nonce]
    
    @classmethod
    def is_valid_ethereum_address(cls, address: str) -> bool:
        """Validate Ethereum address format"""
        if not address:
            return False
        
        # Remove 0x prefix if present
        if address.startswith('0x'):
            address = address[2:]
        
        # Check if it's 40 hex characters
        return bool(re.match(r'^[0-9a-fA-F]{40}$', address))
    
    @classmethod
    def extract_message_components(cls, message: str) -> Optional[Dict[str, Any]]:
        """
        Extract components from the authentication message.
        Expected format from frontend:
        
        Welcome to Nimo Platform!
        
        This request will not trigger a blockchain transaction or cost any gas fees.
        
        Wallet: 0x...
        Nonce: abc123...
        Timestamp: 1234567890
        
        By signing this message, you agree to authenticate with Nimo Platform.
        """
        try:
            lines = message.strip().split('\n')
            
            # Find wallet address
            wallet_line = next((line for line in lines if line.startswith('Wallet:')), None)
            if not wallet_line:
                return None
            wallet_address = wallet_line.split(':', 1)[1].strip()
            
            # Find nonce
            nonce_line = next((line for line in lines if line.startswith('Nonce:')), None)
            if not nonce_line:
                return None
            nonce = nonce_line.split(':', 1)[1].strip()
            
            # Find timestamp
            timestamp_line = next((line for line in lines if line.startswith('Timestamp:')), None)
            if not timestamp_line:
                return None
            timestamp_str = timestamp_line.split(':', 1)[1].strip()
            timestamp = int(timestamp_str)
            
            return {
                'wallet_address': wallet_address,
                'nonce': nonce,
                'timestamp': timestamp
            }
        except (ValueError, IndexError) as e:
            current_app.logger.error(f"Failed to parse message: {e}")
            return None
    
    @classmethod
    def verify_signature(
        cls, 
        message: str, 
        signature: str, 
        expected_address: str,
        allow_timestamp_drift: int = 300  # 5 minutes
    ) -> Dict[str, Any]:
        """
        Verify Ethereum signature for authentication.
        
        Args:
            message: The signed message
            signature: The signature from the wallet
            expected_address: The expected wallet address
            allow_timestamp_drift: Maximum age of message in seconds
            
        Returns:
            dict with 'valid' boolean and 'error' message if invalid
        """
        try:
            # Clean up expired nonces
            cls._cleanup_expired_nonces()
            
            # Validate address format
            if not cls.is_valid_ethereum_address(expected_address):
                return {
                    'valid': False,
                    'error': 'Invalid Ethereum address format'
                }
            
            # Extract message components
            components = cls.extract_message_components(message)
            if not components:
                return {
                    'valid': False,
                    'error': 'Invalid message format'
                }
            
            # Verify wallet address matches
            message_address = components['wallet_address']
            if message_address.lower() != expected_address.lower():
                return {
                    'valid': False,
                    'error': 'Wallet address mismatch'
                }
            
            # Check timestamp (prevent replay attacks)
            current_time = int(time.time())
            message_timestamp = components['timestamp']
            age = current_time - message_timestamp
            
            if age > allow_timestamp_drift:
                return {
                    'valid': False,
                    'error': 'Message too old'
                }
            
            if age < -30:  # Allow 30 seconds for clock drift
                return {
                    'valid': False,
                    'error': 'Message from future'
                }
            
            # Check nonce (prevent replay attacks)
            nonce = components['nonce']
            if nonce in cls._nonce_cache:
                return {
                    'valid': False,
                    'error': 'Nonce already used'
                }
            
            # Verify the signature cryptographically
            try:
                # Create message hash
                encoded_message = encode_defunct(text=message)
                
                # Recover address from signature
                recovered_address = Account.recover_message(
                    encoded_message, 
                    signature=signature
                )
                
                # Compare addresses (case-insensitive)
                if recovered_address.lower() != expected_address.lower():
                    return {
                        'valid': False,
                        'error': 'Signature verification failed'
                    }
                
            except Exception as e:
                current_app.logger.error(f"Signature verification error: {e}")
                return {
                    'valid': False,
                    'error': 'Invalid signature format'
                }
            
            # Store nonce to prevent reuse
            cls._nonce_cache[nonce] = current_time
            
            return {
                'valid': True,
                'nonce': nonce,
                'timestamp': message_timestamp,
                'address': recovered_address
            }
            
        except Exception as e:
            current_app.logger.error(f"Signature verification failed: {e}")
            return {
                'valid': False,
                'error': 'Verification failed'
            }
    
    @classmethod
    def create_challenge_message(cls, wallet_address: str, nonce: str) -> str:
        """
        Create a challenge message for wallet to sign.
        This should match the format expected by extract_message_components.
        """
        timestamp = int(time.time())
        
        return f"""Welcome to Nimo Platform!

This request will not trigger a blockchain transaction or cost any gas fees.

Wallet: {wallet_address}
Nonce: {nonce}
Timestamp: {timestamp}

By signing this message, you agree to authenticate with Nimo Platform."""
    
    @classmethod
    def get_nonce_for_challenge(cls) -> str:
        """Generate a nonce for a new challenge"""
        return cls.generate_nonce()


# Rate limiting for signature verification
class SignatureRateLimit:
    """Rate limiting for signature verification attempts"""
    
    # In production, use Redis for distributed rate limiting
    _attempts = {}
    MAX_ATTEMPTS = 5
    WINDOW_SIZE = 300  # 5 minutes
    
    @classmethod
    def _cleanup_old_attempts(cls):
        """Clean up old rate limit entries"""
        current_time = time.time()
        expired_ips = [
            ip for ip, timestamps in cls._attempts.items()
            if all(current_time - ts > cls.WINDOW_SIZE for ts in timestamps)
        ]
        for ip in expired_ips:
            del cls._attempts[ip]
    
    @classmethod
    def is_rate_limited(cls, ip_address: str) -> bool:
        """Check if IP is rate limited"""
        cls._cleanup_old_attempts()
        
        current_time = time.time()
        if ip_address not in cls._attempts:
            cls._attempts[ip_address] = []
        
        # Remove old attempts outside window
        cls._attempts[ip_address] = [
            ts for ts in cls._attempts[ip_address]
            if current_time - ts <= cls.WINDOW_SIZE
        ]
        
        return len(cls._attempts[ip_address]) >= cls.MAX_ATTEMPTS
    
    @classmethod
    def record_attempt(cls, ip_address: str):
        """Record a signature verification attempt"""
        current_time = time.time()
        if ip_address not in cls._attempts:
            cls._attempts[ip_address] = []
        cls._attempts[ip_address].append(current_time)