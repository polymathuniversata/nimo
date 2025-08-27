# Nimo: Technical Documentation

## System Architecture

Nimo is a decentralized identity and proof of contribution network built on MeTTa language. The system consists of a hybrid architecture combining modern web technologies with MeTTa-based decentralized logic and blockchain-first data storage.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   MeTTa Core    │    │  Smart Contracts│
│   (React/Vite)  │◄──►│   (Flask API)   │◄──►│   (Logic Layer) │◄──►│   (Base Network)│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │              ┌─────────────────┐              │              ┌─────────────────┐
         │              │   Database      │              │              │   Blockchain    │
         └──────────────│   (Caching)     │──────────────┼──────────────│   (Events/State)│
                        └─────────────────┘              │              └─────────────────┘
                                 │                       │                       │
                        ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                        │   IPFS/Arweave  │    │  MeTTa-to-Chain │    │   Token Economy │
                        │  (Metadata)     │    │    Bridge       │    │   (ERC20/NFT)   │
                        └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Hybrid Architecture: MeTTa + React + Blockchain

Nimo implements a novel hybrid architecture that combines:
- **MeTTa Language**: For autonomous reasoning and decision-making
- **React 19.1.1**: For modern, responsive user interface
- **Smart Contracts**: For decentralized state management and token economics
- **Flask Backend**: For API services and MeTTa integration
- **Base Network**: For low-cost, scalable blockchain storage

The system consists of several interconnected modules:

### Core Components

1. **Decentralized Identity System (MeTTa + NFT)**
   - NFT-based identity certificates on Base Network
   - MeTTa reasoning for identity verification logic
   - Unique usernames mapped to blockchain addresses
   - Skill tracking with cryptographic proofs

2. **Smart Contract Layer**
   - **NimoIdentity Contract**: Manages identity NFTs and contributions
   - **NimoToken Contract**: ERC20 tokens for reputation and governance
   - **Impact Bond System**: Decentralized funding mechanisms
   - **Role-based Access Control**: Verifiers, MeTTa agents, administrators

3. **MeTTa Autonomous Reasoning**
   - Contribution verification logic in MeTTa
   - Autonomous token award calculations
   - Complex reputation scoring algorithms
   - Bridge to execute decisions on-chain

4. **React Frontend**
   - Modern React 19.1.1 with hooks and functional components
   - Vite 7.1.2 for fast development and building
   - Tailwind CSS for responsive, utility-first styling
   - React Context API for state management
   - React Router DOM for client-side routing
   - Autonomous token award calculations
   - Complex reputation scoring algorithms
   - Bridge to execute decisions on-chain

4. **Hybrid Data Storage**
   - **On-chain**: Identity ownership, token balances, key events
   - **Off-chain Database**: User sessions, cached data, performance optimization
   - **IPFS/Arweave**: Contribution evidence, metadata, large files
   - **MeTTa Knowledge Base**: Rules, relationships, inference chains

5. **Token Economy & Governance**
   - ERC20 reputation tokens for accessing opportunities
   - NFT identity certificates for proof of ownership
   - Decentralized governance through token voting
   - Automated token distribution via MeTTa agents

6. **Impact Bond Marketplace**
   - Smart contract-based investment tracking
   - Milestone verification through oracles
   - Automated returns based on impact achievements
   - Diaspora investor dashboard

## Data Structures

Nimo uses MeTTa atoms and relations as its fundamental data structures:

### User Identity
```
(user "Kwame")
(skill "Kwame" "Python")
(personal-info "Kwame" "location" "Nairobi")
```

### Contributions
```
(contribution "Kwame" "KRNL_Hackathon")
(verified-by "Kwame" "KRNL_Org")
```

### Tokens
```
(token-balance "Kwame" 320)
```

### Impact Bonds
```
(impact-bond "climate-001" "eco-warriors" "Reforestation project" 10000)
(bond-investment "climate-001" "kenyan-diaspora-1" 1000)
(bond-milestone "climate-001" "1000 trees planted" "photo-evidence-link")
```

## Autonomous Agent Logic

The core autonomous agent logic for automatic token awards is:

```
(= (auto-award $user $task)
   (if (and (contribution $user $task)
            (verified-by $user $_))
       (increase-token $user 50)
       (token-balance $user (get-token-balance $user))))
```

This implements the business rule:
```
(= (auto-award $user $task)
   (and
     (contribution $user $task)
     (verified-by $user $org))
   (increase-token $user 50))
```

## Integration Points

### External Systems
- Integration with blockchain networks for token issuance
- API connections to verification organizations
- Integration with educational platforms and job marketplaces

### User Interfaces
- Mobile app for users to manage their identity and contributions
- Web dashboard for organizations to verify contributions
- Impact bond marketplace for diaspora investors

## MeTTa Integration Details

### Flask-MeTTa Bridge
The backend uses a service layer to bridge Flask APIs with MeTTa logic:

```python
# services/metta_service.py
class MeTTaService:
    def auto_award_tokens(self, user_id, contribution_id):
        # Execute MeTTa logic for automatic token awards
        metta_result = execute_metta(f"(auto-award {user_id} {contribution_id})")
        return metta_result
```

### Enhanced Data Flow: MeTTa + Blockchain Integration

#### Contribution Verification Flow
1. **Frontend** → User submits contribution through Web3 wallet
2. **Smart Contract** → `addContribution()` creates on-chain record
3. **MeTTa Agent** → Analyzes contribution data and evidence
4. **MeTTa Logic** → Executes verification rules and calculates tokens
5. **Blockchain Service** → Calls `verifyContribution()` with MeTTa results
6. **Token Contract** → Mints reputation tokens automatically
7. **Event Listeners** → Update off-chain database and user interface

#### Identity Creation Flow
1. **User Registration** → Creates account in Flask backend
2. **Wallet Connection** → Links Ethereum address to account
3. **MeTTa Identity** → Generates identity atoms and relationships
4. **Smart Contract** → Mints NFT identity certificate
5. **IPFS Upload** → Stores metadata and skills off-chain
6. **Database Sync** → Caches blockchain data locally

#### MeTTa-to-Chain Bridge
```python
class MeTTaChainBridge:
    def execute_rule_on_chain(self, metta_result, user_id):
        # MeTTa reasoning result
        tokens_awarded = metta_result['tokens']
        verification_proof = metta_result['proof']
        
        # Execute on blockchain
        tx_hash = blockchain_service.execute_metta_rule_on_chain(
            rule=verification_proof,
            identity_id=user_id,
            tokens_to_award=tokens_awarded
        )
        
        return tx_hash
```

## Smart Contract Architecture

### Contract Overview

#### NimoIdentity.sol
Main contract managing decentralized identities and contributions:
- **ERC721 NFT**: Each identity is a unique, transferable NFT
- **Role-based Access**: Verifiers, MeTTa agents, and administrators
- **Contribution Tracking**: On-chain record of all contributions
- **Impact Bonds**: Decentralized funding mechanism
- **MeTTa Integration**: Bridge for autonomous agent decisions

Key Functions:
```solidity
function createIdentity(string username, string metadataURI) external
function addContribution(string contributionType, string description, string evidenceURI, string mettaHash) external
function verifyContribution(uint256 contributionId, uint256 tokensToAward) external onlyRole(VERIFIER_ROLE)
function executeMeTTaRule(string rule, uint256 targetIdentityId, uint256 tokensToAward) external onlyRole(METTA_AGENT_ROLE)
```

#### NimoToken.sol
ERC20 reputation token with MeTTa integration:
- **Mintable**: Tokens minted for verified contributions
- **Burnable**: Tokens consumed for accessing opportunities
- **Pausable**: Emergency controls for security
- **MeTTa Proofs**: Each token distribution includes MeTTa reasoning proof

Key Functions:
```solidity
function mintForContribution(address to, uint256 amount, string reason, string mettaProof) external onlyRole(MINTER_ROLE)
function burnForOpportunity(address from, uint256 amount, string reason) external onlyRole(BURNER_ROLE)
```

### Security Features

1. **Access Control**
   - Role-based permissions using OpenZeppelin AccessControl
   - Multi-signature requirements for high-value operations
   - Time-locked administrative functions

2. **Reentrancy Protection**
   - OpenZeppelin ReentrancyGuard on financial functions
   - Checks-Effects-Interactions pattern

3. **Pause Mechanism**
   - Emergency pause for token transfers
   - Gradual pause for different contract functions

4. **Input Validation**
   - String length limits to prevent gas attacks
   - Address zero checks
   - Numerical overflow protection (Solidity 0.8+)

### Gas Optimization

1. **Storage Optimization**
   - Packed structs to minimize storage slots
   - Efficient mapping structures
   - Event logs for historical data instead of storage

2. **Function Optimization**
   - Batch operations where possible
   - Early returns in conditional logic
   - View functions for data retrieval

3. **MeTTa Integration Efficiency**
   - Off-chain MeTTa computation with on-chain verification
   - Hash-based proofs instead of full MeTTa code on-chain
   - Event-driven updates to minimize transaction costs

## Testing Strategy

### MeTTa Tests
Located in `tests/nimo_test.metta`:
```metta
(= (test-auto-award)
   (and (auto-award "TestUser" "TestContribution")
        (> (get-token-balance "TestUser") 0)))
```

### API Tests
```python
# backend/tests/test_api.py
def test_create_contribution():
    response = client.post('/api/contributions', 
                          headers={'Authorization': f'Bearer {token}'},
                          json={'title': 'Test Contribution'})
    assert response.status_code == 201
```

## Deployment Architecture

### Development
- Frontend: `npm run dev` (http://localhost:9000)
- Backend: `flask run` (http://localhost:5000)
- Database: SQLite file

### Production
- **Frontend**: Static files served by CDN/Web server
- **Backend**: Gunicorn + Nginx + Redis caching
- **Database**: PostgreSQL with blockchain event indexing
- **MeTTa Runtime**: Containerized reasoning engine
- **Blockchain**: Ethereum mainnet or L2 (Polygon/Arbitrum)
- **IPFS**: Pinata or dedicated IPFS nodes
- **Monitoring**: Blockchain event listeners and analytics

## Implementation Considerations

### Data Security
- JWT tokens for authentication
- HTTPS enforced in production
- Environment variables for secrets
- Database encryption for sensitive data

### Scalability
- Efficient MeTTa query optimization
- Database indexing for frequent queries
- API rate limiting and caching
- Batch processing for token awards

### Trust Model
- Organizations must be registered and verified
- Multiple verification sources increase contribution trust score
- Transparent verification history
- Cryptographic signatures for high-value transactions