// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title NimoToken
 * @dev ERC20 token for Nimo reputation system on Base
 * Used for governance, accessing opportunities, and measuring reputation
 * Includes voting capabilities and MeTTa integration
 */
contract NimoToken is ERC20, AccessControl, Pausable, ERC20Votes {
    using Strings for uint256;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    // Base network configuration
    uint256 public constant BASE_CHAIN_ID = 8453;
    uint256 public constant BASE_SEPOLIA_CHAIN_ID = 84532;

    // Token distribution tracking with MeTTa integration
    struct Distribution {
        address recipient;
        uint256 amount;
        string reason;
        uint256 timestamp;
        string mettaProof; // MeTTa proof of contribution
        uint256 confidence; // MeTTa confidence score
        string contributionType;
    }

    // Vesting schedule for team and advisors
    struct VestingSchedule {
        address beneficiary;
        uint256 totalAmount;
        uint256 releasedAmount;
        uint256 startTime;
        uint256 duration;
        bool isActive;
    }

    // State variables
    mapping(uint256 => Distribution) public distributions;
    mapping(address => VestingSchedule) public vestingSchedules;
    mapping(address => uint256) public lastClaimTime;

    uint256 private _nextDistributionId = 1;
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1B tokens max supply
    uint256 public constant INITIAL_SUPPLY = 1_000_000 * 10**18; // 1M initial supply

    // Protocol parameters (governable)
    uint256 public minConfidenceForMint = 70; // Minimum confidence for token minting
    uint256 public maxMintPerTransaction = 10000 * 10**18; // Max tokens per mint
    uint256 public burnRate = 100; // 1% burn rate for opportunities (basis points)
    uint256 public vestingDuration = 365 days; // Default vesting period

    // Events
    event TokensDistributed(address indexed recipient, uint256 amount, string reason, uint256 confidence);
    event TokensBurned(address indexed from, uint256 amount, string reason);
    event MeTTaProofAttached(uint256 indexed distributionId, string proof);
    event VestingScheduleCreated(address indexed beneficiary, uint256 amount, uint256 duration);
    event TokensClaimed(address indexed beneficiary, uint256 amount);
    event ProtocolParameterUpdated(string parameter, uint256 oldValue, uint256 newValue);

    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) ERC20Permit(name) {
        require(initialSupply <= MAX_SUPPLY, "Initial supply exceeds max supply");

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(BURNER_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);

        // Mint initial supply to deployer
        _mint(msg.sender, initialSupply);
    }

    /**
     * @dev Mint tokens for verified contributions with MeTTa validation
     * @param to Address to mint tokens to
     * @param amount Amount of tokens to mint
     * @param reason Reason for minting (contribution type)
     * @param mettaProof MeTTa proof of the contribution
     * @param confidence MeTTa confidence score (0-100)
     * @param contributionType Type of contribution
     */
    function mintForContribution(
        address to,
        uint256 amount,
        string memory reason,
        string memory mettaProof,
        uint256 confidence,
        string memory contributionType
    ) external onlyRole(MINTER_ROLE) whenNotPaused {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Amount must be greater than 0");
        require(amount <= maxMintPerTransaction, "Amount exceeds maximum per transaction");
        require(confidence >= minConfidenceForMint, "Confidence below minimum threshold");
        require(confidence <= 100, "Confidence must be between 0-100");
        require(totalSupply() + amount <= MAX_SUPPLY, "Would exceed maximum supply");

        uint256 distributionId = _nextDistributionId++;

        distributions[distributionId] = Distribution({
            recipient: to,
            amount: amount,
            reason: reason,
            timestamp: block.timestamp,
            mettaProof: mettaProof,
            confidence: confidence,
            contributionType: contributionType
        });

        _mint(to, amount);

        emit TokensDistributed(to, amount, reason, confidence);
        emit MeTTaProofAttached(distributionId, mettaProof);
    }

    /**
     * @dev Burn tokens from an account for accessing opportunities
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

        // Apply burn rate
        uint256 burnAmount = (amount * burnRate) / 10000;
        uint256 actualBurn = burnAmount > 0 ? burnAmount : 1; // Minimum 1 wei burn

        _burn(from, actualBurn);

        emit TokensBurned(from, actualBurn, reason);
    }

    /**
     * @dev Create a vesting schedule for team/advisors
     * @param beneficiary Address to receive vested tokens
     * @param amount Total amount to vest
     * @param duration Vesting duration in seconds
     */
    function createVestingSchedule(
        address beneficiary,
        uint256 amount,
        uint256 duration
    ) external onlyRole(GOVERNANCE_ROLE) {
        require(beneficiary != address(0), "Invalid beneficiary");
        require(amount > 0, "Amount must be greater than 0");
        require(duration > 0, "Duration must be greater than 0");
        require(vestingSchedules[beneficiary].isActive == false, "Vesting schedule already exists");

        vestingSchedules[beneficiary] = VestingSchedule({
            beneficiary: beneficiary,
            totalAmount: amount,
            releasedAmount: 0,
            startTime: block.timestamp,
            duration: duration,
            isActive: true
        });

        emit VestingScheduleCreated(beneficiary, amount, duration);
    }

    /**
     * @dev Claim vested tokens
     */
    function claimVestedTokens() external {
        VestingSchedule storage schedule = vestingSchedules[msg.sender];
        require(schedule.isActive, "No active vesting schedule");
        require(block.timestamp >= schedule.startTime, "Vesting not started");

        uint256 vestedAmount = _calculateVestedAmount(schedule);
        uint256 claimableAmount = vestedAmount - schedule.releasedAmount;

        require(claimableAmount > 0, "No tokens available to claim");

        schedule.releasedAmount += claimableAmount;
        lastClaimTime[msg.sender] = block.timestamp;

        _mint(msg.sender, claimableAmount);

        emit TokensClaimed(msg.sender, claimableAmount);
    }

    /**
     * @dev Calculate vested amount for a schedule
     * @param schedule Vesting schedule
     * @return Vested amount
     */
    function _calculateVestedAmount(VestingSchedule memory schedule) internal view returns (uint256) {
        if (block.timestamp < schedule.startTime) {
            return 0;
        }

        uint256 elapsedTime = block.timestamp - schedule.startTime;

        if (elapsedTime >= schedule.duration) {
            return schedule.totalAmount;
        } else {
            return (schedule.totalAmount * elapsedTime) / schedule.duration;
        }
    }

    /**
     * @dev Get vesting information for an address
     * @param beneficiary Address to check
     * @return total Total vested amount
     * @return released Amount already released
     * @return claimable Amount available to claim
     */
    function getVestingInfo(address beneficiary) external view returns (
        uint256 total,
        uint256 released,
        uint256 claimable
    ) {
        VestingSchedule memory schedule = vestingSchedules[beneficiary];
        if (!schedule.isActive) {
            return (0, 0, 0);
        }

        uint256 vestedAmount = _calculateVestedAmount(schedule);
        uint256 claimableAmount = vestedAmount - schedule.releasedAmount;

        return (schedule.totalAmount, schedule.releasedAmount, claimableAmount);
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

        if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("minConfidenceForMint"))) {
            oldValue = minConfidenceForMint;
            minConfidenceForMint = value;
        } else if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("maxMintPerTransaction"))) {
            oldValue = maxMintPerTransaction;
            maxMintPerTransaction = value;
        } else if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("burnRate"))) {
            oldValue = burnRate;
            burnRate = value;
        } else if (keccak256(abi.encodePacked(parameter)) == keccak256(abi.encodePacked("vestingDuration"))) {
            oldValue = vestingDuration;
            vestingDuration = value;
        } else {
            revert("Unknown parameter");
        }

        emit ProtocolParameterUpdated(parameter, oldValue, value);
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

    /**
     * @dev Get current supply information
     */
    function getSupplyInfo() external view returns (
        uint256 currentSupply,
        uint256 maxSupply,
        uint256 remainingSupply
    ) {
        uint256 current = totalSupply();
        return (current, MAX_SUPPLY, MAX_SUPPLY - current);
    }

    /**
     * @dev Get chain ID
     */
    function getChainId() external view returns (uint256) {
        return block.chainid;
    }

    // Override functions required by ERC20Votes
    function _afterTokenTransfer(address from, address to, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._afterTokenTransfer(from, to, amount);
    }

    function _mint(address to, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._mint(to, amount);
    }

    function _burn(address account, uint256 amount)
        internal
        override(ERC20, ERC20Votes)
    {
        super._burn(account, amount);
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }

    function supportsInterface(bytes4 interfaceId) public view virtual returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}