// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/NimoIdentity.sol";
import "../src/NimoToken.sol";

contract DeployScript is Script {
    // Deployment configuration optimized for Base
    uint256 constant INITIAL_TOKEN_SUPPLY = 1_000_000 * 10**18; // 1M tokens with 18 decimals
    uint256 constant TEAM_VESTING_AMOUNT = 200_000 * 10**18; // 200K for team vesting
    uint256 constant VESTING_DURATION = 365 days; // 1 year vesting

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console.log("Deploying Nimo contracts to Base network...");
        console.log("Deployer address:", deployer);
        console.log("Deployer balance:", deployer.balance);
        console.log("Chain ID:", block.chainid);

        // Verify we're on Base network
        require(block.chainid == 8453 || block.chainid == 84532, "Must deploy on Base network");

        vm.startBroadcast(deployerPrivateKey);

        // Deploy NimoToken first with governance capabilities
        console.log("Deploying NimoToken...");
        NimoToken nimoToken = new NimoToken(
            "NimoToken",
            "NIMO",
            INITIAL_TOKEN_SUPPLY
        );
        console.log("NimoToken deployed to:", address(nimoToken));

        // Deploy NimoIdentity with enhanced features
        console.log("Deploying NimoIdentity...");
        NimoIdentity nimoIdentity = new NimoIdentity();
        console.log("NimoIdentity deployed to:", address(nimoIdentity));

        // Setup contract integrations with Base optimizations
        console.log("Setting up contract integrations...");
        setupContracts(nimoIdentity, nimoToken, deployer);

        // Setup initial vesting for team
        console.log("Setting up team vesting...");
        setupTeamVesting(nimoToken, deployer);

        vm.stopBroadcast();

        // Log deployment information
        logDeploymentInfo(nimoIdentity, nimoToken, deployer);

        // Write deployment addresses to file
        writeDeploymentAddresses(nimoIdentity, nimoToken);

        // Verify contracts are working
        verifyDeployment(nimoIdentity, nimoToken);
    }

    function setupContracts(
        NimoIdentity identity,
        NimoToken token,
        address deployer
    ) internal {
        // Grant MINTER_ROLE to NimoIdentity contract for token minting
        bytes32 MINTER_ROLE = keccak256("MINTER_ROLE");
        token.grantRole(MINTER_ROLE, address(identity));
        console.log("Granted MINTER_ROLE to NimoIdentity contract");

        // Grant BURNER_ROLE to NimoIdentity contract for token burning
        bytes32 BURNER_ROLE = keccak256("BURNER_ROLE");
        token.grantRole(BURNER_ROLE, address(identity));
        console.log("Granted BURNER_ROLE to NimoIdentity contract");

        // Grant VERIFIER_ROLE to deployer (can be changed later)
        bytes32 VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
        identity.grantRole(VERIFIER_ROLE, deployer);
        console.log("Granted VERIFIER_ROLE to deployer");

        // Grant METTA_AGENT_ROLE to deployer (can be changed later)
        bytes32 METTA_AGENT_ROLE = keccak256("METTA_AGENT_ROLE");
        identity.grantRole(METTA_AGENT_ROLE, deployer);
        console.log("Granted METTA_AGENT_ROLE to deployer");

        // Grant GOVERNANCE_ROLE to deployer
        bytes32 GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
        identity.grantRole(GOVERNANCE_ROLE, deployer);
        console.log("Granted GOVERNANCE_ROLE to deployer");

        bytes32 TOKEN_GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
        token.grantRole(TOKEN_GOVERNANCE_ROLE, deployer);
        console.log("Granted GOVERNANCE_ROLE to deployer on token contract");
    }

    function setupTeamVesting(
        NimoToken token,
        address deployer
    ) internal {
        // Create vesting schedule for team tokens
        token.createVestingSchedule(
            deployer, // Team multisig should be used in production
            TEAM_VESTING_AMOUNT,
            VESTING_DURATION
        );
        console.log("Created team vesting schedule:", TEAM_VESTING_AMOUNT / 10**18, "tokens");
    }

    function logDeploymentInfo(
        NimoIdentity identity,
        NimoToken token,
        address deployer
    ) internal view {
        console.log("\n=== DEPLOYMENT SUMMARY ===");
        console.log("Network: Base", block.chainid == 8453 ? "Mainnet" : "Sepolia");
        console.log("Chain ID:", block.chainid);
        console.log("Block Number:", block.number);
        console.log("Deployer:", deployer);
        console.log("NimoIdentity:", address(identity));
        console.log("NimoToken:", address(token));
        console.log("Token Name:", token.name());
        console.log("Token Symbol:", token.symbol());
        console.log("Token Total Supply:", token.totalSupply() / 10**18, "NIMO");
        // console.log("Token Max Supply:", token.MAX_SUPPLY / 10**18, "NIMO");
        console.log("Identity Contract Name:", identity.name());
        console.log("Identity Contract Symbol:", identity.symbol());
        console.log("===========================\n");
    }

    function writeDeploymentAddresses(
        NimoIdentity identity,
        NimoToken token
    ) internal {
        string memory chainName = getChainName(block.chainid);

        // Create deployment info JSON
        string memory json = string(
            abi.encodePacked(
                '{\n',
                '  "chainId": ', vm.toString(block.chainid), ',\n',
                '  "chainName": "', chainName, '",\n',
                '  "blockNumber": ', vm.toString(block.number), ',\n',
                '  "timestamp": ', vm.toString(block.timestamp), ',\n',
                '  "contracts": {\n',
                '    "NimoIdentity": "', vm.toString(address(identity)), '",\n',
                '    "NimoToken": "', vm.toString(address(token)), '"\n',
                '  },\n',
                '  "initialSupply": "', vm.toString(INITIAL_TOKEN_SUPPLY), '",\n',
                '  "teamVesting": "', vm.toString(TEAM_VESTING_AMOUNT), '",\n',
                '  "features": {\n',
                '    "ipfsSupport": true,\n',
                '    "mettaIntegration": true,\n',
                '    "governanceEnabled": true,\n',
                '    "vestingEnabled": true,\n',
                '    "baseOptimized": true\n',
                '  }\n',
                '}'
            )
        );

        string memory filename = string(
            abi.encodePacked("deployments/", chainName, ".json")
        );

        vm.writeFile(filename, json);
        console.log("Deployment addresses written to:", filename);
    }

    function verifyDeployment(
        NimoIdentity identity,
        NimoToken token
    ) internal view {
        console.log("Verifying deployment...");

        // Verify identity contract
        // require(identity.getChainId() == block.chainid, "Identity contract chain ID mismatch");

        // Verify token contract
        // require(token.getChainId() == block.chainid, "Token contract chain ID mismatch");
        require(token.totalSupply() == INITIAL_TOKEN_SUPPLY, "Token supply mismatch");

        console.log("Deployment verification successful!");
    }

    function getChainName(uint256 chainId) internal pure returns (string memory) {
        if (chainId == 8453) return "base";
        if (chainId == 84532) return "base-sepolia";
        if (chainId == 1) return "ethereum";
        if (chainId == 11155111) return "sepolia";
        if (chainId == 31337 || chainId == 1337) return "localhost";
        return "unknown";
    }
}