# Nimo: Decentralized Youth Identity & Proof of Contribution Network

## Overview
Nimo is a decentralized reputation system built on MeTTa language that enables African youth to create persistent digital identities, earn reputation tokens for real-world contributions, and use their identity and reputation to unlock access to opportunities like internships, grants, gigs, and DAO proposals.

## Problem Statement
Millions of African youth participate in informal work, activism, and decentralized learning but lack verifiable digital identity or proof of their contributions, limiting their access to jobs, capital, and global platforms.

## Features
- **Decentralized Identity**: Create a persistent MeTTa-based identity
- **Contribution Tracking**: Record and verify real-world actions and contributions
- **Reputation Tokens**: Earn tokens for contributions like volunteering, building projects, attending events, and participating in DAO votes
- **Verification System**: Trusted organizations can verify user contributions
- **Automated Token Awards**: Automatic token distribution for verified contributions
- **NFT-based Diaspora Bonds**: Enable Kenyans abroad to fund local creators or causes via NFT-backed "impact bonds"

## Project Structure
```
Nimo/
├── backend/           # Flask REST API server
│   ├── models/       # Database models (SQLAlchemy)
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic & MeTTa integration
│   └── utils/        # Helper functions
├── frontend/         # Vue.js + Quasar UI
│   ├── src/
│   │   ├── components/  # Reusable Vue components
│   │   ├── pages/      # Application pages
│   │   ├── services/   # API service layer
│   │   └── stores/     # Pinia state management
├── docs/            # Technical documentation
├── tests/           # MeTTa test cases
└── main.metta       # MeTTa demonstration script
```

## Sample MeTTa Atoms
```
(user Kwame)
(skill Kwame Python)
(contribution Kwame KRNL_Hackathon)
(verified_by Kwame KRNL_Org)
(token_balance Kwame 320)
```

## Autonomous Agent Logic
```
(= (auto-award $user $task)
   (and
     (contribution $user $task)
     (verified_by $user $org))
   (increase-token $user 50))
```

## Technology Stack
- **Backend**: Flask (Python) + SQLAlchemy + JWT Authentication
- **Frontend**: Vue.js 3 + Quasar Framework + Pinia
- **Core Logic**: MeTTa language for decentralized identity and reputation
- **Database**: SQLite (development) / PostgreSQL (production)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MeTTa runtime (optional for core testing)

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

4. **Access the Application**
   - Frontend: http://localhost:9000
   - Backend API: http://localhost:5000

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

## Why It Matters
- Creates a portable, tamper-proof record of experience
- Powers a youth-led gig and grant ecosystem without dependency on centralized CVs or diplomas
- Turns participation in community into on-chain economic value