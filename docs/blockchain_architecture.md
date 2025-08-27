# Nimo Blockchain-as-Backend Architecture

## Overview

Nimo uses a blockchain-first architecture where the Base network serves as the primary backend, eliminating traditional database dependencies. This document outlines the technical architecture, data flow, and implementation details with OpenZeppelin MCP (Model Context Protocol) patterns.

## Architecture Principles

### **🎯 Blockchain-First Design with MCP**
- **Primary Storage**: All core data lives on Base network smart contracts
- **Decentralized Files**: IPFS for evidence, metadata, and large documents
- **Event-Driven MCP**: Real-time sync via blockchain event listeners with structured metadata
- **Local Caching**: Redis for performance optimization of frequent queries
- **MCP Context**: Rich contextual data emission for off-chain processing

### **💰 Cost Optimization**
- **Base Network**: ~$0.01 per transaction (vs $20+ on Ethereum mainnet)
- **Batch Operations**: Gas-optimized bulk processing
- **Lazy Loading**: On-demand blockchain queries with caching
- **IPFS Integration**: Cheap storage for large files

## OpenZeppelin MCP Patterns Implementation

### **Enhanced Event Emission**
All contracts follow MCP patterns for comprehensive off-chain indexing:

```solidity
// MCP-compliant event with rich context
event IdentityCreated(
    uint256 indexed tokenId,
    string username,
    address indexed owner,
    string did,
    string metadataURI,
    uint256 timestamp,
    bytes32 contextHash  // MCP context identifier
);

// MCP context structure for off-chain processing
struct MCPContext {
    string protocolVersion;
    string contractName;
    string actionType;
    bytes32 entityId;
    string metadataURI;
    uint256 timestamp;
    address actor;
}
```

### **MCP Metadata Standards**
- **Structured Data**: All metadata follows MCP JSON-LD format
- **IPFS Integration**: Metadata stored on IPFS with content addressing
- **Context Linking**: Events include context hashes for data relationships
- **Version Control**: Protocol versioning for backward compatibility

## Smart Contract Architecture

### **NimoIdentity.sol - Core Identity System with MCP**
```solidity
struct Identity {
    string username;
    string metadataURI; // IPFS URI with MCP-compliant metadata
    uint256 reputationScore;
    uint256 tokenBalance;
    bool isActive;
    uint256 createdAt;
    uint256 lastActivity;
    string did; // Decentralized Identifier
}

struct Contribution {
    uint256 identityId;
    string contributionType;
    string description;
    string evidenceURI; // IPFS URI for evidence
    bool verified;
    address verifier;
    uint256 tokensAwarded;
    uint256 timestamp;
    string mettaHash; // MeTTa proof hash
    uint256 confidence; // MeTTa confidence score
}
```

**MCP-Enhanced Functions:**
- `createIdentity(username, metadataURI, did)` - Create identity with DID and MCP metadata
- `addContribution(type, description, evidenceURI, mettaHash)` - Submit contribution with IPFS evidence
- `verifyContribution(contributionId, tokensToAward, confidence)` - MeTTa-verified validation
- `batchVerifyContributions(ids[], tokens[], confidences[])` - Gas-optimized bulk verification

**MCP Event Emissions:**
```solidity
event IdentityCreated(
    uint256 indexed tokenId,
    string username,
    address indexed owner,
    string did,
    string metadataURI,
    uint256 timestamp,
    bytes32 contextHash
);

event ContributionAdded(
    uint256 indexed contributionId,
    uint256 indexed identityId,
    string contributionType,
    string evidenceURI,
    string mettaHash,
    uint256 timestamp,
    bytes32 contextHash
);
```

### **NimoToken.sol - Reputation Token System with MCP**
```solidity
struct Distribution {
    address recipient;
    uint256 amount;
    string reason;
    uint256 timestamp;
    string mettaProof; // MeTTa proof of contribution
    uint256 confidence; // MeTTa confidence score
    string contributionType;
    bytes32 contextHash; // MCP context link
}
```

**MCP-Enhanced Features:**
- ERC20Votes for governance participation
- MeTTa-Verified minting with confidence scores
- Transfer logging with reason codes and context
- Vesting schedules for team and advisors
- Burn mechanisms for opportunity access

**MCP Event Emissions:**
```solidity
event TokensDistributed(
    address indexed recipient,
    uint256 amount,
    string reason,
    uint256 confidence,
    string mettaProof,
    bytes32 contextHash
);

event MeTTaProofAttached(
    uint256 indexed distributionId,
    string proof,
    bytes32 contextHash
);
```

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

### **BlockchainService - Web3 Interface with MCP**
```python
class BlockchainService:
    def __init__(self, network='base-sepolia'):
        self.web3 = Web3(Web3.HTTPProvider(self.get_rpc_url(network)))
        self.identity_contract = self.load_contract('NimoIdentity')
        self.token_contract = self.load_contract('NimoToken')

    async def create_identity_on_chain(self, username, metadata_uri, did):
        # MCP-compliant transaction with context generation
        context_hash = self.generate_mcp_context('identity_creation', username)
        tx = await self.identity_contract.functions.createIdentity(
            username, metadata_uri, did
        ).build_transaction()
        return await self.send_transaction(tx)

    async def get_user_contributions(self, user_address):
        # Cached blockchain queries with MCP context
        contributions = await self.identity_contract.functions.getContributions(user_address).call()
        return self.enrich_with_mcp_context(contributions)

    def setup_event_listeners(self):
        # Real-time blockchain event processing with MCP context
        self.setup_mcp_event_listener('IdentityCreated')
        self.setup_mcp_event_listener('ContributionAdded')
        self.setup_mcp_event_listener('TokensDistributed')
```

### **MCPService - Model Context Protocol Handler**
```python
class MCPService:
    def __init__(self):
        self.protocol_version = "1.0.0"
        self.context_templates = self.load_context_templates()

    def generate_context_hash(self, action_type, entity_data):
        # Generate deterministic context hash for MCP
        context = {
            "protocol": "Nimo-MCP",
            "version": self.protocol_version,
            "action": action_type,
            "entity": entity_data,
            "timestamp": int(time.time())
        }
        return self.hash_context(context)

    def create_mcp_metadata(self, entity_type, entity_data):
        # Create MCP-compliant metadata structure
        return {
            "@context": "https://nimo.network/mcp/v1",
            "@type": entity_type,
            "data": entity_data,
            "timestamp": int(time.time()),
            "protocol": "Nimo-MCP",
            "version": self.protocol_version
        }

    def validate_mcp_context(self, context_hash, expected_action):
        # Validate MCP context integrity
        return self.verify_context_hash(context_hash, expected_action)
```

### **IPFSService - Decentralized File Storage with MCP**
```python
class IPFSService:
    def __init__(self):
        self.ipfs_client = ipfshttpclient.connect()
        self.mcp_service = MCPService()

    def upload_evidence(self, file_data, contribution_type):
        # Upload to IPFS with MCP metadata
        ipfs_hash = self.ipfs_client.add(file_data)['Hash']

        # Create MCP-compliant metadata
        mcp_metadata = self.mcp_service.create_mcp_metadata('evidence', {
            'contribution_type': contribution_type,
            'ipfs_hash': ipfs_hash,
            'timestamp': int(time.time())
        })

        # Store metadata on IPFS as well
        metadata_hash = self.ipfs_client.add(json.dumps(mcp_metadata))['Hash']

        return ipfs_hash, metadata_hash

    def get_file_with_context(self, ipfs_hash):
        # Retrieve file with MCP context validation
        file_data = self.ipfs_client.cat(ipfs_hash)
        context = self.mcp_service.validate_file_context(ipfs_hash)
        return file_data, context
```

### **CacheService - Performance Layer with MCP**
```python
class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.mcp_service = MCPService()

    def cache_user_data(self, address, data):
        # Redis caching with MCP context
        context_hash = self.mcp_service.generate_context_hash('user_data', address)
        cache_key = f"user:{address}:{context_hash}"
        self.redis_client.setex(cache_key, 3600, json.dumps(data))

    def invalidate_on_event(self, event_type, user_address):
        # Smart cache invalidation based on blockchain events
        pattern = f"user:{user_address}:*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
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

## OpenZeppelin MCP Implementation Details

### **MCP Context Structure**
All Nimo contracts implement MCP (Model Context Protocol) for enhanced off-chain processing:

```solidity
struct MCPContext {
    string protocolVersion;    // "Nimo-MCP-1.0"
    string contractName;       // "NimoIdentity", "NimoToken"
    string actionType;         // "identity_creation", "contribution_add"
    bytes32 entityId;          // Unique entity identifier
    string metadataURI;        // IPFS URI for additional context
    uint256 timestamp;         // Event timestamp
    address actor;             // Transaction initiator
    bytes32 parentContext;     // Link to parent context (optional)
}
```

### **MCP Event Standards**
All events follow MCP standards for consistent off-chain indexing:

```solidity
// Standard MCP event structure
event MCPEvent(
    bytes32 indexed contextHash,    // Unique context identifier
    string eventType,               // Event classification
    address indexed actor,          // Event initiator
    bytes32 indexed entityId,       // Related entity
    string metadataURI,             // Additional context on IPFS
    uint256 timestamp               // Event timestamp
);

// Contract-specific events extend MCP
event IdentityCreated(
    uint256 indexed tokenId,
    string username,
    address indexed owner,
    string did,
    string metadataURI,
    uint256 timestamp,
    bytes32 contextHash
) inherits MCPEvent;
```

### **MCP Metadata Format**
All IPFS-stored metadata follows MCP JSON-LD format:

```json
{
  "@context": "https://nimo.network/mcp/v1",
  "@type": "Identity",
  "protocol": "Nimo-MCP",
  "version": "1.0.0",
  "data": {
    "username": "alice_dev",
    "did": "did:nimo:0x123...",
    "reputationScore": 150,
    "createdAt": 1693526400
  },
  "context": {
    "parent": null,
    "action": "identity_creation",
    "actor": "0x742d35Cc6634C0532925a3b8442c9dF7Cf8Cd9E"
  },
  "timestamp": 1693526400,
  "signature": "0xabcdef..."
}
```

### **MCP Context Linking**
Events are linked through context hashes for relationship tracking:

```solidity
function linkContexts(bytes32 parentContext, bytes32 childContext) external {
    contextLinks[childContext] = parentContext;
    emit ContextLinked(parentContext, childContext);
}
```

This enables off-chain systems to reconstruct the complete context chain for any entity or action.

## Migration Strategy

### **Phase 1: MCP-Enhanced Hybrid Mode (Current)**
- Smart contracts deployed with full MCP implementation
- Backend services enhanced with MCP context handling
- Frontend updated for Web3 wallet integration
- IPFS storage with MCP-compliant metadata
- Event listeners processing MCP-enriched events

### **Phase 2: Full Blockchain Migration**
1. **Deploy Enhanced Contracts**: NimoIdentity and NimoToken with MCP to Base Sepolia
2. **MCP Context Indexing**: Implement off-chain MCP context processors
3. **Replace Database Calls**: Convert SQLAlchemy queries to Web3 calls with MCP context
4. **IPFS MCP Integration**: Full MCP-compliant metadata storage and retrieval
5. **Cache Layer**: Implement Redis with MCP-aware caching strategies

### **Phase 3: Full Decentralization with MCP**
1. **Advanced MCP Features**: Cross-contract context linking and complex relationship mapping
2. **Governance Contracts**: DAO voting with MCP context for proposal tracking
3. **Cross-Chain MCP**: Bridge to other networks with MCP context preservation
4. **MCP Analytics**: Advanced analytics based on rich context data
5. **Performance Optimization**: MCP-driven query optimization and caching

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