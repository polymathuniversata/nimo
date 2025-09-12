# Smart Contract Development Guide

This guide covers smart contract development, deployment, and integration for the Nimo platform.

## 🚀 **CURRENT PRIORITY: Base Sepolia Deployment**

**Status**: Smart contracts are **designed and ready for deployment**. The NimoIdentity and NimoToken contracts are complete and need to be deployed to Base Sepolia testnet to unblock frontend Web3 integration.

### Immediate Action Required

#### Step 1: Environment Setup
```bash
cd contracts
curl -L https://foundry.paradigm.xyz | bash
foundryup
forge install OpenZeppelin/openzeppelin-contracts
```

#### Step 2: Get Base Sepolia ETH
- Visit https://bridge.base.org/deposit
- Get testnet ETH for deployment (minimal amount needed ~0.01 ETH)

#### Step 3: Configure Environment
```bash
# Create .env file in contracts directory
PRIVATE_KEY=your_private_key_here
BASESCAN_API_KEY=your_basescan_api_key
```

#### Step 4: Deploy Contracts
```bash
# Deploy to Base Sepolia using Foundry
forge script script/Deploy.s.sol:DeployScript \
  --rpc-url https://sepolia.base.org \
  --broadcast \
  --verify \
  --chain-id 84532
```

#### Step 5: Update Backend Configuration
After deployment, update `backend/.env`:
```bash
NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA=0x_deployed_address_here
NIMO_TOKEN_CONTRACT_BASE_SEPOLIA=0x_deployed_address_here
```

### Expected Results
- ✅ NimoToken deployed with 1M initial supply
- ✅ NimoIdentity deployed with identity management
- ✅ Roles configured (MINTER_ROLE, VERIFIER_ROLE, METTA_AGENT_ROLE)
- ✅ Contract integration ready for frontend
- ✅ Backend can interact with deployed contracts

### Next Steps After Deployment
1. **Frontend Integration**: Add Web3 wallet connection
2. **Contract Interaction**: Implement hooks for token balance, identity creation
3. **Testing**: End-to-end user flows with blockchain
4. **Production**: Deploy to Base mainnet when ready

---

## Overview

Nimo's smart contracts provide the decentralized backbone for identity management, reputation tokens, and impact bonds. The contracts integrate with MeTTa reasoning agents to create an autonomous system for verifying contributions and awarding tokens.

## Contract Architecture

### Contract Hierarchy

```
NimoIdentity (ERC721 + AccessControl + ReentrancyGuard)
├── Identity Management (NFT-based)
├── Contribution Tracking
├── Impact Bond Creation & Management
└── MeTTa Agent Integration

NimoToken (ERC20 + AccessControl + Pausable)
├── Reputation Token Distribution
├── Governance Token Functionality
├── MeTTa-Verified Minting
└── Opportunity-Based Burning
```

### Key Design Principles

1. **Hybrid Architecture**: Combine on-chain immutability with off-chain MeTTa reasoning
2. **Gas Optimization**: Minimize transaction costs through efficient storage and computation
3. **Security First**: Use OpenZeppelin standards and security best practices
4. **Upgradeability**: Design for future improvements while maintaining decentralization
5. **MeTTa Integration**: Bridge autonomous reasoning with blockchain execution

## Development Setup

### Prerequisites

```bash
npm install -g hardhat
npm install @openzeppelin/contracts
npm install @nomiclabs/hardhat-waffle
npm install @nomiclabs/hardhat-ethers
npm install chai ethereum-waffle
```

### Project Structure

```
contracts/
├── NimoIdentity.sol        # Main identity contract
├── NimoToken.sol          # Reputation token contract
├── interfaces/
│   ├── IMeTTaAgent.sol    # MeTTa agent interface
│   └── IVerifier.sol      # Verifier interface
├── libraries/
│   └── MeTTaProof.sol     # MeTTa proof verification
├── scripts/
│   ├── deploy.js          # Deployment script
│   └── setup.js           # Initial configuration
├── test/
│   ├── NimoIdentity.test.js
│   └── NimoToken.test.js
├── hardhat.config.js      # Hardhat configuration
└── package.json
```

### Environment Configuration

Create `hardhat.config.js`:
```javascript
require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 1337
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 1337
    },
    goerli: {
      url: process.env.GOERLI_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    },
    mainnet: {
      url: process.env.MAINNET_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  }
};
```

## Smart Contract Development

### NimoIdentity Contract Deep Dive

#### Core Data Structures
```solidity
struct Identity {
    string username;           // Unique username
    string metadataURI;       // IPFS URI for profile data
    uint256 reputationScore;  // Calculated reputation
    uint256 tokenBalance;     // Current token balance
    bool isActive;            // Active status
    uint256 createdAt;        // Creation timestamp
}

struct Contribution {
    uint256 identityId;       // Owner's identity NFT ID
    string contributionType;  // Type (hackathon, volunteer, etc.)
    string description;       // Contribution description
    string evidenceURI;       // IPFS evidence link
    bool verified;            // Verification status
    address verifier;         // Verifying organization
    uint256 tokensAwarded;    // Tokens awarded
    uint256 timestamp;        // Submission time
    string mettaHash;         // MeTTa proof hash
}
```

#### Key Functions

**Identity Management:**
```solidity
function createIdentity(string memory username, string memory metadataURI) external {
    require(usernameToTokenId[username] == 0, "Username already exists");
    require(addressToTokenId[msg.sender] == 0, "Address already has identity");
    
    uint256 tokenId = _nextTokenId++;
    
    identities[tokenId] = Identity({
        username: username,
        metadataURI: metadataURI,
        reputationScore: 0,
        tokenBalance: 0,
        isActive: true,
        createdAt: block.timestamp
    });
    
    usernameToTokenId[username] = tokenId;
    addressToTokenId[msg.sender] = tokenId;
    
    _safeMint(msg.sender, tokenId);
    
    emit IdentityCreated(tokenId, username, msg.sender);
}
```

**MeTTa Integration:**
```solidity
function executeMeTTaRule(
    string memory rule,
    uint256 targetIdentityId,
    uint256 tokensToAward
) external onlyRole(METTA_AGENT_ROLE) {
    require(identities[targetIdentityId].isActive, "Target identity not active");
    
    // Award tokens based on MeTTa agent decision
    if (tokensToAward > 0) {
        identities[targetIdentityId].tokenBalance += tokensToAward;
        identities[targetIdentityId].reputationScore += tokensToAward / 10;
        
        emit TokensAwarded(targetIdentityId, tokensToAward, "MeTTa agent award");
    }
    
    emit MeTTaRuleExecuted(rule, "executed successfully");
}
```

### NimoToken Contract Deep Dive

#### MeTTa-Verified Token Distribution
```solidity
function mintForContribution(
    address to,
    uint256 amount,
    string memory reason,
    string memory mettaProof
) external onlyRole(MINTER_ROLE) whenNotPaused {
    require(to != address(0), "Cannot mint to zero address");
    require(amount > 0, "Amount must be greater than 0");
    
    uint256 distributionId = _nextDistributionId++;
    
    distributions[distributionId] = Distribution({
        recipient: to,
        amount: amount,
        reason: reason,
        timestamp: block.timestamp,
        mettaProof: mettaProof
    });
    
    _mint(to, amount);
    
    emit TokensDistributed(to, amount, reason);
    emit MeTTaProofAttached(distributionId, mettaProof);
}
```

## Testing Strategy

### Unit Tests

Create comprehensive test suites for each contract:

```javascript
// test/NimoIdentity.test.js
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("NimoIdentity", function () {
    let nimoIdentity, nimoToken;
    let owner, user1, user2, verifier, mettaAgent;

    beforeEach(async function () {
        [owner, user1, user2, verifier, mettaAgent] = await ethers.getSigners();
        
        const NimoIdentity = await ethers.getContractFactory("NimoIdentity");
        nimoIdentity = await NimoIdentity.deploy();
        
        const NimoToken = await ethers.getContractFactory("NimoToken");
        nimoToken = await NimoToken.deploy("NimoToken", "NIMO", 1000000);
        
        // Setup roles
        const VERIFIER_ROLE = await nimoIdentity.VERIFIER_ROLE();
        const METTA_AGENT_ROLE = await nimoIdentity.METTA_AGENT_ROLE();
        
        await nimoIdentity.grantRole(VERIFIER_ROLE, verifier.address);
        await nimoIdentity.grantRole(METTA_AGENT_ROLE, mettaAgent.address);
    });

    describe("Identity Creation", function () {
        it("Should create a new identity", async function () {
            await nimoIdentity.connect(user1).createIdentity("testuser", "ipfs://test");
            
            const identity = await nimoIdentity.getIdentityByUsername("testuser");
            expect(identity.username).to.equal("testuser");
            expect(identity.isActive).to.be.true;
        });

        it("Should prevent duplicate usernames", async function () {
            await nimoIdentity.connect(user1).createIdentity("testuser", "ipfs://test");
            
            await expect(
                nimoIdentity.connect(user2).createIdentity("testuser", "ipfs://test2")
            ).to.be.revertedWith("Username already exists");
        });
    });

    describe("Contribution Management", function () {
        beforeEach(async function () {
            await nimoIdentity.connect(user1).createIdentity("contributor", "ipfs://profile");
        });

        it("Should add a contribution", async function () {
            await nimoIdentity.connect(user1).addContribution(
                "hackathon",
                "Built amazing DApp",
                "ipfs://evidence",
                "metta-hash-123"
            );
            
            const contribution = await nimoIdentity.getContribution(1);
            expect(contribution.contributionType).to.equal("hackathon");
            expect(contribution.verified).to.be.false;
        });

        it("Should verify contribution and award tokens", async function () {
            await nimoIdentity.connect(user1).addContribution(
                "hackathon",
                "Built amazing DApp",
                "ipfs://evidence",
                "metta-hash-123"
            );
            
            await nimoIdentity.connect(verifier).verifyContribution(1, 100);
            
            const contribution = await nimoIdentity.getContribution(1);
            expect(contribution.verified).to.be.true;
            expect(contribution.tokensAwarded).to.equal(100);
        });
    });

    describe("MeTTa Integration", function () {
        beforeEach(async function () {
            await nimoIdentity.connect(user1).createIdentity("metta-user", "ipfs://profile");
        });

        it("Should execute MeTTa rule and award tokens", async function () {
            const identityId = 1;
            const tokensToAward = 50;
            
            await nimoIdentity.connect(mettaAgent).executeMeTTaRule(
                "(auto-award user contribution)",
                identityId,
                tokensToAward
            );
            
            const identity = await nimoIdentity.getIdentity(identityId);
            expect(identity.tokenBalance).to.equal(tokensToAward);
            expect(identity.reputationScore).to.equal(5); // 10% of tokens
        });
    });
});
```

### Integration Tests

Test the interaction between contracts and MeTTa:

```javascript
// test/integration.test.js
describe("MeTTa-Contract Integration", function () {
    it("Should process contribution through full pipeline", async function () {
        // 1. Create identity
        await nimoIdentity.connect(user1).createIdentity("integrator", "ipfs://profile");
        
        // 2. Add contribution
        await nimoIdentity.connect(user1).addContribution(
            "volunteer",
            "Community cleanup",
            "ipfs://cleanup-photos",
            "metta-proof-xyz"
        );
        
        // 3. MeTTa agent processes and executes decision
        await nimoIdentity.connect(mettaAgent).executeMeTTaRule(
            "(verified-contribution volunteer cleanup-photos)",
            1,
            75
        );
        
        // 4. Verify final state
        const identity = await nimoIdentity.getIdentity(1);
        expect(identity.tokenBalance).to.equal(75);
        expect(identity.reputationScore).to.equal(7);
    });
});
```

## Deployment

### Local Development Deployment

```javascript
// scripts/deploy.js
async function main() {
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());
    
    // Deploy NimoToken
    const NimoToken = await ethers.getContractFactory("NimoToken");
    const nimoToken = await NimoToken.deploy("NimoToken", "NIMO", 1000000);
    await nimoToken.deployed();
    console.log("NimoToken deployed to:", nimoToken.address);
    
    // Deploy NimoIdentity
    const NimoIdentity = await ethers.getContractFactory("NimoIdentity");
    const nimoIdentity = await NimoIdentity.deploy();
    await nimoIdentity.deployed();
    console.log("NimoIdentity deployed to:", nimoIdentity.address);
    
    // Setup initial configuration
    await setupContracts(nimoIdentity, nimoToken, deployer);
    
    // Save deployment addresses
    const deployment = {
        nimoIdentity: nimoIdentity.address,
        nimoToken: nimoToken.address,
        network: "localhost",
        deployer: deployer.address
    };
    
    console.log("Deployment complete:", deployment);
}

async function setupContracts(identity, token, deployer) {
    // Grant roles
    const MINTER_ROLE = await token.MINTER_ROLE();
    await token.grantRole(MINTER_ROLE, identity.address);
    
    const VERIFIER_ROLE = await identity.VERIFIER_ROLE();
    await identity.grantRole(VERIFIER_ROLE, deployer.address);
    
    console.log("Initial setup complete");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
```

### Commands

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Start local blockchain
npx hardhat node

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost

# Deploy to testnet
npx hardhat run scripts/deploy.js --network goerli

# Verify contract on Etherscan
npx hardhat verify --network goerli CONTRACT_ADDRESS
```

## Integration with Backend

### Environment Variables

Add to `backend/.env`:
```bash
# Blockchain Configuration
WEB3_PROVIDER_URL=http://localhost:8545
NIMO_IDENTITY_CONTRACT=0x5FbDB2315678afecb367f032d93F642f64180aa3
NIMO_TOKEN_CONTRACT=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
BLOCKCHAIN_SERVICE_PRIVATE_KEY=0x...

# Contract ABIs (auto-generated)
CONTRACT_BUILD_DIR=../contracts/artifacts/contracts
```

### Backend Integration

The `BlockchainService` class handles all contract interactions:

```python
# services/blockchain_service.py
blockchain_service = BlockchainService()

# Create identity on blockchain
tx_hash = blockchain_service.create_identity_on_chain(
    username="alice",
    metadata_uri="ipfs://QmUserProfile123",
    user_address="0x742d35Cc6634C0532925a3b8D0C9dF7Cf8Cd9E",
)

# Execute MeTTa rule on blockchain
tx_hash = blockchain_service.execute_metta_rule_on_chain(
    rule="(auto-award alice hackathon-2023)",
    identity_id=1,
    tokens_to_award=100
)
```

## Security Considerations

### Access Control
- Use OpenZeppelin's `AccessControl` for role management
- Implement multi-signature for critical functions
- Regular security audits and formal verification

### Gas Optimization
- Pack structs to minimize storage slots
- Use events for historical data instead of storage
- Implement efficient batch operations

### MeTTa Integration Security
- Validate MeTTa proofs before execution
- Implement rate limiting for automated decisions
- Use cryptographic hashes for proof verification

## Monitoring and Analytics

### Event Tracking
Monitor key contract events:
- `IdentityCreated`
- `ContributionVerified`
- `TokensAwarded`
- `MeTTaRuleExecuted`

### Performance Metrics
- Gas usage per transaction type
- Transaction success rates
- MeTTa agent decision accuracy
- Token distribution patterns

## Future Enhancements

### Planned Upgrades
1. **Layer 2 Integration**: Deploy on Polygon/Arbitrum for lower costs
2. **Advanced MeTTa Proofs**: Implement zero-knowledge proofs for privacy
3. **Cross-Chain Identity**: Enable identity portability across blockchains
4. **Governance Evolution**: Transition to full DAO governance
5. **Machine Learning Integration**: Enhance MeTTa agents with ML models