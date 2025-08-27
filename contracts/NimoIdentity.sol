// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

/**
 * @title NimoIdentity
 * @dev Core smart contract for Nimo decentralized identity and reputation system on Base
 * Integrates with MeTTa logic layer for autonomous decision making
 * Optimized for Base L2 with IPFS metadata storage and OpenZeppelin MCP patterns
 */
contract NimoIdentity is ERC721, AccessControl, ReentrancyGuard {
    using Strings for uint256;

    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant METTA_AGENT_ROLE = keccak256("METTA_AGENT_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    // Base network configuration
    uint256 public constant BASE_CHAIN_ID = 8453;
    uint256 public constant BASE_SEPOLIA_CHAIN_ID = 84532;

    // Identity NFT structure with IPFS metadata
    struct Identity {
        string username;
        string metadataURI; // IPFS URI
        uint256 reputationScore;
        uint256 tokenBalance;
        bool isActive;
        uint256 createdAt;
        uint256 lastActivity;
        string did; // Decentralized Identifier
    }

    // Contribution tracking with MeTTa integration
    struct Contribution {
        uint256 identityId;
        string contributionType;
        string description;
        string evidenceURI; // IPFS URI for evidence
        bool verified;
        address verifier;
        uint256 tokensAwarded;
        uint256 timestamp;
        string mettaHash; // Hash of MeTTa representation
        uint256 confidence; // MeTTa confidence score
    }

    // Impact Bond structure for diaspora investment
    struct ImpactBond {
        uint256 bondId;
        address creator;
        string title;
        string description;
        string metadataURI; // IPFS URI for detailed project info
        uint256 targetAmount;
        uint256 currentAmount;
        uint256 maturityDate;
        bool isActive;
        string[] milestones;
        mapping(string => bool) milestoneComplete;
        mapping(address => uint256) investments;
    }

    // MeTTa Rule structure for autonomous execution
    struct MeTTaRule {
        string rule;
        address executor;
        uint256 executionCount;
        uint256 lastExecuted;
        bool isActive;
    }

    // State variables
    mapping(uint256 => Identity) public identities;
    mapping(uint256 => Contribution) public contributions;
    mapping(uint256 => ImpactBond) public impactBonds;
    mapping(string => uint256) public usernameToTokenId;
    mapping(address => uint256) public addressToTokenId;
    mapping(string => uint256) public didToTokenId;
    mapping(uint256 => MeTTaRule) public mettaRules;

    uint256 private _nextTokenId = 1;
    uint256 private _nextContributionId = 1;
    uint256 private _nextBondId = 1;
    uint256 private _nextRuleId = 1;

    // Protocol parameters (governable)
    uint256 public reputationPerToken = 10; // 10% of tokens convert to reputation
    uint256 public minConfidenceThreshold = 70; // Minimum confidence for auto-verification
    uint256 public maxGasForMeTTa = 500000; // Gas limit for MeTTa operations

    // Events
    event IdentityCreated(uint256 indexed tokenId, string username, address owner, string did);
    event ContributionAdded(uint256 indexed contributionId, uint256 indexed identityId, string contributionType);
    event ContributionVerified(uint256 indexed contributionId, address verifier, uint256 tokensAwarded, uint256 confidence);
    event TokensAwarded(uint256 indexed identityId, uint256 amount, string reason);
    event ImpactBondCreated(uint256 indexed bondId, address creator, uint256 targetAmount);
    event BondInvestment(uint256 indexed bondId, address investor, uint256 amount);
    event MilestoneCompleted(uint256 indexed bondId, string milestone);
    event MeTTaRuleExecuted(uint256 indexed ruleId, string rule, string result);
    event ProtocolParameterUpdated(string parameter, uint256 oldValue, uint256 newValue);

    constructor() ERC721("NimoIdentity", "NIMO") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
        _grantRole(METTA_AGENT_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);
    }

    /**
     * @dev Validate IPFS URI format
     * @param uri The URI to validate
     */
    function _isValidIPFSURI(string memory uri) internal pure returns (bool) {
        bytes memory uriBytes = bytes(uri);
        if (uriBytes.length < 7) return false;

        // Check for ipfs:// protocol
        if (uriBytes[0] == 'i' && uriBytes[1] == 'p' && uriBytes[2] == 'f' &&
            uriBytes[3] == 's' && uriBytes[4] == ':' && uriBytes[5] == '/' && uriBytes[6] == '/') {
            return true;
        }

        // Check for https://ipfs.io/ or https://gateway.pinata.cloud/
        if (uriBytes.length > 15) {
            if ((uriBytes[0] == 'h' && uriBytes[1] == 't' && uriBytes[2] == 't' && uriBytes[3] == 'p' &&
                 uriBytes[4] == 's' && uriBytes[5] == ':' && uriBytes[6] == '/' && uriBytes[7] == '/') &&
                ((uriBytes[8] == 'i' && uriBytes[9] == 'p' && uriBytes[10] == 'f' && uriBytes[11] == 's' &&
                  uriBytes[12] == '.' && uriBytes[13] == 'i' && uriBytes[14] == 'o') ||
                 (uriBytes[8] == 'g' && uriBytes[9] == 'a' && uriBytes[10] == 't' && uriBytes[11] == 'e' &&
                  uriBytes[12] == 'w' && uriBytes[13] == 'a' && uriBytes[14] == 'y'))) {
                return true;
            }
        }

        return false;
    }

    /**
     * @dev Create a new decentralized identity with DID
     * @param username Unique username for the identity
     * @param metadataURI IPFS URI containing identity metadata
     * @param did Decentralized Identifier
     */
    function createIdentity(
        string memory username,
        string memory metadataURI,
        string memory did
    ) external {
        require(usernameToTokenId[username] == 0, "Username already exists");
        require(addressToTokenId[msg.sender] == 0, "Address already has identity");
        require(didToTokenId[did] == 0, "DID already registered");
        require(_isValidIPFSURI(metadataURI), "Invalid IPFS URI for metadata");
        require(bytes(did).length > 0, "DID cannot be empty");

        uint256 tokenId = _nextTokenId++;

        identities[tokenId] = Identity({
            username: username,
            metadataURI: metadataURI,
            reputationScore: 0,
            tokenBalance: 0,
            isActive: true,
            createdAt: block.timestamp,
            lastActivity: block.timestamp,
            did: did
        });

        usernameToTokenId[username] = tokenId;
        addressToTokenId[msg.sender] = tokenId;
        didToTokenId[did] = tokenId;

        _safeMint(msg.sender, tokenId);

        emit IdentityCreated(tokenId, username, msg.sender, did);
    }

    /**
     * @dev Add a contribution to an identity with IPFS evidence
     * @param contributionType Type of contribution (e.g., "hackathon", "volunteer")
     * @param description Description of the contribution
     * @param evidenceURI IPFS URI containing evidence of contribution
     * @param mettaHash Hash of the MeTTa representation
     */
    function addContribution(
        string memory contributionType,
        string memory description,
        string memory evidenceURI,
        string memory mettaHash
    ) external {
        uint256 identityId = addressToTokenId[msg.sender];
        require(identityId != 0, "No identity found for address");
        require(identities[identityId].isActive, "Identity is not active");
        require(_isValidIPFSURI(evidenceURI), "Invalid IPFS URI for evidence");

        uint256 contributionId = _nextContributionId++;

        contributions[contributionId] = Contribution({
            identityId: identityId,
            contributionType: contributionType,
            description: description,
            evidenceURI: evidenceURI,
            verified: false,
            verifier: address(0),
            tokensAwarded: 0,
            timestamp: block.timestamp,
            mettaHash: mettaHash,
            confidence: 0
        });

        // Update identity activity
        identities[identityId].lastActivity = block.timestamp;

        emit ContributionAdded(contributionId, identityId, contributionType);
    }

    /**
     * @dev Verify a contribution with MeTTa confidence score
     * @param contributionId ID of the contribution to verify
     * @param tokensToAward Amount of reputation tokens to award
     * @param confidence MeTTa confidence score (0-100)
     */
    function verifyContribution(
        uint256 contributionId,
        uint256 tokensToAward,
        uint256 confidence
    ) external onlyRole(VERIFIER_ROLE) {
        require(contributions[contributionId].identityId != 0, "Contribution does not exist");
        require(!contributions[contributionId].verified, "Contribution already verified");
        require(confidence <= 100, "Confidence must be between 0-100");

        Contribution storage contribution = contributions[contributionId];
        contribution.verified = true;
        contribution.verifier = msg.sender;
        contribution.tokensAwarded = tokensToAward;
        contribution.confidence = confidence;

        // Award tokens to the identity
        Identity storage identity = identities[contribution.identityId];
        identity.tokenBalance += tokensToAward;
        identity.reputationScore += tokensToAward / reputationPerToken;
        identity.lastActivity = block.timestamp;

        emit ContributionVerified(contributionId, msg.sender, tokensToAward, confidence);
        emit TokensAwarded(contribution.identityId, tokensToAward, "Contribution verified");
    }

    /**
     * @dev Execute MeTTa autonomous agent logic with gas optimization
     * @param rule MeTTa rule to execute
     * @param targetIdentityId Target identity for the rule
     * @param tokensToAward Tokens to award based on MeTTa logic
     * @param confidence MeTTa confidence score
     */
    function executeMeTTaRule(
        string memory rule,
        uint256 targetIdentityId,
        uint256 tokensToAward,
        uint256 confidence
    ) external onlyRole(METTA_AGENT_ROLE) {
        require(identities[targetIdentityId].isActive, "Target identity not active");
        require(confidence >= minConfidenceThreshold, "Confidence below threshold");
        require(gasleft() >= maxGasForMeTTa, "Insufficient gas for MeTTa execution");

        // Store the rule for tracking
        uint256 ruleId = _nextRuleId++;
        mettaRules[ruleId] = MeTTaRule({
            rule: rule,
            executor: msg.sender,
            executionCount: 1,
            lastExecuted: block.timestamp,
            isActive: true
        });

        // Award tokens based on MeTTa agent decision
        if (tokensToAward > 0) {
            identities[targetIdentityId].tokenBalance += tokensToAward;
            identities[targetIdentityId].reputationScore += tokensToAward / reputationPerToken;
            identities[targetIdentityId].lastActivity = block.timestamp;

            emit TokensAwarded(targetIdentityId, tokensToAward, "MeTTa agent award");
        }

        emit MeTTaRuleExecuted(ruleId, rule, "executed successfully");
    }

    /**
     * @dev Create an impact bond with IPFS metadata
     * @param title Title of the impact bond
     * @param description Description of the project
     * @param metadataURI IPFS URI for detailed project information
     * @param targetAmount Target funding amount
     * @param maturityDate Bond maturity date
     * @param milestones Array of milestone descriptions
     */
    function createImpactBond(
        string memory title,
        string memory description,
        string memory metadataURI,
        uint256 targetAmount,
        uint256 maturityDate,
        string[] memory milestones
    ) external {
        uint256 identityId = addressToTokenId[msg.sender];
        require(identityId != 0, "Must have identity to create bond");
        require(maturityDate > block.timestamp, "Maturity date must be in future");
        require(_isValidIPFSURI(metadataURI), "Invalid IPFS URI for bond metadata");

        uint256 bondId = _nextBondId++;

        ImpactBond storage bond = impactBonds[bondId];
        bond.bondId = bondId;
        bond.creator = msg.sender;
        bond.title = title;
        bond.description = description;
        bond.metadataURI = metadataURI;
        bond.targetAmount = targetAmount;
        bond.currentAmount = 0;
        bond.maturityDate = maturityDate;
        bond.isActive = true;
        bond.milestones = milestones;

        emit ImpactBondCreated(bondId, msg.sender, targetAmount);
    }

    /**
     * @dev Update protocol parameters (governance only)
     * @param parameter Parameter name
     * @param value New value
     */
    function updateProtocolParameter(
        string memory parameter,
        uint256 value
    ) external onlyRole(GOVERNANCE_ROLE) {
        uint256 oldValue;

        if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("reputationPerToken"))) {
            oldValue = reputationPerToken;
            reputationPerToken = value;
        } else if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("minConfidenceThreshold"))) {
            oldValue = minConfidenceThreshold;
            minConfidenceThreshold = value;
        } else if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("maxGasForMeTTa"))) {
            oldValue = maxGasForMeTTa;
            maxGasForMeTTa = value;
        } else {
            revert("Unknown parameter");
        }

        emit ProtocolParameterUpdated(parameter, oldValue, value);
    }

    // View functions
    function getIdentity(uint256 tokenId) external view returns (Identity memory) {
        return identities[tokenId];
    }

    function getContribution(uint256 contributionId) external view returns (Contribution memory) {
        return contributions[contributionId];
    }

    function getIdentityByUsername(string memory username) external view returns (Identity memory) {
        uint256 tokenId = usernameToTokenId[username];
        return identities[tokenId];
    }

    function getIdentityByDID(string memory did) external view returns (Identity memory) {
        uint256 tokenId = didToTokenId[did];
        return identities[tokenId];
    }

    function getBondInvestment(uint256 bondId, address investor) external view returns (uint256) {
        return impactBonds[bondId].investments[investor];
    }

    function isMilestoneComplete(uint256 bondId, string memory milestone) external view returns (bool) {
        return impactBonds[bondId].milestoneComplete[milestone];
    }

    function getChainId() external view returns (uint256) {
        return block.chainid;
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}