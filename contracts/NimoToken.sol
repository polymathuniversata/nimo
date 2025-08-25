// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title NimoToken
 * @dev ERC20 token for Nimo reputation system
 * Used for governance, accessing opportunities, and measuring reputation
 */
contract NimoToken is ERC20, AccessControl, Pausable {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    
    // Token distribution tracking
    struct Distribution {
        address recipient;
        uint256 amount;
        string reason;
        uint256 timestamp;
        string mettaProof; // MeTTa proof of contribution
    }
    
    mapping(uint256 => Distribution) public distributions;
    uint256 private _nextDistributionId = 1;
    
    // Events
    event TokensDistributed(address indexed recipient, uint256 amount, string reason);
    event TokensBurned(address indexed from, uint256 amount, string reason);
    event MeTTaProofAttached(uint256 indexed distributionId, string proof);
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(BURNER_ROLE, msg.sender);
        
        // Mint initial supply to deployer
        _mint(msg.sender, initialSupply * 10**decimals());
    }
    
    /**
     * @dev Mint tokens for verified contributions
     * @param to Address to mint tokens to
     * @param amount Amount of tokens to mint
     * @param reason Reason for minting (contribution type)
     * @param mettaProof MeTTa proof of the contribution
     */
    function mintForContribution(
        address to,
        uint256 amount,
        string memory reason,
        string memory mettaProof
    ) external onlyRole(MINTER_ROLE) whenNotPaused {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Amount must be greater than 0");
        
        uint256 distributionId = _nextDistributionId++;
        
        distributions[distributionId] = Distribution({
            recipient: to,
            amount: amount,
            reason: reason,
            timestamp: block.timestamp,
            mettaProof: mettaProof
        });
        
        _mint(to, amount);
        
        emit TokensDistributed(to, amount, reason);
        emit MeTTaProofAttached(distributionId, mettaProof);
    }
    
    /**
     * @dev Burn tokens from an account (for accessing opportunities)
     * @param from Address to burn tokens from
     * @param amount Amount of tokens to burn
     * @param reason Reason for burning (opportunity access)
     */
    function burnForOpportunity(
        address from,
        uint256 amount,
        string memory reason
    ) external onlyRole(BURNER_ROLE) whenNotPaused {
        require(from != address(0), "Cannot burn from zero address");
        require(balanceOf(from) >= amount, "Insufficient balance");
        
        _burn(from, amount);
        
        emit TokensBurned(from, amount, reason);
    }
    
    /**
     * @dev Pause token transfers
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause token transfers
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Override transfer to add pause functionality
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
    
    /**
     * @dev Get distribution details by ID
     */
    function getDistribution(uint256 distributionId) external view returns (Distribution memory) {
        return distributions[distributionId];
    }
    
    /**
     * @dev Get total number of distributions
     */
    function getTotalDistributions() external view returns (uint256) {
        return _nextDistributionId - 1;
    }
}