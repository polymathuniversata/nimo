// Nimo Platform - Contribution Validator Tests
// Comprehensive test suite for contribution validation smart contract

use aiken/dict
use aiken/list
use aiken/transaction.{
  ScriptContext, Transaction, Input, Output, OutputReference, TransactionId
}
use aiken/transaction/credential.{VerificationKey}
use aiken/transaction/value.{Value, ada_policy_id, ada_asset_name}
use contribution_validator.{
  ContributionDatum, ContributionRedeemer, PlatformConfig,
  contribution_validator, validate_contribution_submission
}
use lib/nimo_types.{create_test_config, create_test_user_identity}

// Test data setup
fn create_test_contribution_datum() -> ContributionDatum {
  ContributionDatum {
    contributor: #"alice123",
    contribution_type: "coding",
    description: "Built DApp for community voting",
    evidence_hash: "ipfs_QmTestEvidence123",
    metta_proof: "",
    metta_confidence: 0,
    verified: False,
    verifier: #"",
    base_reward: 100,
    confidence_multiplier: 100,
    final_reward: 0,
    submitted_at: 1672531200,
    verified_at: 0,
    is_active: True,
    requires_manual_review: False,
  }
}

fn create_verified_contribution_datum() -> ContributionDatum {
  ContributionDatum {
    contributor: #"alice123",
    contribution_type: "coding", 
    description: "Built DApp for community voting",
    evidence_hash: "ipfs_QmTestEvidence123",
    metta_proof: "metta_proof_hash_verified",
    metta_confidence: 85,
    verified: True,
    verifier: #"verifier1",
    base_reward: 100,
    confidence_multiplier: 135,  // 85% confidence = 135% multiplier
    final_reward: 128,  // (100 * 135 / 100) - 5% platform fee
    submitted_at: 1672531200,
    verified_at: 1672534800,
    is_active: True,
    requires_manual_review: False,
  }
}

fn create_test_transaction() -> Transaction {
  Transaction {
    inputs: [
      Input {
        output_reference: OutputReference {
          transaction_id: TransactionId { hash: #"test_tx_id" },
          output_index: 0
        },
        output: Output {
          address: credential.from_verification_key(#"alice123"),
          value: value.from_lovelace(5000000), // 5 ADA
          datum: InlineDatum(create_test_contribution_datum()),
          reference_script: None,
        }
      }
    ],
    reference_inputs: [],
    outputs: [
      Output {
        address: credential.from_verification_key(#"platform_address"),
        value: value.from_lovelace(2000000), // 2 ADA
        datum: InlineDatum(create_test_contribution_datum()),
        reference_script: None,
      }
    ],
    fee: value.from_lovelace(200000), // 0.2 ADA fee
    mint: value.zero(),
    certificates: [],
    withdrawals: dict.empty(),
    validity_range: Interval { 
      lower_bound: Finite(1672531200),
      upper_bound: Finite(1672534800)
    },
    extra_signatories: [#"alice123"],
    redeemers: dict.empty(),
    datums: dict.empty(),
    id: TransactionId { hash: #"test_tx_hash" }
  }
}

fn create_test_script_context(datum: ContributionDatum, transaction: Transaction) -> ScriptContext {
  ScriptContext {
    transaction: transaction,
    purpose: Spend(OutputReference {
      transaction_id: TransactionId { hash: #"test_tx_id" },
      output_index: 0
    })
  }
}

// Test 1: Valid contribution submission
test test_valid_contribution_submission() {
  let config = create_test_config()
  let datum = create_test_contribution_datum()
  let transaction = create_test_transaction()
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, SubmitContribution, context)
  
  result == True
}

// Test 2: Invalid contribution submission - missing signature
test test_invalid_contribution_submission_no_signature() {
  let config = create_test_config()
  let datum = create_test_contribution_datum()
  let transaction = Transaction { 
    ..create_test_transaction(),
    extra_signatories: [] // No signatures
  }
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, SubmitContribution, context)
  
  result == False
}

// Test 3: Invalid contribution submission - empty description
test test_invalid_contribution_empty_description() {
  let config = create_test_config()
  let datum = ContributionDatum {
    ..create_test_contribution_datum(),
    description: "" // Empty description
  }
  let transaction = create_test_transaction()
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, SubmitContribution, context)
  
  result == False
}

// Test 4: Valid contribution verification
test test_valid_contribution_verification() {
  let config = create_test_config()
  let datum = create_verified_contribution_datum()
  let transaction = Transaction {
    ..create_test_transaction(),
    extra_signatories: [#"verifier1"] // Authorized verifier signed
  }
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, VerifyContribution, context)
  
  result == True
}

// Test 5: Invalid contribution verification - unauthorized verifier
test test_invalid_verification_unauthorized() {
  let config = create_test_config()
  let datum = create_verified_contribution_datum()
  let transaction = Transaction {
    ..create_test_transaction(),
    extra_signatories: [#"unauthorized_verifier"]
  }
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, VerifyContribution, context)
  
  result == False
}

// Test 6: Valid reward claim
test test_valid_reward_claim() {
  let config = create_test_config()
  let datum = ContributionDatum {
    ..create_verified_contribution_datum(),
    is_active: False // Marked as processed
  }
  
  // Create transaction with NIMO token output to contributor
  let reward_output = Output {
    address: credential.from_verification_key(#"alice123"),
    value: value.from_asset(
      config.nimo_policy_id,
      config.nimo_asset_name, 
      128 // Final reward amount
    ),
    datum: NoDatum,
    reference_script: None,
  }
  
  let transaction = Transaction {
    ..create_test_transaction(),
    outputs: [reward_output],
    extra_signatories: [#"alice123"] // Contributor signed
  }
  
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, ClaimReward, context)
  
  result == True
}

// Test 7: Invalid reward claim - insufficient reward in output
test test_invalid_reward_claim_insufficient_tokens() {
  let config = create_test_config()
  let datum = create_verified_contribution_datum()
  
  // Create transaction with insufficient NIMO tokens
  let reward_output = Output {
    address: credential.from_verification_key(#"alice123"),
    value: value.from_asset(
      config.nimo_policy_id,
      config.nimo_asset_name, 
      50 // Less than final reward amount (128)
    ),
    datum: NoDatum,
    reference_script: None,
  }
  
  let transaction = Transaction {
    ..create_test_transaction(),
    outputs: [reward_output],
    extra_signatories: [#"alice123"]
  }
  
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, ClaimReward, context)
  
  result == False
}

// Test 8: Valid MeTTa proof update
test test_valid_metta_proof_update() {
  let config = create_test_config()
  let datum = ContributionDatum {
    ..create_test_contribution_datum(),
    metta_proof: "updated_metta_proof_hash",
    metta_confidence: 92,
    verified_at: 1672534800 // Updated timestamp
  }
  
  let transaction = Transaction {
    ..create_test_transaction(),
    extra_signatories: [config.metta_agent] // MeTTa agent signed
  }
  
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, UpdateMettaProof, context)
  
  result == True
}

// Test 9: Invalid MeTTa proof update - unauthorized agent
test test_invalid_metta_proof_update_unauthorized() {
  let config = create_test_config()
  let datum = ContributionDatum {
    ..create_test_contribution_datum(),
    metta_proof: "updated_metta_proof_hash",
    metta_confidence: 92
  }
  
  let transaction = Transaction {
    ..create_test_transaction(),
    extra_signatories: [#"unauthorized_agent"]
  }
  
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(config, datum, UpdateMettaProof, context)
  
  result == False
}

// Test 10: Valid admin action
test test_valid_admin_action() {
  let config = create_test_config()
  let datum = create_test_contribution_datum()
  
  let transaction = Transaction {
    ..create_test_transaction(),
    extra_signatories: [config.platform_admin] // Admin signed
  }
  
  let context = create_test_script_context(datum, transaction)
  
  let result = contribution_validator(
    config, 
    datum, 
    AdminAction { action: "force_verification" }, 
    context
  )
  
  result == True
}

// Test 11: Reward calculation test
test test_reward_calculation() {
  let base_reward = 100
  let confidence = 85
  let config = create_test_config()
  
  let calculated_reward = calculate_confidence_based_reward(base_reward, confidence, config)
  
  // Expected: (100 * 135 / 100) - 5% fee = 128
  calculated_reward == 128
}

// Test 12: Edge case - minimum confidence
test test_minimum_confidence_reward() {
  let base_reward = 100
  let confidence = 0  // Minimum confidence
  let config = create_test_config()
  
  let calculated_reward = calculate_confidence_based_reward(base_reward, confidence, config)
  
  // Should apply minimum reward (10) as per config
  calculated_reward >= config.min_reward_per_contribution
}

// Test 13: Edge case - maximum confidence
test test_maximum_confidence_reward() {
  let base_reward = 100
  let confidence = 100  // Maximum confidence
  let config = create_test_config()
  
  let calculated_reward = calculate_confidence_based_reward(base_reward, confidence, config)
  
  // Expected: (100 * 150 / 100) - 5% fee = 142
  calculated_reward == 142
}

// Test 14: Edge case - reward capping
test test_reward_capping() {
  let base_reward = 2000  // Very high base reward
  let confidence = 100
  let config = create_test_config()
  
  let calculated_reward = calculate_confidence_based_reward(base_reward, confidence, config)
  
  // Should be capped at max_reward_per_contribution (1000)
  calculated_reward <= config.max_reward_per_contribution
}

// Test 15: Integration test - full contribution flow
test test_full_contribution_flow() {
  let config = create_test_config()
  let initial_datum = create_test_contribution_datum()
  let transaction = create_test_transaction()
  let context = create_test_script_context(initial_datum, transaction)
  
  // Step 1: Submit contribution
  let submission_valid = contribution_validator(
    config, 
    initial_datum, 
    SubmitContribution, 
    context
  )
  
  // Step 2: Verify contribution  
  let verified_datum = create_verified_contribution_datum()
  let verification_transaction = Transaction {
    ..transaction,
    extra_signatories: [#"verifier1"]
  }
  let verification_context = create_test_script_context(verified_datum, verification_transaction)
  
  let verification_valid = contribution_validator(
    config,
    verified_datum,
    VerifyContribution,
    verification_context
  )
  
  // Step 3: Claim reward
  let claim_datum = ContributionDatum {
    ..verified_datum,
    is_active: False
  }
  
  let reward_output = Output {
    address: credential.from_verification_key(#"alice123"),
    value: value.from_asset(config.nimo_policy_id, config.nimo_asset_name, 128),
    datum: NoDatum,
    reference_script: None,
  }
  
  let claim_transaction = Transaction {
    ..transaction,
    outputs: [reward_output],
    extra_signatories: [#"alice123"]
  }
  
  let claim_context = create_test_script_context(claim_datum, claim_transaction)
  
  let claim_valid = contribution_validator(
    config,
    claim_datum,
    ClaimReward,
    claim_context
  )
  
  // All steps should be valid
  submission_valid && verification_valid && claim_valid
}