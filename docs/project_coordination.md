# Nimo Project Coordination Guide
**Updated: August 26, 2025 - React.js Migration Complete**

## 🚀 **MAJOR UPDATE: Frontend Stack Completely Modernized**

### **✅ Aisha's React.js Migration Completed**
- **Vue.js/Quasar** completely removed and replaced
- **React 19.1.1** modern application implemented
- **Vite + Tailwind CSS** for fast development and styling
- **React Router DOM + Context API** for navigation and state
- **All backend work preserved** during migration

## Team Structure & Communication

### Team Members & Clear Role Assignments

#### **Aisha** - Frontend Lead ✅ **REACT.JS MIGRATION COMPLETE**
**Primary Responsibilities:**
- **Frontend Development**: All React.js frontend components and pages
- **Modern Stack**: React 19.1.1, Vite, Tailwind CSS, React Router DOM
- **User Experience Design**: UI/UX design and user flow optimization  
- **Web3 Frontend Integration**: Wallet connections, transaction UI, MetaMask integration
- **Component Architecture**: React hooks, Context API state management, modern patterns
- **Frontend Testing**: React component tests, E2E user journey tests
- **Mobile Responsiveness**: Responsive design with Tailwind CSS

**Focus Areas:**
- Complete ownership of `/frontend/client/` directory (New React app)
- All `.jsx` components and React JavaScript
- Web3 client-side integration (ethers.js, wallet SDKs)
- Vite build process and deployment
- Tailwind CSS styling and responsive design
- React Router navigation and user interface polish

#### **John** - Backend & Infrastructure Lead  
**Primary Responsibilities:**
- **Backend Development**: Flask API, database models, business logic
- **Smart Contract Development**: Solidity contracts, deployment, upgrades
- **MeTTa Integration**: AI reasoning engine, verification algorithms
- **Blockchain Integration**: Web3 backend services, transaction processing
- **Database Architecture**: Models, migrations, data integrity
- **API Design**: RESTful endpoints, authentication, rate limiting
- **DevOps & Deployment**: CI/CD, production deployment, monitoring

**Focus Areas:**
- Complete ownership of `/backend` directory and `/contracts` directory
- All Python backend code and Solidity smart contracts
- MeTTa reasoning service and AI integration
- Blockchain services and Web3 backend integration
- Database design and API architecture
- Production deployment and infrastructure

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

#### **John's Backend/Infrastructure Deliverables for Aisha:**
**Week 1-2: Foundation**
- [ ] Smart contract ABIs and deployment addresses (Base Sepolia)
- [ ] Base Sepolia testnet contract deployments  
- [ ] Basic API endpoints structure and documentation
- [ ] Base network configuration details and environment setup
- [ ] Backend server running with CORS configured for frontend

**Week 3-4: Core Development**
- [ ] Complete user authentication API (`POST /api/auth/login`, `/register`)
- [ ] Identity management endpoints (`GET/POST /api/identity`)
- [ ] Contribution verification API (`POST /api/contributions/verify`)
- [ ] MeTTa reasoning service integrated with contribution verification
- [ ] WebSocket events for real-time verification updates

**Week 5-6: Advanced Features**
- [ ] Token balance and transaction APIs
- [ ] Bond creation and investment backend logic
- [ ] Reputation scoring system via MeTTa integration
- [ ] Complete API documentation with examples

#### **Aisha's Frontend Deliverables for John:**
**Week 1-2: Foundation**  
- [ ] UI/UX mockups and user journey designs
- [ ] Frontend API requirements specification
- [ ] Wallet integration requirements (supported wallets, transaction flows)
- [ ] Component architecture and routing structure

**Week 3-4: Core Development**
- [ ] User registration/login frontend flows
- [ ] Wallet connection components and wallet state management
- [ ] API integration patterns and error handling
- [ ] Responsive design implementation for mobile/desktop

**Week 5-6: Advanced Features**
- [ ] Complete user interface for all platform features
- [ ] Frontend validation and user feedback systems
- [ ] Mobile optimization and PWA features
- [ ] User acceptance testing and feedback

#### **Joint Integration Testing (Both)**
**Week 3-6: Continuous Integration**
- [ ] End-to-end user registration and authentication flow
- [ ] Wallet connection → backend identity creation flow
- [ ] Contribution submission → MeTTa verification → token reward flow
- [ ] Complete user journey testing from registration to token earning

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