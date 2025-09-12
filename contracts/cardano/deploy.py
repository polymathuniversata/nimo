#!/usr/bin/env python3
"""
Nimo Platform - Comprehensive Cardano Smart Contract Deployment Script

This script handles the complete deployment of all Nimo Platform smart contracts
to Cardano networks (Preview, Preprod, Mainnet) using Aiken-compiled contracts
and PyCardano for transaction building.
"""

import os
import json
import logging
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

try:
    from pycardano import (
        BlockFrostChainContext,
        Network,
        PaymentSigningKey,
        PaymentVerificationKey,
        Address,
        TransactionBuilder,
        TransactionOutput,
        Value,
        AssetName,
        ScriptHash,
        MultiAsset,
        Asset,
        PlutusV2Script,
        PlutusData,
        AuxiliaryData,
        Metadata,
        NativeScript,
        ScriptPubkey,
        InvalidAfter,
        ValidityIntervalStart,
        ScriptRef,
        PlutusScriptSource,
        RedeemerTag,
        Redeemer
    )
    PYCARDANO_AVAILABLE = True
except ImportError:
    print("❌ PyCardano not installed. Install with: pip install pycardano blockfrost-python")
    PYCARDANO_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeploymentResult:
    """Result of a smart contract deployment"""
    contract_name: str
    contract_type: str  # "validator", "minting_policy", "native_script"
    script_hash: str
    script_address: str
    tx_hash: str
    network: str
    deployed_at: str
    gas_used: Optional[int] = None
    deployment_cost: Optional[int] = None  # in lovelace

@dataclass
class DeploymentSummary:
    """Summary of complete platform deployment"""
    network: str
    deployer_address: str
    total_contracts: int
    successful_deployments: int
    failed_deployments: int
    total_cost: int  # in lovelace
    deployment_time: str
    results: List[DeploymentResult]

class NimoPlatformDeployer:
    """Comprehensive deployer for all Nimo Platform smart contracts"""
    
    def __init__(self, network: str = "preview"):
        """Initialize the deployer with network configuration"""
        
        if not PYCARDANO_AVAILABLE:
            raise ImportError("PyCardano is required for deployment")
        
        self.network = network
        self.config = self._load_network_config()
        self.deployment_start_time = datetime.now(timezone.utc)
        
        # Initialize chain context
        cardano_network = Network.MAINNET if network == 'mainnet' else Network.TESTNET
        self.chain_context = BlockFrostChainContext(
            project_id=self.config['blockfrost_project_id'],
            network=cardano_network,
            base_url=self.config['blockfrost_url']
        )
        
        # Load deployer keys
        self.deployer_key = self._load_deployer_key()
        self.deployer_address = Address(
            PaymentVerificationKey.from_signing_key(self.deployer_key).hash()
        )
        
        # Contract compilation results
        self.compiled_contracts = {}
        self.deployment_results = []
        
        logger.info(f"🚀 Initialized Nimo Platform deployer for {network}")
        logger.info(f"📍 Deployer address: {self.deployer_address}")
    
    def _load_network_config(self) -> Dict[str, str]:
        """Load network-specific configuration"""
        configs = {
            'mainnet': {
                'blockfrost_project_id': os.getenv('BLOCKFROST_PROJECT_ID_MAINNET'),
                'blockfrost_url': 'https://cardano-mainnet.blockfrost.io/api'
            },
            'preprod': {
                'blockfrost_project_id': os.getenv('BLOCKFROST_PROJECT_ID_PREPROD'),
                'blockfrost_url': 'https://cardano-preprod.blockfrost.io/api'
            },
            'preview': {
                'blockfrost_project_id': os.getenv('BLOCKFROST_PROJECT_ID_PREVIEW'),
                'blockfrost_url': 'https://cardano-preview.blockfrost.io/api'
            }
        }
        
        config = configs.get(self.network)
        if not config or not config['blockfrost_project_id']:
            raise ValueError(f"Blockfrost project ID not configured for {self.network}")
        
        return config
    
    def _load_deployer_key(self) -> PaymentSigningKey:
        """Load deployer signing key"""
        # Try environment variable
        key_hex = os.getenv('CARDANO_DEPLOYER_PRIVATE_KEY')
        if key_hex and key_hex != 'your_deployer_key_here':
            return PaymentSigningKey.from_primitive(bytes.fromhex(key_hex))
        
        # Try key file
        key_file = Path('deployer_key.skey')
        if key_file.exists():
            with open(key_file, 'r') as f:
                key_data = json.load(f)
                return PaymentSigningKey.from_primitive(bytes.fromhex(key_data['cborHex']))
        
        # Generate new key for development
        logger.warning("⚠️  No deployer key found, generating new key")
        signing_key = PaymentSigningKey.generate()
        
        # Save for future use
        key_data = {
            "type": "PaymentSigningKeyShelley_ed25519",
            "description": "Nimo Platform Deployer Key",
            "cborHex": signing_key.to_primitive().hex()
        }
        
        with open('deployer_key.skey', 'w') as f:
            json.dump(key_data, f, indent=2)
        
        logger.info(f"🔑 Generated deployer key saved to deployer_key.skey")
        logger.info(f"💰 Please fund this address: {self.deployer_address}")
        
        return signing_key
    
    def compile_contracts(self) -> Dict[str, Dict]:
        """Compile all Aiken smart contracts"""
        logger.info("🔨 Compiling smart contracts with Aiken...")
        
        # Check if Aiken is installed
        try:
            result = subprocess.run(['aiken', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"✅ Aiken version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Aiken not installed. Install from: https://aiken-lang.org/")
        
        # Compile contracts
        try:
            compile_result = subprocess.run(
                ['aiken', 'build', '--trace-level', 'verbose'],
                capture_output=True, text=True, check=True, cwd=Path.cwd()
            )
            logger.info("✅ Contracts compiled successfully")
            logger.debug(compile_result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Contract compilation failed: {e.stderr}")
            raise
        
        # Load compiled artifacts
        plutus_dir = Path('plutus.json')  # Aiken output
        if not plutus_dir.exists():
            raise FileNotFoundError("Compiled contracts not found. Run 'aiken build' first.")
        
        with open(plutus_dir, 'r') as f:
            plutus_artifacts = json.load(f)
        
        # Extract contract information
        contracts = {}
        for validator_name, artifact in plutus_artifacts.get('validators', {}).items():
            contracts[validator_name] = {
                'type': 'validator',
                'compiled_code': artifact['compiledCode'],
                'hash': artifact['hash'],
                'parameters': artifact.get('parameters', {})
            }
        
        self.compiled_contracts = contracts
        logger.info(f"📋 Compiled {len(contracts)} contracts: {list(contracts.keys())}")
        return contracts
    
    def check_deployer_balance(self) -> Dict[str, Any]:
        """Check deployer address balance and funding status"""
        try:
            balance_info = self.chain_context.api.account(str(self.deployer_address))
            ada_balance = int(balance_info.controlled_amount) / 1000000
            
            logger.info(f"💰 Deployer balance: {ada_balance} ADA")
            
            # Estimate deployment costs
            estimated_cost = self.estimate_deployment_costs()
            required_ada = estimated_cost / 1000000
            
            if ada_balance < required_ada:
                logger.warning(f"⚠️  Low balance! Required: {required_ada} ADA, Available: {ada_balance} ADA")
                if self.network != "mainnet":
                    logger.info("💡 Get test ADA from: https://docs.cardano.org/cardano-testnets/tools/faucet")
                return {'sufficient': False, 'balance': ada_balance, 'required': required_ada}
            
            return {'sufficient': True, 'balance': ada_balance, 'required': required_ada}
            
        except Exception as e:
            logger.error(f"❌ Could not check balance: {e}")
            return {'sufficient': False, 'error': str(e)}
    
    def estimate_deployment_costs(self) -> int:
        """Estimate total deployment costs in lovelace"""
        # Rough estimates based on contract complexity
        costs = {
            'contribution_validator': 5000000,    # ~5 ADA
            'identity_registry': 4000000,        # ~4 ADA  
            'metta_bridge': 6000000,             # ~6 ADA
            'nimo_token_policy': 2000000,        # ~2 ADA
            'deployment_overhead': 3000000        # ~3 ADA for transactions
        }
        
        return sum(costs.values())
    
    def deploy_contribution_validator(self) -> DeploymentResult:
        """Deploy the contribution validator smart contract"""
        logger.info("🏗️  Deploying contribution validator...")
        
        contract_info = self.compiled_contracts.get('contribution_validator')
        if not contract_info:
            raise ValueError("Contribution validator not compiled")
        
        # Create Plutus script
        plutus_script = PlutusV2Script(bytes.fromhex(contract_info['compiled_code']))
        script_hash = plutus_script.hash()
        script_address = Address(script_hash, network=self.chain_context.network)
        
        # Build deployment transaction
        builder = TransactionBuilder(self.chain_context)
        
        # Add script reference output
        builder.add_output(
            TransactionOutput(
                script_address,
                Value(2000000),  # 2 ADA minimum
                script_ref=ScriptRef(plutus_script)
            )
        )
        
        # Add metadata
        metadata = {
            "674": {
                "contract_name": "Nimo Contribution Validator",
                "contract_version": "1.0.0",
                "deployed_by": "Nimo Platform",
                "network": self.network,
                "deployed_at": datetime.now(timezone.utc).isoformat()
            }
        }
        builder.auxiliary_data = AuxiliaryData(Metadata(metadata))
        
        # Build and sign transaction
        tx = builder.build_and_sign([self.deployer_key], self.deployer_address)
        tx_hash = self.chain_context.submit_tx(tx)
        
        result = DeploymentResult(
            contract_name="contribution_validator",
            contract_type="validator",
            script_hash=str(script_hash),
            script_address=str(script_address),
            tx_hash=str(tx_hash),
            network=self.network,
            deployed_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.deployment_results.append(result)
        logger.info(f"✅ Contribution validator deployed: {tx_hash}")
        return result
    
    def deploy_identity_registry(self) -> DeploymentResult:
        """Deploy the identity registry smart contract"""
        logger.info("🏗️  Deploying identity registry...")
        
        contract_info = self.compiled_contracts.get('identity_registry')
        if not contract_info:
            raise ValueError("Identity registry not compiled")
        
        # Create Plutus script
        plutus_script = PlutusV2Script(bytes.fromhex(contract_info['compiled_code']))
        script_hash = plutus_script.hash()
        script_address = Address(script_hash, network=self.chain_context.network)
        
        # Build deployment transaction
        builder = TransactionBuilder(self.chain_context)
        
        # Add script reference output
        builder.add_output(
            TransactionOutput(
                script_address,
                Value(2000000),  # 2 ADA minimum
                script_ref=ScriptRef(plutus_script)
            )
        )
        
        # Add metadata
        metadata = {
            "674": {
                "contract_name": "Nimo Identity Registry",
                "contract_version": "1.0.0",
                "deployed_by": "Nimo Platform",
                "network": self.network,
                "deployed_at": datetime.now(timezone.utc).isoformat()
            }
        }
        builder.auxiliary_data = AuxiliaryData(Metadata(metadata))
        
        # Build and sign transaction
        tx = builder.build_and_sign([self.deployer_key], self.deployer_address)
        tx_hash = self.chain_context.submit_tx(tx)
        
        result = DeploymentResult(
            contract_name="identity_registry",
            contract_type="validator", 
            script_hash=str(script_hash),
            script_address=str(script_address),
            tx_hash=str(tx_hash),
            network=self.network,
            deployed_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.deployment_results.append(result)
        logger.info(f"✅ Identity registry deployed: {tx_hash}")
        return result
    
    def deploy_metta_bridge(self) -> DeploymentResult:
        """Deploy the MeTTa bridge smart contract"""
        logger.info("🏗️  Deploying MeTTa bridge...")
        
        contract_info = self.compiled_contracts.get('metta_bridge')
        if not contract_info:
            raise ValueError("MeTTa bridge not compiled")
        
        # Create Plutus script
        plutus_script = PlutusV2Script(bytes.fromhex(contract_info['compiled_code']))
        script_hash = plutus_script.hash()
        script_address = Address(script_hash, network=self.chain_context.network)
        
        # Build deployment transaction
        builder = TransactionBuilder(self.chain_context)
        
        # Add script reference output
        builder.add_output(
            TransactionOutput(
                script_address,
                Value(3000000),  # 3 ADA minimum (larger contract)
                script_ref=ScriptRef(plutus_script)
            )
        )
        
        # Add metadata
        metadata = {
            "674": {
                "contract_name": "Nimo MeTTa Bridge",
                "contract_version": "1.0.0",
                "deployed_by": "Nimo Platform", 
                "network": self.network,
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "metta_integration": True
            }
        }
        builder.auxiliary_data = AuxiliaryData(Metadata(metadata))
        
        # Build and sign transaction
        tx = builder.build_and_sign([self.deployer_key], self.deployer_address)
        tx_hash = self.chain_context.submit_tx(tx)
        
        result = DeploymentResult(
            contract_name="metta_bridge",
            contract_type="validator",
            script_hash=str(script_hash),
            script_address=str(script_address),
            tx_hash=str(tx_hash),
            network=self.network,
            deployed_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.deployment_results.append(result)
        logger.info(f"✅ MeTTa bridge deployed: {tx_hash}")
        return result
    
    def deploy_nimo_token_policy(self) -> DeploymentResult:
        """Deploy NIMO token minting policy"""
        logger.info("🏗️  Deploying NIMO token minting policy...")
        
        # Create native script for token minting (signature-based)
        key_hash = PaymentVerificationKey.from_signing_key(self.deployer_key).hash()
        native_script = NativeScript(ScriptPubkey(key_hash))
        policy_id = native_script.hash()
        
        # Initial token mint
        asset_name = AssetName(b"NIMO")
        initial_amount = 1000000  # 1M NIMO tokens
        
        token_to_mint = MultiAsset({
            policy_id: Asset({asset_name: initial_amount})
        })
        
        # Build minting transaction
        builder = TransactionBuilder(self.chain_context)
        
        # Set minting
        builder.mint = token_to_mint
        builder.native_scripts = [native_script]
        
        # Mint tokens to deployer address
        builder.add_output(
            TransactionOutput(
                self.deployer_address,
                Value(coin=2000000, multi_asset=token_to_mint)
            )
        )
        
        # Add metadata
        metadata = {
            "721": {  # CIP-25 token metadata
                str(policy_id): {
                    "NIMO": {
                        "name": "NIMO Token",
                        "description": "Reputation token for the Nimo Platform",
                        "image": "ipfs://QmNimoTokenImage",
                        "website": "https://nimo.platform",
                        "ticker": "NIMO",
                        "decimals": 0,
                        "version": "1.0.0"
                    }
                }
            },
            "674": {
                "msg": [f"NIMO token policy deployment - {self.network}"],
                "platform": "Nimo",
                "initial_supply": initial_amount,
                "network": self.network
            }
        }
        builder.auxiliary_data = AuxiliaryData(Metadata(metadata))
        
        # Build and sign transaction
        tx = builder.build_and_sign([self.deployer_key], self.deployer_address)
        tx_hash = self.chain_context.submit_tx(tx)
        
        result = DeploymentResult(
            contract_name="nimo_token_policy",
            contract_type="minting_policy",
            script_hash=str(policy_id),
            script_address=str(self.deployer_address),  # Tokens minted to deployer
            tx_hash=str(tx_hash),
            network=self.network,
            deployed_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.deployment_results.append(result)
        logger.info(f"✅ NIMO token policy deployed: {tx_hash}")
        logger.info(f"🪙 Policy ID: {policy_id}")
        logger.info(f"💰 Initial supply: {initial_amount} NIMO tokens")
        
        return result
    
    def wait_for_confirmations(self, tx_hashes: List[str], required_confirmations: int = 3):
        """Wait for transaction confirmations"""
        logger.info(f"⏳ Waiting for {required_confirmations} confirmations...")
        
        confirmed = set()
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while len(confirmed) < len(tx_hashes) and (time.time() - start_time) < max_wait_time:
            for tx_hash in tx_hashes:
                if tx_hash in confirmed:
                    continue
                
                try:
                    tx_info = self.chain_context.api.transaction(tx_hash)
                    if tx_info and tx_info.get('block_height'):
                        confirmed.add(tx_hash)
                        logger.info(f"✅ Transaction confirmed: {tx_hash}")
                except:
                    pass  # Transaction not yet confirmed
            
            if len(confirmed) < len(tx_hashes):
                time.sleep(10)  # Wait 10 seconds before checking again
        
        if len(confirmed) < len(tx_hashes):
            logger.warning(f"⚠️  Only {len(confirmed)}/{len(tx_hashes)} transactions confirmed")
        else:
            logger.info("✅ All transactions confirmed!")
    
    def deploy_all(self) -> DeploymentSummary:
        """Deploy all smart contracts in the correct order"""
        logger.info("🚀 Starting complete Nimo Platform deployment...")
        
        try:
            # Step 1: Compile contracts
            self.compile_contracts()
            
            # Step 2: Check balance
            balance_info = self.check_deployer_balance()
            if not balance_info['sufficient'] and self.network == 'mainnet':
                raise ValueError(f"Insufficient funds for deployment: {balance_info}")
            
            # Step 3: Deploy contracts in order
            deployment_order = [
                self.deploy_nimo_token_policy,
                self.deploy_contribution_validator,
                self.deploy_identity_registry,
                self.deploy_metta_bridge
            ]
            
            for deploy_func in deployment_order:
                try:
                    result = deploy_func()
                    logger.info(f"✅ {result.contract_name} deployed successfully")
                    time.sleep(5)  # Wait between deployments
                except Exception as e:
                    logger.error(f"❌ Failed to deploy {deploy_func.__name__}: {e}")
                    # Continue with other deployments
            
            # Step 4: Wait for confirmations
            tx_hashes = [result.tx_hash for result in self.deployment_results]
            self.wait_for_confirmations(tx_hashes)
            
            # Step 5: Create deployment summary
            summary = DeploymentSummary(
                network=self.network,
                deployer_address=str(self.deployer_address),
                total_contracts=len(deployment_order),
                successful_deployments=len(self.deployment_results),
                failed_deployments=len(deployment_order) - len(self.deployment_results),
                total_cost=sum(r.deployment_cost or 0 for r in self.deployment_results),
                deployment_time=(datetime.now(timezone.utc) - self.deployment_start_time).total_seconds(),
                results=self.deployment_results
            )
            
            # Step 6: Save deployment results
            self.save_deployment_results(summary)
            
            logger.info("🎉 Deployment completed!")
            logger.info(f"📊 Summary: {summary.successful_deployments}/{summary.total_contracts} contracts deployed")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise
    
    def save_deployment_results(self, summary: DeploymentSummary):
        """Save deployment results to files"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = f"deployment_results_{self.network}_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
        
        # Update current deployment info
        current_file = f"deployment_current_{self.network}.json"
        with open(current_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
        
        # Create environment variables file
        env_file = f"deployment_env_{self.network}.sh"
        with open(env_file, 'w') as f:
            f.write(f"# Nimo Platform Deployment - {self.network}\n")
            f.write(f"export CARDANO_NETWORK={self.network}\n")
            f.write(f"export NIMO_DEPLOYER_ADDRESS={self.deployer_address}\n")
            
            for result in summary.results:
                env_var_name = f"NIMO_{result.contract_name.upper()}_HASH"
                f.write(f"export {env_var_name}={result.script_hash}\n")
                
                env_var_addr = f"NIMO_{result.contract_name.upper()}_ADDRESS"
                f.write(f"export {env_var_addr}={result.script_address}\n")
        
        logger.info(f"💾 Deployment results saved to {results_file}")
        logger.info(f"🔧 Environment variables saved to {env_file}")


def main():
    """Main deployment CLI"""
    parser = argparse.ArgumentParser(description='Deploy Nimo Platform smart contracts')
    parser.add_argument('--network', choices=['preview', 'preprod', 'mainnet'], 
                       default='preview', help='Cardano network')
    parser.add_argument('--contract', choices=['all', 'contribution', 'identity', 'metta', 'token'],
                       default='all', help='Specific contract to deploy')
    parser.add_argument('--check-balance', action='store_true', 
                       help='Check deployer balance only')
    parser.add_argument('--compile-only', action='store_true',
                       help='Compile contracts only, do not deploy')
    
    args = parser.parse_args()
    
    try:
        deployer = NimoPlatformDeployer(args.network)
        
        if args.check_balance:
            balance_info = deployer.check_deployer_balance()
            print(json.dumps(balance_info, indent=2))
            return 0
        
        if args.compile_only:
            contracts = deployer.compile_contracts()
            print(f"✅ Compiled {len(contracts)} contracts")
            return 0
        
        if args.contract == 'all':
            summary = deployer.deploy_all()
            print(f"\n🎉 Deployment Summary:")
            print(f"Network: {summary.network}")
            print(f"Successful: {summary.successful_deployments}/{summary.total_contracts}")
            print(f"Total cost: {summary.total_cost / 1000000:.2f} ADA")
            print(f"Time taken: {summary.deployment_time:.1f} seconds")
        else:
            # Deploy specific contract
            deployer.compile_contracts()
            if args.contract == 'token':
                result = deployer.deploy_nimo_token_policy()
            elif args.contract == 'contribution':
                result = deployer.deploy_contribution_validator()
            elif args.contract == 'identity':
                result = deployer.deploy_identity_registry()
            elif args.contract == 'metta':
                result = deployer.deploy_metta_bridge()
            
            print(f"✅ {result.contract_name} deployed: {result.tx_hash}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())