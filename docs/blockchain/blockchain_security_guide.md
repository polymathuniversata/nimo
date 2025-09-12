# Nimo Blockchain Security Guide

## Overview

This document outlines security considerations, best practices, and recommendations for the Nimo blockchain-as-backend architecture. Since all critical data lives on-chain, security is paramount for user trust and platform integrity.

## Critical Security Priorities

### **🔴 IMMEDIATE (Fix Before Production)**

#### **1. Smart Contract Security**

**Private Key Management**
```python
# ❌ NEVER do this
PRIVATE_KEY = "0x1234567890abcdef..."

# ✅ Correct approach
PRIVATE_KEY = os.getenv('BLOCKCHAIN_SERVICE_PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("BLOCKCHAIN_SERVICE_PRIVATE_KEY environment variable required")
```

**Contract Access Control**
```solidity
// ✅ Role-based access control
contract NimoIdentity is AccessControl {
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    modifier onlyVerifier() {
        require(hasRole(VERIFIER_ROLE, msg.sender), "Not authorized verifier");
        _;
    }
    
    function verifyContribution(uint256 contributionId, uint256 tokens) 
        external onlyVerifier {
        // Verification logic
    }
}
```

#### **2. Input Validation & Sanitization**

**MeTTa Query Sanitization**
```python
class MeTTaSanitizer:
    BLOCKED_PATTERNS = [
        r'(import|eval|exec|system)',  # Code execution
        r'(\.\./|\.\.\\)',              # Path traversal
        r'(drop|delete|truncate)',      # Destructive operations
    ]
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        for pattern in MeTTaSanitizer.BLOCKED_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError(f"Blocked pattern detected: {pattern}")
        return query.strip()[:1000]  # Length limit
```

**Blockchain Parameter Validation**
```python
def validate_blockchain_address(address: str) -> str:
    if not Web3.is_address(address):
        raise ValueError("Invalid Ethereum address")
    return Web3.to_checksum_address(address)

def validate_contribution_data(data: dict) -> dict:
    required_fields = ['title', 'description', 'contribution_type']
    for field in required_fields:
        if not data.get(field) or len(str(data[field]).strip()) == 0:
            raise ValueError(f"Missing required field: {field}")
    
    # Length limits
    data['title'] = data['title'][:200]
    data['description'] = data['description'][:2000]
    
    return data
```

#### **3. Rate Limiting for Blockchain Operations**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/contributions/<int:id>/verify', methods=['POST'])
@limiter.limit("5 per minute")  # Expensive blockchain operation
@jwt_required()
def verify_contribution(id):
    # Verification logic
```

### **🟡 HIGH PRIORITY**

#### **4. Secure IPFS Integration**

**File Upload Validation**
```python
class IPFSSecurityService:
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.txt', '.json'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def validate_file(self, file_data: bytes, filename: str) -> bool:
        # File size check
        if len(file_data) > self.MAX_FILE_SIZE:
            raise ValueError("File too large")
        
        # Extension check
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {ext}")
        
        # Content validation
        if self.detect_malicious_content(file_data):
            raise ValueError("Malicious content detected")
        
        return True
    
    def encrypt_sensitive_data(self, data: dict) -> str:
        """Encrypt personal data before IPFS upload"""
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = f.encrypt(json.dumps(data).encode())
        
        # Store key securely (not on IPFS)
        self.store_encryption_key(data['user_id'], key)
        
        return base64.b64encode(encrypted).decode()
```

#### **5. Transaction Security & Monitoring**

**Transaction Replay Protection**
```python
class TransactionService:
    def __init__(self):
        self.used_nonces = set()
        self.pending_transactions = {}
    
    def build_secure_transaction(self, contract_function, from_address: str):
        nonce = self.web3.eth.get_transaction_count(from_address)
        
        # Prevent nonce reuse
        if (from_address, nonce) in self.used_nonces:
            raise ValueError("Nonce already used")
        
        transaction = contract_function.build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gasPrice': self.get_optimal_gas_price(),
            'gas': self.estimate_gas_safely(contract_function),
            'chainId': self.get_chain_id()
        })
        
        # Track nonce usage
        self.used_nonces.add((from_address, nonce))
        return transaction
```

**Transaction Monitoring**
```python
class BlockchainMonitor:
    def __init__(self):
        self.suspicious_patterns = [
            'high_frequency_transactions',
            'unusual_gas_prices',
            'failed_transaction_patterns'
        ]
    
    async def monitor_transactions(self):
        """Monitor for suspicious blockchain activity"""
        while True:
            recent_txs = await self.get_recent_transactions()
            
            for tx in recent_txs:
                if self.detect_suspicious_pattern(tx):
                    await self.alert_security_team(tx)
                    await self.auto_pause_if_critical(tx)
            
            await asyncio.sleep(30)  # Check every 30 seconds
```

#### **6. Smart Contract Upgrade Security**

**Proxy Pattern with Access Control**
```solidity
contract NimoIdentityProxy is TransparentUpgradeableProxy {
    constructor(
        address implementation,
        address admin,
        bytes memory data
    ) TransparentUpgradeableProxy(implementation, admin, data) {}
}

contract NimoIdentity is Initializable, UUPSUpgradeable, AccessControl {
    function _authorizeUpgrade(address newImplementation) 
        internal override onlyRole(ADMIN_ROLE) {}
    
    // Emergency pause functionality
    bool public paused = false;
    
    modifier whenNotPaused() {
        require(!paused, "Contract paused");
        _;
    }
    
    function emergencyPause() external onlyRole(ADMIN_ROLE) {
        paused = true;
        emit EmergencyPaused(msg.sender, block.timestamp);
    }
}
```

### **🟠 MEDIUM PRIORITY**

#### **7. API Security Hardening**

**Enhanced Authentication**
```python
class BlockchainAuth:
    def verify_signature_ownership(self, message: str, signature: str, address: str) -> bool:
        """Verify user owns the blockchain address"""
        try:
            message_hash = encode_defunct(text=message)
            recovered_address = self.web3.eth.account.recover_message(
                message_hash, signature=signature
            )
            return recovered_address.lower() == address.lower()
        except Exception:
            return False
    
    @jwt_required()
    def require_address_ownership(self):
        """Decorator to ensure JWT user owns claimed blockchain address"""
        user_id = get_jwt_identity()
        claimed_address = request.json.get('address')
        
        if not self.verify_user_owns_address(user_id, claimed_address):
            abort(403, "Address ownership not verified")
```

**CORS Security**
```python
# ❌ Insecure CORS
CORS(app, origins="*")

# ✅ Secure CORS configuration
CORS(app, 
     origins=[
         "https://nimo.africa",
         "https://app.nimo.africa",
         "https://staging.nimo.africa" if ENV == 'staging' else None
     ],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE"],
     supports_credentials=True)
```

#### **8. Error Handling & Information Disclosure**

```python
class SecureErrorHandler:
    def handle_blockchain_error(self, error: Exception) -> dict:
        """Sanitize blockchain errors to prevent information disclosure"""
        
        # Log full error internally
        logger.error(f"Blockchain error: {str(error)}", extra={
            'user_id': get_jwt_identity() if has_request_context() else None,
            'endpoint': request.endpoint if has_request_context() else None,
            'error_type': type(error).__name__
        })
        
        # Return sanitized error to user
        if isinstance(error, Web3Exception):
            return {
                'error': 'Blockchain transaction failed',
                'code': 'BLOCKCHAIN_ERROR',
                'retry': True
            }
        elif isinstance(error, ValueError):
            return {
                'error': 'Invalid input provided',
                'code': 'VALIDATION_ERROR',
                'retry': False
            }
        else:
            return {
                'error': 'Internal server error',
                'code': 'INTERNAL_ERROR',
                'retry': True
            }
```

### **🔵 LOW PRIORITY (Long-term)**

#### **9. Advanced Security Features**

**Multi-Signature Contract Operations**
```solidity
contract NimoMultiSig {
    mapping(bytes32 => uint256) public confirmations;
    mapping(bytes32 => mapping(address => bool)) public confirmed;
    
    function submitTransaction(
        address target,
        bytes memory data,
        string memory description
    ) external onlyOwner returns (bytes32) {
        bytes32 txId = keccak256(abi.encode(target, data, description, block.number));
        
        confirmations[txId] = 1;
        confirmed[txId][msg.sender] = true;
        
        emit TransactionSubmitted(txId, msg.sender, target, description);
        return txId;
    }
    
    function confirmTransaction(bytes32 txId) external onlyOwner {
        require(!confirmed[txId][msg.sender], "Already confirmed");
        
        confirmed[txId][msg.sender] = true;
        confirmations[txId]++;
        
        if (confirmations[txId] >= REQUIRED_CONFIRMATIONS) {
            executeTransaction(txId);
        }
    }
}
```

**Zero-Knowledge Proof Integration**
```python
class ZKProofService:
    def generate_contribution_proof(self, contribution_data: dict, user_private_data: dict) -> dict:
        """Generate ZK proof that user made contribution without revealing identity"""
        # This would integrate with a ZK library like py-ecc or arkworks
        proof = {
            'public_inputs': {
                'contribution_hash': self.hash_contribution(contribution_data),
                'timestamp': int(time.time())
            },
            'proof': self.generate_zk_proof(contribution_data, user_private_data),
            'verification_key': self.get_verification_key()
        }
        return proof
```

## Security Monitoring & Incident Response

### **Automated Security Monitoring**

```python
class SecurityMonitor:
    def __init__(self):
        self.alert_thresholds = {
            'failed_transactions_per_hour': 100,
            'high_gas_price_multiplier': 5.0,
            'unusual_contract_calls': 50
        }
    
    async def monitor_security_metrics(self):
        """Continuous security monitoring"""
        while True:
            metrics = await self.collect_security_metrics()
            
            for metric_name, value in metrics.items():
                if self.is_threshold_exceeded(metric_name, value):
                    await self.trigger_security_alert(metric_name, value)
            
            await asyncio.sleep(60)  # Check every minute
    
    async def trigger_security_alert(self, metric: str, value: float):
        """Send security alerts to team"""
        alert = {
            'severity': 'HIGH' if value > self.alert_thresholds[metric] * 2 else 'MEDIUM',
            'metric': metric,
            'value': value,
            'threshold': self.alert_thresholds[metric],
            'timestamp': datetime.now().isoformat(),
            'suggested_actions': self.get_response_actions(metric)
        }
        
        await self.send_alert_to_security_team(alert)
        
        # Auto-response for critical alerts
        if alert['severity'] == 'HIGH':
            await self.auto_security_response(metric, value)
```

### **Incident Response Plan**

1. **Detection**: Automated monitoring detects suspicious activity
2. **Assessment**: Security team evaluates threat severity
3. **Response**: Immediate actions to contain threat
4. **Recovery**: Restore normal operations safely
5. **Lessons Learned**: Update security measures

### **Emergency Procedures**

```python
class EmergencyResponse:
    def emergency_pause_system(self, reason: str):
        """Emergency system shutdown"""
        # Pause all smart contracts
        for contract in self.get_all_contracts():
            contract.functions.emergencyPause().transact()
        
        # Disable API endpoints
        self.disable_critical_endpoints()
        
        # Notify users
        self.broadcast_emergency_message(reason)
        
        # Alert security team
        self.alert_security_team('EMERGENCY_PAUSE', reason)
    
    def emergency_fund_protection(self, threatened_addresses: list):
        """Protect funds from compromised addresses"""
        for address in threatened_addresses:
            # Move tokens to safety
            self.emergency_token_transfer(address, self.SAFE_WALLET)
            
            # Block further transactions
            self.add_to_blocklist(address)
            
            # Notify affected users
            self.notify_user_of_compromise(address)
```

## Security Checklist

### **Pre-Production Checklist**

- [ ] All private keys stored securely in environment variables
- [ ] Smart contracts audited by external security firm
- [ ] Input validation implemented for all user inputs
- [ ] Rate limiting configured for all endpoints
- [ ] CORS properly configured for production domains
- [ ] Error messages sanitized to prevent information disclosure
- [ ] IPFS file validation and encryption implemented
- [ ] Transaction monitoring and alerting system active
- [ ] Multi-signature controls for admin operations
- [ ] Emergency pause mechanisms tested
- [ ] Incident response plan documented and rehearsed
- [ ] Security monitoring dashboard operational
- [ ] Backup and recovery procedures tested

### **Ongoing Security Maintenance**

- [ ] Weekly security metrics review
- [ ] Monthly penetration testing
- [ ] Quarterly smart contract security audits
- [ ] Regular dependency updates and vulnerability scans
- [ ] Security team training on blockchain-specific threats
- [ ] Community bug bounty program
- [ ] Regular backup of critical IPFS content
- [ ] Performance monitoring of security systems

## Compliance Considerations

### **Data Privacy (GDPR/CCPA)**
- Personal data encrypted before IPFS storage
- Right to be forgotten handled through data encryption key destruction
- Data processing transparency through public blockchain transactions
- User consent mechanisms for data sharing

### **Financial Regulations**
- Token operations compliance with securities regulations
- Anti-money laundering (AML) monitoring for large transactions
- Know Your Customer (KYC) integration for high-value operations
- Regular compliance audits and reporting

This security guide should be regularly updated as new threats emerge and security best practices evolve. The blockchain-first architecture provides inherent security benefits but requires careful implementation to realize these advantages.