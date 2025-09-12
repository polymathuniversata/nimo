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

### **Platform Status - September 2, 2025**
- **92% Complete** - Production ready with full autonomous system
- **92 API Endpoints** - Comprehensive backend functionality
- **Cardano Integration** - 92% complete with native token support
- **MeTTa AI System** - 95% complete with autonomous verification
- **Security Framework** - Enterprise-grade with 31 identified vulnerabilities (remediation in progress)

## Getting Started

### Creating Your Identity

**Prerequisites:**
- Cardano wallet (Yoroi, Daedalus, or Eternl recommended)
- Small amount of ADA for transaction fees
- Access to the Nimo platform
- **Government-issued ID for KYC verification**
- **Valid email address for account verification**

### 🔐 **Account Creation & Authentication**

**All users must complete authentication and KYC verification before accessing dashboards:**

#### **Step 1: Choose Authentication Method**

**Option A: Traditional Registration**
1. Visit the Nimo platform
2. Click "Sign Up" and select "Email Registration"
3. Provide your email and create a secure password
4. Verify your email address via confirmation link

**Option B: Wallet Authentication**
1. Visit the Nimo platform
2. Click "Connect Wallet"
3. Select your Cardano wallet (Yoroi, Daedalus, or Eternl)
4. Approve the connection and sign the authentication message
5. Your wallet address becomes your account identifier

#### **Step 2: Complete KYC Verification**

**KYC verification is mandatory for all users before dashboard access:**

1. **Personal Information**
   - Full legal name
   - Date of birth
   - Nationality and country of residence
   - Contact information

2. **Document Verification**
   - Upload government-issued ID (passport, national ID, or driver's license)
   - Provide proof of address (utility bill, bank statement, or official document)
   - Submit facial photo for biometric verification (optional but recommended)

3. **Cardano Wallet Verification**
   - Connect your Cardano wallet
   - Sign verification message to prove ownership
   - Wallet address is permanently linked to your identity

4. **Review & Approval**
   - KYC documents are reviewed by our automated system and human verifiers
   - Verification typically takes 24-48 hours
   - You'll receive email notification of approval

#### **Step 3: Identity NFT Creation**

**Once KYC is approved:**
1. System automatically creates your identity NFT on Cardano blockchain
2. NFT contains your verified information and unique identifier
3. Initial reputation score: 0 NIMO tokens
4. Identity is permanently stored on Cardano with MeTTa metadata

**Complete Your Profile:**
1. **Access Your Dashboard** - After KYC approval, you'll have full access to your dashboard
2. **Add Profile Details** - Complete your bio, skills, and expertise areas
3. **Upload Profile Picture** - Store on IPFS for decentralized hosting
4. **Link Additional Information** - Connect social profiles and professional certifications
5. **Set Preferences** - Configure location, contact preferences, and notification settings

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
         Policy ID: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
         Asset Name: NIMO
```
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

**NIMO tokens are native Cardano tokens** that represent your reputation on the blockchain:

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
1. **Connect Wallet** and ensure you have ADA for transaction fees
2. **Browse Active Bonds** by category:
   - 🌍 Climate action and environment
   - 📚 Education and skill development  
   - 💼 Economic empowerment and entrepreneurship
   - 🏥 Health and community welfare
   - 🏗️ Infrastructure and technology

3. **Invest in Projects** (any amount):
   - Review project details and milestones
   - Send ADA directly to smart contract
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
Target: 50 ADA | Current: 23 ADA | 12 investors

Milestones:
✅ Curriculum developed (5 ADA released)
✅ First 50 students enrolled (10 ADA released)
🔄 100 students completed training (15 ADA pending)
⏳ Job placement for 80% graduates (20 ADA pending)

Your Investment: 2 ADA
Expected Return: 2.4 ADA (20% impact bonus)
```

### For Local Project Creators

**Create Impact Bonds:**
1. **Identity Required**: Must have Nimo identity NFT with reputation score >50
2. **Project Proposal**:
   - Title and detailed description
   - Target funding amount in ADA
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
- Yoroi (recommended for Cardano)
- Daedalus (full node wallet)
- Eternl (light wallet with advanced features)
- Nami (browser extension)
- Flint (mobile wallet)
- Hardware wallets (Ledger with Cardano app)

**Transaction Types:**
- Identity creation (native token minting)
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
- Ensure you're on the correct Cardano network (Mainnet or Testnet)
- Try refreshing the page and reconnecting
- Clear browser cache and cookies
- Update your Cardano wallet to latest version

**Transaction Failures:**
- Check you have enough ADA for transaction fees
- Increase fee if transaction is complex
- Try again during lower network congestion
- Verify contract addresses are correct

**Missing Tokens/NFTs:**
- Add NIMO token contract to wallet manually
- Import NFT using policy ID and asset name
- Check transaction was confirmed on Cardano explorer
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

---

*Last Updated: September 2, 2025 - User Guide Sync Complete*  
*Platform: Nimo - Decentralized Youth Identity & Proof of Contribution Network*  
*Status: 92% Complete - Production Ready with Full Cardano Integration*  
*Security Alert: 31 vulnerabilities identified - see SECURITY_AUDIT_REPORT.md*  
*For technical support, contact the development team.*