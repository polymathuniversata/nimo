# Nimo Backend - Flask API with MeTTa Integration

**Blockchain-first backend API for the Nimo Decentralized Youth Identity & Proof of Contribution Network**

[![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)](https://flask.palletsprojects.com/)
[![MeTTa](https://img.shields.io/badge/MeTTa-AI_Integration-orange.svg)](https://github.com/trueagi-io/hyperon-experimental)
[![Web3.py](https://img.shields.io/badge/Web3.py-Blockchain-blue.svg)](https://web3py.readthedocs.io/)

## Overview

This Flask backend provides RESTful APIs for the Nimo platform, featuring advanced MeTTa AI integration for autonomous contribution verification and a blockchain-first architecture using Base Network as the primary data layer.

## Architecture

### Blockchain-First Design

The backend follows a **blockchain-first architecture** where:

- **Base Network** serves as the primary data storage layer (~$0.01/tx)
- **Smart Contracts** manage users, contributions, and tokens on-chain
- **IPFS/Arweave** store large files and metadata off-chain
- **Flask API** provides query layer and transaction services
- **MeTTa Engine** provides AI reasoning for verification

### Core Components

- `app.py`: Main Flask application with blockchain integration
- `config.py`: Configuration for blockchain networks and MeTTa settings
- `models/`: Data models compatible with blockchain data structures
- `routes/`: API endpoints for frontend integration
- `services/`: Business logic including MeTTa and blockchain services
- `utils/`: Helper functions for blockchain interactions

## Technology Stack

### Backend Framework
- **Flask**: Lightweight WSGI web application framework
- **SQLAlchemy**: ORM for local caching and session management
- **Flask-JWT-Extended**: Secure authentication with JWT tokens
- **Flask-CORS**: Cross-origin resource sharing for frontend integration

### Blockchain Integration
- **Web3.py**: Python library for Ethereum blockchain interaction
- **Base Network**: Primary data storage (L2 Ethereum network)
- **IPFS Integration**: Decentralized file storage for evidence
- **Smart Contract Interfaces**: Direct interaction with NimoIdentity and NimoToken contracts

### AI & Reasoning
- **MeTTa Language**: Autonomous reasoning and decision-making
- **Hyperon Integration**: Advanced AI verification engine
- **Fraud Detection**: Pattern recognition and anomaly detection
- **Confidence Scoring**: Multi-factor verification confidence

## Quick Start

### Prerequisites
- Python 3.8+
- Access to Base Sepolia testnet (for development)
- MeTTa runtime (optional for core testing)
- Smart contracts deployed on Base network

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   # Edit .env with your Base network RPC URL and contract addresses
   ```

4. **Initialize blockchain connection:**
   ```bash
   python -c "from services.blockchain_service import BlockchainService; bs = BlockchainService(); print('Blockchain connected:', bs.is_connected())"
   ```

5. **Run the development server:**
   ```bash
   flask run
   ```

## API Endpoints

### System Status
- `GET /api/health` - Health check with blockchain and MeTTa status
- `GET /api` - API information and version details

### Authentication & Identity
- `POST /api/auth/register` - User registration with blockchain identity creation
- `POST /api/auth/login` - User login with JWT token generation
- `GET /api/auth/me` - Get current user profile from blockchain

### MeTTa-Powered Contribution System
- `POST /api/contributions` - Submit contribution for MeTTa verification
- `POST /api/contributions/{id}/verify` - Trigger MeTTa AI verification
- `GET /api/contributions/{id}/explain` - Get MeTTa reasoning explanation
- `GET /api/contributions` - List user's contributions from blockchain

### Token Economy
- `GET /api/tokens/balance/{user_id}` - Get token balance from smart contract
- `GET /api/tokens/transactions/{user_id}` - Get token transaction history
- `POST /api/tokens/transfer` - Transfer tokens between users

### Impact Bonds
- `POST /api/bonds` - Create impact bond smart contract
- `GET /api/bonds` - List available impact bonds
- `POST /api/bonds/{id}/invest` - Invest in impact bond
- `GET /api/bonds/{id}/milestones` - Track bond milestone progress

### MeTTa AI Features
- `POST /api/metta/verify-contribution` - Direct MeTTa verification API
- `GET /api/metta/health` - Check MeTTa engine status
- `POST /api/metta/analyze-evidence` - Analyze contribution evidence

## Environment Configuration

Create a `.env` file in the backend directory:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Blockchain Configuration (Base Network)
WEB3_PROVIDER_URL=https://sepolia.base.org
CHAIN_ID=84532
GAS_LIMIT=2000000

# Smart Contract Addresses (Base Sepolia)
NIMO_IDENTITY_CONTRACT=0x...
NIMO_TOKEN_CONTRACT=0x...
NIMO_BOND_CONTRACT=0x...

# MeTTa Configuration
USE_METTA_REASONING=True
METTA_CONFIDENCE_THRESHOLD=0.7
METTA_DB_PATH=metta_state.json

# IPFS Configuration (optional)
IPFS_API_URL=http://localhost:5001
USE_IPFS=True

# Database (for caching only)
DATABASE_URL=sqlite:///nimo_cache.db
```

## MeTTa Integration

### Autonomous Verification

The backend integrates MeTTa for intelligent contribution verification:

```python
# Example MeTTa verification flow
from services.metta_service import MeTTaService

service = MeTTaService()
result = service.verify_contribution(contribution_data)
# Returns: {'verified': True, 'confidence': 0.85, 'tokens': 75, 'explanation': '...'}
```

### Key MeTTa Rules

```metta
;; Main verification rule
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))

;; Token calculation with AI confidence
(= (CalculateTokenAward $contrib-id)
   (let* (($confidence (CalculateConfidence $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($bonus (* $confidence 50)))
     (+ $base-amount $bonus)))
```

## Blockchain Integration

### Smart Contract Interaction

```python
from services.blockchain_service import BlockchainService

# Initialize service
blockchain = BlockchainService()

# Create identity NFT
tx_hash = blockchain.create_identity(user_data)

# Submit contribution
tx_hash = blockchain.submit_contribution(contribution_data)

# Get token balance
balance = blockchain.get_token_balance(user_address)
```

### Event Listening

The backend listens for blockchain events:

```python
# Real-time event processing
@blockchain.on('ContributionVerified')
def handle_verification(contribution_id, tokens_awarded, verifier):
    # Update local cache
    # Trigger frontend notifications
    # Process MeTTa results
    pass
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_api.py
pytest tests/test_metta_integration.py
pytest tests/test_blockchain_service.py

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Run linting
flake8 app tests

# Format code
black app tests
isort app tests
```

## Deployment

### Production Setup

1. **Configure production environment:**
   ```bash
   export FLASK_ENV=production
   export WEB3_PROVIDER_URL=https://mainnet.base.org
   # Set production contract addresses
   ```

2. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 wsgi:app
   ```

3. **Set up reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

## Monitoring & Maintenance

### Health Checks

- `GET /api/health` - Overall system health
- `GET /api/health/blockchain` - Blockchain connectivity
- `GET /api/health/metta` - MeTTa engine status

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Database Maintenance

```bash
# Clear cache (runs daily)
flask clear-cache

# Update MeTTa rules
flask update-metta-rules
```

## Security Considerations

- JWT tokens with expiration
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure key management for blockchain operations
- CORS configuration for frontend domains

## Troubleshooting

### Common Issues

1. **Blockchain Connection Failed**
   - Check RPC URL and network connectivity
   - Verify contract addresses are correct
   - Ensure sufficient gas fees

2. **MeTTa Engine Unavailable**
   - System falls back to mock mode automatically
   - Check MeTTa installation and configuration
   - Review MeTTa logs for errors

3. **Database Sync Issues**
   - Clear local cache: `flask clear-cache`
   - Restart event listeners
   - Check blockchain event logs

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
export WEB3_DEBUG=1
export METTA_DEBUG=1

# Run with verbose output
flask run --verbose
```

## Related Documentation

- [Main Project README](../README.md) - Overall project overview
- [Frontend Integration](../frontend/README.md) - React frontend details
- [Technical Documentation](../docs/technical.md) - System architecture
- [MeTTa Integration Guide](../docs/metta_integration.md) - AI reasoning details
- [Smart Contracts](../docs/smart_contracts.md) - Blockchain implementation

---

**Last Updated: August 27, 2025**