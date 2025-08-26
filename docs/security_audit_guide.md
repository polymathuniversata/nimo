# Nimo Platform Security & Audit Guide

## Overview

This document provides a comprehensive guide to the security measures implemented in the Nimo Platform and outlines the requirements for security audits. The platform handles sensitive data including user identities, contributions, financial tokens, and blockchain transactions, requiring robust security measures at every layer.

**Security Philosophy:**
- Defense in depth with multiple security layers
- Zero-trust architecture principles
- Continuous monitoring and threat detection
- Proactive security measures over reactive fixes
- Transparent security practices and regular audits

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐│
│  │   Frontend       │    │   Backend API    │    │  Blockchain  ││
│  │   Security       │    │   Security       │    │   Security   ││
│  │                  │    │                  │    │              ││
│  │ • Input Sanitize │    │ • Auth/AuthZ     │    │ • Access     ││
│  │ • XSS Protection │    │ • Rate Limiting  │    │   Control    ││
│  │ • CSRF Guards    │    │ • Input Valid.   │    │ • Reentrancy ││
│  │ • Secure Storage │    │ • SQL Injection  │    │   Guards     ││
│  │ • Content Policy │    │ • API Security   │    │ • Integer    ││
│  └──────────────────┘    └──────────────────┘    │   Overflow   ││
│                                                  │   Protection ││
│  ┌──────────────────┐    ┌──────────────────┐    └──────────────┘│
│  │   MeTTa Engine   │    │   Infrastructure │                    │
│  │   Security       │    │   Security       │                    │
│  │                  │    │                  │                    │
│  │ • Rule Validation│    │ • Network        │                    │
│  │ • Execution      │    │   Security       │                    │
│  │   Sandboxing     │    │ • Data Encrypt.  │                    │
│  │ • Access Control │    │ • Monitoring     │                    │
│  │ • Audit Logging  │    │ • Backup Security│                    │
│  └──────────────────┘    └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Authentication & Authorization

### JWT Token Security

**Implementation:** `backend/routes/auth.py`

```python
# Secure JWT configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # Strong secret from environment
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour expiration
JWT_ALGORITHM = 'HS256'  # HMAC-SHA256 algorithm

# Token generation with secure claims
def create_access_token(identity):
    additional_claims = {
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES),
        "iss": "nimo-platform",
        "aud": "nimo-api"
    }
    return create_access_token(identity=identity, additional_claims=additional_claims)
```

**Security Measures:**
- ✅ Strong, randomly generated secret keys
- ✅ Short token expiration (1 hour)
- ✅ Secure algorithm (HMAC-SHA256)
- ✅ Proper issuer/audience validation
- ✅ Token blacklisting for logout
- ✅ Refresh token rotation

### Password Security

```python
# backend/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
import re

class User(db.Model):
    def set_password(self, password):
        # Password strength validation
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        # Hash with strong parameters
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256:100000',  # 100,000 iterations
            salt_length=32
        )
    
    def _validate_password_strength(self, password):
        """Validate password meets security requirements"""
        if len(password) < 12:
            return False
        if not re.search(r'[A-Z]', password):  # Uppercase
            return False
        if not re.search(r'[a-z]', password):  # Lowercase
            return False
        if not re.search(r'\d', password):     # Digit
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Special char
            return False
        return True
```

**Security Requirements:**
- ✅ Minimum 12 characters
- ✅ Mixed case letters, numbers, special characters
- ✅ PBKDF2 with SHA-256 and 100,000 iterations
- ✅ 32-byte random salt
- ✅ Protection against rainbow table attacks

### Role-Based Access Control (RBAC)

```python
# backend/models/user.py
class User(db.Model):
    roles = db.Column(db.JSON, default=lambda: ['user'])
    
    def has_role(self, role):
        return role in (self.roles or [])
    
    def has_permission(self, permission):
        role_permissions = {
            'admin': ['*'],
            'verifier': ['verify_contributions', 'view_all_contributions'],
            'metta_agent': ['execute_metta_rules', 'verify_contributions'],
            'user': ['create_contributions', 'view_own_contributions']
        }
        
        for role in (self.roles or []):
            perms = role_permissions.get(role, [])
            if '*' in perms or permission in perms:
                return True
        return False

# Decorator for endpoint protection
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 2. API Security

### Input Validation & Sanitization

```python
# backend/utils/validation.py
from marshmallow import Schema, fields, validate, ValidationError
import bleach
import re

class ContributionSchema(Schema):
    title = fields.Str(
        required=True,
        validate=[
            validate.Length(min=5, max=200),
            validate.Regexp(r'^[a-zA-Z0-9\s\-_.,!?]+$')  # Safe characters only
        ]
    )
    description = fields.Str(
        validate=validate.Length(max=2000)
    )
    evidence = fields.Dict()
    
    def load(self, data, **kwargs):
        # Sanitize input data
        if 'title' in data:
            data['title'] = bleach.clean(data['title'])
        if 'description' in data:
            data['description'] = bleach.clean(data['description'])
        
        return super().load(data, **kwargs)

# Usage in routes
@contribution_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission('create_contributions')
def add_contribution():
    schema = ContributionSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Proceed with validated and sanitized data
    ...
```

### Rate Limiting

```python
# backend/utils/rate_limiting.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Initialize rate limiter with Redis backend
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["1000 per hour", "100 per minute"]
)

# Apply specific limits to sensitive endpoints
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts")
def login():
    ...

@contribution_bp.route('/<int:contrib_id>/verify', methods=['POST'])
@limiter.limit("10 per minute", error_message="Too many verification attempts")
@jwt_required()
@require_permission('verify_contributions')
def verify_contribution(contrib_id):
    ...
```

### SQL Injection Prevention

**ORM Usage:**
```python
# ✅ SAFE: Using SQLAlchemy ORM
contributions = Contribution.query.filter_by(user_id=current_user_id).all()

# ✅ SAFE: Parameterized queries when raw SQL needed
results = db.session.execute(
    text("SELECT * FROM contributions WHERE user_id = :user_id"),
    {'user_id': user_id}
).fetchall()

# ❌ UNSAFE: String concatenation (never do this)
# query = f"SELECT * FROM contributions WHERE user_id = {user_id}"
```

### CORS Security

```python
# backend/config.py
from flask_cors import CORS

# Restrictive CORS configuration
CORS_CONFIG = {
    'origins': [
        'https://nimo.polymathuniversata.com',
        'https://app.nimo.polymathuniversata.com'
    ],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization'],
    'supports_credentials': True,
    'max_age': 86400  # 24 hours
}

CORS(app, **CORS_CONFIG)
```

---

## 3. Smart Contract Security

### Access Control Implementation

```solidity
// contracts/src/NimoIdentity.sol
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract NimoIdentity is ERC721, AccessControl, ReentrancyGuard, Pausable {
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant METTA_AGENT_ROLE = keccak256("METTA_AGENT_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    
    modifier onlyRole(bytes32 role) {
        require(hasRole(role, msg.sender), "AccessControl: sender must have role");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused(), "Contract is paused");
        _;
    }
    
    // Emergency pause function
    function emergencyPause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }
}
```

### Reentrancy Protection

```solidity
// Using OpenZeppelin's ReentrancyGuard
function investInBond(uint256 bondId) 
    external 
    payable 
    nonReentrant 
    whenNotPaused 
{
    require(impactBonds[bondId].isActive, "Bond is not active");
    require(msg.value > 0, "Investment amount must be greater than 0");
    require(block.timestamp < impactBonds[bondId].maturityDate, "Bond has matured");
    
    ImpactBond storage bond = impactBonds[bondId];
    bond.investments[msg.sender] += msg.value;
    bond.currentAmount += msg.value;
    
    emit BondInvestment(bondId, msg.sender, msg.value);
}
```

### Integer Overflow Protection

```solidity
// Using Solidity 0.8.x built-in overflow protection
function verifyContribution(uint256 contributionId, uint256 tokensToAward) 
    external 
    onlyRole(VERIFIER_ROLE) 
    whenNotPaused
{
    require(contributions[contributionId].identityId != 0, "Contribution does not exist");
    require(!contributions[contributionId].verified, "Contribution already verified");
    
    Contribution storage contribution = contributions[contributionId];
    Identity storage identity = identities[contribution.identityId];
    
    // Safe arithmetic operations (checked by default in Solidity 0.8+)
    identity.tokenBalance += tokensToAward;
    identity.reputationScore += tokensToAward / 10;
    
    contribution.verified = true;
    contribution.verifier = msg.sender;
    contribution.tokensAwarded = tokensToAward;
}
```

### Input Validation

```solidity
function createIdentity(string memory username, string memory metadataURI) external {
    require(bytes(username).length > 0, "Username cannot be empty");
    require(bytes(username).length <= 50, "Username too long");
    require(bytes(metadataURI).length > 0, "Metadata URI cannot be empty");
    require(bytes(metadataURI).length <= 200, "Metadata URI too long");
    require(usernameToTokenId[username] == 0, "Username already exists");
    require(addressToTokenId[msg.sender] == 0, "Address already has identity");
    
    // Additional validation for username format
    bytes memory usernameBytes = bytes(username);
    for (uint i = 0; i < usernameBytes.length; i++) {
        bytes1 char = usernameBytes[i];
        require(
            (char >= 0x30 && char <= 0x39) || // 0-9
            (char >= 0x41 && char <= 0x5A) || // A-Z
            (char >= 0x61 && char <= 0x7A) || // a-z
            char == 0x5F,                     // _
            "Invalid character in username"
        );
    }
    
    uint256 tokenId = _nextTokenId++;
    // ... rest of implementation
}
```

---

## 4. MeTTa Engine Security

### Rule Validation & Sandboxing

```python
# backend/services/metta_reasoning.py
import ast
import re
from typing import Set, List

class MeTTaSecurityManager:
    """Security manager for MeTTa rule execution"""
    
    ALLOWED_FUNCTIONS = {
        # Core MeTTa functions
        'and', 'or', 'not', 'if', 'let', 'match', 'cond',
        # Mathematical operations
        '+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=',
        # String operations
        'string-append', 'string-length', 'substring',
        # List operations
        'list', 'first', 'rest', 'length', 'append',
        # Type checking
        'number?', 'string?', 'list?', 'atom?'
    }
    
    FORBIDDEN_PATTERNS = [
        r'import\s+',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__.*__',
        r'file\s*\(',
        r'open\s*\(',
        r'system\s*\(',
        r'subprocess',
    ]
    
    def validate_rule(self, rule: str) -> bool:
        """Validate MeTTa rule for security"""
        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, rule, re.IGNORECASE):
                raise SecurityError(f"Forbidden pattern detected: {pattern}")
        
        # Validate function usage
        tokens = self._tokenize_rule(rule)
        for token in tokens:
            if token.startswith('(') and token not in self.ALLOWED_FUNCTIONS:
                function_name = token[1:].split()[0] if ' ' in token else token[1:]
                if function_name not in self.ALLOWED_FUNCTIONS:
                    raise SecurityError(f"Unauthorized function: {function_name}")
        
        return True
    
    def execute_rule_safely(self, rule: str, timeout: int = 5):
        """Execute MeTTa rule with security constraints"""
        import signal
        import time
        
        def timeout_handler(signum, frame):
            raise TimeoutError("MeTTa rule execution timeout")
        
        # Validate rule first
        self.validate_rule(rule)
        
        # Set execution timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = self.metta_space.parse_and_eval(rule)
            return result
        finally:
            signal.alarm(0)  # Clear timeout

class MeTTaReasoning:
    def __init__(self, rules_dir=None, db_path=None):
        self.security_manager = MeTTaSecurityManager()
        # ... rest of initialization
    
    def _execute_secure_rule(self, rule: str):
        """Execute rule with security checks"""
        try:
            return self.security_manager.execute_rule_safely(rule)
        except SecurityError as e:
            logger.warning(f"Security violation in MeTTa rule: {e}")
            return None
        except TimeoutError as e:
            logger.warning(f"MeTTa rule execution timeout: {rule[:100]}...")
            return None
```

### Audit Logging

```python
# backend/utils/audit_logger.py
import logging
import json
import hashlib
from datetime import datetime

class AuditLogger:
    """Secure audit logging for sensitive operations"""
    
    def __init__(self):
        self.logger = logging.getLogger('nimo.audit')
        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_verification(self, user_id: str, contribution_id: str, 
                        result: dict, verifier: str):
        """Log contribution verification"""
        audit_entry = {
            'event': 'contribution_verification',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'contribution_id': contribution_id,
            'verifier': verifier,
            'result': {
                'verified': result.get('verified'),
                'confidence': result.get('confidence'),
                'tokens_awarded': result.get('tokens')
            },
            'proof_hash': result.get('metta_proof')
        }
        
        # Create integrity hash
        audit_entry['integrity_hash'] = self._create_integrity_hash(audit_entry)
        
        self.logger.info(json.dumps(audit_entry))
    
    def log_fraud_detection(self, user_id: str, contribution_id: str, 
                          fraud_result: dict):
        """Log fraud detection events"""
        audit_entry = {
            'event': 'fraud_detection',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'contribution_id': contribution_id,
            'fraud_detected': fraud_result.get('is_fraud', False),
            'reason': fraud_result.get('reason'),
            'confidence': fraud_result.get('confidence')
        }
        
        audit_entry['integrity_hash'] = self._create_integrity_hash(audit_entry)
        self.logger.warning(json.dumps(audit_entry))
    
    def _create_integrity_hash(self, entry: dict) -> str:
        """Create integrity hash for audit entry"""
        # Remove hash field if present
        entry_copy = {k: v for k, v in entry.items() if k != 'integrity_hash'}
        
        # Create canonical representation
        canonical = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))
        
        # Generate hash
        return hashlib.sha256(canonical.encode()).hexdigest()
```

---

## 5. Infrastructure Security

### Environment Configuration

```bash
# .env.production - Secure environment configuration
# Database
DATABASE_URL=postgresql://user:password@secure-db-host:5432/nimo_prod
DB_SSL_MODE=require
DB_SSL_CERT=/path/to/client-cert.pem
DB_SSL_KEY=/path/to/client-key.pem
DB_SSL_CA=/path/to/ca-cert.pem

# JWT Security
JWT_SECRET_KEY=<256-bit-random-key>
JWT_ALGORITHM=HS256

# MeTTa Security
USE_METTA_REASONING=true
METTA_CONFIDENCE_THRESHOLD=0.8
METTA_EXECUTION_TIMEOUT=10
METTA_MAX_RULES_PER_USER=100

# Blockchain Security
PROVIDER_URL=https://mainnet.base.org
PRIVATE_KEY_ENCRYPTED=<encrypted-private-key>
CONTRACT_VERIFY_SIGNATURES=true

# Rate Limiting
REDIS_URL=redis://redis-host:6379/0
RATE_LIMIT_STORAGE=redis
RATE_LIMIT_STRATEGY=moving-window

# Monitoring
SENTRY_DSN=<sentry-dsn>
LOG_LEVEL=INFO
AUDIT_LOG_RETENTION_DAYS=2555  # 7 years
```

### Network Security

```yaml
# docker-compose.prod.yml - Production security configuration
version: '3.8'

services:
  backend:
    image: nimo/backend:latest
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    networks:
      - internal
      - web
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - web
    depends_on:
      - backend
    security_opt:
      - no-new-privileges:true

networks:
  internal:
    driver: overlay
    internal: true
  web:
    driver: overlay

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /encrypted/postgres_data
```

### SSL/TLS Configuration

```nginx
# nginx/prod.conf
server {
    listen 443 ssl http2;
    server_name nimo.polymathuniversata.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location /api/ {
        proxy_pass http://backend:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout configuration
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## 6. Frontend Security

### Content Security Policy

```javascript
// frontend/src/main.js - CSP configuration
const cspMeta = document.createElement('meta');
cspMeta.httpEquiv = 'Content-Security-Policy';
cspMeta.content = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' https://fonts.gstatic.com",
  "img-src 'self' data: https:",
  "connect-src 'self' https://sepolia.base.org https://mainnet.base.org",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'"
].join('; ');
document.head.appendChild(cspMeta);
```

### Input Sanitization

```javascript
// frontend/src/utils/security.js
import DOMPurify from 'dompurify';

export class SecurityUtils {
  /**
   * Sanitize HTML content
   */
  static sanitizeHtml(html) {
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
      ALLOWED_ATTR: ['href', 'title'],
      ALLOW_DATA_ATTR: false
    });
  }
  
  /**
   * Validate and sanitize form input
   */
  static sanitizeInput(input, type = 'text') {
    if (typeof input !== 'string') return '';
    
    // Remove potentially dangerous characters
    let sanitized = input.replace(/[<>\"'`]/g, '');
    
    switch (type) {
      case 'email':
        return sanitized.toLowerCase().trim();
      case 'username':
        return sanitized.replace(/[^a-zA-Z0-9_-]/g, '').substring(0, 50);
      case 'url':
        try {
          const url = new URL(sanitized);
          return ['http:', 'https:'].includes(url.protocol) ? url.toString() : '';
        } catch {
          return '';
        }
      default:
        return sanitized.trim();
    }
  }
  
  /**
   * Validate Ethereum address
   */
  static isValidEthereumAddress(address) {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  }
  
  /**
   * Secure local storage wrapper
   */
  static secureStorage = {
    set(key, value) {
      try {
        const encrypted = btoa(JSON.stringify(value));
        localStorage.setItem(key, encrypted);
      } catch (error) {
        console.warn('Failed to store data securely:', error);
      }
    },
    
    get(key) {
      try {
        const encrypted = localStorage.getItem(key);
        return encrypted ? JSON.parse(atob(encrypted)) : null;
      } catch (error) {
        console.warn('Failed to retrieve data securely:', error);
        return null;
      }
    },
    
    remove(key) {
      localStorage.removeItem(key);
    }
  };
}
```

### Wallet Security

```javascript
// frontend/src/composables/useWallet.js
import { ref, computed } from 'vue';
import { SecurityUtils } from '@/utils/security';

export function useWallet() {
  const isConnected = ref(false);
  const address = ref('');
  const error = ref('');
  
  const connectWallet = async () => {
    if (!window.ethereum) {
      error.value = 'MetaMask or compatible wallet not found';
      return;
    }
    
    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });
      
      if (accounts.length === 0) {
        throw new Error('No accounts available');
      }
      
      const account = accounts[0];
      
      // Validate address format
      if (!SecurityUtils.isValidEthereumAddress(account)) {
        throw new Error('Invalid Ethereum address format');
      }
      
      // Verify we're on the correct network
      const chainId = await window.ethereum.request({
        method: 'eth_chainId'
      });
      
      const expectedChainId = import.meta.env.VITE_CHAIN_ID;
      if (chainId !== expectedChainId) {
        await switchNetwork(expectedChainId);
      }
      
      address.value = account;
      isConnected.value = true;
      error.value = '';
      
      // Securely store wallet connection status
      SecurityUtils.secureStorage.set('wallet_connected', {
        address: account,
        chainId: chainId,
        timestamp: Date.now()
      });
      
    } catch (err) {
      console.error('Wallet connection error:', err);
      error.value = err.message || 'Failed to connect wallet';
      isConnected.value = false;
      address.value = '';
    }
  };
  
  const switchNetwork = async (targetChainId) => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: targetChainId }]
      });
    } catch (switchError) {
      // Network doesn't exist, add it
      if (switchError.code === 4902) {
        await addNetwork(targetChainId);
      } else {
        throw switchError;
      }
    }
  };
  
  const disconnect = () => {
    isConnected.value = false;
    address.value = '';
    error.value = '';
    SecurityUtils.secureStorage.remove('wallet_connected');
  };
  
  return {
    isConnected: computed(() => isConnected.value),
    address: computed(() => address.value),
    error: computed(() => error.value),
    connectWallet,
    disconnect
  };
}
```

---

## 7. Security Monitoring & Incident Response

### Security Monitoring

```python
# backend/utils/security_monitor.py
import logging
import time
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import request, g
from functools import wraps

class SecurityMonitor:
    """Real-time security monitoring and alerting"""
    
    def __init__(self):
        self.failed_logins = defaultdict(deque)
        self.suspicious_ips = set()
        self.rate_violations = defaultdict(int)
        self.security_events = deque(maxlen=10000)
        
        # Setup logging
        self.logger = logging.getLogger('nimo.security')
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)
    
    def log_security_event(self, event_type: str, details: dict, severity: str = 'INFO'):
        """Log security event with structured data"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'ip': request.remote_addr if request else 'unknown',
            'user_agent': request.headers.get('User-Agent') if request else 'unknown'
        }
        
        self.security_events.append(event)
        
        log_func = getattr(self.logger, severity.lower(), self.logger.info)
        log_func(json.dumps(event))
        
        # Trigger alerts for high-severity events
        if severity in ['WARNING', 'ERROR', 'CRITICAL']:
            self._trigger_alert(event)
    
    def monitor_login_attempts(self, email: str, success: bool):
        """Monitor login attempts for brute force detection"""
        ip = request.remote_addr
        now = time.time()
        
        if not success:
            self.failed_logins[ip].append(now)
            
            # Remove old attempts (older than 15 minutes)
            cutoff = now - 900  # 15 minutes
            while self.failed_logins[ip] and self.failed_logins[ip][0] < cutoff:
                self.failed_logins[ip].popleft()
            
            # Check for suspicious activity
            if len(self.failed_logins[ip]) >= 5:  # 5 failed attempts in 15 minutes
                self.suspicious_ips.add(ip)
                self.log_security_event('brute_force_attempt', {
                    'ip': ip,
                    'email': email,
                    'attempt_count': len(self.failed_logins[ip])
                }, 'WARNING')
        else:
            # Successful login, clear failed attempts
            if ip in self.failed_logins:
                del self.failed_logins[ip]
            if ip in self.suspicious_ips:
                self.suspicious_ips.remove(ip)
    
    def detect_anomalies(self, user_id: str, action: str, details: dict):
        """Detect anomalous user behavior"""
        # Time-based anomaly detection
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:  # Activity outside business hours
            self.log_security_event('off_hours_activity', {
                'user_id': user_id,
                'action': action,
                'hour': current_hour,
                'details': details
            }, 'INFO')
        
        # Rapid successive actions
        g.user_actions = getattr(g, 'user_actions', deque(maxlen=100))
        g.user_actions.append((time.time(), action))
        
        recent_actions = [a for t, a in g.user_actions if time.time() - t < 60]
        if len(recent_actions) > 10:  # More than 10 actions per minute
            self.log_security_event('rapid_actions', {
                'user_id': user_id,
                'action_count': len(recent_actions),
                'actions': recent_actions
            }, 'WARNING')
    
    def _trigger_alert(self, event: dict):
        """Trigger security alerts for critical events"""
        # In production, this would integrate with alerting systems
        # like PagerDuty, Slack, email notifications, etc.
        
        if event['severity'] == 'CRITICAL':
            # Immediate notification
            print(f"CRITICAL SECURITY ALERT: {event['event_type']}")
            # send_slack_alert(event)
            # send_email_alert(event)
        
        elif event['severity'] == 'WARNING':
            # Queue for review
            print(f"Security Warning: {event['event_type']}")
            # queue_for_review(event)

# Middleware for security monitoring
security_monitor = SecurityMonitor()

def monitor_security(f):
    """Decorator to monitor endpoint security"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            
            # Monitor successful requests
            if hasattr(g, 'current_user'):
                security_monitor.detect_anomalies(
                    g.current_user.id,
                    f.__name__,
                    {'endpoint': request.endpoint, 'method': request.method}
                )
            
            return result
            
        except Exception as e:
            # Log security-relevant errors
            security_monitor.log_security_event('endpoint_error', {
                'endpoint': request.endpoint,
                'method': request.method,
                'error': str(e),
                'duration': time.time() - start_time
            }, 'ERROR')
            raise
    
    return decorated_function
```

### Incident Response Plan

```yaml
# security/incident-response-plan.yml
incident_response:
  severity_levels:
    critical:
      description: "Immediate threat to user data or system integrity"
      response_time: "15 minutes"
      escalation: "Security team, CTO, CEO"
      actions:
        - Activate incident response team
        - Isolate affected systems
        - Notify users if data breach suspected
        - Document all actions
    
    high:
      description: "Significant security issue requiring immediate attention"
      response_time: "1 hour"
      escalation: "Security team, Engineering lead"
      actions:
        - Assess impact and scope
        - Implement containment measures
        - Begin forensic analysis
    
    medium:
      description: "Security concern requiring investigation"
      response_time: "4 hours"
      escalation: "Security team"
      actions:
        - Investigate and document
        - Implement fixes if needed
    
    low:
      description: "Minor security issue or potential vulnerability"
      response_time: "24 hours"
      escalation: "Development team"
      actions:
        - Review and schedule fix
        - Update security documentation

  communication:
    internal:
      - Slack #security-alerts channel
      - Email to security@polymathuniversata.com
      - Incident management system
    
    external:
      - User notifications (if data affected)
      - Regulatory reporting (if required)
      - Public disclosure (if significant)

  recovery:
    data_backup:
      - Daily encrypted backups
      - Point-in-time recovery capability
      - Geographic distribution
    
    system_restoration:
      - Blue-green deployment for quick rollback
      - Infrastructure as code for rapid rebuild
      - Disaster recovery site activation
```

---

## 8. Security Audit Requirements

### Pre-Audit Checklist

**Smart Contract Audit Requirements:**

```markdown
## Smart Contract Security Checklist

### Access Control
- [ ] Role-based permissions properly implemented
- [ ] Admin functions protected with appropriate modifiers
- [ ] Role assignment/revocation logged and audited
- [ ] Multi-signature requirements for critical operations

### Input Validation
- [ ] All user inputs validated for type, range, and format
- [ ] String length limits enforced
- [ ] Address validation for zero address and contract addresses
- [ ] Numerical overflow/underflow protection (Solidity 0.8+)

### Reentrancy Protection
- [ ] External calls follow check-effects-interactions pattern
- [ ] ReentrancyGuard modifier used for state-changing functions
- [ ] No recursive calls to untrusted contracts

### Economic Security
- [ ] Token minting controls and limits
- [ ] Proper accounting for all token transfers
- [ ] Protection against economic attacks (flash loans, etc.)
- [ ] Fair pricing mechanisms

### Emergency Controls
- [ ] Pause/unpause functionality for critical functions
- [ ] Emergency withdrawal mechanisms
- [ ] Circuit breakers for unusual activity
- [ ] Upgrade mechanisms secure and transparent

### Gas Optimization
- [ ] Functions optimized for gas usage
- [ ] No infinite loops or excessive gas consumption
- [ ] Batch operations where appropriate
- [ ] Storage optimization

### Testing Coverage
- [ ] 100% line coverage for all contracts
- [ ] Edge case testing
- [ ] Fuzz testing for critical functions
- [ ] Integration testing with external dependencies
```

**Backend Security Audit:**

```markdown
## Backend Security Audit Checklist

### Authentication & Authorization
- [ ] Strong password policies enforced
- [ ] JWT tokens properly configured and validated
- [ ] Session management secure
- [ ] Role-based access control implemented
- [ ] API endpoints properly protected

### Input Validation & Sanitization
- [ ] All inputs validated server-side
- [ ] SQL injection prevention measures
- [ ] XSS protection implemented
- [ ] CSRF protection enabled
- [ ] File upload security

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS/SSL properly configured
- [ ] Database connections secured
- [ ] Backup encryption implemented
- [ ] Key management secure

### API Security
- [ ] Rate limiting implemented
- [ ] API versioning and deprecation
- [ ] Error handling doesn't leak information
- [ ] CORS properly configured
- [ ] Request/response logging

### Infrastructure Security
- [ ] Server hardening completed
- [ ] Network security configured
- [ ] Container security best practices
- [ ] Monitoring and alerting setup
- [ ] Incident response plan tested
```

### Audit Process

**Phase 1: Automated Security Analysis**
```bash
# Smart contract static analysis
slither contracts/src/ --json-types pretty --exclude-dependencies

# Dependency vulnerability scanning
npm audit --audit-level high
pip-audit --requirement requirements.txt

# Code quality analysis
sonarqube-scanner -Dsonar.projectKey=nimo-platform

# SAST scanning
bandit -r backend/ -f json -o bandit-report.json
semgrep --config=auto backend/ --json --output=semgrep-report.json
```

**Phase 2: Manual Security Review**
- Architecture review
- Threat modeling
- Code review focusing on security-critical paths
- Configuration review
- Documentation review

**Phase 3: Penetration Testing**
- Web application penetration testing
- API security testing
- Smart contract security testing
- Infrastructure penetration testing
- Social engineering assessment

**Phase 4: Bug Bounty Program**
```markdown
## Nimo Security Bug Bounty Program

### Scope
- Smart contracts on mainnet
- API endpoints (https://api.nimo.polymathuniversata.com)
- Web application (https://app.nimo.polymathuniversata.com)
- Mobile applications (when released)

### Out of Scope
- Testnet deployments
- Third-party dependencies
- Social engineering attacks
- Physical security

### Reward Structure
- Critical: $5,000 - $25,000
- High: $1,000 - $5,000
- Medium: $500 - $1,000
- Low: $100 - $500

### Submission Requirements
- Clear proof of concept
- Steps to reproduce
- Impact assessment
- Suggested remediation
```

---

## 9. Compliance & Regulatory Requirements

### Data Privacy (GDPR/CCPA)

```python
# backend/utils/privacy.py
from datetime import datetime, timedelta
import hashlib

class PrivacyManager:
    """Handle privacy and data protection requirements"""
    
    def __init__(self):
        self.data_retention_periods = {
            'user_profiles': timedelta(days=2555),  # 7 years
            'contribution_data': timedelta(days=2555),
            'verification_records': timedelta(days=2555),
            'audit_logs': timedelta(days=2555),
            'session_data': timedelta(days=30),
            'analytics_data': timedelta(days=365)
        }
    
    def anonymize_user_data(self, user_id: str) -> dict:
        """Anonymize user data while preserving system integrity"""
        # Generate consistent anonymous ID
        anonymous_id = hashlib.sha256(f"anon_{user_id}".encode()).hexdigest()[:16]
        
        # Anonymization mapping
        anonymized_data = {
            'original_user_id': user_id,
            'anonymous_id': anonymous_id,
            'anonymized_at': datetime.utcnow(),
            'fields_anonymized': [
                'email', 'name', 'bio', 'location',
                'profile_image', 'contact_info'
            ]
        }
        
        return anonymized_data
    
    def handle_data_deletion_request(self, user_id: str) -> dict:
        """Process user data deletion request (GDPR Article 17)"""
        deletion_log = {
            'user_id': user_id,
            'deletion_requested_at': datetime.utcnow(),
            'deletion_reason': 'user_request',
            'data_categories_deleted': [],
            'data_categories_anonymized': [],
            'legal_basis_for_retention': []
        }
        
        # Identify data that must be retained for legal reasons
        legal_retention_data = self._identify_legal_retention_data(user_id)
        
        # Delete non-essential data
        # Anonymize data that must be retained
        
        return deletion_log
    
    def export_user_data(self, user_id: str) -> dict:
        """Export user data for data portability (GDPR Article 20)"""
        export_data = {
            'user_profile': self._get_user_profile_data(user_id),
            'contributions': self._get_user_contributions(user_id),
            'verifications': self._get_user_verifications(user_id),
            'tokens': self._get_user_token_history(user_id),
            'export_generated_at': datetime.utcnow().isoformat()
        }
        
        return export_data
```

### Financial Regulations

```python
# backend/utils/compliance.py
class FinancialComplianceManager:
    """Handle financial regulatory compliance"""
    
    def __init__(self):
        self.suspicious_activity_thresholds = {
            'large_token_transfer': 10000,  # Tokens
            'rapid_transfers': 50,  # Transfers per hour
            'unusual_patterns': 0.95  # Confidence threshold
        }
    
    def monitor_suspicious_activity(self, user_id: str, transaction_data: dict):
        """Monitor for suspicious financial activity"""
        # Large transaction monitoring
        if transaction_data.get('amount', 0) >= self.suspicious_activity_thresholds['large_token_transfer']:
            self._file_large_transaction_report(user_id, transaction_data)
        
        # Pattern analysis
        if self._detect_unusual_patterns(user_id, transaction_data):
            self._flag_for_manual_review(user_id, transaction_data)
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> dict:
        """Generate compliance report for regulators"""
        return {
            'reporting_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_users': self._count_active_users(start_date, end_date),
            'total_transactions': self._count_transactions(start_date, end_date),
            'suspicious_activities': self._get_suspicious_activities(start_date, end_date),
            'compliance_violations': self._get_violations(start_date, end_date)
        }
```

---

## 10. Security Testing & Validation

### Automated Security Testing

```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Slither Analysis
      uses: crytic/slither-action@v0.3.0
      with:
        target: contracts/src/
        slither-args: --exclude-dependencies --json-types pretty
    
    - name: SAST Scan with Semgrep
      run: |
        pip install semgrep
        semgrep --config=auto --json --output=semgrep-results.json .
    
    - name: Dependency Vulnerability Scan
      run: |
        cd backend
        pip install safety
        safety check --json --output safety-report.json
        
        cd ../frontend
        npm audit --audit-level high --json > npm-audit.json
    
    - name: Container Security Scan
      run: |
        docker build -t nimo/backend:test backend/
        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
          -v $(pwd):/tmp aquasec/trivy image nimo/backend:test
    
    - name: Upload Security Reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          semgrep-results.json
          safety-report.json
          npm-audit.json
```

### Security Test Suite

```python
# backend/tests/security/test_security_suite.py
import pytest
import time
from unittest.mock import patch
from backend.app import create_app
from backend.utils.security_monitor import security_monitor

class TestSecuritySuite:
    """Comprehensive security test suite"""
    
    @pytest.fixture
    def security_app(self):
        """Create app with security monitoring enabled"""
        app = create_app('testing')
        app.config['TESTING'] = True
        return app.test_client()
    
    def test_brute_force_protection(self, security_app):
        """Test brute force attack protection"""
        # Attempt multiple failed logins
        for i in range(6):
            response = security_app.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
        
        # Should be rate limited after 5 attempts
        assert response.status_code == 429
    
    def test_sql_injection_protection(self, security_app):
        """Test SQL injection attack protection"""
        # Attempt SQL injection in search parameter
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' UNION SELECT password FROM users--",
            "1'; DELETE FROM contributions; --"
        ]
        
        for payload in malicious_payloads:
            response = security_app.get(f'/api/contribution/?search={payload}')
            # Should not cause internal server error
            assert response.status_code != 500
    
    def test_xss_protection(self, security_app):
        """Test XSS attack protection"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            response = security_app.post('/api/contribution/', json={
                'title': payload,
                'description': 'test',
                'type': 'development'
            }, headers={'Authorization': 'Bearer valid_token'})
            
            # XSS should be filtered out
            if response.status_code == 201:
                data = response.get_json()
                assert payload not in data.get('title', '')
    
    def test_authorization_bypass(self, security_app):
        """Test authorization bypass attempts"""
        # Try to access admin endpoint without proper role
        response = security_app.post('/api/admin/users', json={
            'action': 'delete_user',
            'user_id': '123'
        }, headers={'Authorization': 'Bearer user_token'})
        
        assert response.status_code in [401, 403]
    
    def test_jwt_token_security(self, security_app):
        """Test JWT token security measures"""
        # Test with expired token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NDA5OTUyMDAsImV4cCI6MTY0MDk5ODgwMH0.invalid"
        
        response = security_app.get('/api/user/me', headers={
            'Authorization': f'Bearer {expired_token}'
        })
        
        assert response.status_code == 401
    
    @patch('backend.utils.security_monitor.SecurityMonitor.log_security_event')
    def test_security_monitoring(self, mock_log, security_app):
        """Test security event logging"""
        # Trigger a security event
        security_app.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        # Verify security event was logged
        mock_log.assert_called()
```

---

## Conclusion

This comprehensive security guide establishes a robust security framework for the Nimo Platform. The multi-layered approach ensures protection at every level:

✅ **Implemented Security Measures:**
- Strong authentication and authorization
- Comprehensive input validation and sanitization
- Smart contract security best practices
- Infrastructure hardening and monitoring
- Privacy and compliance frameworks
- Incident response procedures
- Continuous security testing

🔄 **Ongoing Security Practices:**
- Regular security audits and penetration testing
- Bug bounty program for community security research
- Continuous monitoring and threat detection
- Security training for development team
- Regular updates and vulnerability patches

The platform is designed with security as a fundamental principle, not an afterthought, ensuring user trust and regulatory compliance while maintaining functionality and usability.

---

*Last Updated: January 26, 2025*  
*Author: John (Backend Developer)*  
*Status: Comprehensive security framework ready for audit and implementation*