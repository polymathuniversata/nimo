# Nimo: Decentralized Youth Identity & Proof of Contribution Network

[![Status](https://img.shields.io/badge/Status-95%25_Complete-green.svg)](https://github.com/polymathuniversata/nimo)
[![Ready](https://img.shields.io/badge/Ready-Production_Deployment-blue.svg)](https://github.com/polymathuniversata/nimo)

## Overview

Nimo is a decentralized reputation system built on **Cardano blockchain** and **MeTTa language** that enables African youth to create persistent digital identities, earn reputation tokens for real-world contributions, and use their identity and reputation to unlock access to opportunities like internships, grants, gigs, and DAO proposals.

## Key Features

- 🏗️ **Decentralized Identity & NFTs**: Unique, transferable NFT identities on Cardano
- 🎯 **Smart Contract Integration**: Immutable contribution records with automated token awards
- 💰 **Native Token Economy**: NIMO tokens for reputation rewards and opportunity access
- 🌍 **Impact Bond Marketplace**: Decentralized funding for local projects
- 🤖 **MeTTa Autonomous Agents**: AI-powered contribution verification and reward calculation
- 🔐 **Multi-Chain Support**: Cardano primary with Base Network compatibility

## Quick Start

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

## Project Structure

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

## Detailed Documentation

For comprehensive technical details, implementation guides, API documentation, and development resources, see the [docs/](./docs/) directory:

- **[Technical Architecture](./docs/architecture.md)** - System design and components
- **[API Documentation](./docs/api/)** - Complete API reference
- **[Development Guides](./docs/development/)** - Setup, deployment, and contribution guides
- **[Security Documentation](./docs/security/)** - Security measures and compliance
- **[Blockchain Integration](./docs/blockchain/)** - Cardano and smart contract details

## Technology Stack

**Frontend:** React 18.3.1, TypeScript 5.8.3, Vite 5.4.19, Tailwind CSS 3.4.17
**Backend:** Flask 3.0.3, SQLAlchemy 2.0.32, MeTTa AI (PyMeTTa 0.1.1)
**Blockchain:** Cardano (Aiken 1.0.28-alpha), Plutus v2, Blockfrost API
**AI:** Hyperon Runtime, MeTTa Language for autonomous reasoning

## Contributing

We welcome contributions! See [docs/development/README.md](./docs/development/README.md) for:
- Development workflow and testing requirements
- Code standards and TDD approach
- Areas for contribution (MeTTa rules, smart contracts, frontend components)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For questions, issues, or contributions, please refer to the appropriate documentation in the [docs/](./docs/) directory or create an issue in the GitHub repository.