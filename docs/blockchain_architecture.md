# Nimo Blockchain-as-Backend Architecture

## Overview

Nimo uses a blockchain-first architecture where the Base network serves as the primary backend, eliminating traditional database dependencies. This document outlines the technical architecture, data flow, and implementation details.

## Architecture Principles

### **🎯 Blockchain-First Design**
- **Primary Storage**: All core data lives on Base network smart contracts
- **Decentralized Files**: IPFS for evidence, metadata, and large documents
- **Local Caching**: Redis for performance optimization of frequent queries
- **Event-Driven**: Real-time sync via blockchain event listeners

### **💰 Cost Optimization**
- **Base Network**: ~$0.01 per transaction (vs $20+ on Ethereum mainnet)
- **Batch Operations**: Gas-optimized bulk processing
- **Lazy Loading**: On-demand blockchain queries with caching
- **IPFS Integration**: Cheap storage for large files

## Smart Contract Architecture

### **NimoIdentity.sol - Core Identity System**
```solidity
struct UserIdentity {
    string username;
    string metadataURI;        // IPFS hash for profile data
    uint256 reputationScore;
    uint256 tokenBalance;
    bool isActive;
    uint256 createdAt;
}

struct Contribution {
    uint256 id;
    address user;
    string contributionType;
    string description;
    string evidenceURI;        // IPFS hash for evidence
    string mettaProofHash;     // MeTTa verification proof
    bool isVerified;
    uint256 tokensAwarded;
    uint256 timestamp;
}
```

**Key Functions:**
- `createIdentity(username, metadataURI)` - Create new user identity NFT
- `addContribution(type, description, evidenceURI, mettaHash)` - Submit contribution
- `verifyContribution(contributionId, tokensToAward)` - MeTTa-verified validation
- `batchVerifyContributions(ids[], tokens[])` - Gas-optimized bulk verification

### **NimoToken.sol - Reputation Token System**
```solidity
// ERC20 compatible with custom minting logic
function mintForContribution(
    address to,
    uint256 amount,
    string memory reason,
    string memory mettaProof
) external onlyVerifier;

function transferWithReason(
    address to,
    uint256 amount,
    string memory reason
) external returns (bool);
```

**Key Features:**
- ERC20 compatible for DEX integration
- Mintable only by verified contribution system
- Transfer logging with reason codes
- Built-in staking mechanisms for governance

### **NimoBonds.sol - Impact Bond Marketplace**
```solidity
struct ImpactBond {
    string title;
    string description;
    uint256 targetAmount;
    uint256 raisedAmount;
    uint256 maturityDate;
    string[] milestones;
    bool[] milestoneCompleted;
    address creator;
    BondStatus status;
}
```

**Key Functions:**
- `createBond(title, description, targetAmount, milestones)` - Create diaspora bond
- `investInBond(bondId)` - Invest USDC in bond
- `verifyMilestone(bondId, milestoneId, evidence)` - Verify completion
- `releaseFunds(bondId, milestoneId)` - Automated fund release

## Data Flow Architecture

### **Write Operations (Transactions)**
```
User Action → Flask API → MeTTa Verification → Smart Contract → Blockchain
                ↓
        Event Listener → Cache Update → Real-time UI Update
```

### **Read Operations (Queries)**
```
UI Request → Flask API → Check Redis Cache → If Miss: Query Blockchain → Update Cache → Return Data
```

### **File Storage Flow**
```
Large File → IPFS Upload → Get Hash → Store Hash On-Chain → Retrieve via IPFS Gateway
```

## Backend Service Layer

### **BlockchainService - Web3 Interface**
```python
class BlockchainService:
    def __init__(self, network='base-sepolia'):
        self.web3 = Web3(Web3.HTTPProvider(self.get_rpc_url(network)))
        self.identity_contract = self.load_contract('NimoIdentity')
        self.token_contract = self.load_contract('NimoToken')
        
    async def create_identity_on_chain(self, username, metadata_uri):
        # Gas-optimized transaction building
        
    async def get_user_contributions(self, user_address):
        # Cached blockchain queries
        
    def setup_event_listeners(self):
        # Real-time blockchain event processing
```

### **IPFSService - Decentralized File Storage**
```python
class IPFSService:
    def upload_evidence(self, file_data):
        # Upload to IPFS, return hash
        
    def get_file(self, ipfs_hash):
        # Retrieve from IPFS gateway with CDN
        
    def pin_important_data(self, ipfs_hash):
        # Ensure data persistence
```

### **CacheService - Performance Layer**
```python
class CacheService:
    def cache_user_data(self, address, data):
        # Redis caching with TTL
        
    def invalidate_on_event(self, event_type, user_address):
        # Smart cache invalidation based on blockchain events
```

## Performance Optimization

### **Caching Strategy**
- **L1 Cache**: Redis for frequent queries (user profiles, balances)
- **L2 Cache**: Local memory for request-scoped data
- **Cache Invalidation**: Event-driven updates when blockchain state changes
- **TTL Policies**: Smart expiration based on data volatility

### **Query Optimization**
- **Batch Queries**: Multiple contract calls in single RPC request
- **Event Filtering**: Efficient log queries with indexed parameters
- **Lazy Loading**: Load detailed data only when requested
- **Pagination**: Blockchain-native pagination for large datasets

### **Gas Optimization**
- **Batch Operations**: Process multiple items in single transaction
- **Optimized Data Structures**: Minimal storage slots usage
- **Event-Based Updates**: Reduce on-chain storage, use events for history
- **Base Network**: ~100x cheaper than Ethereum mainnet

## Security Considerations

### **Smart Contract Security**
- **OpenZeppelin**: Battle-tested contract patterns
- **Access Control**: Role-based permissions (Admin, Verifier, User)
- **Input Validation**: Comprehensive parameter checking
- **Upgrade Patterns**: Proxy contracts for future improvements

### **API Security**
- **Signature Verification**: Cryptographic proof of ownership
- **Rate Limiting**: Prevent blockchain spam attacks
- **MeTTa Validation**: AI-powered fraud detection before blockchain commits
- **Private Key Management**: Secure service account handling

### **Data Security**
- **IPFS Encryption**: Sensitive files encrypted before upload
- **Metadata Privacy**: Personal data hashed or encrypted
- **Blockchain Privacy**: Public by design, private data stays off-chain
- **Backup Strategy**: Multiple IPFS nodes and blockchain redundancy

## Migration Strategy

### **Phase 1: Hybrid Mode (Current)**
- SQLite for rapid development and testing
- Blockchain service layer ready for contract interactions
- MeTTa integration with blockchain proof generation

### **Phase 2: Blockchain Migration**
1. **Deploy Contracts**: NimoIdentity and NimoToken to Base Sepolia
2. **Replace Database Calls**: Convert SQLAlchemy queries to Web3 calls
3. **IPFS Integration**: Move file storage to decentralized system
4. **Cache Layer**: Implement Redis for performance

### **Phase 3: Full Decentralization**
1. **Governance Contracts**: DAO voting and platform upgrades
2. **Cross-Chain**: Bridge to other networks for broader access
3. **Advanced Features**: Complex MeTTa rules, reputation algorithms
4. **Performance Optimization**: Advanced caching and query strategies

## Developer Experience

### **Local Development**
```bash
# Start local blockchain (optional)
anvil --chain-id 31337

# Deploy contracts to local/testnet
forge script script/Deploy.s.sol --broadcast --rpc-url base-sepolia

# Start backend with blockchain connection
cd backend
python -c "from services.blockchain_service import BlockchainService; print('Connected:', BlockchainService().is_connected())"
flask run
```

### **Testing Strategy**
- **Unit Tests**: Individual contract functions
- **Integration Tests**: End-to-end blockchain interactions
- **Load Tests**: Performance under high transaction volume
- **Security Tests**: Smart contract vulnerability scanning

### **Monitoring & Debugging**
- **Blockchain Explorers**: Base Sepolia/Mainnet transaction tracking
- **Event Monitoring**: Real-time contract event processing
- **Gas Analytics**: Transaction cost optimization
- **Error Handling**: Graceful degradation when blockchain unavailable

## Cost Analysis

### **Transaction Costs (Base Network)**
- User Registration: ~$0.008
- Add Contribution: ~$0.012  
- Verify Contribution: ~$0.015
- Token Transfer: ~$0.005
- Create Bond: ~$0.025

### **Storage Costs**
- On-Chain: ~$0.20 per KB (only critical data)
- IPFS: ~$0.001 per MB (evidence, metadata)
- Caching: Negligible (Redis/local storage)

### **Operational Benefits**
- **No Server Costs**: Decentralized infrastructure
- **Global CDN**: IPFS provides worldwide file access
- **No Database Licensing**: Blockchain replaces traditional DB
- **Automatic Scaling**: Network scales with usage

## Future Enhancements

### **Advanced Features**
- **Layer 2 Scaling**: Custom rollup for even lower costs
- **Cross-Chain Bridges**: Multi-network identity portability
- **ZK Proofs**: Privacy-preserving verification
- **DAO Governance**: Community-driven platform evolution

### **Enterprise Integration**
- **API Gateways**: High-performance read layers
- **Analytics Dashboard**: Blockchain-based impact metrics
- **Partner Integrations**: Direct contract interfaces for organizations
- **Compliance Tools**: Regulatory reporting and audit trails

This blockchain-first architecture positions Nimo as a truly decentralized platform that can operate independently of any centralized infrastructure while maintaining high performance and low costs.