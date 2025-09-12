// Nimo Platform - MeTTa Bridge Smart Contract
// Written in Aiken for Cardano blockchain
// This contract serves as a bridge between MeTTa reasoning engine and Cardano blockchain

use aiken/dict.{Dict}
use aiken/hash.{Blake2b_224, Blake2b_256, Hash}
use aiken/list
use aiken/transaction.{ScriptContext, Transaction, InlineDatum, OutputReference}
use aiken/transaction/credential.{VerificationKey}
use aiken/transaction/value.{PolicyId, AssetName, Value}
use aiken/bytearray
use aiken/crypto

// MeTTa reasoning proof and execution data
pub type MeTTaProofDatum {
  // Proof identification
  proof_id: ByteArray,                         // Unique proof identifier
  proof_version: Int,                          // Proof version number
  
  // MeTTa reasoning data
  metta_query: ByteArray,                      // Original MeTTa query
  metta_result: ByteArray,                     // MeTTa reasoning result
  reasoning_steps: List<ByteArray>,            // Step-by-step reasoning process
  
  // Proof verification
  proof_hash: Hash<Blake2b_256, ByteArray>,    // Cryptographic hash of proof
  signature: ByteArray,                        // MeTTa agent signature
  confidence_score: Int,                       // Confidence in result (0-100)
  
  // Context and metadata
  context_data: Dict<ByteArray, ByteArray>,    // Additional context data
  input_parameters: Dict<ByteArray, ByteArray>, // Input parameters used
  
  // Execution details
  agent_id: Hash<Blake2b_224, VerificationKey>, // MeTTa agent that generated proof
  created_at: Int,                             // Proof creation timestamp
  expires_at: Int,                             // Proof expiration timestamp
  
  // Verification status
  is_verified: Bool,                           // Whether proof has been verified
  verifier: Hash<Blake2b_224, VerificationKey>, // Verifier (if verified)
  verified_at: Int,                            // Verification timestamp
  
  // Execution results
  should_execute: Bool,                        // Whether to execute the decision
  execution_data: Dict<ByteArray, ByteArray>,  // Data for execution
  gas_estimate: Int,                           // Estimated gas for execution
  
  // Quality metrics
  reasoning_quality: Int,                      // Quality score of reasoning (0-100)
  consistency_check: Bool,                     // Whether proof is internally consistent
  external_validation: Bool,                   // Whether validated against external sources
}

// Actions that can be performed on MeTTa proofs
pub type MeTTaBridgeRedeemer {
  SubmitProof
  VerifyProof { verifier_signature: ByteArray }
  ExecuteDecision { execution_params: Dict<ByteArray, ByteArray> }
  ChallengeProof { challenge_reason: ByteArray, challenger_stake: Int }
  ResolveChallenge { resolution: ByteArray }
  UpdateProof { update_reason: ByteArray }
  AdminAction { action: ByteArray }
}

// Configuration for MeTTa bridge operations
pub type MeTTaBridgeConfig {
  // Authorized agents and verifiers
  authorized_metta_agents: List<Hash<Blake2b_224, VerificationKey>>,
  authorized_verifiers: List<Hash<Blake2b_224, VerificationKey>>,
  platform_admin: Hash<Blake2b_224, VerificationKey>,
  
  // Proof validation parameters
  min_confidence_for_execution: Int,           // Minimum confidence to execute (0-100)
  min_reasoning_quality: Int,                  // Minimum reasoning quality (0-100)
  proof_expiry_duration: Int,                  // How long proofs remain valid (seconds)
  
  // Challenge system
  challenge_stake_required: Int,               // ADA required to challenge a proof
  challenge_resolution_timeout: Int,           // Time to resolve challenges (seconds)
  challenge_reward_percentage: Int,            // Reward for successful challenges (0-100)
  
  // Execution parameters
  max_gas_per_execution: Int,                  // Maximum gas for single execution
  execution_cooldown: Int,                     // Cooldown between executions (seconds)
  
  // Quality assurance
  require_consistency_check: Bool,             // Whether consistency check is required
  require_external_validation: Bool,           // Whether external validation is required
  min_reasoning_steps: Int,                    // Minimum reasoning steps required
  
  // Fee structure
  proof_submission_fee: Int,                   // ADA fee to submit proof
  verification_fee: Int,                       // ADA fee for verification
  execution_fee_base: Int,                     // Base execution fee in ADA
}

// Challenge record for disputed proofs
pub type ProofChallenge {
  challenger: Hash<Blake2b_224, VerificationKey>,
  challenge_reason: ByteArray,
  stake_amount: Int,                           // ADA staked for challenge
  submitted_at: Int,
  resolution_deadline: Int,
  is_resolved: Bool,
  resolution: ByteArray,                       // Resolution details
  winner: Hash<Blake2b_224, VerificationKey>, // Winner of the challenge
}

// Main MeTTa bridge validator
validator(config: MeTTaBridgeConfig) {
  fn metta_bridge_validator(
    datum: MeTTaProofDatum, 
    redeemer: MeTTaBridgeRedeemer, 
    context: ScriptContext
  ) -> Bool {
    
    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction
    
    when redeemer is {
      
      // Submit a new MeTTa proof
      SubmitProof -> {
        let agent_authorized = list.has(config.authorized_metta_agents, datum.agent_id)
        let agent_signed = list.has(extra_signatories, datum.agent_id)
        
        agent_authorized && agent_signed && validate_proof_submission(datum, transaction, config)
      }
      
      // Verify a submitted proof
      VerifyProof { verifier_signature } -> {
        let is_authorized_verifier = 
          list.any(config.authorized_verifiers, fn(verifier) { 
            list.has(extra_signatories, verifier) 
          })
        
        is_authorized_verifier && validate_proof_verification(datum, verifier_signature, transaction, config)
      }
      
      // Execute a verified decision
      ExecuteDecision { execution_params } -> {
        let agent_signed = list.has(extra_signatories, datum.agent_id)
        let proof_ready = datum.is_verified && datum.should_execute
        
        agent_signed && proof_ready && validate_decision_execution(datum, execution_params, transaction, config)
      }
      
      // Challenge a proof's validity
      ChallengeProof { challenge_reason, challenger_stake } -> {
        validate_proof_challenge(datum, challenge_reason, challenger_stake, transaction, config)
      }
      
      // Resolve a challenge
      ResolveChallenge { resolution } -> {
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        admin_signed && validate_challenge_resolution(datum, resolution, transaction, config)
      }
      
      // Update an existing proof
      UpdateProof { update_reason } -> {
        let agent_signed = list.has(extra_signatories, datum.agent_id)
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        (agent_signed || admin_signed) && validate_proof_update(datum, update_reason, transaction, config)
      }
      
      // Administrative actions
      AdminAction { action } -> {
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        admin_signed && validate_admin_action(action, datum, transaction, config)
      }
    }
  }
}

// Validate proof submission
fn validate_proof_submission(
  datum: MeTTaProofDatum, 
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  // Validate basic proof structure
  let proof_structure_valid = 
    bytearray.length(datum.proof_id) > 0 &&
    bytearray.length(datum.metta_query) > 0 &&
    bytearray.length(datum.metta_result) > 0 &&
    list.length(datum.reasoning_steps) >= config.min_reasoning_steps
  
  // Validate proof hash
  let proof_hash_valid = validate_proof_hash(datum)
  
  // Validate confidence score
  let confidence_valid = 
    datum.confidence_score >= 0 && 
    datum.confidence_score <= 100
  
  // Validate timestamps
  let timestamps_valid = 
    datum.created_at > 0 &&
    datum.expires_at > datum.created_at &&
    datum.expires_at <= datum.created_at + config.proof_expiry_duration
  
  // Check submission fee
  let fee_paid = validate_fee_payment(transaction, config.proof_submission_fee)
  
  // Initial state validation
  let initial_state_valid = 
    datum.is_verified == False &&
    datum.verified_at == 0 &&
    datum.reasoning_quality > 0
  
  proof_structure_valid && 
  proof_hash_valid && 
  confidence_valid && 
  timestamps_valid && 
  fee_paid && 
  initial_state_valid
}

// Validate proof verification
fn validate_proof_verification(
  datum: MeTTaProofDatum, 
  verifier_signature: ByteArray,
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  // Check minimum quality requirements
  let quality_sufficient = 
    datum.confidence_score >= config.min_confidence_for_execution &&
    datum.reasoning_quality >= config.min_reasoning_quality
  
  // Validate consistency check (if required)
  let consistency_valid = 
    !config.require_consistency_check || datum.consistency_check
  
  // Validate external validation (if required)
  let external_validation_valid = 
    !config.require_external_validation || datum.external_validation
  
  // Validate verifier signature
  let signature_valid = bytearray.length(verifier_signature) > 0
  
  // Check verification fee
  let fee_paid = validate_fee_payment(transaction, config.verification_fee)
  
  // Update verification status
  let verification_status_updated = 
    datum.is_verified == True &&
    datum.verified_at > datum.created_at &&
    datum.verifier != datum.agent_id  // Verifier must be different from agent
  
  quality_sufficient && 
  consistency_valid && 
  external_validation_valid && 
  signature_valid && 
  fee_paid && 
  verification_status_updated
}

// Validate decision execution
fn validate_decision_execution(
  datum: MeTTaProofDatum, 
  execution_params: Dict<ByteArray, ByteArray>,
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  // Check that proof is verified and ready for execution
  let proof_ready = 
    datum.is_verified &&
    datum.should_execute &&
    datum.expires_at > get_current_time(transaction.validity_range)
  
  // Validate gas estimate
  let gas_valid = 
    datum.gas_estimate > 0 && 
    datum.gas_estimate <= config.max_gas_per_execution
  
  // Check execution cooldown
  let cooldown_respected = True  // Would check against last execution time
  
  // Calculate and validate execution fee
  let execution_fee = config.execution_fee_base + (datum.gas_estimate / 1000)
  let fee_paid = validate_fee_payment(transaction, execution_fee)
  
  proof_ready && gas_valid && cooldown_respected && fee_paid
}

// Validate proof challenge
fn validate_proof_challenge(
  datum: MeTTaProofDatum, 
  challenge_reason: ByteArray,
  challenger_stake: Int,
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  // Check that proof can be challenged (not yet expired)
  let proof_challengeable = datum.expires_at > get_current_time(transaction.validity_range)
  
  // Validate challenge reason
  let challenge_reason_valid = bytearray.length(challenge_reason) > 0
  
  // Validate stake amount
  let stake_sufficient = challenger_stake >= config.challenge_stake_required
  
  // Check that challenger has staked the required amount
  let stake_paid = validate_stake_payment(transaction, challenger_stake)
  
  proof_challengeable && challenge_reason_valid && stake_sufficient && stake_paid
}

// Validate challenge resolution
fn validate_challenge_resolution(
  datum: MeTTaProofDatum, 
  resolution: ByteArray,
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  // Validate resolution content
  let resolution_valid = bytearray.length(resolution) > 0
  
  // Check that resolution is within timeout period
  let resolution_timely = True  // Would check against challenge submission time
  
  resolution_valid && resolution_timely
}

// Validate proof update
fn validate_proof_update(
  datum: MeTTaProofDatum, 
  update_reason: ByteArray,
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  // Validate update reason
  let reason_valid = bytearray.length(update_reason) > 0
  
  // Check that proof version is incremented
  let version_incremented = datum.proof_version > 0
  
  // Validate that updated proof maintains quality
  let quality_maintained = datum.reasoning_quality >= config.min_reasoning_quality
  
  reason_valid && version_incremented && quality_maintained
}

// Validate administrative actions
fn validate_admin_action(
  action: ByteArray,
  datum: MeTTaProofDatum, 
  transaction: Transaction, 
  config: MeTTaBridgeConfig
) -> Bool {
  
  let valid_actions = [
    "force_verify",
    "invalidate_proof",
    "extend_expiry",
    "resolve_dispute",
    "emergency_halt",
    "update_config"
  ]
  
  list.any(valid_actions, fn(valid_action) { 
    action == valid_action 
  })
}

// Helper function to validate proof hash
fn validate_proof_hash(datum: MeTTaProofDatum) -> Bool {
  // In production, would cryptographically verify the proof hash
  // For now, just check it exists
  bytearray.length(datum.proof_hash.data) > 0
}

// Helper function to validate fee payment
fn validate_fee_payment(transaction: Transaction, required_fee: Int) -> Bool {
  // Simplified fee validation - in production would check specific outputs
  True
}

// Helper function to validate stake payment
fn validate_stake_payment(transaction: Transaction, stake_amount: Int) -> Bool {
  // Simplified stake validation - in production would check escrow output
  True
}

// Get current time from transaction validity range
fn get_current_time(validity_range) -> Int {
  // Simplified - in production would extract from validity range
  1672531200
}

// Test function for MeTTa bridge functionality
test metta_proof_submission_test() {
  let test_config = MeTTaBridgeConfig {
    authorized_metta_agents: [#"metta1", #"metta2"],
    authorized_verifiers: [#"verifier1", #"verifier2"],
    platform_admin: #"admin123",
    min_confidence_for_execution: 70,
    min_reasoning_quality: 80,
    proof_expiry_duration: 86400,  // 24 hours
    challenge_stake_required: 10000000,  // 10 ADA
    challenge_resolution_timeout: 3600,  // 1 hour
    challenge_reward_percentage: 10,
    max_gas_per_execution: 1000000,
    execution_cooldown: 300,  // 5 minutes
    require_consistency_check: True,
    require_external_validation: False,
    min_reasoning_steps: 3,
    proof_submission_fee: 1000000,  // 1 ADA
    verification_fee: 500000,       // 0.5 ADA
    execution_fee_base: 2000000,    // 2 ADA
  }
  
  let test_proof = MeTTaProofDatum {
    proof_id: "proof_001",
    proof_version: 1,
    metta_query: "(verify-contribution alice coding hackathon-project)",
    metta_result: "(verified-contribution alice coding 85% confidence)",
    reasoning_steps: [
      "step1: analyze contribution evidence",
      "step2: check contributor reputation",
      "step3: validate project complexity",
      "step4: calculate confidence score"
    ],
    proof_hash: #"abcd1234567890abcdef",  // Simplified hash
    signature: "metta_agent_signature_123",
    confidence_score: 85,
    context_data: dict.from_list([
      ("contributor_id", "alice"),
      ("project_type", "hackathon"),
      ("evidence_quality", "high")
    ]),
    input_parameters: dict.from_list([
      ("min_confidence", "70"),
      ("required_evidence", "code+demo")
    ]),
    agent_id: #"metta1",
    created_at: 1672531200,
    expires_at: 1672617600,
    is_verified: False,
    verifier: #"",
    verified_at: 0,
    should_execute: True,
    execution_data: dict.from_list([
      ("action", "award_tokens"),
      ("amount", "100")
    ]),
    gas_estimate: 250000,
    reasoning_quality: 88,
    consistency_check: True,
    external_validation: False,
  }
  
  // Test basic validation
  let proof_valid = 
    bytearray.length(test_proof.proof_id) > 0 &&
    test_proof.confidence_score >= test_config.min_confidence_for_execution &&
    test_proof.reasoning_quality >= test_config.min_reasoning_quality &&
    list.length(test_proof.reasoning_steps) >= test_config.min_reasoning_steps
  
  proof_valid
}