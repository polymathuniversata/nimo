# Nimo Cardano Smart Contracts

This directory contains Plutus smart contracts for the Nimo Platform on Cardano blockchain.

## Overview

The Nimo Platform has been migrated from Ethereum/Base/Polygon to Cardano for:
- Lower transaction fees
- Better sustainability (Proof-of-Stake)
- Native multi-asset support
- Built-in metadata standards

## Smart Contracts

### 1. NIMO Token (Native Asset)
- **Type**: Cardano Native Token
- **Policy**: Will be generated during deployment
- **Purpose**: Reputation tokens for verified contributions
- **Features**: 
  - Mintable by platform validators
  - Transferable between users
  - Metadata support for contribution proofs

### 2. Contribution Validator (Plutus)
- **File**: `contribution_validator.plutus`
- **Purpose**: Validates contribution submissions and MeTTa proofs
- **Features**:
  - Validates MeTTa reasoning proofs
  - Locks ADA/tokens until verification
  - Releases rewards based on verification results

### 3. Identity Registry (Plutus)
- **File**: `identity_registry.plutus`
- **Purpose**: Manages user identities and reputation scores
- **Features**:
  - Links Cardano addresses to user profiles
  - Tracks reputation scores on-chain
  - Supports DID integration

## Development Setup

### Prerequisites

1. **Cardano Node & CLI**
   ```bash
   # Install Cardano node and CLI tools
   # Follow: https://developers.cardano.org/docs/get-started/installing-cardano-node
   ```

2. **Plutus Development Environment**
   ```bash
   # Install Nix (required for Plutus)
   curl -L https://nixos.org/nix/install | sh
   
   # Clone Plutus repository
   git clone https://github.com/input-output-hk/plutus-apps.git
   cd plutus-apps
   nix-shell
   ```

3. **Python Environment (for PyCardano)**
   ```bash
   pip install pycardano
   pip install blockfrost-python
   ```

### Building Contracts

1. **Compile Plutus Scripts**
   ```bash
   # In Plutus development environment
   cabal run plutus-compile contribution_validator.hs
   cabal run plutus-compile identity_registry.hs
   ```

2. **Generate Policy Scripts**
   ```bash
   # Generate NIMO token policy
   cardano-cli transaction policyid --script-file nimo_token_policy.json
   ```

### Testing

1. **Local Testnet**
   ```bash
   # Start local Cardano testnet
   cardano-testnet --testnet-magic 42
   ```

2. **Preview Testnet**
   ```bash
   # Use Cardano Preview testnet
   export CARDANO_NODE_SOCKET_PATH="path/to/preview/node.socket"
   ```

3. **Get Test ADA**
   - Visit: https://docs.cardano.org/cardano-testnets/tools/faucet
   - Enter your testnet address
   - Receive test ADA within minutes

## Deployment

### Testnet Deployment

1. **Set Environment**
   ```bash
   export BLOCKFROST_PROJECT_ID="your_preview_project_id"
   export CARDANO_NETWORK="preview"
   ```

2. **Deploy Token Policy**
   ```bash
   python deploy_nimo_token.py
   ```

3. **Deploy Validators**
   ```bash
   python deploy_validators.py
   ```

### Mainnet Deployment

1. **Security Audit**
   - Complete security audit of all Plutus scripts
   - Verify policy scripts and minting logic
   - Test extensively on testnet

2. **Deploy Process**
   ```bash
   export BLOCKFROST_PROJECT_ID="your_mainnet_project_id"
   export CARDANO_NETWORK="mainnet"
   python deploy_mainnet.py
   ```

## Integration with Backend

The Nimo backend service integrates with these contracts through:

1. **CardanoService** (`backend/services/cardano_service.py`)
   - Handles ADA transfers
   - Manages NIMO token minting/transfers
   - Interacts with Plutus validators

2. **API Endpoints** (`backend/routes/cardano.py`)
   - `/api/cardano/status` - Service status
   - `/api/cardano/balance/{address}` - Check balances
   - `/api/cardano/mint-nimo` - Mint NIMO tokens
   - `/api/cardano/send-ada` - Send ADA rewards

## Security Considerations

1. **Plutus Script Security**
   - All scripts should be formally verified
   - Use established patterns and libraries
   - Audit for common vulnerabilities

2. **Token Policy**
   - Implement proper access controls
   - Prevent unauthorized minting
   - Include metadata validation

3. **Key Management**
   - Use hardware wallets for mainnet
   - Implement proper key rotation
   - Secure policy keys appropriately

## Resources

- [Cardano Developer Portal](https://developers.cardano.org/)
- [Plutus Documentation](https://plutus-pioneer-program.readthedocs.io/)
- [PyCardano Documentation](https://pycardano.readthedocs.io/)
- [Blockfrost API](https://docs.blockfrost.io/)
- [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnets/tools/faucet)