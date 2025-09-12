# Backend Security Hardening Roadmap

## Executive Summary

This roadmap outlines a prioritized security hardening plan for the Nimo backend codebase based on the Bandit security audit findings. The plan addresses 147 identified vulnerabilities with a focus on critical security issues that pose immediate risk to the system.

## Risk Assessment Overview

### Critical Vulnerabilities (Immediate Action Required)
- **12 High-Severity Issues**: Hardcoded secrets, network exposure, injection vulnerabilities
- **35 Medium-Severity Issues**: Service disruption risks, insecure random usage
- **100 Low-Severity Issues**: Code quality issues, primarily in test files

### Attack Surface Analysis
- **Primary Attack Vectors**: Credential exposure, network attacks, injection attacks
- **Secondary Risks**: DoS attacks, privilege escalation, data leakage
- **Business Impact**: Authentication bypass, data breach, service disruption

## Phase 1: Critical Security Fixes (Week 1)

### Priority 1: Credential Security (Day 1-2)

#### 1.1 Remove Hardcoded Secrets
**Objective**: Eliminate all hardcoded credentials and secrets

**Target Files**:
- `app.py` (lines 27, 45)
- `config.py` (lines 45, 67, 89)
- `services/blockchain_service.py`
- `services/ipfs_service.py`

**Implementation Plan**:

```python
# BEFORE (Vulnerable)
# app.py
SECRET_KEY = "nimo-secret-key-2024"
JWT_SECRET = "nimo-jwt-secret-2024"

# AFTER (Secure)
# app.py
import os
SECRET_KEY = os.getenv('NIMO_SECRET_KEY')
JWT_SECRET = os.getenv('NIMO_JWT_SECRET')

if not SECRET_KEY or not JWT_SECRET:
    raise ValueError("Required environment variables not set")
```

**Deliverables**:
- [ ] Environment variable configuration
- [ ] `.env.example` file with required variables
- [ ] Secret validation on startup
- [ ] Documentation for secret management

#### 1.2 Environment Configuration
**Objective**: Implement secure environment-based configuration

**Implementation**:

```python
# config.py - Secure Configuration
from pydantic import BaseSettings, validator
import os

class SecurityConfig(BaseSettings):
    secret_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600

    @validator('secret_key', 'jwt_secret')
    def validate_secrets(cls, v):
        if not v or len(v) < 32:
            raise ValueError("Secret must be at least 32 characters")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
```

### Priority 2: Network Security (Day 3-4)

#### 2.1 Fix Network Binding
**Objective**: Prevent unauthorized network access

**Target Files**:
- `app.py` (line 89)

**Implementation**:

```python
# BEFORE (Vulnerable)
app.run(host='0.0.0.0', port=5000, debug=True)

# AFTER (Secure)
app.run(
    host=os.getenv('NIMO_HOST', '127.0.0.1'),
    port=int(os.getenv('NIMO_PORT', 5000)),
    debug=False
)
```

#### 2.2 Add Security Headers
**Objective**: Implement security headers middleware

**Implementation**:

```python
# middleware/security_headers.py
from flask import Flask
from flask_cors import CORS

def init_security_headers(app: Flask):
    """Initialize security headers."""

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
```

### Priority 3: Input Validation (Day 5)

#### 3.1 Subprocess Security
**Objective**: Prevent command injection attacks

**Target Files**:
- `services/blockchain_service.py`
- `services/ipfs_service.py`
- `utils/shell_utils.py`

**Implementation**:

```python
# BEFORE (Vulnerable)
subprocess.call(f"cardano-cli query tip {network}")

# AFTER (Secure)
import shlex

def run_cardano_command(network: str) -> str:
    """Secure cardano command execution."""
    # Validate network parameter
    allowed_networks = ['mainnet', 'testnet', 'preview']
    if network not in allowed_networks:
        raise ValueError(f"Invalid network: {network}")

    # Use shell=False with argument list
    cmd = ['cardano-cli', 'query', 'tip', '--network', network]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False
    )

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )

    return result.stdout
```

## Phase 2: Service Hardening (Week 2)

### Priority 4: HTTP Request Security (Day 1-2)

#### 4.1 Add Request Timeouts
**Objective**: Prevent hanging connections and DoS attacks

**Target Files**:
- `services/ipfs_service.py`
- `services/blockchain_service.py`
- `services/metta_service.py`

**Implementation**:

```python
# services/ipfs_service.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SecureIPFSService:
    """IPFS service with security hardening."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_secure_session()

    def _create_secure_session(self) -> requests.Session:
        """Create session with retry strategy and timeouts."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get_content(self, cid: str) -> str:
        """Retrieve content with timeout and validation."""
        # Validate CID format
        if not self._validate_cid(cid):
            raise ValueError("Invalid CID format")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v0/cat",
                params={'arg': cid},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text

        except requests.Timeout:
            raise ExternalServiceException("IPFS request timeout")
        except requests.RequestException as e:
            raise ExternalServiceException(f"IPFS request failed: {e}")

    def _validate_cid(self, cid: str) -> bool:
        """Validate CID format."""
        # Basic CID validation (can be enhanced)
        return bool(cid and len(cid) > 10 and cid.replace('/', '').replace('.', '').isalnum())
```

#### 4.2 Implement Rate Limiting
**Objective**: Prevent abuse and DoS attacks

**Implementation**:

```python
# middleware/rate_limiting.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

def init_rate_limiting(app: Flask, redis_url: str):
    """Initialize rate limiting."""

    redis_client = Redis.from_url(redis_url)

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=redis_url,
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window"
    )

    # Global rate limits
    limiter.limit("100 per minute")(app)
    limiter.limit("1000 per hour")(app)

    # API-specific limits
    @app.route("/api/contributions")
    @limiter.limit("10 per minute")
    def create_contribution():
        pass

    return limiter
```

### Priority 5: Cryptographic Security (Day 3-4)

#### 5.1 Replace Insecure Random
**Objective**: Use cryptographically secure random generation

**Target Files**:
- `utils/security.py`
- `services/token_service.py`

**Implementation**:

```python
# BEFORE (Vulnerable)
import random
token = random.randint(1000, 9999)

# AFTER (Secure)
import secrets

def generate_secure_token(length: int = 6) -> str:
    """Generate cryptographically secure token."""
    if not 4 <= length <= 32:
        raise ValueError("Token length must be between 4 and 32")

    # Use secrets module for cryptographic security
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def generate_session_id() -> str:
    """Generate secure session ID."""
    return secrets.token_hex(32)  # 64 character hex string

def generate_api_key() -> str:
    """Generate secure API key."""
    return secrets.token_urlsafe(32)  # URL-safe base64-encoded string
```

#### 5.2 Secure Password Handling
**Objective**: Implement proper password hashing

**Implementation**:

```python
# utils/password_security.py
import bcrypt
import secrets
from typing import Optional

class PasswordManager:
    """Secure password management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate secure password reset token."""
        return secrets.token_urlsafe(32)
```

### Priority 6: Error Handling Security (Day 5)

#### 6.1 Remove Try/Except/Pass
**Objective**: Implement proper error handling

**Target Files**:
- `services/cache_service.py`
- `services/monitoring_service.py`

**Implementation**:

```python
# BEFORE (Vulnerable)
try:
    # risky operation
    result = risky_operation()
except Exception:
    pass  # Silent failure

# AFTER (Secure)
try:
    result = risky_operation()
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise ExternalServiceException("Service temporarily unavailable")
except TimeoutError as e:
    logger.error(f"Operation timeout: {e}")
    raise ExternalServiceException("Operation timeout")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise InternalServerException("Internal server error")
```

## Phase 3: Infrastructure Security (Week 3)

### Priority 7: File System Security (Day 1-2)

#### 7.1 Secure Temp File Usage
**Objective**: Prevent temp file vulnerabilities

**Target Files**:
- `utils/file_utils.py`
- `services/ipfs_service.py`

**Implementation**:

```python
# utils/secure_file_utils.py
import tempfile
import os
from pathlib import Path
from typing import Optional

class SecureFileManager:
    """Secure file operations."""

    @staticmethod
    def create_secure_temp_file(suffix: Optional[str] = None) -> str:
        """Create secure temporary file."""
        # Use NamedTemporaryFile for automatic cleanup
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)

        # Set restrictive permissions
        os.chmod(temp_path, 0o600)  # Owner read/write only

        # Close file descriptor to prevent leaks
        os.close(temp_fd)

        return temp_path

    @staticmethod
    def write_secure_temp_file(content: str, suffix: Optional[str] = None) -> str:
        """Write content to secure temporary file."""
        temp_path = SecureFileManager.create_secure_temp_file(suffix)

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return temp_path
        except Exception:
            # Clean up on failure
            Path(temp_path).unlink(missing_ok=True)
            raise

    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Securely cleanup temporary file."""
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
```

### Priority 8: Logging Security (Day 3-4)

#### 8.1 Secure Logging Implementation
**Objective**: Prevent sensitive data leakage in logs

**Implementation**:

```python
# utils/secure_logger.py
import logging
import re
from typing import Dict, Any

class SecureLogger:
    """Security-aware logging."""

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        (re.compile(r'password["\s:]*["\']([^"\']+)["\']', re.IGNORECASE), '[PASSWORD]'),
        (re.compile(r'secret["\s:]*["\']([^"\']+)["\']', re.IGNORECASE), '[SECRET]'),
        (re.compile(r'token["\s:]*["\']([^"\']+)["\']', re.IGNORECASE), '[TOKEN]'),
        (re.compile(r'key["\s:]*["\']([^"\']+)["\']', re.IGNORECASE), '[KEY]'),
    ]

    @staticmethod
    def sanitize_message(message: str) -> str:
        """Remove sensitive data from log messages."""
        sanitized = message
        for pattern, replacement in SecureLogger.SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary values."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = SecureLogger.sanitize_message(value)
            elif isinstance(value, dict):
                sanitized[key] = SecureLogger.sanitize_dict(value)
            else:
                sanitized[key] = value
        return sanitized

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get security-aware logger."""
        logger = logging.getLogger(name)

        # Add custom filter to sanitize all log records
        class SanitizeFilter(logging.Filter):
            def filter(self, record):
                if hasattr(record, 'msg'):
                    record.msg = cls.sanitize_message(str(record.msg))
                return True

        logger.addFilter(SanitizeFilter())
        return logger
```

## Phase 4: Testing and Validation (Week 4)

### Priority 9: Security Testing (Day 1-3)

#### 9.1 Automated Security Tests
**Objective**: Implement security regression tests

**Implementation**:

```python
# tests/security/test_hardening.py
import pytest
import os
from unittest.mock import patch

class TestSecurityHardening:
    """Security hardening tests."""

    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist."""
        # This would scan source files for hardcoded patterns
        pass

    def test_environment_variables_required(self):
        """Test that required environment variables are set."""
        required_vars = ['NIMO_SECRET_KEY', 'NIMO_JWT_SECRET']

        for var in required_vars:
            assert os.getenv(var), f"Required environment variable {var} not set"

    def test_secure_headers_present(self, client):
        """Test that security headers are present."""
        response = client.get('/api/health')

        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers

    def test_rate_limiting_active(self, client):
        """Test that rate limiting is active."""
        # Make multiple requests to test rate limiting
        pass

    def test_secure_random_usage(self):
        """Test that secure random is used instead of random."""
        # Scan imports to ensure secrets module is used
        pass
```

#### 9.2 Penetration Testing Checklist
**Objective**: Prepare for external security assessment

**Deliverables**:
- [ ] API endpoint security testing
- [ ] Authentication bypass testing
- [ ] Injection attack testing
- [ ] DoS attack testing
- [ ] Data leakage testing

## Implementation Timeline

### Week 1: Critical Fixes
- [ ] Remove hardcoded secrets
- [ ] Fix network binding
- [ ] Secure subprocess usage
- [ ] Add request timeouts

### Week 2: Service Hardening
- [ ] Implement rate limiting
- [ ] Secure random usage
- [ ] Proper error handling
- [ ] Password security

### Week 3: Infrastructure Security
- [ ] Secure file operations
- [ ] Security-aware logging
- [ ] Input validation
- [ ] Configuration security

### Week 4: Testing and Validation
- [ ] Security test suite
- [ ] Penetration testing
- [ ] Security documentation
- [ ] Compliance checklist

## Success Metrics

### Security Metrics
- **Zero Critical Vulnerabilities**: All high-severity issues resolved
- **Reduced Attack Surface**: Network and injection vulnerabilities eliminated
- **Secure Configuration**: All secrets properly managed
- **Monitoring Coverage**: 100% of security events monitored

### Performance Metrics
- **Response Time Impact**: <5% increase from security measures
- **Resource Usage**: <10% increase in memory/CPU from security features
- **Scalability**: No degradation in concurrent user handling

### Compliance Metrics
- **Security Headers**: 100% of responses include required headers
- **Rate Limiting**: Active on all public endpoints
- **Logging**: All security events properly logged and monitored
- **Encryption**: All sensitive data encrypted in transit and at rest

## Risk Mitigation

### Technical Risks
1. **Performance Impact**: Comprehensive performance testing
2. **Breaking Changes**: Gradual rollout with feature flags
3. **Third-party Dependencies**: Regular dependency vulnerability scanning

### Operational Risks
1. **Downtime**: Zero-downtime deployment strategy
2. **Monitoring Gaps**: Enhanced security monitoring
3. **Incident Response**: Updated security incident procedures

## Monitoring and Alerting

### Security Monitoring Setup
1. **Log Analysis**: Automated scanning for security events
2. **Intrusion Detection**: Network-level security monitoring
3. **Anomaly Detection**: Behavioral analysis for suspicious activity
4. **Compliance Monitoring**: Regular security posture assessment

### Alert Configuration
1. **Critical Alerts**: Authentication failures, unauthorized access
2. **Warning Alerts**: Rate limit violations, suspicious patterns
3. **Info Alerts**: Security configuration changes, updates

## Conclusion

This security hardening roadmap provides a comprehensive, prioritized approach to addressing all critical vulnerabilities identified in the Bandit security audit. The phased implementation ensures that the most critical security issues are addressed first, while maintaining system stability and performance.

The roadmap focuses on:
- **Immediate Risk Reduction**: Critical vulnerabilities fixed in Week 1
- **Defense in Depth**: Multiple layers of security controls
- **Sustainable Security**: Automated testing and monitoring for long-term security
- **Business Continuity**: Minimal disruption during implementation

Successful implementation will result in a significantly more secure backend system with robust protection against common attack vectors and compliance with security best practices.

---

**Document Version**: 1.0
**Last Updated**: Current Session
**Implementation Timeline**: 4 weeks
**Risk Level**: High (Critical vulnerabilities present)
**Business Impact**: Critical (Security breach prevention)