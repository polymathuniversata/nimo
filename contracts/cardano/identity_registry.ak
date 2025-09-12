// Nimo Platform - Identity Registry Smart Contract
// Written in Aiken for Cardano blockchain
// This contract manages user identities and reputation scores

use aiken/dict.{Dict}
use aiken/hash.{Blake2b_224, Hash}
use aiken/list
use aiken/transaction.{ScriptContext, Transaction, InlineDatum, OutputReference}
use aiken/transaction/credential.{VerificationKey}
use aiken/transaction/value.{PolicyId, AssetName, Value}
use aiken/bytearray

// Identity data structure
pub type IdentityDatum {
  // Core identity information
  owner: Hash<Blake2b_224, VerificationKey>,   // Owner's public key hash
  username: ByteArray,                         // Unique username
  display_name: ByteArray,                     // Display name
  
  // Profile metadata
  profile_metadata_hash: ByteArray,            // IPFS hash of profile data
  avatar_hash: ByteArray,                      // IPFS hash of avatar image
  bio: ByteArray,                              // Short biography
  
  // Reputation and activity
  reputation_score: Int,                       // Calculated reputation (0-10000)
  total_contributions: Int,                    // Number of verified contributions
  total_tokens_earned: Int,                    // Total NIMO tokens earned
  
  // Identity verification
  verification_level: Int,                     // 0=unverified, 1=basic, 2=enhanced, 3=expert
  verifications: List<VerificationRecord>,     // List of verifications received
  
  // Social connections
  followers_count: Int,
  following_count: Int,
  endorsements: List<Hash<Blake2b_224, VerificationKey>>,  // Endorsements from other users
  
  // Platform status
  is_active: Bool,
  is_verified: Bool,
  created_at: Int,                             // Timestamp
  updated_at: Int,                             // Last update timestamp
  
  // Advanced features
  skill_tags: List<ByteArray>,                 // User's skill tags
  location: ByteArray,                         // Location (optional)
  preferred_language: ByteArray,               // Preferred language
  
  // Platform-specific data
  nft_token_id: Int,                          // Associated NFT token ID (if any)
  did_document_hash: ByteArray,               // DID document hash
  
  // Privacy settings
  profile_visibility: Int,                     // 0=private, 1=followers, 2=public
  contact_preferences: Int,                    // Contact settings
}

// Verification record for different types of verifications
pub type VerificationRecord {
  verifier: Hash<Blake2b_224, VerificationKey>,
  verification_type: ByteArray,               // "email", "phone", "document", "skill", etc.
  verification_data_hash: ByteArray,          // Hash of verification data
  verified_at: Int,
  expires_at: Int,                            // Expiration timestamp (0 = no expiration)
  is_active: Bool,
}

// Actions that can be performed on identities
pub type IdentityRedeemer {
  CreateIdentity
  UpdateProfile
  AddVerification
  RevokeVerification  
  UpdateReputation { 
    score_change: Int, 
    reason: ByteArray,
    proof_hash: ByteArray 
  }
  EndorseUser { endorsed_user: Hash<Blake2b_224, VerificationKey> }
  TransferIdentity { new_owner: Hash<Blake2b_224, VerificationKey> }
  AdminAction { action: ByteArray, target: Hash<Blake2b_224, VerificationKey> }
}

// Platform configuration for identity management
pub type IdentityConfig {
  // Authorized addresses
  platform_admin: Hash<Blake2b_224, VerificationKey>,
  reputation_oracle: Hash<Blake2b_224, VerificationKey>,  // Can update reputation
  verifier_pool: List<Hash<Blake2b_224, VerificationKey>>,
  
  // Identity parameters
  min_username_length: Int,
  max_username_length: Int,
  max_bio_length: Int,
  max_display_name_length: Int,
  
  // Reputation parameters
  max_reputation_score: Int,
  reputation_decay_rate: Int,                 // Reputation decay per day
  endorsement_value: Int,                     // Reputation points per endorsement
  
  // Verification settings
  verification_expiry_days: Int,              // Default expiration for verifications
  required_verifications_for_expert: Int,     // Required verifications for expert level
  
  // Platform settings
  identity_creation_fee: Int,                 // ADA fee to create identity
  username_change_fee: Int,                   // ADA fee to change username
  profile_update_cooldown: Int,               // Cooldown period between updates (seconds)
}

// Main identity validator
validator(config: IdentityConfig) {
  fn identity_validator(
    datum: IdentityDatum, 
    redeemer: IdentityRedeemer, 
    context: ScriptContext
  ) -> Bool {
    
    let ScriptContext { transaction, purpose } = context
    let Transaction { inputs, outputs, validity_range, extra_signatories, .. } = transaction
    
    when redeemer is {
      
      // Create a new identity
      CreateIdentity -> {
        validate_identity_creation(datum, transaction, config)
      }
      
      // Update profile information
      UpdateProfile -> {
        let owner_signed = list.has(extra_signatories, datum.owner)
        owner_signed && validate_profile_update(datum, transaction, config)
      }
      
      // Add a new verification to identity
      AddVerification -> {
        let is_authorized_verifier = 
          list.any(config.verifier_pool, fn(verifier) { 
            list.has(extra_signatories, verifier) 
          }) ||
          list.has(extra_signatories, config.platform_admin)
        
        is_authorized_verifier && validate_verification_addition(datum, transaction, config)
      }
      
      // Revoke a verification
      RevokeVerification -> {
        let owner_signed = list.has(extra_signatories, datum.owner)
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        (owner_signed || admin_signed) && validate_verification_revocation(datum, transaction, config)
      }
      
      // Update reputation score (by oracle or admin)
      UpdateReputation { score_change, reason, proof_hash } -> {
        let oracle_signed = list.has(extra_signatories, config.reputation_oracle)
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        
        (oracle_signed || admin_signed) && 
        validate_reputation_update(datum, score_change, reason, proof_hash, transaction, config)
      }
      
      // Endorse another user
      EndorseUser { endorsed_user } -> {
        let endorser_signed = list.has(extra_signatories, datum.owner)
        endorser_signed && validate_user_endorsement(datum, endorsed_user, transaction, config)
      }
      
      // Transfer identity ownership
      TransferIdentity { new_owner } -> {
        let current_owner_signed = list.has(extra_signatories, datum.owner)
        let new_owner_signed = list.has(extra_signatories, new_owner)
        
        current_owner_signed && new_owner_signed && 
        validate_identity_transfer(datum, new_owner, transaction, config)
      }
      
      // Administrative actions
      AdminAction { action, target } -> {
        let admin_signed = list.has(extra_signatories, config.platform_admin)
        admin_signed && validate_admin_action(action, target, datum, transaction, config)
      }
    }
  }
}

// Validate identity creation
fn validate_identity_creation(
  datum: IdentityDatum, 
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Check that owner signed the transaction
  let owner_signed = list.has(transaction.extra_signatories, datum.owner)
  
  // Validate username requirements
  let username_length = bytearray.length(datum.username)
  let username_valid = 
    username_length >= config.min_username_length && 
    username_length <= config.max_username_length &&
    is_valid_username_format(datum.username)
  
  // Validate display name
  let display_name_length = bytearray.length(datum.display_name)
  let display_name_valid = display_name_length <= config.max_display_name_length
  
  // Validate bio length
  let bio_length = bytearray.length(datum.bio)
  let bio_valid = bio_length <= config.max_bio_length
  
  // Check initial values are correct
  let initial_values_correct = 
    datum.reputation_score == 0 &&
    datum.total_contributions == 0 &&
    datum.total_tokens_earned == 0 &&
    datum.verification_level == 0 &&
    list.length(datum.verifications) == 0 &&
    datum.followers_count == 0 &&
    datum.following_count == 0 &&
    list.length(datum.endorsements) == 0 &&
    datum.is_active == True &&
    datum.is_verified == False &&
    datum.created_at > 0 &&
    datum.updated_at == datum.created_at
  
  // Check identity creation fee is paid
  let creation_fee_paid = validate_fee_payment(transaction, config.identity_creation_fee)
  
  owner_signed && 
  username_valid && 
  display_name_valid && 
  bio_valid && 
  initial_values_correct &&
  creation_fee_paid
}

// Validate profile update
fn validate_profile_update(
  datum: IdentityDatum, 
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Check update cooldown
  let current_time = get_current_time(transaction.validity_range)
  let cooldown_passed = 
    current_time >= datum.updated_at + config.profile_update_cooldown
  
  // Validate field lengths
  let display_name_valid = 
    bytearray.length(datum.display_name) <= config.max_display_name_length
  let bio_valid = 
    bytearray.length(datum.bio) <= config.max_bio_length
  
  // Check that updated_at timestamp is updated
  let timestamp_updated = datum.updated_at > datum.created_at
  
  cooldown_passed && display_name_valid && bio_valid && timestamp_updated
}

// Validate verification addition
fn validate_verification_addition(
  datum: IdentityDatum, 
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Check that a new verification was added
  let has_new_verification = list.length(datum.verifications) > 0
  
  // Validate each verification record
  let all_verifications_valid = list.all(datum.verifications, fn(verification) {
    verification.verified_at > 0 &&
    bytearray.length(verification.verification_type) > 0 &&
    bytearray.length(verification.verification_data_hash) > 0 &&
    verification.is_active == True
  })
  
  // Update verification level if applicable
  let verification_level_updated = 
    calculate_verification_level(datum.verifications, config) == datum.verification_level
  
  has_new_verification && all_verifications_valid && verification_level_updated
}

// Validate reputation update
fn validate_reputation_update(
  datum: IdentityDatum, 
  score_change: Int, 
  reason: ByteArray, 
  proof_hash: ByteArray,
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Check that reputation score is within valid range
  let new_score = datum.reputation_score
  let score_within_range = 
    new_score >= 0 && new_score <= config.max_reputation_score
  
  // Validate reason and proof
  let has_valid_reason = bytearray.length(reason) > 0
  let has_valid_proof = bytearray.length(proof_hash) > 0
  
  // Check that updated_at timestamp is updated
  let timestamp_updated = datum.updated_at > datum.created_at
  
  score_within_range && has_valid_reason && has_valid_proof && timestamp_updated
}

// Validate user endorsement
fn validate_user_endorsement(
  datum: IdentityDatum, 
  endorsed_user: Hash<Blake2b_224, VerificationKey>,
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Check that endorser is not endorsing themselves
  let not_self_endorsement = datum.owner != endorsed_user
  
  // Check that user hasn't already endorsed this user
  let not_already_endorsed = !list.has(datum.endorsements, endorsed_user)
  
  // Check that endorser has sufficient reputation to endorse
  let sufficient_reputation = datum.reputation_score >= 100  // Minimum reputation to endorse
  
  not_self_endorsement && not_already_endorsed && sufficient_reputation
}

// Validate identity transfer
fn validate_identity_transfer(
  datum: IdentityDatum, 
  new_owner: Hash<Blake2b_224, VerificationKey>,
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Check that new owner is different from current owner
  let different_owner = datum.owner != new_owner
  
  // Check that identity is active and verified
  let identity_transferable = datum.is_active && datum.is_verified
  
  // Validate that transfer fee is paid (if required)
  let transfer_fee_paid = True  // Could add transfer fee if needed
  
  different_owner && identity_transferable && transfer_fee_paid
}

// Validate admin actions
fn validate_admin_action(
  action: ByteArray,
  target: Hash<Blake2b_224, VerificationKey>,
  datum: IdentityDatum, 
  transaction: Transaction, 
  config: IdentityConfig
) -> Bool {
  
  // Define allowed admin actions
  let valid_actions = [
    "suspend_identity",
    "reactivate_identity",
    "force_verification",
    "reset_reputation",
    "ban_user",
    "unban_user"
  ]
  
  list.any(valid_actions, fn(valid_action) { 
    action == valid_action 
  })
}

// Helper function to validate username format
fn is_valid_username_format(username: ByteArray) -> Bool {
  // Username should only contain alphanumeric characters and underscores
  // This is a simplified validation - in production, you'd want more robust checking
  bytearray.length(username) > 0
}

// Calculate verification level based on verifications
fn calculate_verification_level(
  verifications: List<VerificationRecord>, 
  config: IdentityConfig
) -> Int {
  
  let active_verifications = list.filter(verifications, fn(v) { v.is_active })
  let verification_count = list.length(active_verifications)
  
  if verification_count == 0 then
    0  // Unverified
  else if verification_count >= config.required_verifications_for_expert then
    3  // Expert
  else if verification_count >= 2 then
    2  // Enhanced
  else
    1  // Basic
}

// Validate fee payment (simplified - in production you'd check specific outputs)
fn validate_fee_payment(transaction: Transaction, required_fee: Int) -> Bool {
  // For now, just return True - in production, you'd validate ADA payment
  True
}

// Get current time from validity range
fn get_current_time(validity_range) -> Int {
  // Simplified - in production, you'd extract from validity range
  1672531200  // Placeholder timestamp
}

// Test function
test identity_creation_test() {
  let test_config = IdentityConfig {
    platform_admin: #"admin123",
    reputation_oracle: #"oracle456",
    verifier_pool: [#"verifier1", #"verifier2"],
    min_username_length: 3,
    max_username_length: 20,
    max_bio_length: 500,
    max_display_name_length: 50,
    max_reputation_score: 10000,
    reputation_decay_rate: 1,
    endorsement_value: 10,
    verification_expiry_days: 365,
    required_verifications_for_expert: 3,
    identity_creation_fee: 1000000,  // 1 ADA
    username_change_fee: 500000,     // 0.5 ADA
    profile_update_cooldown: 3600,   // 1 hour
  }
  
  let test_datum = IdentityDatum {
    owner: #"user123",
    username: "alice",
    display_name: "Alice Smith",
    profile_metadata_hash: "ipfs_profile_hash",
    avatar_hash: "ipfs_avatar_hash",
    bio: "Blockchain developer and community organizer",
    reputation_score: 0,
    total_contributions: 0,
    total_tokens_earned: 0,
    verification_level: 0,
    verifications: [],
    followers_count: 0,
    following_count: 0,
    endorsements: [],
    is_active: True,
    is_verified: False,
    created_at: 1672531200,
    updated_at: 1672531200,
    skill_tags: ["blockchain", "solidity", "cardano"],
    location: "Lagos, Nigeria",
    preferred_language: "English",
    nft_token_id: 0,
    did_document_hash: "did_hash_123",
    profile_visibility: 2,
    contact_preferences: 1,
  }
  
  // Test username validation
  let username_valid = 
    bytearray.length(test_datum.username) >= test_config.min_username_length &&
    bytearray.length(test_datum.username) <= test_config.max_username_length
  
  username_valid
}