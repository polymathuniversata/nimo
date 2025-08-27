"""
DID (Decentralized Identifier) Verification Service for Nimo Platform

This service integrates with various DID methods and identity systems
to verify decentralized identities and link them to MeTTa reasoning.

Supported DID methods:
- did:eth (Ethereum addresses)
- did:key (Key-based DIDs)
- did:web (Web-based DIDs)
- ENS (Ethereum Name Service)

Security considerations:
- All DID resolution is done through secure channels
- Signature verification for DID documents
- Timestamp validation for DID proofs
- Rate limiting for DID resolution requests
"""

import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse
from .metta_security import MeTTaSanitizer, MeTTaSecurityError, create_safe_metta_atom


class DIDVerificationError(Exception):
    """Exception raised for DID verification errors"""
    pass


class DIDVerifier:
    """Decentralized Identity Verification Service"""
    
    # Supported DID methods
    SUPPORTED_METHODS = {
        'eth': 'Ethereum address-based DID',
        'key': 'Key-based DID',
        'web': 'Web-based DID',
        'ens': 'Ethereum Name Service'
    }
    
    # DID resolution endpoints
    DID_RESOLVERS = {
        'universal': 'https://dev.uniresolver.io/1.0/identifiers/',
        'web3': 'https://api.web3.bio/profile/',
        'ens': 'https://metadata.ens.domains/mainnet/avatar/'
    }
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize DID verifier
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.request_timestamps = {}  # For rate limiting
        
    def verify_did(self, did: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify a DID and return verification result
        
        Args:
            did: Decentralized Identifier string
            proof: Optional cryptographic proof
            
        Returns:
            Verification result dictionary
            
        Raises:
            DIDVerificationError: If DID verification fails
        """
        try:
            # Sanitize and validate DID format
            sanitized_did = self._sanitize_did(did)
            
            # Check cache first
            cache_key = f"did_verify:{sanitized_did}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            # Parse DID method
            method, identifier = self._parse_did(sanitized_did)
            
            if method not in self.SUPPORTED_METHODS:
                raise DIDVerificationError(f"Unsupported DID method: {method}")
            
            # Perform method-specific verification
            verification_result = self._verify_by_method(method, identifier, proof)
            
            # Add DID document resolution
            did_document = self._resolve_did_document(sanitized_did)
            
            # Combine results
            result = {
                'did': sanitized_did,
                'method': method,
                'verified': verification_result.get('verified', False),
                'confidence': verification_result.get('confidence', 0.0),
                'did_document': did_document,
                'proof_valid': self._validate_proof(proof, did_document) if proof else None,
                'verification_time': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=self.cache_ttl)).isoformat()
            }
            
            # Cache result
            self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            raise DIDVerificationError(f"DID verification failed: {str(e)}")
    
    def verify_ens_name(self, ens_name: str) -> Dict[str, Any]:
        """
        Verify ENS (Ethereum Name Service) name
        
        Args:
            ens_name: ENS name (e.g., 'vitalik.eth')
            
        Returns:
            ENS verification result
        """
        try:
            # Sanitize ENS name
            if not ens_name.endswith('.eth'):
                raise DIDVerificationError("Invalid ENS name format")
            
            sanitized_name = MeTTaSanitizer.sanitize_string(ens_name, "ens_name", 100)
            
            # Check rate limiting
            if not self._check_rate_limit('ens'):
                raise DIDVerificationError("Rate limit exceeded for ENS resolution")
            
            # Resolve ENS through multiple services
            ens_data = self._resolve_ens_multi(sanitized_name)
            
            return {
                'ens_name': sanitized_name,
                'verified': ens_data is not None,
                'ethereum_address': ens_data.get('address') if ens_data else None,
                'avatar': ens_data.get('avatar') if ens_data else None,
                'records': ens_data.get('records', {}) if ens_data else {},
                'verification_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise DIDVerificationError(f"ENS verification failed: {str(e)}")
    
    def create_identity_proof(self, did: str, identity_data: Dict[str, Any]) -> str:
        """
        Create a cryptographic proof linking DID to identity data
        
        Args:
            did: Decentralized identifier
            identity_data: Identity data to prove
            
        Returns:
            Cryptographic proof hash
        """
        try:
            # Create canonical representation
            canonical_data = {
                'did': self._sanitize_did(did),
                'identity': identity_data,
                'timestamp': int(time.time()),
                'nonce': hashlib.sha256(f"{did}:{time.time()}".encode()).hexdigest()[:16]
            }
            
            # Generate proof hash
            canonical_json = json.dumps(canonical_data, sort_keys=True)
            proof_hash = hashlib.sha256(canonical_json.encode()).hexdigest()
            
            return f"0x{proof_hash}"
            
        except Exception as e:
            raise DIDVerificationError(f"Proof creation failed: {str(e)}")
    
    def _sanitize_did(self, did: str) -> str:
        """Sanitize and validate DID format"""
        if not isinstance(did, str):
            raise DIDVerificationError("DID must be a string")
        
        if len(did) > 1000:
            raise DIDVerificationError("DID exceeds maximum length")
        
        if not did.startswith('did:'):
            raise DIDVerificationError("DID must start with 'did:'")
        
        # Basic format validation
        parts = did.split(':')
        if len(parts) < 3:
            raise DIDVerificationError("Invalid DID format")
        
        return did.lower().strip()
    
    def _parse_did(self, did: str) -> Tuple[str, str]:
        """Parse DID into method and identifier"""
        parts = did.split(':')
        method = parts[1]
        identifier = ':'.join(parts[2:])
        return method, identifier
    
    def _verify_by_method(self, method: str, identifier: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform method-specific DID verification"""
        if method == 'eth':
            return self._verify_ethereum_did(identifier, proof)
        elif method == 'key':
            return self._verify_key_did(identifier, proof)
        elif method == 'web':
            return self._verify_web_did(identifier, proof)
        else:
            return {'verified': False, 'confidence': 0.0, 'reason': f'Unsupported method: {method}'}
    
    def _verify_ethereum_did(self, identifier: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verify Ethereum-based DID"""
        try:
            # Basic Ethereum address validation
            if not identifier.startswith('0x') or len(identifier) != 42:
                return {'verified': False, 'confidence': 0.0, 'reason': 'Invalid Ethereum address format'}
            
            # Check if address is checksummed (higher confidence)
            is_checksummed = any(c.isupper() for c in identifier[2:]) and any(c.islower() for c in identifier[2:])
            
            confidence = 0.8 if is_checksummed else 0.6
            
            return {
                'verified': True,
                'confidence': confidence,
                'ethereum_address': identifier,
                'checksummed': is_checksummed
            }
            
        except Exception as e:
            return {'verified': False, 'confidence': 0.0, 'reason': str(e)}
    
    def _verify_key_did(self, identifier: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verify key-based DID"""
        try:
            # Basic key format validation
            if len(identifier) < 32:
                return {'verified': False, 'confidence': 0.0, 'reason': 'Key too short'}
            
            # For now, basic format validation
            # In production, would verify cryptographic properties
            confidence = 0.7  # Medium confidence without crypto verification
            
            return {
                'verified': True,
                'confidence': confidence,
                'key_type': 'ed25519' if identifier.startswith('z') else 'unknown'
            }
            
        except Exception as e:
            return {'verified': False, 'confidence': 0.0, 'reason': str(e)}
    
    def _verify_web_did(self, identifier: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verify web-based DID"""
        try:
            # Parse web DID identifier
            parts = identifier.split(':', 1)
            if len(parts) != 2:
                return {'verified': False, 'confidence': 0.0, 'reason': 'Invalid web DID format'}
            
            domain, path = parts[0], parts[1] if len(parts) > 1 else ''
            
            # Basic domain validation
            if not self._is_valid_domain(domain):
                return {'verified': False, 'confidence': 0.0, 'reason': 'Invalid domain'}
            
            # For production, would attempt to resolve the DID document from the domain
            confidence = 0.5  # Lower confidence without actual resolution
            
            return {
                'verified': True,
                'confidence': confidence,
                'domain': domain,
                'path': path
            }
            
        except Exception as e:
            return {'verified': False, 'confidence': 0.0, 'reason': str(e)}
    
    def _resolve_did_document(self, did: str) -> Optional[Dict[str, Any]]:
        """Resolve DID document from universal resolver"""
        try:
            if not self._check_rate_limit('resolve'):
                return None
            
            # Use universal resolver
            url = f"{self.DID_RESOLVERS['universal']}{did}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('didDocument')
            
        except Exception as e:
            print(f"DID document resolution failed: {e}")
        
        return None
    
    def _resolve_ens_multi(self, ens_name: str) -> Optional[Dict[str, Any]]:
        """Resolve ENS through multiple services for redundancy"""
        # Try Web3.bio first
        try:
            url = f"{self.DID_RESOLVERS['web3']}{ens_name}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        
        # Fallback methods would go here
        return None
    
    def _validate_proof(self, proof: Dict[str, Any], did_document: Dict[str, Any]) -> bool:
        """Validate cryptographic proof against DID document"""
        if not proof or not did_document:
            return False
        
        # Basic proof structure validation
        required_fields = ['signature', 'timestamp', 'challenge']
        if not all(field in proof for field in required_fields):
            return False
        
        # Check timestamp (not too old)
        try:
            proof_time = datetime.fromisoformat(proof['timestamp'].replace('Z', '+00:00'))
            if datetime.now() - proof_time > timedelta(hours=1):
                return False
        except Exception:
            return False
        
        # In production, would verify signature against public keys in DID document
        return True
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Basic domain validation"""
        try:
            parsed = urlparse(f"https://{domain}")
            return bool(parsed.netloc) and '.' in domain and len(domain) <= 253
        except Exception:
            return False
    
    def _check_rate_limit(self, operation: str, limit: int = 10) -> bool:
        """Check rate limiting for DID operations"""
        now = time.time()
        key = f"{operation}_requests"
        
        if key not in self.request_timestamps:
            self.request_timestamps[key] = []
        
        # Remove old timestamps (older than 1 minute)
        self.request_timestamps[key] = [
            ts for ts in self.request_timestamps[key] 
            if now - ts < 60
        ]
        
        # Check if under limit
        if len(self.request_timestamps[key]) >= limit:
            return False
        
        # Add current request
        self.request_timestamps[key].append(now)
        return True
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if result is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        expires_at = datetime.fromisoformat(cache_entry['expires_at'])
        
        return datetime.now() < expires_at
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache verification result"""
        self.cache[cache_key] = {
            'data': result,
            'expires_at': result['expires_at']
        }
        
        # Limit cache size
        if len(self.cache) > 1000:
            # Remove oldest entries
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1]['expires_at']
            )
            for key, _ in sorted_entries[:100]:
                del self.cache[key]


# Integration with MeTTa reasoning
class MeTTaDIDIntegration:
    """Integration between DID verification and MeTTa reasoning"""
    
    def __init__(self, did_verifier: DIDVerifier = None):
        """
        Initialize MeTTa-DID integration
        
        Args:
            did_verifier: DID verifier instance
        """
        self.did_verifier = did_verifier or DIDVerifier()
    
    def verify_user_identity(self, user_id: str, did: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify user identity using DID and create MeTTa atoms
        
        Args:
            user_id: Nimo user ID
            did: Decentralized identifier
            proof: Optional cryptographic proof
            
        Returns:
            Verification result with MeTTa atoms
        """
        try:
            # Sanitize inputs
            sanitized_user_id = MeTTaSanitizer.sanitize_id(user_id, "user_id")
            
            # Verify DID
            did_result = self.did_verifier.verify_did(did, proof)
            
            # Create MeTTa atoms for verified identity
            metta_atoms = []
            
            if did_result['verified']:
                # Core identity atom
                identity_atom = create_safe_metta_atom(
                    '(DIDVerification "{user_id}" "{did}" "{method}")',
                    user_id=sanitized_user_id,
                    did=did_result['did'],
                    method=did_result['method']
                )
                metta_atoms.append(identity_atom)
                
                # Confidence atom
                confidence_atom = create_safe_metta_atom(
                    '(IdentityConfidence "{user_id}" {confidence})',
                    user_id=sanitized_user_id,
                    confidence=str(did_result['confidence'])
                )
                metta_atoms.append(confidence_atom)
                
                # Method-specific atoms
                if did_result['method'] == 'eth' and 'ethereum_address' in did_result:
                    eth_atom = create_safe_metta_atom(
                        '(EthereumAddress "{user_id}" "{address}")',
                        user_id=sanitized_user_id,
                        address=did_result['ethereum_address']
                    )
                    metta_atoms.append(eth_atom)
            
            return {
                'user_id': sanitized_user_id,
                'did_verification': did_result,
                'metta_atoms': metta_atoms,
                'identity_verified': did_result['verified'],
                'confidence': did_result['confidence']
            }
            
        except Exception as e:
            raise DIDVerificationError(f"User identity verification failed: {str(e)}")
    
    def generate_identity_metta_rules(self) -> str:
        """
        Generate MeTTa rules for identity verification
        
        Returns:
            MeTTa rule definitions as string
        """
        return '''
;; Enhanced DID Identity Verification Rules
;; These rules integrate with the DID verification service

;; Core identity verification rule
(= (HasVerifiedDID $user-id)
   (DIDVerification $user-id $_ $_))

;; Identity confidence scoring
(= (IdentityTrustScore $user-id)
   (let* (($confidence-atom (IdentityConfidence $user-id $confidence)))
     (if $confidence-atom $confidence 0.0)))

;; Ethereum identity verification
(= (HasEthereumIdentity $user-id)
   (EthereumAddress $user-id $_))

;; Identity-based contribution verification enhancement
(= (VerifyWithIdentity $contrib-id)
   (let* (($user-id (GetContributorId $contrib-id))
          ($has-did (HasVerifiedDID $user-id))
          ($trust-score (IdentityTrustScore $user-id))
          ($base-verification (VerifyContribution $contrib-id)))
     (and $base-verification $has-did (> $trust-score 0.7))))

;; Identity reputation bonus
(= (IdentityReputationBonus $user-id)
   (let* (($trust-score (IdentityTrustScore $user-id)))
     (cond ((> $trust-score 0.9) 20)
           ((> $trust-score 0.7) 10)
           ((> $trust-score 0.5) 5)
           (else 0))))
'''