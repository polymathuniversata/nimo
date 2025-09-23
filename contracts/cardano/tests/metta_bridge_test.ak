use aiken/hash.{Blake2b_224, Blake2b_256, Hash}
use aiken/transaction.{Transaction, ScriptContext}
use aiken/transaction/credential.{VerificationKey}
use aiken/dict
use aiken/list
use aiken/time.{PosixTime}

use metta_bridge.{
  MeTTaProofDatum,
  MeTTaBridgeRedeemer,
  MeTTaBridgeConfig,
  ProofChallenge,
  AdminActionType,
  metta_bridge_validator
}

// Test helper functions
fn create_test_config() -> MeTTaBridgeConfig {
  MeTTaBridgeConfig {
    authorized_metta_agents: [#"agent1", #"agent2"],
    authorized_verifiers: [#"verifier1", #"verifier2"],
    admin_public_keys: [#"admin1", #"admin2", #"admin3"],
    min_admin_signatures: 2,
    is_paused: False,
    last_config_update: 0,
    min_confidence_for_execution: 80,
    min_reasoning_quality: 75,
    proof_expiry_duration: 86400,
    challenge_stake_required: 100000000,
    challenge_resolution_timeout: 7200,
    challenge_reward_percentage: 20,
    max_gas_per_execution: 1000000,
    execution_cooldown: 3600,
    require_consistency_check: True,
    require_external_validation: True,
    min_reasoning_steps: 3,
    proof_submission_fee: 10000000,
    verification_fee: 5000000,
    execution_fee_base: 2000000,
    emergency_withdrawal_limit: 1000000000,
    config_update_cooldown: 86400
  }
}

fn create_test_datum() -> MeTTaProofDatum {
  MeTTaProofDatum {
    proof_id: #"test_proof_1",
    proof_version: 1,
    metta_query: #"(+ 2 2)",
    metta_result: #"4",
    reasoning_steps: [#"step1", #"step2", #"step3"],
    proof_hash: #"proof_hash",
    signature: #"agent_signature",
    confidence_score: 85,
    context_data: dict.new(),
    input_parameters: dict.new(),
    agent_id: #"agent1",
    created_at: 1000,
    expires_at: 87400,
    is_verified: False,
    verifier: #"verifier1",
    verified_at: 0,
    should_execute: True,
    execution_data: dict.new(),
    gas_estimate: 500000,
    reasoning_quality: 80,
    consistency_check: True,
    external_validation: True
  }
}

fn create_test_context(signatories: List<Hash<Blake2b_224, VerificationKey>>) -> ScriptContext {
  ScriptContext {
    transaction: Transaction {
      inputs: [],
      outputs: [],
      fee: 0,
      mint: value.zero(),
      certificates: [],
      withdrawals: dict.new(),
      validity_range: time.Interval { start: None, end: None },
      extra_signatories: signatories,
      redeemers: dict.new(),
      datums: dict.new(),
      id: #"tx_id"
    },
    purpose: spend.Spend(#"output_ref")
  }
}

// Test cases
test submit_proof_valid() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"agent1"])
  
  metta_bridge_validator(config, datum, SubmitProof, context) == True
}

test submit_proof_invalid_agent() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"unauthorized_agent"])
  
  metta_bridge_validator(config, datum, SubmitProof, context) == False
}

test verify_proof_valid() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"verifier1"])
  
  metta_bridge_validator(
    config,
    datum,
    VerifyProof { verifier_signature: #"valid_signature" },
    context
  ) == True
}

test verify_proof_invalid_verifier() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"unauthorized_verifier"])
  
  metta_bridge_validator(
    config,
    datum,
    VerifyProof { verifier_signature: #"valid_signature" },
    context
  ) == False
}

test execute_decision_valid() {
  let config = create_test_config()
  let datum = create_test_datum().with_fields({
    is_verified: True,
    verified_at: 1100
  })
  let context = create_test_context([#"agent1"])
  
  metta_bridge_validator(
    config,
    datum,
    ExecuteDecision { execution_params: dict.new() },
    context
  ) == True
}

test execute_decision_unverified() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"agent1"])
  
  metta_bridge_validator(
    config,
    datum,
    ExecuteDecision { execution_params: dict.new() },
    context
  ) == False
}

test challenge_proof_valid() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"challenger1"])
  
  metta_bridge_validator(
    config,
    datum,
    ChallengeProof {
      challenge_reason: #"invalid_reasoning",
      challenger_stake: 100000000
    },
    context
  ) == True
}

test challenge_proof_insufficient_stake() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"challenger1"])
  
  metta_bridge_validator(
    config,
    datum,
    ChallengeProof {
      challenge_reason: #"invalid_reasoning",
      challenger_stake: 50000000
    },
    context
  ) == False
}

test emergency_pause_valid() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    AdminAction { action: EmergencyPause },
    context
  ) == True
}

test emergency_pause_insufficient_signatures() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"admin1"])
  
  metta_bridge_validator(
    config,
    datum,
    AdminAction { action: EmergencyPause },
    context
  ) == False
}

test emergency_withdraw_valid() {
  let config = create_test_config().with_fields({ is_paused: True })
  let datum = create_test_datum()
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    AdminAction {
      action: EmergencyWithdraw {
        recipient: #"admin1",
        amount: 500000000
      }
    },
    context
  ) == True
}

test emergency_withdraw_not_paused() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    AdminAction {
      action: EmergencyWithdraw {
        recipient: #"admin1",
        amount: 500000000
      }
    },
    context
  ) == False
}

test update_config_valid() {
  let config = create_test_config()
  let new_config = config.with_fields({
    min_confidence_for_execution: 85,
    challenge_stake_required: 150000000
  })
  let datum = create_test_datum()
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    AdminAction {
      action: UpdateConfig { new_config }
    },
    context
  ) == True
}

test update_config_invalid_params() {
  let config = create_test_config()
  let new_config = config.with_fields({
    min_admin_signatures: 1,  // Invalid: minimum 2 required
    challenge_stake_required: 0  // Invalid: must be positive
  })
  let datum = create_test_datum()
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    AdminAction {
      action: UpdateConfig { new_config }
    },
    context
  ) == False
}

test resolve_challenge_valid() {
  let config = create_test_config()
  let challenge = ProofChallenge {
    challenger: #"challenger1",
    challenge_reason: #"invalid_reasoning",
    stake_amount: 100000000,
    submitted_at: 1000,
    resolution_deadline: 8200,
    is_resolved: False,
    resolution: #"",
    winner: #""
  }
  let datum = create_test_datum().with_fields({
    challenges: [challenge]
  })
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    ResolveChallenge {
      resolution: #"challenge_accepted"
    },
    context
  ) == True
}

test resolve_challenge_expired() {
  let config = create_test_config()
  let challenge = ProofChallenge {
    challenger: #"challenger1",
    challenge_reason: #"invalid_reasoning",
    stake_amount: 100000000,
    submitted_at: 1000,
    resolution_deadline: 1100,  // Already expired
    is_resolved: False,
    resolution: #"",
    winner: #""
  }
  let datum = create_test_datum().with_fields({
    challenges: [challenge]
  })
  let context = create_test_context([#"admin1", #"admin2"])
  
  metta_bridge_validator(
    config,
    datum,
    ResolveChallenge {
      resolution: #"challenge_accepted"
    },
    context
  ) == False
}

test update_proof_valid() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"agent1"])
  
  metta_bridge_validator(
    config,
    datum,
    UpdateProof {
      update_reason: #"improved_reasoning"
    },
    context
  ) == True
}

test update_proof_contract_paused() {
  let config = create_test_config().with_fields({ is_paused: True })
  let datum = create_test_datum()
  let context = create_test_context([#"agent1"])
  
  metta_bridge_validator(
    config,
    datum,
    UpdateProof {
      update_reason: #"improved_reasoning"
    },
    context
  ) == False
}

test update_proof_unauthorized() {
  let config = create_test_config()
  let datum = create_test_datum()
  let context = create_test_context([#"unauthorized_agent"])
  
  metta_bridge_validator(
    config,
    datum,
    UpdateProof {
      update_reason: #"improved_reasoning"
    },
    context
  ) == False
}