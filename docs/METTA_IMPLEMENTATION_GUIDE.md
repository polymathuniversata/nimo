# MeTTa Implementation Guide for Nimo

This guide provides detailed information about the MeTTa implementation for the Nimo platform, a Decentralized Youth Identity & Proof of Contribution Network with blockchain integration.

## Introduction to MeTTa

MeTTa (Meta Type Talk) is a symbolic programming language that combines logic programming with functional programming. It provides a powerful framework for representing knowledge, defining rules, and performing automated reasoning - making it ideal for the identity verification and autonomous token award systems in Nimo.

## Implementation Structure

The MeTTa implementation is structured as follows:

```
backend/
├── src/
│   ├── models/
│   │   ├── identity.metta       # Identity representation and operations
│   │   ├── contribution.metta   # Contribution tracking and verification
│   │   ├── token.metta          # Token economy implementation
│   │   └── diaspora_bonds.metta # Impact bond implementation
│   └── controllers/
│       ├── auto_award.metta     # Autonomous verification and awards
│       ├── nimo_core.metta      # Core controller and orchestration
│       └── cardano_operations.metta # Blockchain integration
├── utils/
│   └── utils.metta              # Utility functions
└── main.metta                   # Entry point with demonstration script
```

## Key Concepts

### Atoms and Relations

MeTTa uses atoms and relations to represent data and knowledge:

```metta
;; Identity representation
(= (Identity $id $username $created_at)
   (User $id $username $created_at))

;; Contribution representation
(= (Contribution $id $user_id $title $timestamp)
   (UserContribution $id $user_id $title $timestamp))
```

### Pattern Matching

Pattern matching is used extensively for querying and data retrieval:

```metta
;; Get user by ID
(= (get-user-by-id $id)
   (Identity $id $username $created_at))

;; Get verified contributions for a user
(= (get-verified-contributions $username)
   (let (($user_id (GetUserID $username))
         ($all_contributions (FindAll (Contribution $id $user_id $title $timestamp))))
     (filter $all_contributions IsVerifiedContribution)))
```

### External Functions

Many lower-level functions are marked with "External..." and would be implemented in the MeTTa runtime:

```metta
;; String operations
(= (StringStartsWith $str $prefix)
   (ExternalStringStartsWith $str $prefix))

;; List operations
(= (ListLength $list)
   (ExternalListLength $list))
```

## Detailed Module Overview

### 1. Identity System (`identity.metta`)

The identity module provides functionality for creating and managing user identities:

#### Core Identity Structure
```metta
(= (Identity $id $username $created_at)
   (User $id $username $created_at))
```

#### Identity Status
```metta
(= (IdentityStatus $id "unverified")
   (IsUnverified $id))
(= (IdentityStatus $id "verified")
   (IsVerified $id))
(= (IdentityStatus $id "trusted")
   (IsTrusted $id))
```

#### Blockchain Integration
```metta
(= (IdentityWallet $id $network $address)
   (HasWallet $id $network $address))

(= (WalletVerified $id $network $address)
   (IsWalletVerified $id $network $address))
```

#### Key Operations
- User creation: `define-user`
- Adding personal info: `add-personal-info`
- Adding skills: `add-skill`
- Adding blockchain addresses: `add-cardano-address`, `add-ethereum-address`
- Verification: `verify-identity`, `promote-to-trusted`

### 2. Contribution System (`contribution.metta`)

The contribution module handles recording, tracking, and verifying user contributions:

#### Core Contribution Structure
```metta
(= (Contribution $id $user_id $title $timestamp)
   (UserContribution $id $user_id $title $timestamp))
```

#### Verification Status
```metta
(= (ContributionStatus $id "unverified")
   (IsUnverified $id))
(= (ContributionStatus $id "verified")
   (IsVerified $id))
(= (ContributionStatus $id "rejected")
   (IsRejected $id))
```

#### Cryptographic Proofs
```metta
(= (ContributionProof $id $proof_hash $timestamp)
   (HasProof $id $proof_hash $timestamp))
```

#### Key Operations
- Adding contributions: `add-contribution`, `add-contribution-with-metadata`
- Adding metadata: `add-contribution-metadata`
- Verification: `verify-contribution`, `verify-specific-contribution`
- Proof generation: `generate-metta-proof`

### 3. Token System (`token.metta`)

The token module implements the economic system for rewarding contributions:

#### Token Types and Balances
```metta
(= (TokenType "NIMO") (PlatformToken))
(= (TokenType "ADA") (BlockchainNativeToken "Cardano"))

(= (TokenBalance $user_id $token_type $amount)
   (HasBalance $user_id $token_type $amount))
```

#### Transactions
```metta
(= (TokenTransaction $id $token_type $from $to $amount $reason $timestamp)
   (Transaction $id $token_type $from $to $amount $reason $timestamp))
```

#### Key Operations
- Balance initialization: `init-token-balance`, `init-nimo-balance`, `init-ada-balance`
- Transfers: `transfer-tokens`
- Minting: `mint-tokens`
- Burning: `burn-tokens`
- Auto-awards: `auto-award-nimo`, `auto-award-ada`

### 4. Diaspora Bond System (`diaspora_bonds.metta`)

The bond module enables the creation and management of impact bonds:

#### Bond Structure
```metta
(= (ImpactBond $id $creator_id $title $target_amount $created_at)
   (Bond $id $creator_id $title $target_amount $created_at))
```

#### Investments and Milestones
```metta
(= (BondInvestment $id $investor_id $amount $timestamp)
   (InvestedIn $id $investor_id $amount $timestamp))

(= (BondMilestone $bond_id $milestone_id $description $evidence $timestamp)
   (HasMilestone $bond_id $milestone_id $description $evidence $timestamp))
```

#### NFT Representation
```metta
(= (BondNFT $bond_id $nft_id $metadata)
   (RepresentedByNFT $bond_id $nft_id $metadata))
```

#### Key Operations
- Bond creation: `create-impact-bond`
- Cause linking: `link-bond-to-cause`
- Investment: `purchase-impact-bond`
- Milestone tracking: `record-bond-milestone`, `verify-bond-milestone`
- Completion checking: `check-bond-completion`

### 5. Autonomous Award System (`auto_award.metta`)

The autonomous award module provides AI-driven verification and rewards:

#### Agent Configuration
```metta
(= (AgentConfig "verification_threshold" 0.75)
   (ConfigValue "verification_threshold" 0.75))
(= (AgentConfig "min_verifications" 2)
   (ConfigValue "min_verifications" 2))
```

#### Verification Criteria
```metta
(= (VerificationCriterion $criterion_id $name $weight)
   (Criterion $criterion_id $name $weight))
```

#### Key Operations
- Auto-verification: `run-auto-verification`, `VerifyContributionAutonomously`
- Confidence calculation: `CalculateVerificationConfidence`
- Auto-awards: `CheckForAutoAward`
- Monitoring: `get-agent-daily-stats`, `get-recent-agent-activity`

### 6. Core Controller (`nimo_core.metta`)

The core controller orchestrates the interactions between different modules:

#### System Initialization
```metta
(= (initialize-system)
   (let ()
     ;; Initialize configuration
     (SystemConfig "version" "1.0.0")
     (SystemConfig "name" "Nimo Platform")
     (SystemConfig "initialized_at" (CurrentTimestamp))
     
     ;; Initialize subsystems
     (InitializeIdentitySystem)
     (InitializeContributionSystem)
     (InitializeTokenSystem)
     (InitializeBondSystem)
     (InitializeVerificationCriteria)
     
     ;; Log initialization
     (SystemLog "initialization" "system" "System initialized successfully" (CurrentTimestamp))
     true))
```

#### Orchestration Functions
```metta
(= (register-user $username $location)
   (let* (($user_id (define-user $username))
          ($timestamp (CurrentTimestamp)))
     (add-personal-info $username "location" $location)
     (init-nimo-balance $username 0)
     (SystemLog "registration" "identity_system" (ConcatString "User registered: " $username) $timestamp)
     $user_id))
```

#### Key Operations
- System initialization: `initialize-system`
- User registration: `register-user`
- Contribution processing: `process-contribution`
- Bond processing: `process-impact-bond`, `process-bond-investment`
- Token transfers: `process-token-transfer`
- Reporting: `get-system-status`, `get-recent-activities`, `get-top-contributors`
- Maintenance: `run-daily-maintenance`, `update-all-reputation-scores`

### 7. Cardano Operations (`cardano_operations.metta`)

The Cardano operations module provides blockchain integration:

#### Network Configuration
```metta
(= (CardanoNetwork "preview") (NetworkType "testnet"))
(= (CardanoNetwork "preprod") (NetworkType "testnet"))
(= (CardanoNetwork "mainnet") (NetworkType "mainnet"))
```

#### Wallet Management
```metta
(= (CardanoWallet $wallet_id $user_id $network $address $public_key $payment_key_hash $stake_key_hash $created_at)
   (Wallet $wallet_id $user_id $network $address $public_key $payment_key_hash $stake_key_hash $created_at))
```

#### Transaction Management
```metta
(= (CardanoTransaction $tx_id $network $inputs $outputs $fee $metadata $status $created_at $submitted_at $confirmed_at)
   (Transaction $tx_id $network $inputs $outputs $fee $metadata $status $created_at $submitted_at $confirmed_at))
```

#### Key Operations
- Wallet creation: `CreateWallet`
- Transaction creation: `CreateADATransaction`, `MintTransaction`
- Transaction submission: `SubmitTransaction`
- Transaction querying: `GetTransaction`, `CheckTransactionStatus`, `GetWalletTransactions`
- Stake pool operations: `RegisteredStakePool`, `GetStakePool`, `GetDelegationInfo`
- Token operations: `MintNIMOTokens`

## Using the MeTTa Implementation

### Integration with Flask API

The MeTTa implementation is designed to be integrated with a Flask API through a Python bridge:

```python
from services.metta_service import MeTTaService

# Initialize MeTTa service
metta = MeTTaService()

# Define a user
user_id = metta.execute_query("define-user", "Kwame")

# Add skills
metta.execute_query("add-skill", "Kwame", "Python")
metta.execute_query("add-skill", "Kwame", "JavaScript")

# Add contribution
contribution_id = metta.execute_query("add-contribution-with-metadata", 
                                     "Kwame", 
                                     "Open_Source_Project", 
                                     "Created a library for educational games")

# Verify contribution
metta.execute_query("verify-contribution", "Kwame", "KRNL_Org")

# Award tokens automatically
metta.execute_query("auto-award-nimo", "Kwame", "Open_Source_Project")
```

### Creating Custom Verification Rules

You can extend the autonomous verification system by adding custom rules:

```metta
;; Custom verification rule for educational contributions
(= (VerifyEducationalContribution $contribution_id)
   (let* (($metadata (CollectContributionMetadata $contribution_id))
          ($description (GetMetadataValue $metadata "description"))
          ($category (GetMetadataValue $metadata "category")))
     (and (Equal $category "education")
          (ContainsEducationalTerms $description))))

;; Add to verification pipeline
(= (CalculateVerificationConfidence $contribution_id)
   (let* (($metadata (CollectContributionMetadata $contribution_id))
          ($contribution_type (GetMetadataValue $metadata "type"))
          ($evidence_count (CountEvidenceItems $metadata))
          ($description_quality (AnalyzeDescriptionQuality $metadata))
          ($reputation_factor (GetContributorReputationFactor $contribution_id))
          ($criteria_score (EvaluateCriteriaScore $contribution_id $metadata))
          ($educational_bonus (if (VerifyEducationalContribution $contribution_id) 0.1 0.0))
          ;; Weight different factors
          ($confidence (+ (* 0.3 $description_quality)
                         (* 0.2 (min 1.0 (/ $evidence_count 3)))
                         (* 0.2 $reputation_factor)
                         (* 0.3 $criteria_score)
                         $educational_bonus)))
     (max 0.0 (min 1.0 $confidence))))
```

### Adding New Token Types

To add support for new token types:

```metta
;; Define new token type
(= (TokenType "ETH") (BlockchainNativeToken "Ethereum"))

;; Initialize balances
(= (init-eth-balance $username $amount)
   (let (($user_id (GetUserID $username)))
     (TokenBalance $user_id "ETH" $amount)))

;; Add ETH rewards
(= (auto-award-eth $username $contribution_title)
   (let* (($user_id (GetUserID $username))
          ($contribution_id (FindContributionID $user_id $contribution_title))
          ($verification_count (CountVerifications $contribution_id))
          ($confidence (CalculateConfidence $contribution_id))
          ($nimo_query (auto-award-nimo $username $contribution_title))
          ($nimo_amount (GetMintAmount $nimo_query))
          ($eth_amount (CalculateETHReward $nimo_amount $confidence))
          ($reason (ConcatString "ETH reward for " $contribution_title)))
     (if (> $verification_count 0)
         (mint-tokens $username "ETH" $eth_amount $reason)
         (Error "Cannot award ETH for unverified contribution"))))
```

## Testing the MeTTa Implementation

The MeTTa implementation can be tested through the main.metta demonstration script:

```bash
# Run the demonstration script (requires MeTTa runtime)
cd backend
hyperon-metta main.metta
```

## Extending the MeTTa Implementation

### Adding New Blockchain Networks

```metta
;; Define new blockchain network
(= (SolanaNetwork "devnet") (NetworkType "testnet"))
(= (SolanaNetwork "mainnet") (NetworkType "mainnet"))

;; Define Solana wallet integration
(= (SolanaWallet $wallet_id $user_id $network $address $public_key $created_at)
   (Wallet $wallet_id $user_id $network $address $public_key $created_at))

;; Add wallet validation
(= (ValidSolanaAddress $address)
   (and (= (StringLength $address) 44)
        (not (StartsWith $address "0x"))))
```

### Customizing the Token Economic Model

```metta
;; Define new token award rules
(= (TokenAwardRule "technical" 100)
   (AwardRule "technical" 100))
(= (TokenAwardRule "community" 75)
   (AwardRule "community" 75))
(= (TokenAwardRule "education" 80)
   (AwardRule "education" 80))
(= (TokenAwardRule "environmental" 90)
   (AwardRule "environmental" 90))

;; Add time-based bonuses
(= (CalculateTimeBonus $creation_timestamp)
   (let* (($current_time (CurrentTimestamp))
          ($age_days (/ (- $current_time $creation_timestamp) 86400))
          ($bonus (if (< $age_days 7)
                    (* (- 7 $age_days) 5)
                    0)))
     $bonus))
```

### Adding Advanced Analytics

```metta
;; Calculate user engagement score
(= (CalculateUserEngagementScore $username)
   (let* (($user_id (GetUserID $username))
          ($contribution_count (CountUserContributions $user_id))
          ($verification_count (CountUserVerifications $user_id))
          ($investment_count (CountUserInvestments $user_id))
          ($milestone_count (CountUserMilestones $user_id))
          ($engagement_score (+ (* $contribution_count 5)
                               (* $verification_count 3)
                               (* $investment_count 2)
                               (* $milestone_count 1))))
     $engagement_score))

;; Predict future contribution probability
(= (PredictContributionProbability $username)
   (let* (($engagement_score (CalculateUserEngagementScore $username))
          ($recent_activity (GetRecentActivityCount $username 30))
          ($reputation_score (GetUserReputation $username))
          ($probability (min 1.0 (/ (+ $engagement_score 
                                      (* $recent_activity 10)
                                      (* $reputation_score 0.5))
                                   200))))
     $probability))
```

## Performance Considerations

1. **Query Optimization**: Use indices and specific queries to avoid full database scans
2. **Caching**: Cache common queries and verification results
3. **Batch Processing**: Use batch processing for token awards and verification
4. **External Function Implementation**: Implement external functions efficiently

## Security Considerations

1. **Input Validation**: Validate all inputs before processing
2. **Transaction Safety**: Ensure blockchain transactions are safe and secure
3. **Access Control**: Implement proper access control for sensitive operations
4. **Key Management**: Securely manage blockchain keys and credentials

## Conclusion

The MeTTa implementation provides a flexible, extensible foundation for the Nimo platform's decentralized identity and proof of contribution system. By combining logical rules, pattern matching, and blockchain integration, it enables autonomous verification, token awards, and impact bond management in a secure, transparent manner.

For practical examples of using this implementation, refer to the `main.metta` file which contains a comprehensive demonstration script.

## Additional Resources

- [MeTTa Documentation](https://metta.org/docs)
- [Hyperon GitHub Repository](https://github.com/trueagi-io/hyperon-experimental)
- [Cardano Developer Portal](https://developers.cardano.org/)
- [Nimo Project Documentation](../docs/README.md)