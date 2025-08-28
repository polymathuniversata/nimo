# Nimo Backend - Flask API with Cardano & MeTTa Integration

**Blockchain-first backend API for the Nimo Decentralized Youth Identity & Proof of Contribution Network**

[![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)](https://flask.palletsprojects.com/)
[![MeTTa](https://img.shields.io/badge/MeTTa-AI_Integration-orange.svg)](https://github.com/trueagi-io/hyperon-experimental)
[![Cardano](https://img.shields.io/badge/Cardano-Blockchain-blue.svg)](https://cardano.org/)

## Overview

This Flask backend provides RESTful APIs for the Nimo platform, featuring advanced MeTTa AI integration for autonomous contribution verification and a blockchain-first architecture using **Cardano** as the primary data layer.

## Architecture

### Blockchain-First Design

The backend follows a **blockchain-first architecture** where:

- **Cardano** serves as the primary data storage layer (low-cost transactions)
- **Plutus Smart Contracts** manage users, contributions, and tokens on-chain
- **IPFS/Arweave** store large files and metadata off-chain
- **Flask API** provides query layer and transaction services
- **MeTTa Engine** provides AI reasoning for verification

### Core Components

- `app.py`: Main Flask application with Cardano integration
- `config.py`: Configuration for Cardano networks and MeTTa settings
- `models/`: Data models compatible with Cardano data structures
- `routes/`: API endpoints for frontend integration
- `services/`: Business logic including MeTTa and Cardano services
- `utils/`: Helper functions for Cardano interactions

## Technology Stack

### Backend Framework
- **Flask**: Lightweight WSGI web application framework
- **SQLAlchemy**: ORM for local caching and session management
- **Flask-JWT-Extended**: Secure authentication with JWT tokens
- **Flask-CORS**: Cross-origin resource sharing for frontend integration

### Cardano Integration
- **PyCardano**: Python library for Cardano blockchain interaction
- **Blockfrost API**: Cardano network access and transaction monitoring
- **Cardano Networks**: Preview, Preprod, and Mainnet support
- **Plutus Contracts**: Smart contract interfaces for NimoIdentity and NimoToken

### AI & Reasoning
- **MeTTa Language**: Autonomous reasoning and decision-making
- **Hyperon Integration**: Advanced AI verification engine
- **Fraud Detection**: Pattern recognition and anomaly detection
- **Confidence Scoring**: Multi-factor verification confidence

## 🚀 Quick Start

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

### Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv nimo_env
   # Windows:
   nimo_env\Scripts\activate
   # macOS/Linux:
   source nimo_env/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_cardano.txt
   pip install hyperon  # MeTTa/Hyperon (optional)
   ```

3. **Configure environment:**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   # Edit .env with your Cardano network RPC and contract addresses
   ```

4. **Initialize Cardano connection:**
   ```bash
   python -c "from services.cardano_service import CardanoService; cs = CardanoService(); print('Cardano connected:', cs.is_connected())"
   ```

5. **Run the development server:**
   ```bash
   python app.py
   ```

## 📋 Prerequisites

- **Python 3.9+**
- **Blockfrost API Account** (for Cardano network access)
- **Cardano Wallet** (for service operations)
- **MeTTa Runtime** (optional for core testing)

## API Endpoints

### System Status
- `GET /api/health` - Health check with Cardano and MeTTa status
- `GET /api` - API information and version details

### Authentication & Identity
- `POST /api/auth/register` - User registration with Cardano identity creation
- `POST /api/auth/login` - User login with JWT token generation
- `GET /api/auth/me` - Get current user profile from Cardano

### MeTTa-Powered Contribution System
- `POST /api/contributions` - Submit contribution for MeTTa verification
- `POST /api/contributions/{id}/verify` - Trigger MeTTa AI verification
- `GET /api/contributions/{id}/explain` - Get MeTTa reasoning explanation
- `GET /api/contributions` - List user's contributions from Cardano

### Token Economy (ADA/NIMO)
- `GET /api/tokens/balance/{address}` - Get ADA/NIMO balance from Cardano
- `GET /api/tokens/transactions/{address}` - Get token transaction history
- `POST /api/tokens/transfer` - Transfer tokens between users

### Impact Bonds (Cardano Native)
- `POST /api/bonds` - Create impact bond smart contract
- `GET /api/bonds` - List available impact bonds
- `POST /api/bonds/{id}/invest` - Invest in impact bond
- `GET /api/bonds/{id}/milestones` - Track bond milestone progress

### Cardano-Specific Endpoints
- `GET /api/cardano/balance/{address}` - Check address ADA balance
- `POST /api/cardano/transaction` - Create and submit transaction
- `GET /api/cardano/transaction/{tx_hash}` - Get transaction status
- `GET /api/cardano/address/{address}` - Get address information
- `POST /api/cardano/wallet/create` - Create new wallet

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

# Cardano Network Configuration
CARDANO_NETWORK=preview  # preview, preprod, mainnet
BLOCKFROST_PROJECT_ID_PREVIEW=your_preview_api_key
BLOCKFROST_PROJECT_ID_PREPROD=your_preprod_api_key
BLOCKFROST_PROJECT_ID_MAINNET=your_mainnet_api_key

# Service Wallet (for automated operations)
CARDANO_SERVICE_PRIVATE_KEY=your_service_wallet_private_key
CARDANO_SERVICE_KEY_FILE=service_key.skey

# Plutus Contract Addresses (Cardano Mainnet)
NIMO_IDENTITY_CONTRACT=addr1...
NIMO_TOKEN_CONTRACT=addr1...
NIMO_BOND_CONTRACT=addr1...

# MeTTa Configuration
USE_METTA_REASONING=True
METTA_MODE=real  # or 'mock' for testing
METTA_CONFIDENCE_THRESHOLD=0.7
METTA_DB_PATH=metta_state.json

# IPFS Configuration (optional)
IPFS_API_URL=http://localhost:5001
USE_IPFS=True

# Database (for caching only)
DATABASE_URL=sqlite:///nimo_cache.db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nimo.log
```

## MeTTa Integration

### Autonomous Verification

The backend integrates MeTTa for intelligent contribution verification:

```python
# Example MeTTa verification flow
from services.metta_integration_enhanced import MeTTaIntegrationEnhanced

service = MeTTaIntegrationEnhanced()
result = service.verify_contribution(contribution_data)
# Returns: {'verified': True, 'confidence': 0.85, 'tokens': 75, 'explanation': '...'}
```

### Key MeTTa Rules (Cardano-Specific)

```metta
;; Cardano network atoms
(= (CardanoNetwork "preview") (NetworkType "testnet"))
(= (CardanoNetwork "preprod") (NetworkType "testnet"))
(= (CardanoNetwork "mainnet") (NetworkType "mainnet"))

;; ADA and NIMO token handling
(= (TokenType "ADA") (NativeToken "Cardano"))
(= (TokenType "NIMO") (NativeToken "NimoPlatform"))

;; Main verification rule with Cardano context
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $cardano-addr)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (CardanoAddressValid $cardano-addr)
        (ImpactAssessment $contrib-id "moderate")))

;; Token calculation with AI confidence and Cardano fees
(= (CalculateTokenAward $contrib-id)
   (let* (($confidence (CalculateConfidence $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($bonus (* $confidence 50))
          ($cardano-fee (EstimateCardanoFee $contrib-id)))
     (- (+ $base-amount $bonus) $cardano-fee)))
```

### Cardano Integration in MeTTa

```metta
;; Cardano wallet and address handling
(= (CardanoWallet $wallet-id $address)
   (and (WalletID $wallet-id)
        (ValidCardanoAddress $address)))

;; Transaction verification
(= (VerifyCardanoTransaction $tx-hash)
   (and (TransactionExists $tx-hash)
        (TransactionConfirmed $tx-hash)
        (ValidTransactionInputs $tx-hash)))

;; Balance checking
(= (CheckCardanoBalance $address $min-amount)
   (and (ValidCardanoAddress $address)
        (>= (GetAddressBalance $address) $min-amount)))
```

## Cardano Integration

### Smart Contract Interaction

```python
from services.cardano_service import CardanoService

# Initialize service
cardano = CardanoService()

# Create identity on Cardano
tx_hash = cardano.create_identity(user_data)

# Submit contribution
tx_hash = cardano.submit_contribution(contribution_data)

# Get ADA/NIMO balance
balance = cardano.get_token_balance(user_address)
```

### Plutus Contract Deployment

```python
from services.plutus_service import PlutusService

# Deploy NimoIdentity contract
identity_contract = PlutusService.deploy_identity_contract()

# Deploy NimoToken contract
token_contract = PlutusService.deploy_token_contract()

# Deploy Impact Bond contract
bond_contract = PlutusService.deploy_bond_contract()
```

### Transaction Building

```python
# Create transaction with multiple outputs
tx_builder = cardano.create_transaction_builder()

# Add contribution reward
tx_builder.add_output(recipient_address, reward_amount)

# Add protocol fee
tx_builder.add_output(protocol_address, fee_amount)

# Build and submit
tx_hash = tx_builder.build_and_submit()
```

### Event Listening

The backend listens for Cardano events:

```python
# Real-time event processing
@cardano.on('ContributionVerified')
def handle_verification(contribution_id, tokens_awarded, verifier):
    # Update local cache
    # Trigger frontend notifications
    # Process MeTTa results
    pass

@cardano.on('TokenMinted')
def handle_token_mint(recipient, amount, tx_hash):
    # Update balance cache
    # Send notifications
    # Log transaction
    pass
```

## 🧪 Testing

### Run All Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Specific Components

```bash
# Test API endpoints
python test_api_endpoints.py

# Test Cardano integration
python test_cardano_connection.py

# Test MeTTa integration
python test_real_metta_integration.py

# Test complete flow
python test_complete_flow.py

# Test Plutus contracts
python test_plutus_contracts.py
```

### Cardano-Specific Tests

```bash
# Test wallet operations
python -c "from services.cardano_service import CardanoService; cs = CardanoService(); print('Wallet test:', cs.test_wallet_operations())"

# Test transaction building
python -c "from services.cardano_service import CardanoService; cs = CardanoService(); print('Transaction test:', cs.test_transaction_building())"

# Test Blockfrost integration
python -c "import blockfrost; print('Blockfrost test: OK')"
```

### Mock Mode Testing

For testing without live Cardano network:

```bash
# Set environment for mock mode
export CARDANO_NETWORK=mock
export METTA_MODE=mock

# Run tests
python -m pytest tests/ -v
```

### Code Quality

```bash
# Run linting
flake8 app tests

# Format code
black app tests
isort app tests
```

## 🚀 Deployment

### Network Environments

#### Preview Testnet (Development)
```bash
export CARDANO_NETWORK=preview
export BLOCKFROST_PROJECT_ID_PREVIEW=your_preview_api_key
# Use tADA for testing
```

#### Preprod Testnet (Staging)
```bash
export CARDANO_NETWORK=preprod
export BLOCKFROST_PROJECT_ID_PREPROD=your_preprod_api_key
# Use realistic test data
```

#### Mainnet (Production)
```bash
export CARDANO_NETWORK=mainnet
export BLOCKFROST_PROJECT_ID_MAINNET=your_mainnet_api_key
# Use real ADA and NIMO tokens
```

### Production Setup

1. **Configure production environment:**
   ```bash
   export FLASK_ENV=production
   export CARDANO_NETWORK=mainnet
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
COPY requirements.txt requirements_cardano.txt ./
RUN pip install -r requirements.txt -r requirements_cardano.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### Plutus Contract Deployment

1. **Deploy to Preview Testnet:**
   ```bash
   python contracts/deploy_to_preview.py
   ```

2. **Deploy to Preprod Testnet:**
   ```bash
   python contracts/deploy_to_preprod.py
   ```

3. **Deploy to Mainnet:**
   ```bash
   python contracts/deploy_to_mainnet.py
   ```

### Service Wallet Setup

1. **Generate service wallet:**
   ```bash
   python -c "from services.cardano_service import CardanoService; cs = CardanoService(); wallet = cs.generate_service_wallet(); print('Service wallet:', wallet)"
   ```

2. **Fund service wallet:**
   - Preview: Use [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnet/tools/faucet)
   - Mainnet: Fund with real ADA

3. **Configure wallet in environment:**
   ```bash
   export CARDANO_SERVICE_PRIVATE_KEY=your_private_key
   export CARDANO_SERVICE_KEY_FILE=service_key.skey
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

## 🛠 Troubleshooting

### Common Issues

1. **Cardano Connection Failed**
   - Check Blockfrost API key validity
   - Verify network selection (preview/preprod/mainnet)
   - Ensure sufficient ADA for transaction fees

2. **PyCardano Installation Issues**
   ```bash
   pip install --upgrade pip
   pip install pycardano --force-reinstall
   ```

3. **Blockfrost API Errors**
   - Check API key permissions
   - Verify rate limits (free tier: 50,000 requests/day)
   - Check network status on [Cardano Status](https://status.cardano.org/)

4. **MeTTa Engine Unavailable**
   - System falls back to mock mode automatically
   - Check MeTTa installation: `pip install hyperon`
   - Review MeTTa logs for errors

5. **Transaction Submission Failed**
   - Check wallet balance for fees
   - Verify address format (bech32)
   - Check transaction size limits
   - Ensure proper network selection

6. **Database Sync Issues**
   - Clear local cache: `python -c "from app import db; db.drop_all(); db.create_all()"`
   - Restart event listeners
   - Check Cardano node synchronization

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
export CARDANO_DEBUG=1
export METTA_DEBUG=1

# Run with verbose output
python app.py --verbose
```

### Health Checks

```bash
# Application health
curl http://localhost:5000/api/health

# Cardano network status
curl http://localhost:5000/api/cardano/status

# MeTTa system status
curl http://localhost:5000/api/metta/status

# Blockfrost API status
curl http://localhost:5000/api/cardano/blockfrost-status
```

### Getting Help

- Check logs in `backend/logs/nimo.log`
- Run health checks with verbose output
- Review configuration in `.env`
- Test individual components in isolation
- Check [Cardano Developer Documentation](https://docs.cardano.org/)

## 📖 Additional Resources

- [Main Project README](../README.md) - Overall project overview
- [Backend Implementation Status](../docs/backend_implementation_status.md) - Current status and roadmap
- [MeTTa Integration Analysis](../docs/METTA_INTEGRATION_ANALYSIS.md) - AI reasoning details
- [Cardano Migration Guide](../docs/CARDANO_MIGRATION_GUIDE.md) - Migration from Ethereum/Base
- [Frontend Integration Guide](../docs/frontend_integration_guide.md) - React frontend details
- [API Documentation](../docs/api_documentation.md) - Complete API reference
- [Blockchain Security Guide](../docs/blockchain_security_guide.md) - Security implementation
- [Smart Contracts](../contracts/) - Plutus contract implementations
- [Technical Documentation](../docs/) - System architecture and design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for Cardano and MeTTa functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Last Updated: December 2024**
**Cardano Migration: Complete**
**MeTTa Integration: Active**