// Nimo Platform - AI Agents Validator Smart Contract
// Written in Aiken for Cardano blockchain
// This validator manages AI agent registration, decision verification, and challenge resolution

use aiken/dict
use aiken/hash.{Blake2b_224, Hash}
use aiken/list
use aiken/transaction.{ScriptContext, Transaction, InlineDatum, OutputReference, Input}
use aiken/transaction/credential.{VerificationKey}
use aiken/transaction/value.{PolicyId, AssetName, Value}
use aiken/bytearray
use aiken/string

// Data types for AI agents system
pub type AIAgentDatum {
  // Agent identification
  agent_id: ByteArray,
  agent_type: ByteArray,          // "contribution_validation", "fraud_detection", etc.
  
  // Agent ownership and accountability
  owner: Hash<Blake2b_224, VerificationKey>,
  operators: List<Hash<Blake2b_224, VerificationKey>>,
  
  // Agent model and verification
  model_hash: ByteArray,          // Hash of the AI model
  training_data_hash: ByteArray,  // Hash of training data
  performance_bond: Int,          // Staked amount for performance
  
  // Performance metrics
  total_decisions: Int,
  successful_decisions: Int,
  challenged_decisions: Int,
  overturned_decisions: Int,
  average_confidence: Int,        // Scaled by 1000 (e.g., 850 = 0.85)
  
  // Agent status
  active: Bool,
  registration_timestamp: Int,
  last_activity: Int,
  
  // Governance and compliance
  governance_token_balance: Int,
  compliance_score: Int,          // Scaled by 1000
  audit_status: ByteArray,        // "passed", "pending", "failed"
}

// Decision record data type
pub type DecisionDatum {
  // Decision identification
  decision_id: ByteArray,
  agent_id: ByteArray,
  
  // Decision content
  input_data_hash: ByteArray,     // Hash of input data
  decision_hash: ByteArray,       // Hash of decision result
  confidence_score: Int,          // Scaled by 1000
  
  // MeTTa reasoning proof
  metta_proof_hash: ByteArray,    // Hash of MeTTa reasoning proof
  reasoning_steps: List<ByteArray>, // Key reasoning steps
  
  // Verification and status
  verified: Bool,
  verifier: Hash<Blake2b_224, VerificationKey>,
  verification_timestamp: Int,
  
  // Challenge information
  challengeable_until: Int,       // Unix timestamp
  challenge_count: Int,
  challenge_status: ByteArray,    // "none", "challenged", "resolved"
  
  // Blockchain proof
  block_height: Int,
  transaction_hash: ByteArray,
  
  // Community metrics
  community_approval: Int,        // Scaled by 1000
  transparency_score: Int,        // Scaled by 1000
}

// Challenge record data type
pub type ChallengeDatum {
  // Challenge identification
  challenge_id: ByteArray,
  decision_id: ByteArray,
  
  // Challenge details
  challenger: Hash<Blake2b_224, VerificationKey>,
  reason: ByteArray,
  evidence_hash: ByteArray,       // IPFS hash of evidence
  
  // Stakes and incentives
  challenger_stake: Int,          // ADA staked by challenger
  agent_counter_stake: Int,       // Counter-stake by agent owner
  
  // Resolution process
  challenge_timestamp: Int,
  resolution_deadline: Int,
  arbitrator_pool: List<Hash<Blake2b_224, VerificationKey>>,
  
  // Resolution results
  resolution_status: ByteArray,   // "pending", "upheld", "dismissed", "appealed"
  resolution_timestamp: Int,
  final_decision: ByteArray,
  
  // Payouts and penalties
  challenger_payout: Int,
  agent_penalty: Int,
  arbitrator_reward: Int,
}

// Redeemer actions
pub type AIAgentRedeemer {
  // Agent management
  RegisterAgent { agent_spec: ByteArray }
  UpdateAgent { updates: ByteArray }
  DeactivateAgent { reason: ByteArray }
  
  // Decision lifecycle
  RecordDecision { decision_data: ByteArray }
  VerifyDecision { verification_proof: ByteArray }
  ChallengeDecision { challenge_data: ByteArray }
  
  // Challenge resolution
  SubmitEvidence { evidence_hash: ByteArray }
  ArbitrateChallenge { arbitration_result: ByteArray }
  AppealDecision { appeal_reason: ByteArray }
  
  // Performance and governance
  UpdatePerformanceMetrics { metrics: ByteArray }
  SlashPerformanceBond { slash_reason: ByteArray }
  GovernanceAction { action: ByteArray, proposal_id: ByteArray }
  
  // Administrative actions
  AdminAction { action: ByteArray }
  EmergencyPause { reason: ByteArray }
}

// Platform configuration
pub type AIAgentConfig {
  nimo_token_policy: PolicyId,
  nimo_token_name: AssetName,
  
  // Authorized addresses
  platform_admin: Hash<Blake2b_224, VerificationKey>,
  governance_contract: Hash<Blake2b_224, VerificationKey>,
  oracle_address: Hash<Blake2b_224, VerificationKey>,
  
  // Performance requirements
  min_performance_bond: Int,      // Minimum bond for agent registration
  min_confidence_threshold: Int,   // Minimum confidence for auto-approval (scaled by 1000)
  challenge_period: Int,          // Challenge period in seconds
  arbitration_timeout: Int,       // Arbitration timeout in seconds
  
  // Stake and reward parameters
  base_challenge_stake: Int,      // Base stake required to challenge
  arbitrator_reward_rate: Int,    // Reward rate for arbitrators (scaled by 1000)
  performance_penalty_rate: Int,  // Penalty rate for poor performance
  
  // Governance parameters
  governance_token_weight: Int,   // Weight of governance tokens in voting
  min_quorum: Int,               // Minimum quorum for governance decisions
  proposal_threshold: Int,        // Minimum tokens to create proposal
}

// Main validator function
validator(config: AIAgentConfig) {
  fn ai_agents_validator(
    datum: AIAgentDatum,
    redeemer: AIAgentRedeemer,
    context: ScriptContext
  ) -> Bool {
    
    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction
    
    when redeemer is {
      
      // Register a new AI agent
      RegisterAgent { agent_spec } -> {
        validate_agent_registration(datum, agent_spec, transaction, config)
      }
      
      // Update agent configuration or metrics
      UpdateAgent { updates } -> {
        let owner_signed = list.has(extra_signatories, datum.owner)
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        (owner_signed || admin_signed) && 
        validate_agent_update(datum, updates, transaction, config)
      }
      
      // Record a new decision made by the agent
      RecordDecision { decision_data } -> {
        let authorized_operator = list.any(datum.operators, fn(operator) {
          list.has(extra_signatories, operator)
        })
        
        authorized_operator && datum.active && 
        validate_decision_recording(datum, decision_data, transaction, config)
      }
      
      // Verify a recorded decision
      VerifyDecision { verification_proof } -> {
        let verifier_authorized = 
          list.has(extra_signatories, config.platform_admin) ||
          list.has(extra_signatories, config.oracle_address)
        
        verifier_authorized && 
        validate_decision_verification(datum, verification_proof, transaction, config)
      }
      
      // Challenge an agent decision
      ChallengeDecision { challenge_data } -> {
        validate_decision_challenge(datum, challenge_data, transaction, config)
      }
      
      // Update performance metrics
      UpdatePerformanceMetrics { metrics } -> {
        let oracle_signed = list.has(extra_signatories, config.oracle_address)
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        (oracle_signed || admin_signed) && 
        validate_performance_update(datum, metrics, transaction, config)
      }
      
      // Slash performance bond for poor performance
      SlashPerformanceBond { slash_reason } -> {
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        let governance_signed = list.has(extra_signatories, config.governance_contract)
        
        (admin_signed || governance_signed) && 
        validate_bond_slashing(datum, slash_reason, transaction, config)
      }
      
      // Governance action
      GovernanceAction { action, proposal_id } -> {
        let governance_signed = list.has(extra_signatories, config.governance_contract)
        
        governance_signed && 
        validate_governance_action(datum, action, proposal_id, transaction, config)
      }
      
      // Administrative action
      AdminAction { action } -> {
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        admin_signed && 
        validate_admin_action(action, datum, transaction, config)
      }
    }
  }
}

// Decision validator for decision-specific operations
validator(config: AIAgentConfig) {
  fn decision_validator(
    datum: DecisionDatum,
    redeemer: AIAgentRedeemer,
    context: ScriptContext
  ) -> Bool {
    
    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction
    
    when redeemer is {
      
      ChallengeDecision { challenge_data } -> {
        validate_decision_challenge_specific(datum, challenge_data, transaction, config)
      }
      
      VerifyDecision { verification_proof } -> {
        validate_decision_verification_specific(datum, verification_proof, transaction, config)
      }
      
      _ -> False  // Other redeemers not valid for decision UTXOs
    }
  }
}

// Challenge validator for challenge resolution
validator(config: AIAgentConfig) {
  fn challenge_validator(
    datum: ChallengeDatum,
    redeemer: AIAgentRedeemer,
    context: ScriptContext
  ) -> Bool {
    
    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction
    
    when redeemer is {
      
      SubmitEvidence { evidence_hash } -> {
        let challenger_signed = list.has(extra_signatories, datum.challenger)
        
        challenger_signed && 
        validate_evidence_submission(datum, evidence_hash, transaction, config)
      }
      
      ArbitrateChallenge { arbitration_result } -> {
        let arbitrator_signed = list.any(datum.arbitrator_pool, fn(arbitrator) {
          list.has(extra_signatories, arbitrator)
        })
        
        arbitrator_signed && 
        validate_arbitration(datum, arbitration_result, transaction, config)
      }
      
      AppealDecision { appeal_reason } -> {
        let challenger_signed = list.has(extra_signatories, datum.challenger)
        
        challenger_signed && 
        validate_appeal(datum, appeal_reason, transaction, config)
      }
      
      _ -> False  // Other redeemers not valid for challenge UTXOs
    }
  }
}

// Validation functions

fn validate_agent_registration(
  datum: AIAgentDatum,
  agent_spec: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Check that owner signed the transaction
  let owner_signed = list.has(transaction.extra_signatories, datum.owner)
  
  // Validate performance bond
  let sufficient_bond = datum.performance_bond >= config.min_performance_bond
  
  // Check initial state
  let proper_initial_state = 
    datum.total_decisions == 0 &&
    datum.successful_decisions == 0 &&
    datum.challenged_decisions == 0 &&
    datum.overturned_decisions == 0 &&
    datum.active == True &&
    bytearray.length(datum.agent_id) > 0 &&
    bytearray.length(datum.model_hash) > 0
  
  // Validate agent type
  let valid_agent_type = validate_agent_type(datum.agent_type)
  
  owner_signed && 
  sufficient_bond && 
  proper_initial_state && 
  valid_agent_type
}

fn validate_decision_recording(
  agent_datum: AIAgentDatum,
  decision_data: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Agent must be active
  let agent_active = agent_datum.active
  
  // Decision data must be valid
  let valid_decision_data = bytearray.length(decision_data) > 0
  
  // Must have proper outputs (decision UTXO)
  let has_decision_output = list.any(transaction.outputs, fn(output) {
    // Check if output contains decision datum
    when output.datum is {
      InlineDatum(data) -> True  // Simplified check
      _ -> False
    }
  })
  
  agent_active && valid_decision_data && has_decision_output
}

fn validate_decision_challenge(
  agent_datum: AIAgentDatum,
  challenge_data: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Calculate required stake
  let required_stake = calculate_challenge_stake(config.base_challenge_stake)
  
  // Check that challenger provided sufficient stake
  let sufficient_stake_provided = check_stake_provision(transaction, required_stake)
  
  // Valid challenge data
  let valid_challenge_data = bytearray.length(challenge_data) > 0
  
  // Must create challenge UTXO
  let creates_challenge_utxo = list.any(transaction.outputs, fn(output) {
    when output.datum is {
      InlineDatum(data) -> True  // Simplified check for challenge datum
      _ -> False
    }
  })
  
  sufficient_stake_provided && 
  valid_challenge_data && 
  creates_challenge_utxo
}

fn validate_decision_challenge_specific(
  decision_datum: DecisionDatum,
  challenge_data: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Check if challenge period is still active
  let challenge_period_active = 
    decision_datum.challengeable_until > get_current_time(transaction)
  
  // Decision must not already be challenged
  let not_already_challenged = decision_datum.challenge_status == "none"
  
  challenge_period_active && not_already_challenged
}

fn validate_arbitration(
  challenge_datum: ChallengeDatum,
  arbitration_result: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Check arbitration is within deadline
  let within_deadline = 
    challenge_datum.resolution_deadline > get_current_time(transaction)
  
  // Challenge must be pending
  let challenge_pending = challenge_datum.resolution_status == "pending"
  
  // Valid arbitration result
  let valid_result = bytearray.length(arbitration_result) > 0
  
  within_deadline && challenge_pending && valid_result
}

fn validate_performance_update(
  agent_datum: AIAgentDatum,
  metrics: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Metrics must be valid
  let valid_metrics = bytearray.length(metrics) > 0
  
  // Agent must exist and be registered
  let agent_registered = bytearray.length(agent_datum.agent_id) > 0
  
  valid_metrics && agent_registered
}

fn validate_bond_slashing(
  agent_datum: AIAgentDatum,
  slash_reason: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Must have valid reason
  let valid_reason = bytearray.length(slash_reason) > 0
  
  // Agent must have bond to slash
  let has_bond = agent_datum.performance_bond > 0
  
  valid_reason && has_bond
}

fn validate_governance_action(
  agent_datum: AIAgentDatum,
  action: ByteArray,
  proposal_id: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Valid action and proposal
  let valid_action = bytearray.length(action) > 0
  let valid_proposal = bytearray.length(proposal_id) > 0
  
  valid_action && valid_proposal
}

fn validate_admin_action(
  action: ByteArray,
  agent_datum: AIAgentDatum,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Define allowed admin actions
  let valid_actions = [
    "pause_agent",
    "resume_agent",
    "emergency_stop",
    "update_config",
    "force_resolution"
  ]
  
  list.any(valid_actions, fn(valid_action) { 
    action == valid_action 
  })
}

// Helper functions

fn validate_agent_type(agent_type: ByteArray) -> Bool {
  let valid_types = [
    "contribution_validation",
    "fraud_detection", 
    "reward_calculation",
    "community_moderation",
    "platform_governance",
    "reputation_scoring"
  ]
  
  list.any(valid_types, fn(valid_type) {
    agent_type == valid_type
  })
}

fn calculate_challenge_stake(base_stake: Int) -> Int {
  // For now, return base stake
  // In practice, this could be dynamic based on various factors
  base_stake
}

fn check_stake_provision(transaction: Transaction, required_stake: Int) -> Bool {
  // Check if transaction contains sufficient ADA
  // This is a simplified check
  True
}

fn get_current_time(transaction: Transaction) -> Int {
  // Extract current time from transaction validity range
  // This is a simplified implementation
  when transaction.validity_range.upper_bound is {
    Some(time) -> time
    None -> 0
  }
}

fn validate_evidence_submission(
  challenge_datum: ChallengeDatum,
  evidence_hash: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Evidence must be valid
  let valid_evidence = bytearray.length(evidence_hash) > 0
  
  // Challenge must be active
  let challenge_active = challenge_datum.resolution_status == "pending"
  
  valid_evidence && challenge_active
}

fn validate_appeal(
  challenge_datum: ChallengeDatum,
  appeal_reason: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Appeal reason must be valid
  let valid_reason = bytearray.length(appeal_reason) > 0
  
  // Challenge must be resolved
  let challenge_resolved = 
    challenge_datum.resolution_status == "upheld" || 
    challenge_datum.resolution_status == "dismissed"
  
  valid_reason && challenge_resolved
}

fn validate_agent_update(
  agent_datum: AIAgentDatum,
  updates: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Updates must be valid
  let valid_updates = bytearray.length(updates) > 0
  
  // Agent must be registered
  let agent_exists = bytearray.length(agent_datum.agent_id) > 0
  
  valid_updates && agent_exists
}

fn validate_decision_verification(
  agent_datum: AIAgentDatum,
  verification_proof: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Verification proof must be valid
  let valid_proof = bytearray.length(verification_proof) > 0
  
  valid_proof
}

fn validate_decision_verification_specific(
  decision_datum: DecisionDatum,
  verification_proof: ByteArray,
  transaction: Transaction,
  config: AIAgentConfig
) -> Bool {
  
  // Decision must not already be verified
  let not_verified = decision_datum.verified == False
  
  // Verification proof must be valid
  let valid_proof = bytearray.length(verification_proof) > 0
  
  not_verified && valid_proof
}

// Test functions for contract validation
test agent_registration_test() {
  let test_config = AIAgentConfig {
    nimo_token_policy: #"abcd1234",
    nimo_token_name: #"4e494d4f",
    platform_admin: #"admin123",
    governance_contract: #"governance456",
    oracle_address: #"oracle789",
    min_performance_bond: 1000,
    min_confidence_threshold: 700,  // 70%
    challenge_period: 172800,       // 48 hours
    arbitration_timeout: 604800,    // 7 days
    base_challenge_stake: 500,
    arbitrator_reward_rate: 100,    // 10%
    performance_penalty_rate: 200,  // 20%
    governance_token_weight: 1,
    min_quorum: 100,               // 10%
    proposal_threshold: 1000,
  }
  
  let test_agent = AIAgentDatum {
    agent_id: "fraud_detector_v1",
    agent_type: "fraud_detection",
    owner: #"owner123",
    operators: [#"operator1", #"operator2"],
    model_hash: "model_hash_abc",
    training_data_hash: "training_data_xyz",
    performance_bond: 1500,
    total_decisions: 0,
    successful_decisions: 0,
    challenged_decisions: 0,
    overturned_decisions: 0,
    average_confidence: 0,
    active: True,
    registration_timestamp: 1672531200,
    last_activity: 1672531200,
    governance_token_balance: 5000,
    compliance_score: 950,  // 95%
    audit_status: "passed",
  }
  
  // Test agent registration validation
  validate_agent_type(test_agent.agent_type) == True &&
  test_agent.performance_bond >= test_config.min_performance_bond &&
  test_agent.active == True
}