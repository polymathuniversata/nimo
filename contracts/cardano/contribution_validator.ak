// Nimo Platform - Contribution Validator Smart Contract
// Written in Aiken for Cardano blockchain
// This validator manages contribution verification and reward distribution

use aiken/dict
use aiken/hash.{Blake2b_224, Hash}
use aiken/list
use aiken/transaction.{ScriptContext, Transaction, InlineDatum, OutputReference, Input}
use aiken/transaction/credential.{VerificationKey}
use aiken/transaction/value.{PolicyId, AssetName, Value}
use aiken/bytearray

// Data types for contribution validation
pub type ContributionDatum {
  // Contributor's public key hash
  contributor: Hash<Blake2b_224, VerificationKey>,
  
  // Contribution details
  contribution_type: ByteArray,  // "coding", "community", "research", etc.
  description: ByteArray,
  evidence_hash: ByteArray,      // IPFS hash of evidence
  
  // MeTTa reasoning proof
  metta_proof: ByteArray,        // Hash of MeTTa reasoning result
  metta_confidence: Int,         // Confidence score (0-100)
  
  // Verification status
  verified: Bool,
  verifier: Hash<Blake2b_224, VerificationKey>,
  
  // Reward calculation
  base_reward: Int,              // Base NIMO token amount
  confidence_multiplier: Int,    // Applied based on MeTTa confidence
  final_reward: Int,             // Final calculated reward
  
  // Timestamps
  submitted_at: Int,
  verified_at: Int,
  
  // Status tracking
  is_active: Bool,
  requires_manual_review: Bool,
}

// Redeemer actions for the validator
pub type ContributionRedeemer {
  SubmitContribution
  VerifyContribution
  ClaimReward
  UpdateMettaProof
  AdminAction { action: ByteArray }
}

// Configuration for the platform (stored as parameters)
pub type PlatformConfig {
  nimo_token_policy: PolicyId,
  nimo_token_name: AssetName,
  
  // Authorized addresses
  platform_admin: Hash<Blake2b_224, VerificationKey>,
  metta_agent: Hash<Blake2b_224, VerificationKey>,
  verifier_pool: List<Hash<Blake2b_224, VerificationKey>>,
  
  // Reward parameters
  min_confidence_for_auto_reward: Int,  // Minimum confidence for automatic reward
  max_reward_amount: Int,               // Maximum NIMO tokens per contribution
  min_reward_amount: Int,               // Minimum NIMO tokens per contribution
  
  // Platform fees
  platform_fee_percentage: Int,        // Platform fee (0-100)
  verifier_reward_percentage: Int,      // Reward for verifiers (0-100)
}

// Main validator function
validator(config: PlatformConfig) {
  fn contribution_validator(
    datum: ContributionDatum, 
    redeemer: ContributionRedeemer, 
    context: ScriptContext
  ) -> Bool {
    
    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction
    
    when redeemer is {
      
      // Submit a new contribution for verification
      SubmitContribution -> {
        // Validate contribution submission
        validate_contribution_submission(datum, transaction, config)
      }
      
      // Verify a contribution and calculate rewards
      VerifyContribution -> {
        // Only authorized verifiers can verify contributions
        let is_authorized_verifier = 
          list.any(config.verifier_pool, fn(verifier) { 
            list.has(extra_signatories, verifier) 
          }) ||
          list.has(extra_signatories, config.metta_agent) ||
          list.has(extra_signatories, config.platform_admin)
        
        is_authorized_verifier && validate_contribution_verification(datum, transaction, config)
      }
      
      // Claim reward tokens after verification
      ClaimReward -> {
        // Contributor can claim their reward
        let contributor_signed = list.has(extra_signatories, datum.contributor)
        let reward_ready = datum.verified && datum.final_reward > 0
        
        contributor_signed && reward_ready && validate_reward_claim(datum, transaction, config)
      }
      
      // Update MeTTa proof for a contribution
      UpdateMettaProof -> {
        // Only MeTTa agents can update proof
        let metta_agent_signed = list.has(extra_signatories, config.metta_agent)
        
        metta_agent_signed && validate_metta_proof_update(datum, transaction, config)
      }
      
      // Administrative actions
      AdminAction { action } -> {
        // Only platform admin can perform admin actions
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        admin_signed && validate_admin_action(action, datum, transaction, config)
      }
    }
  }
}

// Validate contribution submission
fn validate_contribution_submission(
  datum: ContributionDatum, 
  transaction: Transaction, 
  config: PlatformConfig
) -> Bool {
  
  // Check that contributor signed the transaction
  let contributor_signed = list.has(transaction.extra_signatories, datum.contributor)
  
  // Validate contribution data
  let valid_contribution_type = bytearray.length(datum.contribution_type) > 0
  let valid_description = bytearray.length(datum.description) > 0
  let valid_evidence = bytearray.length(datum.evidence_hash) > 0
  
  // Check initial state
  let proper_initial_state = 
    datum.verified == False &&
    datum.final_reward == 0 &&
    datum.submitted_at > 0 &&
    datum.is_active == True
  
  contributor_signed && 
  valid_contribution_type && 
  valid_description && 
  valid_evidence && 
  proper_initial_state
}

// Validate contribution verification
fn validate_contribution_verification(
  datum: ContributionDatum, 
  transaction: Transaction, 
  config: PlatformConfig
) -> Bool {
  
  // Check MeTTa confidence and calculate reward
  let confidence_valid = datum.metta_confidence >= 0 && datum.metta_confidence <= 100
  let should_auto_reward = datum.metta_confidence >= config.min_confidence_for_auto_reward
  
  // Calculate final reward based on confidence
  let calculated_reward = calculate_confidence_based_reward(
    datum.base_reward, 
    datum.metta_confidence, 
    config
  )
  
  // Validate reward calculation
  let reward_calculation_correct = datum.final_reward == calculated_reward
  let reward_within_limits = 
    datum.final_reward >= config.min_reward_amount && 
    datum.final_reward <= config.max_reward_amount
  
  // Check verification requirements
  let verification_requirements = 
    datum.verified == True &&
    datum.verified_at > datum.submitted_at &&
    bytearray.length(datum.metta_proof) > 0
  
  confidence_valid && 
  reward_calculation_correct && 
  reward_within_limits && 
  verification_requirements &&
  (should_auto_reward || !datum.requires_manual_review)
}

// Validate reward claim
fn validate_reward_claim(
  datum: ContributionDatum, 
  transaction: Transaction, 
  config: PlatformConfig
) -> Bool {
  
  // Find the output that should contain the reward tokens
  let reward_outputs = list.filter(transaction.outputs, fn(output) {
    let output_value = output.value
    let nimo_amount = value.quantity_of(output_value, config.nimo_token_policy, config.nimo_token_name)
    nimo_amount >= datum.final_reward
  })
  
  // Validate that reward is being sent to contributor
  let reward_to_contributor = list.any(reward_outputs, fn(output) {
    when output.address.payment_credential is {
      VerificationKey(pkh) -> pkh == datum.contributor
      _ -> False
    }
  })
  
  // Check that contribution is marked as claimed/inactive
  let contribution_processed = !datum.is_active
  
  list.length(reward_outputs) > 0 && 
  reward_to_contributor && 
  contribution_processed
}

// Validate MeTTa proof update
fn validate_metta_proof_update(
  datum: ContributionDatum, 
  transaction: Transaction, 
  config: PlatformConfig
) -> Bool {
  
  // Ensure MeTTa proof is being updated
  let proof_updated = bytearray.length(datum.metta_proof) > 0
  let confidence_updated = datum.metta_confidence > 0
  
  // Check timing constraints
  let update_timing_valid = datum.verified_at > datum.submitted_at
  
  proof_updated && confidence_updated && update_timing_valid
}

// Validate administrative actions
fn validate_admin_action(
  action: ByteArray, 
  datum: ContributionDatum, 
  transaction: Transaction, 
  config: PlatformConfig
) -> Bool {
  
  // Define allowed admin actions
  let valid_actions = [
    "pause_contribution",
    "resume_contribution", 
    "force_verification",
    "update_config",
    "emergency_claim"
  ]
  
  list.any(valid_actions, fn(valid_action) { 
    action == valid_action 
  })
}

// Calculate reward based on MeTTa confidence score
fn calculate_confidence_based_reward(
  base_reward: Int, 
  confidence: Int, 
  config: PlatformConfig
) -> Int {
  
  // Apply confidence multiplier (50% to 150% of base reward)
  let confidence_multiplier = 50 + confidence  // 50-150% range
  let adjusted_reward = (base_reward * confidence_multiplier) / 100
  
  // Apply platform fee
  let fee = (adjusted_reward * config.platform_fee_percentage) / 100
  let final_reward = adjusted_reward - fee
  
  // Ensure within limits
  if final_reward < config.min_reward_amount then
    config.min_reward_amount
  else if final_reward > config.max_reward_amount then
    config.max_reward_amount
  else
    final_reward
}

// Test function to validate the contract logic
test contribution_flow_test() {
  let test_config = PlatformConfig {
    nimo_token_policy: #"abcd1234",
    nimo_token_name: #"4e494d4f",  // "NIMO" in hex
    platform_admin: #"admin123",
    metta_agent: #"metta456", 
    verifier_pool: [#"verifier1", #"verifier2"],
    min_confidence_for_auto_reward: 70,
    max_reward_amount: 1000,
    min_reward_amount: 10,
    platform_fee_percentage: 5,
    verifier_reward_percentage: 2,
  }
  
  let test_datum = ContributionDatum {
    contributor: #"contributor123",
    contribution_type: "coding",
    description: "Built DApp for community",
    evidence_hash: "ipfs_hash_123",
    metta_proof: "metta_reasoning_proof",
    metta_confidence: 85,
    verified: True,
    verifier: #"verifier1",
    base_reward: 100,
    confidence_multiplier: 135,  // 85% confidence = 135% multiplier
    final_reward: 128,  // (100 * 135 / 100) - 5% fee = 128
    submitted_at: 1672531200,
    verified_at: 1672534800,
    is_active: True,
    requires_manual_review: False,
  }
  
  // Test reward calculation
  let calculated = calculate_confidence_based_reward(100, 85, test_config)
  calculated == 128
}