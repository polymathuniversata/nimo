# Nimo Platform - Production Deployment Guide

## 🚀 **PRODUCTION DEPLOYMENT READY**

This guide provides comprehensive instructions for deploying Nimo Platform smart contracts to Cardano networks (Preview, Preprod, and Mainnet) within a **3-week timeline**.

## 📋 **Pre-Deployment Checklist**

### ✅ **Prerequisites**
- [ ] Aiken v1.0.28-alpha installed
- [ ] PyCardano and Blockfrost Python libraries installed
- [ ] Blockfrost API keys for target networks
- [ ] Sufficient ADA for deployment (estimated costs below)
- [ ] Secure key management setup
- [ ] Network access and stable internet connection

### ✅ **Security Requirements**
- [ ] Hardware wallet for mainnet deployments
- [ ] Multi-signature setup for critical operations
- [ ] Code audit completed (see security section)
- [ ] Test coverage >90% achieved
- [ ] Disaster recovery procedures documented

### ✅ **Network Configuration**
- [ ] Preview testnet: Development and initial testing
- [ ] Preprod testnet: Pre-production validation
- [ ] Mainnet: Production deployment

## 💰 **Deployment Cost Estimates**

### Preview Testnet (Free Test ADA)
- **Contribution Validator**: ~5 ADA
- **Identity Registry**: ~4 ADA  
- **MeTTa Bridge**: ~6 ADA
- **NIMO Token Policy**: ~2 ADA
- **Transaction Fees**: ~3 ADA
- **Total Estimated**: ~20 ADA

### Preprod Testnet (Free Test ADA)
- **Same as Preview**: ~20 ADA

### Mainnet (Real ADA Required)
- **Same contracts**: ~20 ADA (~$8-12 at current rates)
- **Additional buffer**: 10 ADA recommended
- **Total Recommended**: 30 ADA

## 🏗️ **Deployment Process**

### Phase 1: Environment Setup (Days 1-2)

#### 1.1 Install Dependencies
```bash
# Install Aiken
curl -sSfL https://install.aiken-lang.org | sh

# Verify installation
aiken --version

# Install Python dependencies
cd contracts/cardano
pip install -r requirements.txt
```

#### 1.2 Configure API Keys
```bash
# Set Blockfrost API keys (get from https://blockfrost.io)
export BLOCKFROST_PROJECT_ID_PREVIEW="preview_api_key_here"
export BLOCKFROST_PROJECT_ID_PREPROD="preprod_api_key_here"
export BLOCKFROST_PROJECT_ID_MAINNET="mainnet_api_key_here"

# Optional: Save to .env file
echo "BLOCKFROST_PROJECT_ID_PREVIEW=preview_api_key_here" >> .env
```

#### 1.3 Generate Deployer Keys
```bash
# The deployment script will generate keys automatically
# For production, use hardware wallets:

# Generate secure key (use hardware wallet for mainnet)
python -c "
from pycardano import PaymentSigningKey
key = PaymentSigningKey.generate()
print(f'Private Key: {key.to_primitive().hex()}')
print(f'Address: {Address(PaymentVerificationKey.from_signing_key(key).hash())}')
"
```

### Phase 2: Testing Deployment (Days 3-7)

#### 2.1 Preview Testnet Deployment
```bash
cd contracts/cardano

# Check balance
python deploy.py --network preview --check-balance

# Get test ADA if needed (use address from balance check)
# Visit: https://docs.cardano.org/cardano-testnets/tools/faucet

# Compile contracts
python deploy.py --network preview --compile-only

# Deploy all contracts
python deploy.py --network preview

# Verify deployment
python verify_deployment.py --network preview
```

#### 2.2 Integration Testing
```bash
# Test contract interactions
python test_integration.py --network preview

# Test MeTTa bridge functionality
python test_metta_integration.py --network preview

# Validate token minting and transfers
python test_token_operations.py --network preview
```

#### 2.3 Preprod Testnet Deployment
```bash
# Deploy to preprod for final validation
python deploy.py --network preprod

# Run full test suite
python -m pytest tests/ --network preprod

# Performance testing
python test_performance.py --network preprod
```

### Phase 3: Production Deployment (Days 8-14)

#### 3.1 Final Security Audit
```bash
# Run security audit tools
aiken check --all
aiken test --coverage

# Review all contract code
# Get external audit if required for mainnet

# Test disaster recovery procedures
python test_recovery.py --network preprod
```

#### 3.2 Mainnet Deployment
```bash
# IMPORTANT: Use hardware wallet for mainnet
# Set up hardware wallet signing

# Fund deployer address with sufficient ADA (30 ADA recommended)
# Verify balance
python deploy.py --network mainnet --check-balance

# Deploy with production configuration
python deploy.py --network mainnet

# Verify all contracts are deployed correctly
python verify_deployment.py --network mainnet

# Test basic functionality with small amounts
python test_mainnet_basic.py
```

### Phase 4: Production Integration (Days 15-21)

#### 4.1 Backend Integration
```bash
# Update backend environment variables
cd ../../backend

# Load deployment results
source ../contracts/cardano/deployment_env_mainnet.sh

# Update .env file with contract addresses
echo "NIMO_CONTRIBUTION_VALIDATOR_HASH=$NIMO_CONTRIBUTION_VALIDATOR_HASH" >> .env
echo "NIMO_IDENTITY_REGISTRY_HASH=$NIMO_IDENTITY_REGISTRY_HASH" >> .env
echo "NIMO_METTA_BRIDGE_HASH=$NIMO_METTA_BRIDGE_HASH" >> .env
echo "NIMO_NIMO_TOKEN_POLICY_HASH=$NIMO_NIMO_TOKEN_POLICY_HASH" >> .env

# Test backend integration
python test_cardano_integration.py
```

#### 4.2 Frontend Integration
```bash
cd ../frontend

# Update contract addresses in configuration
# Update environment variables for production

# Test Web3 wallet integration
npm test
```

#### 4.3 Go Live
```bash
# Start production services
cd ../backend
python run.py

# Start frontend
cd ../frontend  
npm run build
npm run preview  # or deploy to hosting
```

## 🛠️ **Deployment Commands Reference**

### Quick Deployment
```bash
# Deploy everything to preview testnet
python deploy.py --network preview

# Deploy specific contract
python deploy.py --network preview --contract contribution

# Check deployment status
python check_deployment_status.py --network preview
```

### Advanced Options
```bash
# Compile contracts only
python deploy.py --compile-only

# Deploy with custom configuration
python deploy.py --network mainnet --config custom_config.json

# Emergency contract update
python deploy.py --network mainnet --update-contract contribution

# Monitor deployment
tail -f deployment.log
```

## 🔒 **Security Best Practices**

### Key Management
- **Development**: Generated keys, stored securely
- **Testnet**: Dedicated testnet keys, not used for mainnet
- **Mainnet**: Hardware wallet mandatory, multi-sig recommended
- **Rotation**: Regular key rotation schedule
- **Backup**: Secure backup and recovery procedures

### Contract Security
- **Formal Verification**: All contracts formally verified
- **Audit**: External security audit completed
- **Testing**: >90% test coverage achieved
- **Monitoring**: Real-time monitoring and alerting
- **Emergency**: Emergency pause mechanisms implemented

### Infrastructure Security
- **Network**: Secure network connections, VPN if required
- **Servers**: Hardened deployment servers
- **Access Control**: Multi-factor authentication
- **Logging**: Comprehensive audit logging
- **Monitoring**: 24/7 monitoring and alerting

## 📊 **Monitoring and Maintenance**

### Real-Time Monitoring
```bash
# Monitor contract interactions
python monitor_contracts.py --network mainnet

# Check system health
python health_check.py --all

# Monitor token transfers
python monitor_tokens.py --policy-id $NIMO_TOKEN_POLICY_ID
```

### Regular Maintenance
- **Daily**: Health checks, balance monitoring
- **Weekly**: Performance analysis, usage statistics  
- **Monthly**: Security review, key rotation check
- **Quarterly**: Full system audit, disaster recovery test

## 🚨 **Emergency Procedures**

### Contract Issues
1. **Immediate**: Activate emergency pause if available
2. **Assess**: Determine scope and impact of issue
3. **Communicate**: Notify users and stakeholders
4. **Fix**: Deploy fix or workaround
5. **Resume**: Carefully resume operations

### Network Issues
1. **Monitor**: Check Cardano network status
2. **Fallback**: Use alternative Blockfrost endpoints
3. **Queue**: Queue transactions if network degraded
4. **Resume**: Process queued transactions when recovered

### Recovery Procedures
```bash
# Recover from backup
python recovery.py --network mainnet --backup-date 2025-01-15

# Verify recovery
python verify_recovery.py --network mainnet

# Resume operations
python resume_operations.py --network mainnet
```

## 📈 **Performance Optimization**

### Transaction Optimization
- **Batching**: Batch multiple operations
- **UTxO Management**: Optimize UTxO consolidation
- **Fee Estimation**: Dynamic fee estimation
- **Timing**: Deploy during low network usage

### Monitoring Performance
```bash
# Analyze transaction costs
python analyze_costs.py --network mainnet

# Monitor contract performance
python monitor_performance.py --contract-hash $NIMO_CONTRIBUTION_VALIDATOR_HASH

# Generate performance reports
python generate_report.py --type performance --network mainnet
```

## 📚 **Documentation and Support**

### Documentation Requirements
- [ ] Architecture documentation updated
- [ ] API documentation reflects contract integration
- [ ] User guides updated with new features
- [ ] Troubleshooting guides created
- [ ] Recovery procedures documented

### Support Infrastructure
- [ ] Monitoring dashboards configured
- [ ] Alert systems activated
- [ ] Support team trained
- [ ] Escalation procedures defined
- [ ] Communication channels established

## ✅ **Post-Deployment Validation**

### Functional Testing
```bash
# Test core user flows
python test_user_flows.py --network mainnet

# Validate MeTTa integration
python validate_metta.py --network mainnet

# Test token operations
python test_tokens.py --network mainnet
```

### Performance Validation
```bash
# Load testing
python load_test.py --network mainnet --concurrent-users 100

# Stress testing
python stress_test.py --network mainnet --duration 3600

# Monitoring validation
python validate_monitoring.py --network mainnet
```

## 🎯 **Success Criteria**

### Technical Criteria
- [ ] All smart contracts deployed successfully
- [ ] Backend integration working correctly
- [ ] Frontend Web3 integration functional
- [ ] MeTTa reasoning integration operational
- [ ] Token minting and transfers working
- [ ] Identity management system active

### Operational Criteria
- [ ] Monitoring and alerting active
- [ ] Performance meeting requirements
- [ ] Security measures implemented
- [ ] Documentation complete
- [ ] Support team ready
- [ ] Emergency procedures tested

### Business Criteria
- [ ] Platform accessible to users
- [ ] Core features functional
- [ ] Reputation system operational
- [ ] Autonomous agents working
- [ ] User onboarding smooth
- [ ] Community feedback positive

## 📞 **Support and Resources**

### Technical Support
- **Aiken Documentation**: https://aiken-lang.org/
- **Cardano Developers**: https://developers.cardano.org/
- **PyCardano Docs**: https://pycardano.readthedocs.io/
- **Blockfrost API**: https://docs.blockfrost.io/

### Community Resources
- **Cardano Discord**: https://discord.gg/cardano
- **Aiken Community**: https://discord.gg/Vc3x8N9nz2
- **Developer Forums**: https://forum.cardano.org/

### Emergency Contacts
- **Platform Admin**: [Add contact info]
- **Security Team**: [Add contact info]  
- **Infrastructure**: [Add contact info]
- **On-call Engineer**: [Add contact info]

---

## 🏁 **Deployment Timeline Summary**

| Phase | Duration | Activities | Deliverables |
|-------|----------|------------|--------------|
| **Week 1** | Days 1-7 | Environment setup, Preview testnet deployment, Integration testing | Contracts deployed on Preview, Tests passing |
| **Week 2** | Days 8-14 | Preprod deployment, Security audit, Mainnet preparation | Preprod validation, Security audit complete |
| **Week 3** | Days 15-21 | Mainnet deployment, Production integration, Go live | Production system operational |

**🎉 TOTAL TIMELINE: 3 WEEKS TO PRODUCTION**

This guide ensures a systematic, secure, and successful deployment of the Nimo Platform smart contracts to Cardano within the specified 3-week timeline.