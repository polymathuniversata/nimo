"""
Tests for MeTTa reasoning and blockchain bridge implementation

This module contains tests for the MeTTa reasoning engine and its
integration with the blockchain through the bridge service.
"""

import unittest
import json
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.metta_reasoning import MeTTaReasoning
from services.metta_blockchain_bridge import MeTTaBlockchainBridge
from services.blockchain_service import BlockchainService

class MockBlockchainService:
    """Mock implementation of BlockchainService for testing"""
    
    def __init__(self):
        self.calls = []
    
    async def verify_contribution_on_chain(self, contribution_id, user_address, 
                                        tokens_to_award, proof_hash):
        """Mock blockchain verification"""
        self.calls.append({
            'method': 'verify_contribution_on_chain',
            'contribution_id': contribution_id,
            'user_address': user_address,
            'tokens': tokens_to_award,
            'proof': proof_hash
        })
        return "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    async def mint_tokens_for_contribution(self, to_address, amount, reason, metta_proof):
        """Mock token minting"""
        self.calls.append({
            'method': 'mint_tokens_for_contribution',
            'address': to_address,
            'amount': amount,
            'reason': reason,
            'proof': metta_proof
        })
        return "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    
    async def link_contributions_to_bond(self, bond_id, user_id, 
                                     contribution_count, impact_score):
        """Mock linking contributions to bond"""
        self.calls.append({
            'method': 'link_contributions_to_bond',
            'bond_id': bond_id,
            'user_id': user_id,
            'contribution_count': contribution_count,
            'impact_score': impact_score
        })
        return "0x7890abcdef1234567890abcdef1234567890abcdef1234567890abcdef123456"

class TestMeTTaReasoning(unittest.TestCase):
    """Test the MeTTa reasoning engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.metta = MeTTaReasoning()
        
        # Define test data for user
        self.user_data = {
            "id": "test_user",
            "skills": ["python", "web_development", "community_building"],
            "reputation": 75,
            "past_contributions": 5,
            "verification_rate": 0.8
        }
        
        # Define test data for contribution
        self.contribution_data = {
            "id": "test_contrib",
            "title": "Python Web Application",
            "type": "coding",
            "required_skills": ["python", "web_development"],
            "impact": "significant",
            "metadata": {
                "date": "2025-07-15",
                "location": "Online",
                "participants": 30
            }
        }
        
        # Define test data for evidence
        self.github_evidence = {
            "url": "https://github.com/test_user/python_project",
            "type": "github_repo",
            "description": "Repository containing the Python web application code"
        }
        
        self.website_evidence = {
            "url": "https://example.com/project",
            "type": "website",
            "description": "Project website showing the deployed application"
        }
    
    def test_verification_with_github_evidence(self):
        """Test contribution verification with GitHub evidence"""
        # Mock the internal methods
        self.metta._get_user_data = Mock(return_value=self.user_data)
        self.metta._get_contribution_data = Mock(return_value=self.contribution_data)
        self.metta._process_evidence = Mock(return_value=self.github_evidence)
        
        # Execute verification
        result = self.metta.verify_contribution(
            "test_user", "test_contrib", self.github_evidence
        )
        
        # Check verification result
        self.assertIn('verified', result)
        self.assertIn('confidence', result)
        self.assertIn('explanation', result)
        self.assertIn('tokens', result)
        self.assertIn('metta_proof', result)
        
        # With GitHub evidence, we expect verification to pass
        self.assertTrue(result['verified'])
        self.assertGreaterEqual(result['confidence'], 0.7)
        self.assertGreaterEqual(result['tokens'], 50)
    
    def test_verification_with_website_evidence(self):
        """Test contribution verification with website evidence"""
        # Mock the internal methods
        self.metta._get_user_data = Mock(return_value=self.user_data)
        self.metta._get_contribution_data = Mock(return_value=self.contribution_data)
        self.metta._process_evidence = Mock(return_value=self.website_evidence)
        
        # Execute verification
        result = self.metta.verify_contribution(
            "test_user", "test_contrib", self.website_evidence
        )
        
        # Check verification result
        self.assertIn('verified', result)
        self.assertIn('confidence', result)
        self.assertIn('explanation', result)
        self.assertIn('tokens', result)
        self.assertIn('metta_proof', result)
    
    def test_fraud_detection(self):
        """Test fraud detection functionality"""
        # Mock the internal methods
        self.metta._get_user_data = Mock(return_value=self.user_data)
        self.metta._get_contribution_data = Mock(return_value=self.contribution_data)
        
        # Execute fraud detection
        result = self.metta.detect_fraudulent_activity(
            "test_user", "test_contrib"
        )
        
        # Check fraud detection result
        self.assertIn('is_fraud', result)
        
        # If fraud is detected, check for reason and confidence
        if result['is_fraud']:
            self.assertIn('reason', result)
            self.assertIn('confidence', result)
    
    def test_reputation_calculation(self):
        """Test user reputation calculation"""
        # Mock the internal methods
        self.metta._get_user_data = Mock(return_value=self.user_data)
        
        # Calculate reputation
        reputation = self.metta.calculate_reputation("test_user")
        
        # Reputation should be a number
        self.assertIsInstance(reputation, (int, float))
        self.assertGreaterEqual(reputation, 0)

class TestMeTTaBlockchainBridge(unittest.TestCase):
    """Test the MeTTa blockchain bridge"""
    
    def setUp(self):
        """Set up test environment"""
        self.metta = Mock(spec=MeTTaReasoning)
        self.blockchain = MockBlockchainService()
        self.bridge = MeTTaBlockchainBridge(self.blockchain, self.metta)
        
        # Mock the User, Contribution, and Verification models
        self.user_patch = patch('backend.models.user.User')
        self.contrib_patch = patch('backend.models.contribution.Contribution')
        self.verify_patch = patch('backend.models.contribution.Verification')
        self.tx_patch = patch('backend.models.bond.BlockchainTransaction')
        
        # Start the patches
        self.mock_user_model = self.user_patch.start()
        self.mock_contrib_model = self.contrib_patch.start()
        self.mock_verify_model = self.verify_patch.start()
        self.mock_tx_model = self.tx_patch.start()
        
        # Setup mock user
        self.mock_user = Mock()
        self.mock_user.blockchain_address = "0xabcd1234abcd1234abcd1234abcd1234abcd1234"
        self.mock_user_model.query.get.return_value = self.mock_user
        
        # Setup mock contribution
        self.mock_contrib = Mock()
        self.mock_contrib.title = "Test Contribution"
        self.mock_contrib_model.query.get.return_value = self.mock_contrib
        
        # Setup MeTTa result
        self.metta_result = {
            'verified': True,
            'confidence': 0.85,
            'explanation': 'Contribution verified with 85% confidence. Key factor: Strong GitHub repository evidence',
            'tokens': 75,
            'metta_proof': '0x1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d'
        }
        
        # Setup MeTTa fraud detection result
        self.fraud_result = {
            'is_fraud': False
        }
        
        # Configure mocks
        self.metta.verify_contribution.return_value = self.metta_result
        self.metta.detect_fraudulent_activity.return_value = self.fraud_result
    
    def tearDown(self):
        """Clean up after test"""
        self.user_patch.stop()
        self.contrib_patch.stop()
        self.verify_patch.stop()
        self.tx_patch.stop()
    
    async def test_verify_contribution_on_chain(self):
        """Test verification and blockchain integration"""
        # Mock evidence
        evidence = {
            "url": "https://github.com/test_user/python_project",
            "type": "github_repo",
            "description": "Repository containing the Python web application code"
        }
        
        # Execute the bridge verification
        result = await self.bridge.verify_contribution_on_chain(
            user_id=1,
            contribution_id=1,
            evidence=evidence
        )
        
        # Check the result
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(result['tokens_awarded'], 75)
        self.assertEqual(result['explanation'], self.metta_result['explanation'])
        self.assertEqual(result['confidence'], 0.85)
        self.assertIn('verification_tx', result)
        self.assertIn('token_tx', result)
        
        # Check that blockchain service was called
        self.assertEqual(len(self.blockchain.calls), 2)
        self.assertEqual(self.blockchain.calls[0]['method'], 'verify_contribution_on_chain')
        self.assertEqual(self.blockchain.calls[1]['method'], 'mint_tokens_for_contribution')
        
        # Verify the parameters passed to blockchain service
        self.assertEqual(self.blockchain.calls[0]['contribution_id'], 1)
        self.assertEqual(self.blockchain.calls[0]['tokens'], 75)
        self.assertEqual(self.blockchain.calls[1]['amount'], 75)
    
    async def test_verify_contribution_rejection(self):
        """Test rejection of invalid contribution"""
        # Configure MeTTa to reject the contribution
        self.metta.verify_contribution.return_value = {
            'verified': False,
            'confidence': 0.4,
            'explanation': 'Contribution could not be verified with sufficient confidence (40%). Reason: Insufficient evidence',
            'tokens': 0,
            'metta_proof': '0x1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d'
        }
        
        # Mock evidence
        evidence = {
            "url": "https://example.com/weak-evidence",
            "type": "website",
            "description": "A website with minimal proof of contribution"
        }
        
        # Execute the bridge verification
        result = await self.bridge.verify_contribution_on_chain(
            user_id=1,
            contribution_id=1,
            evidence=evidence
        )
        
        # Check the result
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('reason', result)
        self.assertEqual(result['confidence'], 0.4)
        
        # No blockchain calls should have been made
        self.assertEqual(len(self.blockchain.calls), 0)
    
    async def test_verify_contribution_fraud_detection(self):
        """Test fraud detection during verification"""
        # Configure MeTTa to detect fraud
        self.metta.detect_fraudulent_activity.return_value = {
            'is_fraud': True,
            'reason': 'Duplicate submission detected',
            'confidence': 0.9
        }
        
        # Mock evidence
        evidence = {
            "url": "https://github.com/test_user/python_project",
            "type": "github_repo",
            "description": "Repository containing the Python web application code"
        }
        
        # Execute the bridge verification
        result = await self.bridge.verify_contribution_on_chain(
            user_id=1,
            contribution_id=1,
            evidence=evidence
        )
        
        # Check the result
        self.assertEqual(result['status'], 'flagged_for_fraud')
        self.assertEqual(result['reason'], 'Duplicate submission detected')
        self.assertEqual(result['confidence'], 0.9)
        
        # No blockchain calls should have been made
        self.assertEqual(len(self.blockchain.calls), 0)

# Run the tests
if __name__ == '__main__':
    unittest.main()
```