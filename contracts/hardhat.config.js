// NOTE: This file is kept for backward compatibility
// The project now uses Foundry for smart contract development
// See foundry.toml for Foundry configuration

require("dotenv").config();

// Legacy Hardhat config - use Foundry instead
console.log("⚠️  This project uses Foundry for smart contract development");
console.log("📚 See foundry.toml for configuration");
console.log("🔧 Use 'forge build', 'forge test', etc. instead of Hardhat commands");

module.exports = {
  // Minimal config for tools that might still expect hardhat.config.js
  solidity: "0.8.19",
  networks: {
    hardhat: {
      chainId: 1337
    }
  }
};