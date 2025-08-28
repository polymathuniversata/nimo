# User Guide: Nimo Platform

## Introduction

Nimo is a decentralized platform that allows African youth to create verifiable digital identities and earn reputation tokens for their real-world contributions. Built on **Cardano blockchain** with MeTTa-powered autonomous agents, Nimo provides a permanent, tamper-proof record of your achievements and contributions.

### What Makes Nimo Unique

- 🏗️ **Native Token Identity**: Your identity is represented by native Cardano tokens
- 🤖 **AI Verification**: MeTTa autonomous agents intelligently verify contributions
- 💰 **ADA & NIMO Tokens**: Earn ADA rewards and NIMO reputation tokens
- 🌍 **Global Access**: Use your identity across platforms and opportunities worldwide
- 🔒 **Permanent Record**: Immutable Cardano blockchain storage ensures your reputation is never lost
- 🌱 **Sustainable**: Proof-of-Stake blockchain with minimal environmental impact

## Getting Started

### Creating Your Identity

**Prerequisites:**
- Cardano wallet (Yoroi, Daedalus, or Eternl recommended)
- Small amount of ADA for transaction fees
- Access to the Nimo platform

**Step-by-step process:**

1. **Connect Your Wallet**
   - Visit the Nimo platform
   - Click "Connect Wallet" and approve the connection
   - Ensure you're on the correct Cardano network (Mainnet or Testnet)

2. **Create Your Token-Based Identity**
   - Choose a unique username
   - Add your skills and expertise areas
   - Upload a profile picture (stored on IPFS)
   - Provide location and bio information
   - Click "Create Identity" and sign the transaction

3. **Your Identity is Established**
   - Receive native tokens representing your identity
   - Initial reputation score: 0 NIMO tokens
   - Initial ADA balance: 0 (rewards earned through contributions)
   - Identity stored on Cardano blockchain with MeTTa metadata

**Technical Details:**
Your identity is stored as both MeTTa atoms and Cardano native tokens:
```
MeTTa: (user "YourName")
       (skill "YourName" "Python")
       (location "YourName" "Nairobi")
       (cardanoAddress "YourName" "addr1qx...")

Cardano: Native tokens with metadata
         ADA balance for rewards
         NIMO tokens for reputation
```
       Owner: 0x742d35Cc...
       Metadata: ipfs://QmProfile...
```

### Recording Your Contributions

**On-Chain Contribution Process:**

1. **Submit Your Contribution**
   - Navigate to "Add Contribution" page
   - Select contribution type (volunteer, hackathon, education, etc.)
   - Provide detailed description of your work
   - Upload evidence (photos, certificates, project links) to IPFS
   - Sign blockchain transaction to create permanent record

2. **Automatic MeTTa Analysis**
   - MeTTa agents analyze your contribution automatically
   - AI evaluates evidence quality and impact level
   - System calculates appropriate token reward
   - MeTTa reasoning generates cryptographic proof

3. **Smart Contract Execution**
   - Verified contributions trigger automatic token minting
   - Reputation score updated based on contribution value
   - All decisions recorded immutably on blockchain
   - Event emitted for real-time updates

**Example Contribution Flow:**
```
1. User submits: "Organized coding bootcamp for 50 youth"
   - Evidence: ipfs://QmBootcampPhotos123
   - Category: education
   - Impact: high

2. MeTTa Agent processes:
   (contribution "Alice" "coding-bootcamp-nairobi")
   (evidence-verified "Alice" "education-ngo")
   (calculate-tokens "Alice" education high 50-participants) 
   → Result: 150 tokens

3. Smart Contract executes:
   - Mint 150 NIMO tokens to Alice's wallet
   - Update reputation score: +15 points
   - Create permanent contribution record
   - Trigger frontend update
```

## Earning Reputation Tokens

### Token Award System

**NIMO tokens are ERC20 tokens** that represent your reputation on the blockchain:

**Automatic Awards via MeTTa Agents:**
- **Hackathons**: 50-200 tokens based on project quality and impact
- **Volunteer Work**: 25-100 tokens based on hours and cause importance  
- **Education**: 75-250 tokens for teaching/training others
- **Open Source**: 30-150 tokens for code contributions and maintenance
- **Community Leadership**: 100-300 tokens for organizing events/initiatives

**Award Factors:**
- **Impact Scale**: Number of people helped or reached
- **Quality of Evidence**: Photos, testimonials, project links, certificates
- **Verification Source**: Reputation of verifying organization
- **Consistency**: Regular contributors receive bonus multipliers
- **Innovation**: Novel contributions get higher rewards

**Example Token Awards:**
```
Basic volunteer work: 25 tokens
Teaching 10 students: 75 tokens
Winning hackathon: 150 tokens
Leading community project: 200 tokens
Major open source contribution: 175 tokens
```

### Using Your Tokens

**Access Opportunities:**
- **Job Applications**: Burn tokens to apply for premium positions
- **Grant Proposals**: Token balance proves your track record
- **DAO Participation**: Vote on platform decisions and funding
- **Skill Verification**: Stake tokens to endorse others' skills

**Token Utility Examples:**
- Apply for $10K grant: Requires 100+ tokens
- Premium job listing: Costs 25 tokens to apply
- Verify another user's skill: Stake 10 tokens
- Vote on governance proposal: 1 token = 1 vote

**Trading and Transfers:**
- Tokens are tradeable ERC20s - can be sent/sold
- Transfer reputation to others (with consent)
- Use tokens across DeFi protocols and DAOs
- Build token-gated communities and services

## Impact Bonds

### Smart Contract-Based Impact Investment

**Impact Bonds** are decentralized funding mechanisms that connect diaspora investors with local African projects.

### For Diaspora Investors

**Browse and Invest:**
1. **Connect Wallet** and ensure you have ETH for transactions
2. **Browse Active Bonds** by category:
   - 🌍 Climate action and environment
   - 📚 Education and skill development  
   - 💼 Economic empowerment and entrepreneurship
   - 🏥 Health and community welfare
   - 🏗️ Infrastructure and technology

3. **Invest in Projects** (any amount):
   - Review project details and milestones
   - Send ETH directly to smart contract
   - Receive impact bond tokens as proof of investment
   - Track progress through blockchain events

4. **Monitor Impact** in real-time:
   - Milestone completion notifications
   - Photo/video evidence via IPFS
   - Verified impact metrics on-chain
   - Automated returns based on success

**Example Investment Flow:**
```
Project: "Digital Skills Training for 200 Rural Youth"
Target: 5 ETH | Current: 2.3 ETH | 12 investors

Milestones:
✅ Curriculum developed (0.5 ETH released)
✅ First 50 students enrolled (1 ETH released)
🔄 100 students completed training (1.5 ETH pending)
⏳ Job placement for 80% graduates (2 ETH pending)

Your Investment: 0.2 ETH
Expected Return: 0.24 ETH (20% impact bonus)
```

### For Local Project Creators

**Create Impact Bonds:**
1. **Identity Required**: Must have Nimo identity NFT with reputation score >50
2. **Project Proposal**:
   - Title and detailed description
   - Target funding amount in ETH
   - Clear, measurable milestones
   - Timeline and expected impact
   - Evidence collection plan

3. **Smart Contract Deployment**:
   - Bond created on blockchain automatically
   - Milestone verification system set up
   - Multi-signature fund release mechanisms
   - Investor tracking and communication tools

4. **Milestone Management**:
   - Submit evidence for each milestone
   - Get verification from approved organizations
   - Automatic fund release upon verification
   - Real-time updates to all investors

## Advanced Features

### MeTTa AI Verification Process

**Automated Verification:**
Nimo uses MeTTa autonomous agents for intelligent contribution verification:

1. **Evidence Analysis**: AI examines photos, documents, and links
2. **Pattern Recognition**: Detects fraudulent or duplicate submissions  
3. **Impact Assessment**: Calculates actual vs claimed contribution value
4. **Cross-Verification**: Checks against other users and organizations
5. **Smart Scoring**: Generates confidence score for each contribution

**Human Verification Override:**
- Trusted organizations can manually verify contributions
- Multi-signature verification for high-value contributions  
- Appeals process for disputed AI decisions
- Community governance for verification standards

### Wallet Integration

**Supported Wallets:**
- MetaMask (recommended)
- WalletConnect compatible wallets
- Coinbase Wallet
- Trust Wallet
- Hardware wallets (Ledger, Trezor)

**Transaction Types:**
- Identity creation (one-time NFT minting)
- Contribution submission (creates on-chain record)
- Token transfers and trading
- Impact bond investments
- Governance voting

## Best Practices

1. **Document Everything**: Keep evidence of your contributions
2. **Seek Multiple Verifications**: More verifications increase credibility
3. **Diversify Contributions**: Build a well-rounded reputation profile
4. **Update Regularly**: Keep your skills and accomplishments current
5. **Connect with Organizations**: Build relationships with verifying entities

## Troubleshooting

### Common Issues

**Wallet Connection Problems:**
- Ensure you're on the correct network (Ethereum mainnet/testnet)
- Try refreshing the page and reconnecting
- Clear browser cache and cookies
- Update MetaMask to latest version

**Transaction Failures:**
- Check you have enough ETH for gas fees
- Increase gas limit if transaction is complex
- Try again during lower network congestion
- Verify contract addresses are correct

**Missing Tokens/NFTs:**
- Add NIMO token contract to wallet manually
- Import NFT using contract address and token ID
- Check transaction was confirmed on blockchain explorer
- Contact support if funds are missing

**Contribution Not Verified:**
- Ensure evidence is clear and relevant
- Wait for MeTTa agent processing (up to 24 hours)
- Check if additional verification is needed
- Appeal through governance if disputed

### Getting Support

**Community Channels:**
- Discord: https://discord.gg/nimo-platform
- Telegram: @nimo-support
- Twitter: @NimoPlatform

**Documentation:**
- Technical docs: `/docs/technical.md`
- Smart contracts: `/docs/smart_contracts.md` 
- Development: `/docs/development.md`

**Direct Support:**
- General questions: community@nimo.org
- Technical issues: support@nimo.org  
- Partnerships: partners@nimo.org
- Security concerns: security@nimo.org