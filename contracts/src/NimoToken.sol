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
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1B tokens max supply
    
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
    
    // Vesting schedule for team and advisors
    struct VestingSchedule {
        uint256 totalAmount;
        uint256 releasedAmount;
        uint256 startTime;
        uint256 duration;
        bool isActive;
    }

    mapping(address => VestingSchedule) public vestingSchedules;
    uint256 public vestingDuration = 365 days; // Default vesting period

    // Events
    event TokensDistributed(address indexed recipient, uint256 amount, string reason);
    event TokensBurned(address indexed from, uint256 amount, string reason);
    event MeTTaProofAttached(uint256 indexed distributionId, string proof);
    event VestingScheduleCreated(address indexed beneficiary, uint256 amount, uint256 duration);
    event VestingTokensReleased(address indexed beneficiary, uint256 amount);
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) {
        require(initialSupply <= MAX_SUPPLY, "Initial supply exceeds max supply");

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(BURNER_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);

        // Mint initial supply to deployer
        _mint(msg.sender, initialSupply * 10**decimals());
    }    /**
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
        require(totalSupply() + amount <= MAX_SUPPLY, "Would exceed maximum supply");

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
    }    /**
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

    /**
     * @dev Create a vesting schedule for team/advisors
     * @param beneficiary Address that will receive the vested tokens
     * @param amount Total amount of tokens to vest
     * @param duration Vesting duration in seconds
     */
    function createVestingSchedule(
        address beneficiary,
        uint256 amount,
        uint256 duration
    ) external onlyRole(GOVERNANCE_ROLE) {
        require(beneficiary != address(0), "Beneficiary cannot be zero address");
        require(amount > 0, "Amount must be greater than 0");
        require(vestingSchedules[beneficiary].isActive == false, "Vesting schedule already exists");

        vestingSchedules[beneficiary] = VestingSchedule({
            totalAmount: amount,
            releasedAmount: 0,
            startTime: block.timestamp,
            duration: duration,
            isActive: true
        });

        emit VestingScheduleCreated(beneficiary, amount, duration);
    }

    /**
     * @dev Release vested tokens for the caller
     */
    function releaseVestedTokens() external whenNotPaused {
        VestingSchedule storage schedule = vestingSchedules[msg.sender];
        require(schedule.isActive, "No active vesting schedule");
        require(block.timestamp >= schedule.startTime, "Vesting not started");

        uint256 vestedAmount = _calculateVestedAmount(schedule);
        uint256 releasableAmount = vestedAmount - schedule.releasedAmount;

        require(releasableAmount > 0, "No tokens available for release");

        schedule.releasedAmount += releasableAmount;
        _mint(msg.sender, releasableAmount);

        emit VestingTokensReleased(msg.sender, releasableAmount);
    }

    /**
     * @dev Calculate the amount of tokens that have vested
     * @param schedule Vesting schedule
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
     * @dev Get vesting schedule for an address
     */
    function getVestingSchedule(address beneficiary) external view returns (VestingSchedule memory) {
        return vestingSchedules[beneficiary];
    }

    /**
     * @dev Get releasable amount for an address
     */
    function getReleasableAmount(address beneficiary) external view returns (uint256) {
        VestingSchedule memory schedule = vestingSchedules[beneficiary];
        if (!schedule.isActive) {
            return 0;
        }

        uint256 vestedAmount = _calculateVestedAmount(schedule);
        return vestedAmount - schedule.releasedAmount;
    }
}