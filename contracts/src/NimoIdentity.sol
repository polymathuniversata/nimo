// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title NimoIdentity
 * @dev Core smart contract for Nimo decentralized identity and reputation system
 * Integrates with MeTTa logic layer for autonomous decision making
 */
contract NimoIdentity is ERC721, AccessControl, ReentrancyGuard {
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant METTA_AGENT_ROLE = keccak256("METTA_AGENT_ROLE");
    
    // Identity NFT structure
    struct Identity {
        string username;
        string metadataURI;
        uint256 reputationScore;
        uint256 tokenBalance;
        bool isActive;
        uint256 createdAt;
    }
    
    // Contribution tracking
    struct Contribution {
        uint256 identityId;
        string contributionType;
        string description;
        string evidenceURI;
        bool verified;
        address verifier;
        uint256 tokensAwarded;
        uint256 timestamp;
        string mettaHash; // Hash of MeTTa representation
    }
    
    // Impact Bond structure
    struct ImpactBond {
        uint256 bondId;
        address creator;
        string title;
        string description;
        uint256 targetAmount;
        uint256 currentAmount;
        uint256 maturityDate;
        bool isActive;
        string[] milestones;
        mapping(string => bool) milestoneComplete;
        mapping(address => uint256) investments;
    }
    
    // State variables
    mapping(uint256 => Identity) public identities;
    mapping(uint256 => Contribution) public contributions;
    mapping(uint256 => ImpactBond) public impactBonds;
    mapping(string => uint256) public usernameToTokenId;
    mapping(address => uint256) public addressToTokenId;
    
    uint256 private _nextTokenId = 1;
    uint256 private _nextContributionId = 1;
    uint256 private _nextBondId = 1;
    
    // Events
    event IdentityCreated(uint256 indexed tokenId, string username, address owner);
    event ContributionAdded(uint256 indexed contributionId, uint256 indexed identityId, string contributionType);
    event ContributionVerified(uint256 indexed contributionId, address verifier, uint256 tokensAwarded);
    event TokensAwarded(uint256 indexed identityId, uint256 amount, string reason);
    event ImpactBondCreated(uint256 indexed bondId, address creator, uint256 targetAmount);
    event BondInvestment(uint256 indexed bondId, address investor, uint256 amount);
    event MilestoneCompleted(uint256 indexed bondId, string milestone);
    event MeTTaRuleExecuted(string rule, string result);
    
    constructor() ERC721("NimoIdentity", "NIMO") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
        _grantRole(METTA_AGENT_ROLE, msg.sender);
    }
    
    /**
     * @dev Create a new decentralized identity
     * @param username Unique username for the identity
     * @param metadataURI IPFS URI containing identity metadata
     */
    function createIdentity(string memory username, string memory metadataURI) external {
        require(usernameToTokenId[username] == 0, "Username already exists");
        require(addressToTokenId[msg.sender] == 0, "Address already has identity");
        
        uint256 tokenId = _nextTokenId++;
        
        identities[tokenId] = Identity({
            username: username,
            metadataURI: metadataURI,
            reputationScore: 0,
            tokenBalance: 0,
            isActive: true,
            createdAt: block.timestamp
        });
        
        usernameToTokenId[username] = tokenId;
        addressToTokenId[msg.sender] = tokenId;
        
        _safeMint(msg.sender, tokenId);
        
        emit IdentityCreated(tokenId, username, msg.sender);
    }
    
    /**
     * @dev Add a contribution to an identity
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
            mettaHash: mettaHash
        });
        
        emit ContributionAdded(contributionId, identityId, contributionType);
    }
    
    /**
     * @dev Verify a contribution (only verifiers can call)
     * @param contributionId ID of the contribution to verify
     * @param tokensToAward Amount of reputation tokens to award
     */
    function verifyContribution(uint256 contributionId, uint256 tokensToAward) 
        external 
        onlyRole(VERIFIER_ROLE) 
    {
        require(contributions[contributionId].identityId != 0, "Contribution does not exist");
        require(!contributions[contributionId].verified, "Contribution already verified");
        
        Contribution storage contribution = contributions[contributionId];
        contribution.verified = true;
        contribution.verifier = msg.sender;
        contribution.tokensAwarded = tokensToAward;
        
        // Award tokens to the identity
        Identity storage identity = identities[contribution.identityId];
        identity.tokenBalance += tokensToAward;
        identity.reputationScore += tokensToAward / 10; // 10% of tokens as reputation
        
        emit ContributionVerified(contributionId, msg.sender, tokensToAward);
        emit TokensAwarded(contribution.identityId, tokensToAward, "Contribution verified");
    }
    
    /**
     * @dev Execute MeTTa autonomous agent logic (only MeTTa agents can call)
     * @param rule MeTTa rule to execute
     * @param targetIdentityId Target identity for the rule
     * @param tokensToAward Tokens to award based on MeTTa logic
     */
    function executeMeTTaRule(
        string memory rule,
        uint256 targetIdentityId,
        uint256 tokensToAward
    ) external onlyRole(METTA_AGENT_ROLE) {
        require(identities[targetIdentityId].isActive, "Target identity not active");
        
        // Award tokens based on MeTTa agent decision
        if (tokensToAward > 0) {
            identities[targetIdentityId].tokenBalance += tokensToAward;
            identities[targetIdentityId].reputationScore += tokensToAward / 10;
            
            emit TokensAwarded(targetIdentityId, tokensToAward, "MeTTa agent award");
        }
        
        emit MeTTaRuleExecuted(rule, "executed successfully");
    }
    
    /**
     * @dev Create an impact bond for diaspora investment
     * @param title Title of the impact bond
     * @param description Description of the project
     * @param targetAmount Target funding amount
     * @param maturityDate Bond maturity date
     * @param milestones Array of milestone descriptions
     */
    function createImpactBond(
        string memory title,
        string memory description,
        uint256 targetAmount,
        uint256 maturityDate,
        string[] memory milestones
    ) external {
        uint256 identityId = addressToTokenId[msg.sender];
        require(identityId != 0, "Must have identity to create bond");
        require(maturityDate > block.timestamp, "Maturity date must be in future");
        
        uint256 bondId = _nextBondId++;
        
        ImpactBond storage bond = impactBonds[bondId];
        bond.bondId = bondId;
        bond.creator = msg.sender;
        bond.title = title;
        bond.description = description;
        bond.targetAmount = targetAmount;
        bond.currentAmount = 0;
        bond.maturityDate = maturityDate;
        bond.isActive = true;
        bond.milestones = milestones;
        
        emit ImpactBondCreated(bondId, msg.sender, targetAmount);
    }
    
    /**
     * @dev Invest in an impact bond
     * @param bondId ID of the bond to invest in
     */
    function investInBond(uint256 bondId) external payable nonReentrant {
        require(impactBonds[bondId].isActive, "Bond is not active");
        require(msg.value > 0, "Investment amount must be greater than 0");
        require(block.timestamp < impactBonds[bondId].maturityDate, "Bond has matured");
        
        ImpactBond storage bond = impactBonds[bondId];
        bond.investments[msg.sender] += msg.value;
        bond.currentAmount += msg.value;
        
        emit BondInvestment(bondId, msg.sender, msg.value);
    }
    
    /**
     * @dev Complete a milestone for an impact bond
     * @param bondId ID of the bond
     * @param milestone Milestone description
     */
    function completeMilestone(uint256 bondId, string memory milestone) 
        external 
        onlyRole(VERIFIER_ROLE) 
    {
        require(impactBonds[bondId].isActive, "Bond is not active");
        require(!impactBonds[bondId].milestoneComplete[milestone], "Milestone already completed");
        
        impactBonds[bondId].milestoneComplete[milestone] = true;
        
        emit MilestoneCompleted(bondId, milestone);
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
    
    function getBondInvestment(uint256 bondId, address investor) external view returns (uint256) {
        return impactBonds[bondId].investments[investor];
    }
    
    function isMilestoneComplete(uint256 bondId, string memory milestone) external view returns (bool) {
        return impactBonds[bondId].milestoneComplete[milestone];
    }
}