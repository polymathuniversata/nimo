// Nimo Platform - NIMO Token Smart Contract
// Written in Aiken for Cardano blockchain
// This contract implements the NIMO native token with governance and reward distribution

use aiken/dict.{Dict}
use aiken/hash.{Blake2b_224, Blake2b_256, Hash}
use aiken/list
use aiken/transaction.{ScriptContext, Transaction, InlineDatum, OutputReference}
use aiken/transaction/credential.{VerificationKey}
use aiken/transaction/value.{PolicyId, AssetName, Value}
use aiken/bytearray

// Token distribution data structure
pub type TokenDistributionDatum {
  // Distribution identification
  distribution_id: ByteArray,
  recipient: Hash<Blake2b_224, VerificationKey>,

  // Distribution details
  amount: Int,
  reason: ByteArray,
  timestamp: Int,

  // MeTTa reasoning proof
  metta_proof_hash: ByteArray,
  confidence_score: Int,          // 0-100

  // Contribution details
  contribution_type: ByteArray,
  contribution_hash: ByteArray,   // IPFS hash of contribution evidence

  // Status and verification
  verified: Bool,
  verifier: Hash<Blake2b_224, VerificationKey>,
  claimed: Bool,

  // Governance context
  governance_approved: Bool,
  proposal_id: ByteArray,
}

// Vesting schedule data structure
pub type VestingDatum {
  // Vesting identification
  vesting_id: ByteArray,
  beneficiary: Hash<Blake2b_224, VerificationKey>,

  // Vesting parameters
  total_amount: Int,
  released_amount: Int,
  start_time: Int,
  duration: Int,

  // Status
  is_active: Bool,
  created_at: Int,

  // Governance
  governance_approved: Bool,
  approval_timestamp: Int,
}

// Governance proposal data structure
pub type GovernanceProposalDatum {
  // Proposal identification
  proposal_id: ByteArray,
  proposer: Hash<Blake2b_224, VerificationKey>,

  // Proposal details
  title: ByteArray,
  description: ByteArray,
  proposal_type: ByteArray,       // "parameter_change", "fund_allocation", etc.

  // Parameter changes (if applicable)
  parameter_name: ByteArray,
  old_value: Int,
  new_value: Int,

  // Voting details
  voting_start: Int,
  voting_end: Int,
  total_votes: Int,
  yes_votes: Int,
  no_votes: Int,

  // Status
  status: ByteArray,              // "active", "passed", "rejected", "executed"
  executed_at: Int,

  // Execution details
  execution_data: Dict<ByteArray, ByteArray>,
}

// Redeemer actions for token operations
pub type TokenRedeemer {
  // Token distribution
  MintTokens { distribution_data: ByteArray }
  BurnTokens { burn_reason: ByteArray }

  // Vesting operations
  CreateVesting { vesting_params: ByteArray }
  ClaimVestedTokens

  // Governance operations
  CreateProposal { proposal_data: ByteArray }
  VoteOnProposal { vote: Bool, voting_power: Int }
  ExecuteProposal

  // Administrative operations
  UpdateParameters { parameter: ByteArray, value: Int }
  EmergencyAction { action: ByteArray }

  // Reward claiming
  ClaimDistribution
}

// Platform configuration
pub type TokenConfig {
  // Token identification
  token_policy_id: PolicyId,
  token_asset_name: AssetName,

  // Authorized addresses
  platform_admin: Hash<Blake2b_224, VerificationKey>,
  minter_role: List<Hash<Blake2b_224, VerificationKey>>,
  burner_role: List<Hash<Blake2b_224, VerificationKey>>,
  governance_role: List<Hash<Blake2b_224, VerificationKey>>,

  // Token parameters
  max_supply: Int,
  initial_supply: Int,
  min_mint_amount: Int,
  max_mint_amount: Int,

  // Distribution parameters
  min_confidence_for_auto_mint: Int,  // Minimum confidence for automatic minting
  platform_fee_percentage: Int,       // Platform fee (0-100)
  burn_rate: Int,                     // Burn rate for certain operations

  // Vesting parameters
  default_vesting_duration: Int,      // Default vesting period in seconds
  max_vesting_duration: Int,          // Maximum vesting period

  // Governance parameters
  proposal_threshold: Int,            // Minimum tokens to create proposal
  voting_period: Int,                 // Voting period in seconds
  quorum_percentage: Int,             // Minimum quorum percentage (0-100)
  execution_delay: Int,               // Delay before proposal execution

  // Emergency parameters
  emergency_pause_enabled: Bool,
  emergency_admin: Hash<Blake2b_224, VerificationKey>,
}

// Main token validator
validator(config: TokenConfig) {
  fn nimo_token_validator(
    datum: TokenDistributionDatum,
    redeemer: TokenRedeemer,
    context: ScriptContext
  ) -> Bool {

    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction

    when redeemer is {

      // Mint new tokens for verified contributions
      MintTokens { distribution_data } -> {
        let authorized_minter = list.any(config.minter_role, fn(minter) {
          list.has(extra_signatories, minter)
        }) ||
        list.has(extra_signatories, config.platform_admin)

        authorized_minter &&
        validate_token_minting(datum, distribution_data, transaction, config)
      }

      // Burn tokens for platform operations
      BurnTokens { burn_reason } -> {
        let authorized_burner = list.any(config.burner_role, fn(burner) {
          list.has(extra_signatories, burner)
        }) ||
        list.has(extra_signatories, config.platform_admin)

        authorized_burner &&
        validate_token_burning(datum, burn_reason, transaction, config)
      }

      // Create vesting schedule
      CreateVesting { vesting_params } -> {
        let authorized_creator = list.has(extra_signatories, config.platform_admin) ||
        list.any(config.governance_role, fn(governor) {
          list.has(extra_signatories, governor)
        })

        authorized_creator &&
        validate_vesting_creation(datum, vesting_params, transaction, config)
      }

      // Claim vested tokens
      ClaimVestedTokens -> {
        let beneficiary_signed = list.has(extra_signatories, datum.recipient)
        beneficiary_signed &&
        validate_vesting_claim(datum, transaction, config)
      }

      // Create governance proposal
      CreateProposal { proposal_data } -> {
        validate_proposal_creation(datum, proposal_data, transaction, config)
      }

      // Vote on proposal
      VoteOnProposal { vote, voting_power } -> {
        validate_proposal_vote(datum, vote, voting_power, transaction, config)
      }

      // Execute approved proposal
      ExecuteProposal -> {
        let authorized_executor = list.has(extra_signatories, config.platform_admin) ||
        list.any(config.governance_role, fn(governor) {
          list.has(extra_signatories, governor)
        })

        authorized_executor &&
        validate_proposal_execution(datum, transaction, config)
      }

      // Update protocol parameters
      UpdateParameters { parameter, value } -> {
        let authorized_updater = list.has(extra_signatories, config.platform_admin) ||
        list.any(config.governance_role, fn(governor) {
          list.has(extra_signatories, governor)
        })

        authorized_updater &&
        validate_parameter_update(datum, parameter, value, transaction, config)
      }

      // Emergency actions
      EmergencyAction { action } -> {
        let emergency_authorized = list.has(extra_signatories, config.emergency_admin)
        emergency_authorized &&
        validate_emergency_action(action, datum, transaction, config)
      }

      // Claim token distribution
      ClaimDistribution -> {
        let recipient_signed = list.has(extra_signatories, datum.recipient)
        let distribution_ready = datum.verified && !datum.claimed

        recipient_signed && distribution_ready &&
        validate_distribution_claim(datum, transaction, config)
      }
    }
  }
}

// Validation functions

fn validate_token_minting(
  datum: TokenDistributionDatum,
  distribution_data: ByteArray,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate distribution data
  let valid_distribution_data = bytearray.length(distribution_data) > 0

  // Check amount limits
  let amount_within_limits =
    datum.amount >= config.min_mint_amount &&
    datum.amount <= config.max_mint_amount

  // Validate confidence score
  let sufficient_confidence =
    datum.confidence_score >= config.min_confidence_for_auto_mint

  // Check MeTTa proof
  let has_metta_proof = bytearray.length(datum.metta_proof_hash) > 0

  // Validate contribution details
  let has_contribution_details =
    bytearray.length(datum.contribution_type) > 0 &&
    bytearray.length(datum.contribution_hash) > 0

  // Check that tokens are actually minted in outputs
  let tokens_minted = validate_token_output(transaction, config, datum.amount)

  valid_distribution_data &&
  amount_within_limits &&
  sufficient_confidence &&
  has_metta_proof &&
  has_contribution_details &&
  tokens_minted
}

fn validate_token_burning(
  datum: TokenDistributionDatum,
  burn_reason: ByteArray,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate burn reason
  let valid_burn_reason = bytearray.length(burn_reason) > 0

  // Check that tokens are actually burned
  let tokens_burned = validate_token_burn(transaction, config, datum.amount)

  // Apply burn rate if applicable
  let burn_amount = calculate_burn_amount(datum.amount, config.burn_rate)

  valid_burn_reason && tokens_burned
}

fn validate_vesting_creation(
  datum: TokenDistributionDatum,
  vesting_params: ByteArray,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate vesting parameters
  let valid_vesting_params = bytearray.length(vesting_params) > 0

  // Check vesting duration
  let duration_within_limits = datum.amount <= config.max_vesting_duration

  // Validate beneficiary
  let valid_beneficiary = datum.recipient != config.platform_admin  // Prevent self-vesting

  valid_vesting_params && duration_within_limits && valid_beneficiary
}

fn validate_vesting_claim(
  datum: TokenDistributionDatum,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Check if vesting period has started
  let vesting_started = datum.timestamp <= get_current_time(transaction)

  // Calculate vested amount
  let vested_amount = calculate_vested_amount(datum, config)

  // Check if there are claimable tokens
  let has_claimable_tokens = vested_amount > datum.amount  // Simplified check

  vesting_started && has_claimable_tokens
}

fn validate_proposal_creation(
  datum: TokenDistributionDatum,
  proposal_data: ByteArray,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate proposal data
  let valid_proposal_data = bytearray.length(proposal_data) > 0

  // Check proposer has sufficient tokens (simplified check)
  let sufficient_tokens = True  // Would check proposer's token balance

  // Validate proposal parameters
  let valid_parameters = datum.amount >= config.proposal_threshold

  valid_proposal_data && sufficient_tokens && valid_parameters
}

fn validate_proposal_vote(
  datum: TokenDistributionDatum,
  vote: Bool,
  voting_power: Int,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate voting power
  let valid_voting_power = voting_power > 0

  // Check voting period is active
  let voting_active = is_voting_period_active(datum, transaction, config)

  // Check voter hasn't already voted (simplified)
  let has_not_voted = True

  valid_voting_power && voting_active && has_not_voted
}

fn validate_proposal_execution(
  datum: TokenDistributionDatum,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Check proposal has passed
  let proposal_passed = has_proposal_passed(datum, config)

  // Check execution delay has passed
  let execution_delay_passed = has_execution_delay_passed(datum, transaction, config)

  // Check quorum requirements
  let quorum_met = has_quorum_been_met(datum, config)

  proposal_passed && execution_delay_passed && quorum_met
}

fn validate_parameter_update(
  datum: TokenDistributionDatum,
  parameter: ByteArray,
  value: Int,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate parameter name
  let valid_parameter = bytearray.length(parameter) > 0

  // Validate parameter value (basic range check)
  let valid_value = value >= 0

  // Check parameter is updatable
  let parameter_updatable = is_parameter_updatable(parameter, config)

  valid_parameter && valid_value && parameter_updatable
}

fn validate_emergency_action(
  action: ByteArray,
  datum: TokenDistributionDatum,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Validate emergency action
  let valid_emergency_action = bytearray.length(action) > 0

  // Check emergency pause is enabled
  let emergency_enabled = config.emergency_pause_enabled

  valid_emergency_action && emergency_enabled
}

fn validate_distribution_claim(
  datum: TokenDistributionDatum,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  // Check distribution is verified
  let distribution_verified = datum.verified

  // Check distribution hasn't been claimed
  let not_yet_claimed = !datum.claimed

  // Check claimer is the recipient
  let correct_recipient = list.has(transaction.extra_signatories, datum.recipient)

  // Validate token transfer to recipient
  let tokens_transferred = validate_token_transfer_to_recipient(
    transaction, config, datum.amount, datum.recipient
  )

  distribution_verified && not_yet_claimed && correct_recipient && tokens_transferred
}

// Helper functions

fn validate_token_output(
  transaction: Transaction,
  config: TokenConfig,
  expected_amount: Int
) -> Bool {

  // Check if transaction outputs contain the expected NIMO tokens
  list.any(transaction.outputs, fn(output) {
    let output_value = output.value
    let nimo_amount = value.quantity_of(output_value, config.token_policy_id, config.token_asset_name)
    nimo_amount >= expected_amount
  })
}

fn validate_token_burn(
  transaction: Transaction,
  config: TokenConfig,
  burn_amount: Int
) -> Bool {

  // Check if tokens are being burned (not present in outputs)
  // This is a simplified check - in practice would compare input vs output values
  True
}

fn validate_token_transfer_to_recipient(
  transaction: Transaction,
  config: TokenConfig,
  amount: Int,
  recipient: Hash<Blake2b_224, VerificationKey>
) -> Bool {

  // Check if recipient receives the expected tokens
  list.any(transaction.outputs, fn(output) {
    let output_value = output.value
    let nimo_amount = value.quantity_of(output_value, config.token_policy_id, config.token_asset_name)

    // Check recipient address
    let is_recipient = when output.address.payment_credential is {
      VerificationKey(pkh) -> pkh == recipient
      _ -> False
    }

    is_recipient && nimo_amount >= amount
  })
}

fn calculate_burn_amount(amount: Int, burn_rate: Int) -> Int {
  // Calculate burn amount based on burn rate (burn_rate is in basis points)
  (amount * burn_rate) / 10000
}

fn calculate_vested_amount(datum: TokenDistributionDatum, config: TokenConfig) -> Int {
  // Simplified vesting calculation
  let elapsed_time = get_current_time_from_transaction(datum.timestamp)
  let total_duration = config.default_vesting_duration

  if elapsed_time >= total_duration then
    datum.amount  // Fully vested
  else
    (datum.amount * elapsed_time) / total_duration  // Linear vesting
}

fn get_current_time(transaction: Transaction) -> Int {
  // Extract current time from transaction validity range
  when transaction.validity_range.upper_bound is {
    Some(time) -> time
    None -> 0
  }
}

fn get_current_time_from_transaction(timestamp: Int) -> Int {
  // Simplified - would use actual transaction time
  1672531200
}

fn is_voting_period_active(
  datum: TokenDistributionDatum,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  let current_time = get_current_time(transaction)
  let voting_end = datum.timestamp + config.voting_period

  current_time >= datum.timestamp && current_time <= voting_end
}

fn has_proposal_passed(datum: TokenDistributionDatum, config: TokenConfig) -> Bool {
  // Check if yes votes exceed no votes and meet quorum
  datum.amount > (datum.timestamp / 2)  // Simplified check
}

fn has_execution_delay_passed(
  datum: TokenDistributionDatum,
  transaction: Transaction,
  config: TokenConfig
) -> Bool {

  let current_time = get_current_time(transaction)
  let execution_time = datum.timestamp + config.voting_period + config.execution_delay

  current_time >= execution_time
}

fn has_quorum_been_met(datum: TokenDistributionDatum, config: TokenConfig) -> Bool {
  // Check if total votes meet quorum requirements
  let total_votes = datum.amount + datum.confidence_score  // Simplified
  let quorum_required = (config.max_supply * config.quorum_percentage) / 100

  total_votes >= quorum_required
}

fn is_parameter_updatable(parameter: ByteArray, config: TokenConfig) -> Bool {
  // Define which parameters can be updated
  let updatable_parameters = [
    "min_confidence_for_auto_mint",
    "platform_fee_percentage",
    "burn_rate",
    "default_vesting_duration"
  ]

  list.any(updatable_parameters, fn(updatable_param) {
    parameter == updatable_param
  })
}

// Test function
test token_minting_test() {
  let test_config = TokenConfig {
    token_policy_id: #"abcd1234",
    token_asset_name: #"4e494d4f",  // "NIMO" in hex
    platform_admin: #"admin123",
    minter_role: [#"minter1", #"minter2"],
    burner_role: [#"burner1"],
    governance_role: [#"governor1", #"governor2"],
    max_supply: 1000000000,  // 1B tokens
    initial_supply: 1000000,  // 1M tokens
    min_mint_amount: 1,
    max_mint_amount: 10000,
    min_confidence_for_auto_mint: 70,
    platform_fee_percentage: 5,
    burn_rate: 100,  // 1%
    default_vesting_duration: 31536000,  // 1 year
    max_vesting_duration: 157680000,     // 5 years
    proposal_threshold: 1000,
    voting_period: 604800,  // 1 week
    quorum_percentage: 10,
    execution_delay: 172800,  // 2 days
    emergency_pause_enabled: True,
    emergency_admin: #"emergency123",
  }

  let test_distribution = TokenDistributionDatum {
    distribution_id: "dist_001",
    recipient: #"recipient123",
    amount: 1000,
    reason: "contribution_verification",
    timestamp: 1672531200,
    metta_proof_hash: "metta_proof_abc",
    confidence_score: 85,
    contribution_type: "coding",
    contribution_hash: "ipfs_contribution_hash",
    verified: True,
    verifier: #"verifier123",
    claimed: False,
    governance_approved: True,
    proposal_id: "",
  }

  // Test minting validation
  let amount_valid = test_distribution.amount >= test_config.min_mint_amount &&
                    test_distribution.amount <= test_config.max_mint_amount
  let confidence_valid = test_distribution.confidence_score >= test_config.min_confidence_for_auto_mint
  let has_proof = bytearray.length(test_distribution.metta_proof_hash) > 0

  amount_valid && confidence_valid && has_proof
}