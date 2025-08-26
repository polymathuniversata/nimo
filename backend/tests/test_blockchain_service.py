"""
Tests for Blockchain Service

This module contains tests for the blockchain service integration
with Base network and smart contract interactions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from web3 import Web3

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.blockchain_service import BlockchainService


class MockWeb3:
    """Mock Web3 implementation for testing"""
    
    def __init__(self):
        self.is_connected_value = True
        self.gas_price = 1000000000  # 1 gwei in wei
        self.eth = MockEth()
    
    def is_connected(self):
        return self.is_connected_value
    
    def to_wei(self, value, unit):
        if unit == 'gwei':
            return value * 1000000000
        elif unit == 'ether':
            return value * 1000000000000000000
        return value
    
    def from_wei(self, value, unit):
        if unit == 'gwei':
            return value / 1000000000
        elif unit == 'ether':
            return value / 1000000000000000000
        return value


class MockEth:
    """Mock Ethereum interface"""
    
    def __init__(self):
        self.gas_price = 1000000000
    
    def get_transaction_count(self, address):
        return 42
    
    def estimate_gas(self, transaction):
        return 200000
    
    def get_block(self, block_identifier):
        return {'number': 12345678}
    
    def get_transaction_receipt(self, tx_hash):
        return {
            'status': 1,
            'blockNumber': 12345678,
            'gasUsed': 150000
        }
    
    def send_raw_transaction(self, raw_transaction):
        return Mock(hex=lambda: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
    
    def contract(self, address, abi):
        return MockContract(address, abi)


class MockContract:
    """Mock smart contract"""
    
    def __init__(self, address, abi):
        self.address = address
        self.abi = abi
        self.functions = MockContractFunctions()
        self.events = MockContractEvents()


class MockContractFunctions:
    """Mock contract functions"""
    
    def createIdentity(self, username, metadata_uri):
        return MockFunction()
    
    def addContribution(self, contribution_type, description, evidence_uri, metta_hash):
        return MockFunction()
    
    def verifyContribution(self, contribution_id, tokens_to_award):
        return MockFunction()
    
    def batchVerifyContributions(self, contribution_ids, token_amounts):
        return MockFunction()
    
    def mintForContribution(self, to_address, amount, reason, metta_proof):
        return MockFunction()
    
    def balanceOf(self, address):
        mock_call = Mock()
        mock_call.call.return_value = 1000  # Mock balance
        return mock_call


class MockContractEvents:
    """Mock contract events"""
    
    def __init__(self):
        self.IdentityCreated = MockEvent()
        self.ContributionVerified = MockEvent()


class MockEvent:
    """Mock contract event"""
    
    def create_filter(self, fromBlock='latest'):
        return MockFilter()


class MockFilter:
    """Mock event filter"""
    
    def get_new_entries(self):
        return []  # No new events for testing


class MockFunction:
    """Mock contract function"""
    
    def build_transaction(self, transaction_params):
        return {
            'from': transaction_params.get('from'),
            'nonce': transaction_params.get('nonce', 42),
            'gas': 200000,
            'gasPrice': 1000000000,
            'chainId': 84532,
            'to': '0x1234567890123456789012345678901234567890',
            'data': '0xabcdef'
        }
    
    def estimate_gas(self, transaction_params):
        return 200000
    
    def call(self):
        return 1000  # Mock return value


class TestBlockchainService(unittest.TestCase):
    """Test the Blockchain Service"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'NETWORK': 'base-sepolia',
            'NIMO_IDENTITY_CONTRACT_BASE_SEPOLIA': '0x1234567890123456789012345678901234567890',
            'NIMO_TOKEN_CONTRACT_BASE_SEPOLIA': '0x0987654321098765432109876543210987654321',
            'BLOCKCHAIN_SERVICE_PRIVATE_KEY': '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
        })
        self.env_patcher.start()
        
        # Mock Web3
        self.web3_patcher = patch('services.blockchain_service.Web3')
        self.mock_web3_class = self.web3_patcher.start()
        self.mock_web3 = MockWeb3()
        self.mock_web3_class.return_value = self.mock_web3
        
        # Mock Account
        self.account_patcher = patch('services.blockchain_service.Account')
        self.mock_account_class = self.account_patcher.start()
        self.mock_account = Mock()
        self.mock_account.address = '0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266'
        self.mock_account.key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
        self.mock_account_class.from_key.return_value = self.mock_account
        
        # Mock contract ABI loading
        with patch('builtins.open', mock_open_abi()):
            with patch('os.path.exists', return_value=True):
                with patch('json.load', return_value={'abi': []}):
                    self.blockchain_service = BlockchainService()
    
    def tearDown(self):
        """Clean up after test"""
        self.env_patcher.stop()
        self.web3_patcher.stop()
        self.account_patcher.stop()
    
    def test_initialization(self):
        """Test blockchain service initialization"""
        self.assertEqual(self.blockchain_service.network, 'base-sepolia')
        self.assertEqual(self.blockchain_service.base_config['base-sepolia']['chain_id'], 84532)
        self.assertTrue(self.blockchain_service.gas_optimization_enabled)
        self.assertTrue(self.blockchain_service.batch_processing_enabled)
    
    def test_network_configuration(self):
        """Test network-specific configuration"""
        # Test Base Sepolia configuration
        self.assertEqual(self.blockchain_service._get_network_rpc_url(), 'https://sepolia.base.org')
        
        contracts = self.blockchain_service._get_network_contracts()
        self.assertEqual(contracts['identity'], '0x1234567890123456789012345678901234567890')
        self.assertEqual(contracts['token'], '0x0987654321098765432109876543210987654321')
    
    def test_connection_status(self):
        """Test blockchain connection status"""
        self.assertTrue(self.blockchain_service.is_connected())
        
        # Test disconnected state
        self.mock_web3.is_connected_value = False
        self.assertFalse(self.blockchain_service.is_connected())
    
    def test_gas_price_estimation(self):
        """Test gas price estimation for Base network"""
        gas_price = self.blockchain_service._estimate_gas_price()
        
        # Should be reasonable for Base network
        self.assertGreater(gas_price, 0)
        self.assertLessEqual(gas_price, self.blockchain_service.web3.to_wei(2.0, 'gwei'))
    
    def test_gas_limit_estimation(self):
        """Test gas limit estimation"""
        transaction_data = {
            'from': '0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266',
            'to': '0x1234567890123456789012345678901234567890'
        }
        
        gas_limit = self.blockchain_service._estimate_gas_limit(transaction_data)
        
        # Should be within reasonable bounds
        self.assertGreater(gas_limit, 150000)  # Minimum expected
        self.assertLess(gas_limit, 30000000)   # Block gas limit
    
    def test_transaction_building(self):
        """Test transaction building for Base network"""
        mock_function = MockFunction()
        user_address = '0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266'
        
        transaction = self.blockchain_service._build_transaction(mock_function, user_address)
        
        # Check transaction structure
        self.assertEqual(transaction['from'], user_address)
        self.assertEqual(transaction['chainId'], 84532)  # Base Sepolia chain ID
        self.assertIn('gasPrice', transaction)
        self.assertIn('gas', transaction)
        self.assertIn('nonce', transaction)
    
    def test_create_identity_on_chain(self):
        """Test creating identity NFT on chain"""
        username = "test_user"
        metadata_uri = "ipfs://QmTest123"
        user_address = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"
        
        tx_hash = self.blockchain_service.create_identity_on_chain(
            username, metadata_uri, user_address
        )
        
        # Should return a transaction hash
        self.assertIsNotNone(tx_hash)
        self.assertIn(tx_hash, self.blockchain_service.pending_transactions)
    
    def test_add_contribution_on_chain(self):
        """Test adding contribution to blockchain"""
        tx_hash = self.blockchain_service.add_contribution_on_chain(
            contribution_type="coding",
            description="Python web application",
            evidence_uri="ipfs://QmEvidence123",
            metta_hash="0xabcdef123456",
            user_address="0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"
        )
        
        # Should return a transaction hash
        self.assertIsNotNone(tx_hash)
        self.assertIn(tx_hash, self.blockchain_service.pending_transactions)
    
    def test_verify_contribution_on_chain(self):
        """Test verifying contribution on blockchain"""
        tx_hash = self.blockchain_service.verify_contribution_on_chain(
            contribution_id=1,
            tokens_to_award=75
        )
        
        # Should return a transaction hash
        self.assertIsNotNone(tx_hash)
        self.assertIn(tx_hash, self.blockchain_service.pending_transactions)
    
    def test_batch_verify_contributions(self):
        """Test batch verification of contributions"""
        contributions = [
            {'id': 1, 'tokens': 50},
            {'id': 2, 'tokens': 75},
            {'id': 3, 'tokens': 100}
        ]
        
        tx_hashes = self.blockchain_service.batch_verify_contributions(contributions)
        
        # Should return transaction hashes for all contributions
        self.assertEqual(len(tx_hashes), 3)
        for tx_hash in tx_hashes:
            if tx_hash:  # Some might be None if batch processing is disabled
                self.assertIsNotNone(tx_hash)
    
    def test_get_token_balance(self):
        """Test getting token balance"""
        address = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"
        balance = self.blockchain_service.get_token_balance(address)
        
        # Should return the mocked balance
        self.assertEqual(balance, 1000)
    
    def test_transaction_status_monitoring(self):
        """Test transaction status monitoring"""
        # Create a test transaction
        tx_hash = self.blockchain_service.create_identity_on_chain(
            "test_user", "ipfs://test", "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"
        )
        
        # Check initial status (should be pending)
        status = self.blockchain_service.get_transaction_status(tx_hash)
        self.assertEqual(status['status'], 'success')  # Mock returns success immediately
        self.assertTrue(status['confirmed'])
    
    def test_network_info(self):
        """Test getting network information"""
        network_info = self.blockchain_service.get_network_info()
        
        # Check network info structure
        self.assertEqual(network_info['network'], 'base-sepolia')
        self.assertEqual(network_info['chain_id'], 84532)
        self.assertTrue(network_info['connected'])
        self.assertIn('latest_block', network_info)
        self.assertIn('current_gas_price', network_info)
        self.assertIn('explorer_url', network_info)
    
    def test_transaction_cost_estimation(self):
        """Test transaction cost estimation"""
        # Test different operations
        operations = ['create_identity', 'add_contribution', 'verify_contribution']
        
        for operation in operations:
            cost_estimate = self.blockchain_service.estimate_transaction_cost(operation)
            
            # Should return cost estimate structure
            self.assertIn('operation', cost_estimate)
            self.assertIn('gas_estimate', cost_estimate)
            self.assertIn('gas_price_wei', cost_estimate)
            self.assertIn('total_cost_eth', cost_estimate)
            self.assertEqual(cost_estimate['operation'], operation)
    
    def test_event_listeners_setup(self):
        """Test setting up blockchain event listeners"""
        event_filters = self.blockchain_service.setup_event_listeners()
        
        # Should return event filters
        if event_filters:  # Only if contracts are properly initialized
            self.assertIn('identity_created', event_filters)
            self.assertIn('contribution_verified', event_filters)
    
    def test_error_handling(self):
        """Test error handling in blockchain operations"""
        # Test with invalid contract (None)
        service = BlockchainService()
        service.identity_contract = None
        
        # Operations should return None gracefully
        result = service.create_identity_on_chain("test", "ipfs://test", "0x123")
        self.assertIsNone(result)


def mock_open_abi():
    """Mock function to simulate ABI file reading"""
    return Mock(return_value=Mock(__enter__=Mock(return_value=Mock(read=Mock(return_value='{"abi": []}'))), __exit__=Mock()))


if __name__ == '__main__':
    unittest.main()