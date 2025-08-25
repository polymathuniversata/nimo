# Nimo Project Coordination Guide

## Team Structure & Communication

### Team Members
- **John**: Backend Developer, Smart Contract Developer, AI/MeTTa Integration
- **Aisha**: Frontend Developer, Web3 Integration, User Experience Designer

### Communication Channels

#### Daily Standups (9:00 AM)
- **Duration**: 15 minutes
- **Format**: Voice call or in-person
- **Agenda**:
  - What did you accomplish yesterday?
  - What are you working on today?
  - Any blockers or questions?

#### Weekly Planning (Mondays 10:00 AM)
- **Duration**: 1 hour
- **Review**: Previous week's progress
- **Plan**: Current week's priorities
- **Coordinate**: Integration points and dependencies

#### Integration Sessions (Wednesdays & Fridays 4:00 PM)
- **Duration**: 1-2 hours
- **Purpose**: Test full-stack integration
- **Activities**:
  - End-to-end functionality testing
  - Bug fixing and debugging
  - User flow validation

## Project Setup & Environment

### Initial Setup Checklist

#### For Both Team Members
- [ ] Clone the repository
- [ ] Set up Git workflow (feature branches, PR process)
- [ ] Install required development tools
- [ ] Configure development environment variables
- [ ] Set up local development databases/blockchain

#### John's Setup (Backend/Contracts/AI)
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Smart contracts setup (Foundry + Base)
cd contracts

# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install dependencies
forge install OpenZeppelin/openzeppelin-contracts
forge install OpenZeppelin/openzeppelin-contracts-upgradeable
forge install foundry-rs/forge-std

# Compile contracts
forge build

# Run tests
forge test

# Deploy to Base Sepolia
forge script script/Deploy.s.sol:DeployScript --rpc-url base-sepolia --broadcast --verify

# MeTTa setup
# Install MeTTa runtime according to documentation
pip install pymetta

# Database setup
flask db init
flask db migrate
flask db upgrade
```

#### Aisha's Setup (Frontend)
```bash
# Frontend setup
cd frontend
npm install

# Start development server
npm run dev

# Install additional Web3 dependencies
npm install web3 ethers @metamask/sdk
npm install @walletconnect/web3-provider
```

### Environment Variables

#### Backend (.env)
```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-development-secret-key
DATABASE_URL=sqlite:///nimo.db
JWT_SECRET_KEY=your-jwt-secret

# Blockchain Configuration (Base Network)
WEB3_PROVIDER_URL=https://sepolia.base.org
BASE_RPC_URL=https://mainnet.base.org
NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA=
NIMO_TOKEN_CONTRACT_BASE_SEPOLIA=
BLOCKCHAIN_SERVICE_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
BASESCAN_API_KEY=your-basescan-api-key

# MeTTa Configuration
METTA_RUNTIME_PATH=/usr/local/bin/metta
METTA_KNOWLEDGE_BASE=./metta_knowledge/

# IPFS Configuration
IPFS_API_URL=http://localhost:5001
IPFS_GATEWAY_URL=http://localhost:8080

# External APIs
ETHERSCAN_API_KEY=your-etherscan-api-key
```

#### Frontend (.env)
```bash
# API Configuration
VUE_APP_API_URL=http://localhost:5000/api
VUE_APP_WEBSOCKET_URL=ws://localhost:5000

# Blockchain Configuration (Base Network)
VUE_APP_CHAIN_ID=84532
VUE_APP_BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
VUE_APP_BASE_MAINNET_RPC_URL=https://mainnet.base.org
VUE_APP_IDENTITY_CONTRACT_BASE_SEPOLIA=
VUE_APP_TOKEN_CONTRACT_BASE_SEPOLIA=

# IPFS Configuration
VUE_APP_IPFS_GATEWAY=http://localhost:8080

# Environment
VUE_APP_ENVIRONMENT=development
VUE_APP_DEBUG=true
```

## Development Workflow

### Git Workflow

#### Branch Structure
```
main (production)
├── develop (integration branch)
├── feature/john-smart-contracts
├── feature/john-metta-integration
├── feature/john-api-endpoints
├── feature/aisha-wallet-integration
├── feature/aisha-ui-components
└── feature/aisha-contribution-flow
```

#### Commit Message Format
```
type(scope): description

Types: feat, fix, refactor, docs, test, chore
Scopes: contracts, backend, frontend, docs, tests

Examples:
feat(contracts): implement identity NFT minting
fix(frontend): resolve wallet connection issues
refactor(backend): optimize MeTTa query performance
```

#### Pull Request Process
1. Create feature branch from `develop`
2. Implement feature with tests
3. Create PR to `develop` branch
4. Code review by team member
5. Merge after approval and CI passes

### Integration Points & Dependencies

#### Week 1-2: Foundation
**John's Dependencies for Aisha:**
- [ ] Smart contract ABIs and deployment addresses (Base Sepolia)
- [ ] Base Sepolia testnet contract deployments
- [ ] Basic API endpoints for testing
- [ ] Base network configuration details

**Aisha's Dependencies for John:**
- [ ] UI mockups and user flow designs
- [ ] Web3 integration requirements
- [ ] Frontend API requirements specification

#### Week 3-4: Core Development
**John's Deliverables for Aisha:**
- [ ] User authentication API
- [ ] Identity management endpoints
- [ ] Contract interaction helpers
- [ ] WebSocket events for real-time updates

**Aisha's Deliverables for John:**
- [ ] User registration/login flows
- [ ] Wallet connection components
- [ ] API integration feedback
- [ ] Frontend error handling requirements

#### Week 5-6: Advanced Features
**Integration Testing Together:**
- [ ] End-to-end user registration flow
- [ ] Identity NFT creation and display
- [ ] Contribution submission and verification
- [ ] Token balance display and transactions

### Testing Strategy

#### Unit Testing
**John's Responsibilities:**
- [ ] Smart contract unit tests (Hardhat/Waffle)
- [ ] Backend API tests (pytest)
- [ ] MeTTa reasoning function tests
- [ ] Database model tests

**Aisha's Responsibilities:**
- [ ] Vue component unit tests (Vitest)
- [ ] Store logic tests (Pinia)
- [ ] Utility function tests
- [ ] Web3 integration tests

#### Integration Testing
**Shared Responsibilities:**
- [ ] API integration tests
- [ ] Blockchain transaction flow tests
- [ ] User journey tests (Cypress)
- [ ] Performance and load testing

### Debugging & Troubleshooting

#### Common Integration Issues

**Blockchain Connection Issues:**
- Check Base Sepolia RPC connectivity (John)
- Verify contract addresses in frontend config (Aisha)
- Ensure MetaMask is connected to Base Sepolia network (Aisha)
- Check Base Sepolia ETH balance for gas fees (Both)
- Verify BaseScan API key for contract verification (John)

**API Integration Issues:**
- Verify CORS configuration (John)
- Check API endpoint URLs (Aisha)
- Validate request/response formats (Both)
- Debug authentication token handling (Both)

**Web3 Integration Issues:**
- Contract ABI mismatches (John to provide latest)
- Transaction failures (check gas limits and network)
- Event listening problems (verify event emission)
- Wallet connection issues (test different wallets)

#### Debugging Tools
**John's Tools:**
- Foundry's cast and forge for contract debugging
- Anvil for local Base network forking
- Flask debugger and logging
- Postman/Insomnia for API testing
- MeTTa interactive console
- BaseScan for transaction and event monitoring

**Aisha's Tools:**
- Vue DevTools for component debugging
- Browser DevTools for Web3 debugging
- Network tab for API request debugging
- MetaMask developer mode

## Code Review Guidelines

### Review Checklist
- [ ] Code follows project conventions and standards
- [ ] All tests pass and new tests added for new features
- [ ] Documentation updated for public APIs
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] No sensitive data exposed in logs or code

### Focus Areas

**John's Code Reviews:**
- Smart contract security and gas optimization
- API design and error handling
- MeTTa reasoning logic correctness
- Database query performance

**Aisha's Code Reviews:**
- Component reusability and maintainability  
- User experience and accessibility
- Web3 integration security
- Mobile responsiveness

## Deployment Strategy

### Development Environment
- **Backend**: Local Flask development server
- **Frontend**: Quasar development server with hot reload
- **Blockchain**: Base Sepolia testnet + Anvil for local forking
- **Database**: SQLite for rapid development

### Staging Environment
- **Backend**: Docker container on cloud server
- **Frontend**: Deployed to Netlify/Vercel with preview URLs
- **Blockchain**: Base Sepolia testnet
- **Database**: PostgreSQL

### Production Environment
- **Backend**: Production server with load balancing
- **Frontend**: CDN-optimized static files
- **Blockchain**: Base mainnet (low-cost Ethereum L2)
- **Database**: PostgreSQL with replication

## OpenZeppelin MCP Integration

### Installation & Setup
```bash
# For John (Smart Contract Development with Foundry)
cd contracts

# Use OpenZeppelin MCP for contract generation
npx -y @openzeppelin/contracts-mcp

# Install Foundry dependencies
forge install OpenZeppelin/openzeppelin-contracts
forge install foundry-rs/forge-std
```

### Usage in Development
When writing smart contracts, John can use the OpenZeppelin MCP to:
- Generate secure contract templates
- Get best practice recommendations
- Access latest OpenZeppelin patterns
- Validate security implementations

### Claude Desktop Configuration
Add to MCP configuration:
```json
{
  "servers": {
    "OpenZeppelinContracts": {
      "type": "stdio", 
      "command": "npx",
      "args": ["-y", "@openzeppelin/contracts-mcp"]
    }
  }
}
```

## Project Milestones & Deliverables

### Week 3 Demo (Foundation Complete)
**Demo Script:**
1. Show local blockchain running with deployed contracts
2. Demonstrate basic user registration through frontend
3. Show wallet connection and account linking
4. Display basic identity creation flow

### Week 6 Demo (Core Features)
**Demo Script:**
1. Complete user onboarding flow
2. Contribution submission and evidence upload
3. MeTTa AI verification in action
4. Token balance updates and reputation display

### Week 9 Demo (Advanced Features)
**Demo Script:**
1. Impact bond creation and investment flow
2. Governance voting system
3. Mobile responsiveness demonstration
4. Performance and security features

### Week 12 Production Launch
**Launch Checklist:**
- [ ] All tests passing (unit, integration, E2E)
- [ ] Security audit completed
- [ ] Performance optimization verified
- [ ] Documentation complete
- [ ] Deployment automation working
- [ ] Monitoring and analytics configured

## Risk Management

### Technical Risks
**Smart Contract Bugs:**
- Mitigation: Comprehensive testing + OpenZeppelin MCP validation
- Contingency: Upgrade mechanisms and emergency pause

**Web3 Integration Issues:**
- Mitigation: Multiple wallet support and fallback options
- Contingency: Traditional auth backup for critical features

**MeTTa Performance:**
- Mitigation: Caching and optimization strategies
- Contingency: Manual verification fallback system

### Project Risks
**Scope Creep:**
- Solution: Weekly scope reviews and priority alignment
- Escalation: Feature parking lot for post-launch

**Integration Delays:**
- Solution: Daily integration testing
- Contingency: Fallback implementations for complex features

**Resource Constraints:**
- Solution: Pair programming and knowledge sharing
- Escalation: External contractor support if needed

This coordination guide ensures John and Aisha can work efficiently together while building a robust, secure, and user-friendly decentralized identity platform.