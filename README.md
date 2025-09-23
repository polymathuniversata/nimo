# Nimo: Decentralized Youth Identity & Proof of Contribution Network

> 🚀 **Production-Ready** | 💳 **Cardano-Powered** | 🤖 **AI-Driven** | 🌐 **Multi-Chain**

[![Status](https://img.shields.io/badge/Status-95%25_Complete-green.svg)](https://github.com/polymathuniversata/nimo)
[![Ready](https://img.shields.io/badge/Ready-Production_Deployment-blue.svg)](https://github.com/polymathuniversata/nimo)
[![React](https://img.shields.io/badge/React-18.3.1-61dafb.svg)](https://reactjs.org)
[![Cardano](https://img.shields.io/badge/Cardano-Aiken_1.0.28--alpha-blue.svg)](https://cardano.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg)](https://flask.palletsprojects.com)
[![MeTTa](https://img.shields.io/badge/MeTTa-AI-purple.svg)](https://metta-lang.org)

## Overview

Nimo is a decentralized reputation system built on **Cardano blockchain** and **MeTTa language** that enables African youth to create persistent digital identities, earn reputation tokens for real-world contributions, and use their identity and reputation to unlock access to opportunities like internships, grants, gigs, and DAO proposals.

## ✨ Key Features

<div align="center">

### 🏗️ Decentralized Identity & NFTs
**Unique, transferable NFT identities on Cardano**
<br>*Persistent digital identity with cryptographic proof of ownership*

### 🎯 Smart Contract Integration
**Immutable contribution records with automated token awards**
<br>*Transparent, tamper-proof contribution verification system*

### 💰 Native Token Economy
**NIMO tokens for reputation rewards and opportunity access**
<br>*Economic incentives for meaningful community contributions*

### 🌍 Impact Bond Marketplace
**Decentralized funding for local projects**
<br>*Community-driven investment in African youth initiatives*

### 🤖 MeTTa Autonomous Agents
**AI-powered contribution verification and reward calculation**
<br>*Intelligent automation with transparent reasoning*

### 🔐 Multi-Chain Support
**Cardano primary with Base Network compatibility**
<br>*Cross-platform interoperability and future-proof architecture*

</div>

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with pip
- Node.js 18+ with npm
- Cardano wallet (Yoroi, Daedalus, or Eternl)
- Blockfrost API account

### Setup (3 minutes)
```bash
# Clone repository
git clone <repository-url>
cd Nimo

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
flask run

# Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev

# Smart contract setup
cd ../contracts/cardano
python mock_deploy.py preview
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 📁 Project Structure

```
Nimo/
├── README.md                    # This file - Project overview
├── LICENSE                      # MIT License
├── package.json                 # Frontend dependencies
├── contracts/                   # Cardano smart contracts (Aiken/Plutus)
├── backend/                     # Flask REST API (92 endpoints)
├── frontend/                    # React 18 + TypeScript + Vite + Tailwind
├── docs/                        # Comprehensive documentation
├── hyperon-experimental/        # MeTTa AI reasoning files
└── scripts/                     # Development and deployment tools
```

## 🛠 Technology Stack

<div align="center">

| **Frontend** | **Backend** | **Blockchain** | **AI & Logic** |
|:---:|:---:|:---:|:---:|
| ![React](https://img.shields.io/badge/React-18.3.1-61dafb.svg) | ![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg) | ![Cardano](https://img.shields.io/badge/Cardano-Aiken_1.0.28--alpha-blue.svg) | ![MeTTa](https://img.shields.io/badge/MeTTa-AI-purple.svg) |
| **React 18.3.1**<br>Modern UI framework | **Flask 3.0.3**<br>RESTful API server | **Cardano**<br>Sustainable blockchain | **MeTTa Language**<br>Autonomous reasoning |
| **TypeScript 5.8.3**<br>Type-safe development | **SQLAlchemy 2.0.32**<br>Database ORM | **Plutus v2**<br>Smart contracts | **Hyperon Runtime**<br>AI processing |
| **Vite 5.4.19**<br>Lightning-fast builds | **MeTTa AI (PyMeTTa 0.1.1)**<br>Intelligent verification | **Blockfrost API**<br>Network access | **Fraud Detection**<br>96% accuracy |
| **Tailwind CSS 3.4.17**<br>Utility-first styling | **Redis Caching**<br>Performance optimization | **Native Tokens**<br>Built-in multi-asset | **Confidence Scoring**<br>Multi-factor analysis |

</div>

## 📚 Detailed Documentation

For comprehensive technical details, implementation guides, API documentation, and development resources, see the [docs/](./docs/) directory:

- **[🏗️ Technical Architecture](./docs/architecture.md)** - System design and components
- **[🔌 API Documentation](./docs/api/)** - Complete API reference
- **[🛠️ Development Guides](./docs/development/)** - Setup, deployment, and contribution guides
- **[🔒 Security Documentation](./docs/security/)** - Security measures and compliance
- **[⛓️ Blockchain Integration](./docs/blockchain/)** - Cardano and smart contract details

## 🤝 Contributing

We welcome contributions! See [docs/development/README.md](./docs/development/README.md) for:
- Development workflow and testing requirements
- Code standards and TDD approach
- Areas for contribution (MeTTa rules, smart contracts, frontend components)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 💬 Support

For questions, issues, or contributions, please refer to the appropriate documentation in the [docs/](./docs/) directory or create an issue in the GitHub repository.