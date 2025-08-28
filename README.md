# Nimo: Decentralized Youth Identity & Proof of Contribution Network
**🚀 CARDANO MIGRATION COMPLETE - August 28, 2025**

[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.1.2-purple.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3.4-teal.svg)](https://tailwindcss.com/)
[![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)](https://flask.palletsprojects.com/)
[![Cardano](https://img.shields.io/badge/Cardano-Blockchain-blue.svg)](https://cardano.org/)
[![MeTTa](https://img.shields.io/badge/MeTTa-AI_Integration-orange.svg)](https://github.com/trueagi-io/hyperon-experimental)

## ✅ **Cardano Migration Complete**
- **Ethereum/Base** → **Cardano Blockchain** migration complete
- **USDC Tokens** → **Native ADA & NIMO Tokens**
- **Solidity Contracts** → **Plutus Smart Contracts**
- **Web3.py** → **PyCardano & Blockfrost API**
- **All backend MeTTa integration preserved** and enhanced

## 🤖 MeTTa Autonomous Agents
- **Intelligent Verification**: AI agents analyze contributions and calculate appropriate rewards
- **Complex Logic**: Handle multi-factor reputation scoring and contribution weighting
- **Transparent Reasoning**: All MeTTa decisions include cryptographic proofs
- **Persistent Identity**: MeTTa-based identity representations enable cross-platform verification
- **Fraud Detection**: Sophisticated pattern recognition to detect fraudulent contributions

## Overview
Nimo is a decentralized reputation system built on **Cardano blockchain** and **MeTTa language** that enables African youth to create persistent digital identities, earn reputation tokens for real-world contributions, and use their identity and reputation to unlock access to opportunities like internships, grants, gigs, and DAO proposals.

## Problem Statement
Millions of African youth participate in informal work, activism, and decentralized learning but lack verifiable digital identity or proof of their contributions, limiting their access to jobs, capital, and global platforms.

## Features

### 🏗️ Decentralized Identity & NFTs
- **NFT Identity Certificates**: Each identity is a unique, transferable NFT on Cardano
- **MeTTa-Powered Logic**: Autonomous reasoning for identity verification and reputation
- **Cross-Platform Portability**: Use your identity across multiple platforms and applications

### 🎯 Smart Contract Integration
- **On-Chain Contributions**: Immutable record of all contributions and verifications
- **Automated Token Awards**: Smart contracts execute MeTTa decisions automatically
- **Role-Based Access Control**: Verifiers, MeTTa agents, and users with different permissions

### 💰 Native Token Economy (ADA & NIMO)
- **NIMO Native Tokens**: Cardano native assets for reputation rewards
- **ADA Rewards**: Direct ADA transfers for high-confidence contributions
- **Conversion Rate**: 1 ADA = 100 NIMO tokens (configurable)
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
├── contracts/              # Plutus smart contracts (Cardano)
│   ├── cardano/           # Cardano-specific contracts
│   │   ├── NimoToken.hs   # NIMO token minting policy
│   │   ├── ContributionValidator.hs  # Contribution validation
│   │   └── scripts/       # Deployment scripts
│   └── scripts/           # Deployment utilities
├── backend/               # Flask REST API server
│   ├── models/            # Data models (Cardano-compatible)
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic, MeTTa & Cardano integration
│   │   ├── cardano_service.py     # Cardano blockchain integration
│   │   ├── metta_integration_enhanced.py  # MeTTa AI reasoning
│   │   └── blockchain/    # Cardano contract interfaces
│   └── utils/             # Helper functions
├── frontend/              # React.js + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/    # React JSX components
│   │   ├── pages/         # React pages
│   │   ├── contexts/      # React Context API
│   │   └── hooks/         # Custom React hooks
│   ├── package.json       # React dependencies
│   └── vite.config.js     # Vite configuration
├── docs/                  # Technical documentation
├── tests/                 # MeTTa test cases
├── main.metta            # MeTTa demonstration script
├── setup_backend.sh      # Linux/Mac automated setup
└── setup_backend.ps1     # Windows automated setup
```

## Sample MeTTa Atoms (Cardano-Enhanced)
```
; User Identity and Skills
(User "user-123" "Kwame")
(HasSkill "user-123" "Python" 4)
(HasSkill "user-123" "community_building" 3)

; Cardano Addresses and Balances
(CardanoAddress "user-123" "addr1qxqs59lphg8g6qndelq8xwqn60ag3aeyfcp33c2kdp46a429mgm3sjwq")
(ADABalance "user-123" 1500000)  ; In lovelace (1.5 ADA)
(NIMOBalance "user-123" 50000)   ; 500 NIMO tokens

; Contributions and Evidence
(Contribution "contrib-456" "user-123" "coding")
(ContributionTitle "contrib-456" "KRNL Hackathon Project")
(Evidence "evidence-789" "contrib-456" "github" "https://github.com/kwame/krnl-project")

; Verification and Impact
(HasVerification "contrib-456" "KRNL_Org" "verifier-101")
(ContributionImpact "contrib-456" "significant")
(TokenBalance "user-123" 320)
```

## Autonomous Agent Logic (Cardano-Integrated)
```
; Verification rule with confidence scoring
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))

; Dynamic ADA/NIMO reward based on evidence quality and verification
(= (CalculateTokenAward $contrib-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($confidence (CalculateConfidence $contrib-id))
          ($quality-bonus (* $confidence 50))
          ($cardano-fee (EstimateCardanoFee $contrib-id))
          ($total-amount (+ $base-amount $quality-bonus)))
     (- $total-amount $cardano-fee)))
```

## Technology Stack 🔧

### **🎨 Frontend (Completely Modernized)**
- **React 19.1.1**: Modern UI framework with hooks
- **Vite 7.1.2**: Lightning-fast build tool and dev server  
- **Tailwind CSS 3.3.4**: Utility-first CSS framework
- **React Router DOM 7.8.2**: Client-side routing
- **React Context API**: State management
- **React Icons**: Icon system

### **⚙️ Backend (Cardano-First Architecture)**
- **Flask (Python)**: RESTful API server
- **Cardano Blockchain**: Primary data storage (low-cost transactions)
- **PyCardano**: Python library for Cardano transaction building
- **Blockfrost API**: Cardano network access and monitoring
- **MeTTa Integration**: AI reasoning engine (✅ COMPLETE)
- **JWT Authentication**: Secure authentication
- **SQLAlchemy**: Database ORM for caching

### **⛓️ Cardano Blockchain & Smart Contracts**
- **Cardano Networks**: Preview, Preprod, and Mainnet support
- **Plutus Smart Contracts**: Functional smart contracts in Haskell
- **Native Token Support**: Built-in multi-asset functionality
- **Blockfrost API**: Comprehensive blockchain data access
- **Cardano Addresses**: Bech32 address format support
- **Transaction Metadata**: Rich metadata support for MeTTa proofs

### **🧠 AI & Logic**
- **MeTTa Language**: Autonomous reasoning and decision-making
- **Hyperon Integration**: Advanced AI verification
- **Fraud Detection**: Pattern recognition and anomaly detection
- **Confidence Scoring**: Multi-factor verification confidence

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Blockfrost API account (for Cardano network access)
- MeTTa runtime (optional for core testing)
- Cardano wallet (for service operations)
- Test ADA (for Cardano testnet deployment)

### Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x setup_backend.sh
./setup_backend.sh
```

**Windows:**
```powershell
.\setup_backend.ps1
```

### Manual Development Setup

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
   # Initialize blockchain connection (no database needed)
   python -c "from services.blockchain_service import BlockchainService; bs = BlockchainService(); print('Blockchain connected:', bs.is_connected())"
   flask run
   ```

3. **Frontend Setup** 🆕 **React.js Stack** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   # React app with hot reload runs on http://localhost:5173
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

## 📚 Documentation
- [Backend Implementation Status](docs/backend_implementation_status.md) - Current status and roadmap
- [MeTTa Integration Analysis](docs/METTA_INTEGRATION_ANALYSIS.md) - AI reasoning details
- [Cardano Migration Guide](CARDANO_MIGRATION_GUIDE.md) - Migration from Ethereum/Base
- [Frontend Integration Guide](docs/frontend_integration_guide.md) - React frontend details
- [API Documentation](docs/api_documentation.md) - Complete API reference
- [Blockchain Security Guide](docs/blockchain_security_guide.md) - Security implementation
- [Backend README](backend/README.md) - Detailed backend setup and API docs

## 🌐 Cardano Network Architecture

### **🔗 Why Cardano Blockchain?**
- **Sustainability**: Proof-of-Stake with 99.95% lower energy consumption than Bitcoin
- **Low Cost**: Average transaction ~0.17 ADA (~$0.08)
- **Reliability**: High uptime and network stability
- **Native Assets**: Built-in multi-asset support without smart contracts
- **Formal Verification**: Mathematically-proven smart contract correctness
- **Rich Metadata**: Native support for complex data structures

### **📊 Data Architecture**
```
Cardano Blockchain:
├── Native Tokens (NIMO)     → Reputation tokens via minting policies
├── ADA Transfers            → Direct ADA rewards for contributions
├── Plutus Validators        → Contribution verification logic
├── Transaction Metadata     → MeTTa proofs and reasoning data
└── Addresses (Bech32)       → User wallet addresses

IPFS Storage:
├── User avatars & documents
├── Contribution evidence files
├── Bond documentation
└── Large metadata objects

Backend Services:
├── Blockfrost API layer (reads blockchain state)
├── PyCardano transaction service (writes to blockchain)
├── MeTTa verification engine
└── IPFS file management
```

### **⚡ Performance Strategy**
- **Blockfrost API**: Fast blockchain data access
- **Transaction Batching**: Optimized for low Cardano fees
- **Metadata Richness**: Store MeTTa proofs on-chain
- **Event Monitoring**: Real-time transaction tracking
- **Caching Layer**: Redis for frequent queries

## Why It Matters
- Creates a truly portable, tamper-proof record of experience
- Powers a youth-led gig and grant ecosystem without dependency on centralized servers
- Turns participation in community into on-chain economic value
- Enables global access without geographical restrictions or server downtime
- Provides sustainable blockchain infrastructure with formal verification

## 🤝 Contributing

We welcome contributions from developers, researchers, and community members!

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with proper tests
4. Update documentation as needed
5. Submit a pull request

### Areas for Contribution
- **MeTTa Rule Development**: Enhance AI reasoning capabilities
- **Plutus Smart Contracts**: Improve on-chain logic
- **Frontend Components**: Build user interfaces
- **Documentation**: Improve guides and tutorials
- **Testing**: Add comprehensive test coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Cardano Foundation** for the sustainable blockchain infrastructure
- **TrueAGI** for the MeTTa reasoning engine
- **Blockfrost** for comprehensive Cardano API services
- **Open Source Community** for the tools and libraries that make this possible

---

**🚀 Nimo Platform - Building the Future of Decentralized Reputation on Cardano**
**Last Updated: August 28, 2025**