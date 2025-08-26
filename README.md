# Nimo: Decentralized Youth Id## MeTTa Autonomous Agents
- **Intelligent Verification**: AI agents analyze contributions and calculate appropriate rewards
- **Complex Logic**: Handle multi-factor reputation scoring and contribution weighting
- **Transparent Reasoning**: All MeTTa decisions include cryptographic proofs
- **Persistent Identity**: MeTTa-based identity representations enable cross-platform verification
- **Fraud Detection**: Sophisticated pattern recognition to detect fraudulent contributionsty & Proof of Contribution Network

## Overview
Nimo is a decentralized reputation system built on MeTTa language that enables African youth to create persistent digital identities, earn reputation tokens for real-world contributions, and use their identity and reputation to unlock access to opportunities like internships, grants, gigs, and DAO proposals.

## Problem Statement
Millions of African youth participate in informal work, activism, and decentralized learning but lack verifiable digital identity or proof of their contributions, limiting their access to jobs, capital, and global platforms.

## Features

### 🏗️ Decentralized Identity & NFTs
- **NFT Identity Certificates**: Each identity is a unique, transferable NFT on Ethereum
- **MeTTa-Powered Logic**: Autonomous reasoning for identity verification and reputation
- **Cross-Platform Portability**: Use your identity across multiple platforms and applications

### 🎯 Smart Contract Integration  
- **On-Chain Contributions**: Immutable record of all contributions and verifications
- **Automated Token Awards**: Smart contracts execute MeTTa decisions automatically
- **Role-Based Access Control**: Verifiers, MeTTa agents, and users with different permissions

### 💰 Token Economy & Governance
- **ERC20 Reputation Tokens**: Earn tradeable tokens for verified contributions
- **DAO Governance**: Token holders vote on platform decisions and upgrades
- **Opportunity Access**: Spend tokens to unlock jobs, grants, and opportunities

### 🌍 Impact Bond Marketplace
- **Decentralized Funding**: Diaspora investors fund local projects through smart contracts
- **Milestone Tracking**: Automated milestone verification and fund release
- **Impact Measurement**: Transparent tracking of social and economic impact

### 🤖 MeTTa Autonomous Agents
- **Intelligent Verification**: AI agents analyze contributions and calculate appropriate rewards
- **Complex Logic**: Handle multi-factor reputation scoring and contribution weighting
- **Transparent Reasoning**: All MeTTa decisions include cryptographic proofs

## Project Structure
```
Nimo/
├── contracts/         # Smart contracts (Solidity)
│   ├── NimoIdentity.sol  # Identity NFT & contribution tracking
│   ├── NimoToken.sol     # ERC20 reputation tokens
│   └── scripts/          # Deployment scripts
├── backend/          # Flask REST API server
│   ├── models/       # Database models (SQLAlchemy)
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic, MeTTa & blockchain integration
│   └── utils/        # Helper functions
├── frontend/         # Vue.js + Quasar UI
│   ├── src/
│   │   ├── components/  # Reusable Vue components
│   │   ├── pages/      # Application pages
│   │   ├── services/   # API & Web3 service layer
│   │   └── stores/     # Pinia state management
├── docs/            # Technical documentation
├── tests/           # MeTTa test cases
└── main.metta       # MeTTa demonstration script
```

## Sample MeTTa Atoms
```
; User Identity and Skills
(User "user-123" "Kwame")
(HasSkill "user-123" "Python" 4)
(HasSkill "user-123" "community_building" 3)

; Contributions and Evidence
(Contribution "contrib-456" "user-123" "coding")
(ContributionTitle "contrib-456" "KRNL Hackathon Project")
(Evidence "evidence-789" "contrib-456" "github" "https://github.com/kwame/krnl-project")

; Verification and Impact
(HasVerification "contrib-456" "KRNL_Org" "verifier-101")
(ContributionImpact "contrib-456" "significant")
(TokenBalance "user-123" 320)
```

## Autonomous Agent Logic
```
; Verification rule with confidence scoring
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))

; Dynamic token award based on evidence quality and verification
(= (CalculateTokenAward $contrib-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($confidence (CalculateConfidence $contrib-id))
          ($quality-bonus (* $confidence 50))
          ($total-amount (+ $base-amount $quality-bonus)))
     $total-amount))
```

## Technology Stack
- **Backend**: Flask (Python) + SQLAlchemy + JWT Authentication + Web3.py
- **Frontend**: Vue.js 3 + Quasar Framework + Pinia + Web3 Wallet Integration
- **Smart Contracts**: Solidity + OpenZeppelin + Foundry (deployed on Base)
- **Core Logic**: MeTTa language for autonomous reasoning and decision-making
- **Blockchain**: Base Network (Ethereum L2) for low-cost identity NFTs and reputation tokens
- **Storage**: PostgreSQL (relational) + IPFS (metadata) + On-chain (critical state)
- **Infrastructure**: Docker + Redis + Blockchain event indexing

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Foundry (for smart contract development)
- MeTTa runtime (optional for core testing)
- Ethereum wallet (MetaMask) with Base network configured
- Base Sepolia ETH for testnet deployment

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Nimo
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   flask db init
   flask db migrate
   flask db upgrade
   flask run
   ```

3. **Frontend Setup** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Smart Contract Setup** (Foundry + Base Network)
   ```bash
   cd contracts
   
   # Install Foundry dependencies
   forge install OpenZeppelin/openzeppelin-contracts
   forge install foundry-rs/forge-std
   
   # Compile contracts
   forge build
   
   # Run tests
   forge test
   
   # Deploy to Base Sepolia testnet
   forge script script/Deploy.s.sol:DeployScript --rpc-url base-sepolia --broadcast --verify
   
   # Copy contract addresses to backend/.env
   ```

5. **Access the Application**
   - Frontend: http://localhost:9000
   - Backend API: http://localhost:5000
   - Base Sepolia: https://sepolia.basescan.org
   - Base Mainnet: https://basescan.org

### Running MeTTa Examples
```bash
# From project root
metta main.metta
```

## Documentation
- [Technical Documentation](docs/technical.md) - System architecture and MeTTa integration
- [User Guide](docs/user_guide.md) - How to use the platform
- [Backend API](backend/README.md) - REST API endpoints
- [Workflow Diagrams](docs/) - Visual system architecture
- [MeTTa Implementation Plan](docs/metta_implementation_plan.md) - Detailed MeTTa integration plan
- [MeTTa User Guide](docs/metta_user_guide.md) - How to use and extend the MeTTa integration
- [MeTTa Research Findings](docs/metta_research_findings.md) - Latest research on MeTTa integration best practices
- [Backend Implementation Status](docs/backend_implementation_status.md) - Current implementation status and roadmap

## Why It Matters
- Creates a portable, tamper-proof record of experience
- Powers a youth-led gig and grant ecosystem without dependency on centralized CVs or diplomas
- Turns participation in community into on-chain economic value