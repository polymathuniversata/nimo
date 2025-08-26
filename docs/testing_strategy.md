# Nimo Platform Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the Nimo Platform, covering all components including the backend API, smart contracts, MeTTa reasoning engine, and frontend integration. The testing approach ensures reliability, security, and performance across the entire system.

**Testing Philosophy:**
- Test-driven development for critical components
- Comprehensive coverage for security-sensitive areas
- Automated testing pipeline for CI/CD
- Performance and load testing for scalability
- End-to-end testing for user workflows

---

## Testing Pyramid

```
                    ┌─────────────────────────────┐
                    │      E2E Tests              │
                    │   - User workflows          │
                    │   - Cross-component         │
                    │   - Browser automation      │
                    └─────────────────────────────┘
              ┌──────────────────────────────────────┐
              │        Integration Tests             │
              │   - API endpoints                    │
              │   - Database interactions            │
              │   - Blockchain integration           │
              │   - MeTTa reasoning workflows        │
              └──────────────────────────────────────┘
      ┌────────────────────────────────────────────────────┐
      │                Unit Tests                          │
      │   - Individual functions                           │
      │   - Business logic                                 │
      │   - MeTTa rules                                    │
      │   - Smart contract functions                       │
      │   - Frontend components                            │
      └────────────────────────────────────────────────────┘
```

---

## 1. Backend API Testing

### Unit Tests

**Location:** `backend/tests/`
**Framework:** pytest
**Coverage Target:** 95%

#### Test Categories

```python
# backend/tests/test_api_routes.py
import pytest
from flask import json
from app import create_app, db
from models.user import User
from models.contribution import Contribution

@pytest.fixture
def client():
    """Test client fixture"""
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_user_registration(self, client):
        """Test user registration endpoint"""
        response = client.post('/api/auth/register', 
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'securepassword',
                'name': 'Test User'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        assert b'User registered successfully' in response.data
    
    def test_user_login(self, client):
        """Test user login endpoint"""
        # Create user first
        user = User(email='test@example.com', password='password', name='Test')
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['email'] == 'test@example.com'
```

#### Service Layer Tests

```python
# backend/tests/test_services.py
import pytest
from services.metta_reasoning import MeTTaReasoning
from services.token_service import award_tokens_for_verification

class TestMeTTaService:
    """Test MeTTa reasoning service"""
    
    def setUp(self):
        self.metta = MeTTaReasoning()
        
    def test_user_creation_in_metta_space(self):
        """Test adding user to MeTTa space"""
        self.metta.add_user("test_user", "testuser", [
            {"name": "python", "level": 3},
            {"name": "web_development", "level": 2}
        ])
        
        # Verify user exists in space
        user_exists = self.metta.space.parse_and_eval('(User "test_user" "testuser")')
        assert user_exists
        
        # Verify skills exist
        python_skill = self.metta.space.parse_and_eval('(HasSkill "test_user" "python" 3)')
        assert python_skill
    
    def test_contribution_verification_workflow(self):
        """Test complete verification workflow"""
        # Setup test data
        self.metta.add_user("user1", "contributor", ["coding", "python"])
        self.metta.add_contribution("contrib1", "user1", "development", 
                                  "Python Library", "significant")
        self.metta.add_evidence("contrib1", "github", 
                               "https://github.com/user1/python-lib")
        
        # Test verification
        result = self.metta.verify_contribution_with_explanation("contrib1")
        
        assert 'verified' in result
        assert 'confidence' in result
        assert 'explanation' in result
        assert result['confidence'] > 0.0
    
    def test_fraud_detection_patterns(self):
        """Test fraud detection capabilities"""
        # Create user with rapid submissions
        self.metta.add_user("fraud_user", "fraudster", ["coding"])
        
        # Add multiple contributions quickly (simulated)
        for i in range(5):
            self.metta.add_contribution(f"contrib{i}", "fraud_user", "development")
        
        # Test fraud detection
        result = self.metta.space.parse_and_eval('(DetectFraud "contrib1")')
        # Should detect suspicious patterns
        assert result  # Fraud detected
```

### Integration Tests

```python
# backend/tests/test_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from services.metta_blockchain_bridge import MeTTaBlockchainBridge

class TestMeTTaBlockchainIntegration:
    """Test MeTTa to blockchain integration"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_verification(self):
        """Test complete verification and blockchain recording"""
        # Setup services
        metta_service = MeTTaReasoning()
        blockchain_service = MockBlockchainService()
        bridge = MeTTaBlockchainBridge(metta_service, blockchain_service)
        
        # Setup test data
        with patch('models.user.User') as mock_user:
            mock_user.query.get.return_value.blockchain_address = "0xtest123"
            
            with patch('models.contribution.Contribution') as mock_contrib:
                mock_contrib.query.get.return_value.title = "Test Contribution"
                
                # Test verification
                result = await bridge.verify_contribution_on_chain(
                    user_id=1,
                    contribution_id=1,
                    evidence={"url": "https://github.com/test/repo", "type": "github"}
                )
                
                # Verify results
                assert result['status'] == 'verified'
                assert 'tokens_awarded' in result
                assert 'verification_tx' in result
                assert 'token_tx' in result
```

### API Endpoint Tests

```python
# backend/tests/test_endpoints.py
class TestContributionEndpoints:
    """Test contribution-related endpoints"""
    
    def test_get_contributions_authenticated(self, client, auth_header):
        """Test getting user contributions"""
        response = client.get('/api/contribution/', 
                            headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_add_contribution(self, client, auth_header):
        """Test adding a new contribution"""
        contribution_data = {
            'title': 'Test Contribution',
            'description': 'A test contribution',
            'type': 'development',
            'evidence': {
                'url': 'https://github.com/test/repo',
                'type': 'repository'
            }
        }
        
        response = client.post('/api/contribution/',
                             data=json.dumps(contribution_data),
                             content_type='application/json',
                             headers=auth_header)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Contribution'
    
    def test_verify_contribution_with_metta(self, client, auth_header):
        """Test MeTTa-powered verification"""
        # Create contribution first
        contrib_response = client.post('/api/contribution/',
                                     data=json.dumps({
                                         'title': 'Verification Test',
                                         'type': 'development'
                                     }),
                                     content_type='application/json',
                                     headers=auth_header)
        
        contrib_id = json.loads(contrib_response.data)['id']
        
        # Test verification
        verify_response = client.post(f'/api/contribution/{contrib_id}/verify',
                                    data=json.dumps({
                                        'organization': 'Test Org',
                                        'verifier_name': 'Test Verifier'
                                    }),
                                    content_type='application/json',
                                    headers=auth_header)
        
        assert verify_response.status_code == 200
        verify_data = json.loads(verify_response.data)
        assert 'verification' in verify_data
```

---

## 2. Smart Contract Testing

### Foundry Unit Tests

**Location:** `contracts/test/`
**Framework:** Forge (Foundry)
**Coverage Target:** 100%

#### Core Contract Tests

```solidity
// contracts/test/NimoIdentityTest.t.sol
contract NimoIdentityAdvancedTest is Test {
    NimoIdentity public nimoIdentity;
    NimoToken public nimoToken;
    
    function testFuzzIdentityCreation(string memory username, string memory metadataURI) public {
        // Fuzz test identity creation with various inputs
        vm.assume(bytes(username).length > 0 && bytes(username).length < 50);
        vm.assume(bytes(metadataURI).length > 0);
        
        vm.prank(user1);
        nimoIdentity.createIdentity(username, metadataURI);
        
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentity(1);
        assertEq(identity.username, username);
        assertEq(identity.metadataURI, metadataURI);
    }
    
    function testContributionVerificationGasUsage() public {
        // Setup
        vm.prank(user1);
        nimoIdentity.createIdentity("gastest", "ipfs://test");
        
        vm.prank(user1);
        nimoIdentity.addContribution("test", "description", "evidence", "hash");
        
        // Measure gas usage
        uint256 gasBefore = gasleft();
        vm.prank(verifier);
        nimoIdentity.verifyContribution(1, 100);
        uint256 gasUsed = gasBefore - gasleft();
        
        // Assert gas usage is within acceptable limits
        assertLt(gasUsed, 150000);
    }
    
    function testReentrancyProtection() public {
        // Test reentrancy protection on investInBond function
        ReentrancyAttacker attacker = new ReentrancyAttacker(nimoIdentity);
        
        // Setup bond
        vm.prank(user1);
        nimoIdentity.createIdentity("creator", "ipfs://test");
        
        string[] memory milestones = new string[](1);
        milestones[0] = "Test milestone";
        
        vm.prank(user1);
        nimoIdentity.createImpactBond("Test Bond", "Description", 10 ether, 
                                    block.timestamp + 365 days, milestones);
        
        // Attempt reentrancy attack
        vm.expectRevert("ReentrancyGuard: reentrant call");
        attacker.attack{value: 1 ether}(1);
    }
}

// Reentrancy attack contract for testing
contract ReentrancyAttacker {
    NimoIdentity target;
    
    constructor(NimoIdentity _target) {
        target = _target;
    }
    
    function attack(uint256 bondId) external payable {
        target.investInBond{value: msg.value}(bondId);
    }
    
    receive() external payable {
        if (address(target).balance >= msg.value) {
            target.investInBond{value: msg.value}(1);
        }
    }
}
```

#### Token Contract Tests

```solidity
// contracts/test/NimoTokenTest.t.sol
contract NimoTokenTest is Test {
    NimoToken public nimoToken;
    
    function testMintingWithMeTTaProof() public {
        address recipient = address(0x123);
        uint256 amount = 100 * 10**18;
        string memory reason = "Verified contribution";
        string memory mettaProof = "0x1a2b3c4d...";
        
        nimoToken.mintForContribution(recipient, amount, reason, mettaProof);
        
        // Check token balance
        assertEq(nimoToken.balanceOf(recipient), amount);
        
        // Check distribution record
        NimoToken.Distribution memory dist = nimoToken.getDistribution(1);
        assertEq(dist.recipient, recipient);
        assertEq(dist.amount, amount);
        assertEq(dist.reason, reason);
        assertEq(dist.mettaProof, mettaProof);
    }
    
    function testPauseUnpauseFunctionality() public {
        address user = address(0x123);
        
        // Mint some tokens
        nimoToken.mintForContribution(user, 100, "test", "proof");
        
        // Pause contract
        nimoToken.pause();
        
        // Transfers should fail when paused
        vm.prank(user);
        vm.expectRevert("Pausable: paused");
        nimoToken.transfer(address(0x456), 50);
        
        // Unpause contract
        nimoToken.unpause();
        
        // Transfers should work again
        vm.prank(user);
        nimoToken.transfer(address(0x456), 50);
        
        assertEq(nimoToken.balanceOf(address(0x456)), 50);
    }
}
```

### Gas Optimization Tests

```bash
# Gas analysis script
#!/bin/bash

# Run gas report
forge test --gas-report

# Check specific functions don't exceed thresholds
forge test --match-test "testContributionVerificationGasUsage" --gas-limit 200000

# Profile gas usage for deployment
forge create --gas-limit 5000000 src/NimoIdentity.sol:NimoIdentity
```

---

## 3. MeTTa Reasoning Engine Testing

### Rule Testing

**Location:** `backend/tests/test_metta_rules.py`

```python
# backend/tests/test_metta_rules.py
import unittest
from services.metta_reasoning import MeTTaReasoning

class TestMeTTaRules(unittest.TestCase):
    """Test individual MeTTa rules and reasoning patterns"""
    
    def setUp(self):
        self.metta = MeTTaReasoning()
        
    def test_verification_rule_logic(self):
        """Test core verification rule"""
        # Setup test data
        self.metta.add_user("testuser", "Test User", [
            {"name": "python", "level": 3}
        ])
        self.metta.add_contribution("contrib1", "testuser", "coding")
        self.metta.add_evidence("contrib1", "github", "https://github.com/test/repo")
        
        # Test verification
        result = self.metta.space.parse_and_eval('(VerifyContribution "contrib1")')
        self.assertTrue(result)
        
    def test_confidence_calculation_accuracy(self):
        """Test confidence scoring accuracy"""
        # Test with high-quality evidence
        self.metta.add_user("highuser", "High Quality User", [
            {"name": "blockchain", "level": 5}
        ])
        self.metta.add_contribution("highcontrib", "highuser", "development")
        self.metta.add_evidence("highcontrib", "github", "https://github.com/expert/project")
        
        confidence = self.metta.space.parse_and_eval('(CalculateConfidence "highcontrib")')
        self.assertGreaterEqual(confidence, 0.8)
        
        # Test with low-quality evidence
        self.metta.add_user("lowuser", "Low Quality User", [])
        self.metta.add_contribution("lowcontrib", "lowuser", "development")
        
        low_confidence = self.metta.space.parse_and_eval('(CalculateConfidence "lowcontrib")')
        self.assertLessEqual(low_confidence, 0.5)
        
    def test_token_award_calculation(self):
        """Test token award calculation for different categories"""
        test_cases = [
            ("coding", 75),
            ("education", 60),
            ("volunteer", 50),
            ("activism", 65)
        ]
        
        for category, expected_base in test_cases:
            self.metta.add_contribution(f"contrib_{category}", "user1", category)
            award = self.metta.space.parse_and_eval(f'(BaseTokenAmount "{category}")')
            self.assertEqual(award, expected_base)
            
    def test_fraud_detection_patterns(self):
        """Test fraud detection rules"""
        # Test duplicate submission detection
        self.metta.add_user("frauduser", "Fraud User", ["coding"])
        
        # Add multiple contributions with same evidence
        evidence_url = "https://github.com/fake/repo"
        for i in range(3):
            contrib_id = f"fraud_contrib_{i}"
            self.metta.add_contribution(contrib_id, "frauduser", "development")
            self.metta.add_evidence(contrib_id, "github", evidence_url)
        
        # Test fraud detection
        fraud_detected = self.metta.space.parse_and_eval('(DetectFraud "fraud_contrib_1")')
        self.assertTrue(fraud_detected)
        
    def test_reputation_calculation_components(self):
        """Test individual components of reputation calculation"""
        # Setup user with verified contributions
        self.metta.add_user("repuser", "Reputation User", [
            {"name": "python", "level": 4},
            {"name": "javascript", "level": 3},
            {"name": "react", "level": 2}
        ])
        
        # Add verified contributions
        for i in range(5):
            contrib_id = f"verified_contrib_{i}"
            self.metta.add_contribution(contrib_id, "repuser", "development")
            # Simulate verification
            self.metta.space.parse_and_eval(f'(SetVerified "{contrib_id}" true)')
        
        # Test reputation components
        verified_count = self.metta.space.parse_and_eval('(CountVerifiedContributions "repuser")')
        self.assertEqual(verified_count, 5)
        
        skill_diversity = self.metta.space.parse_and_eval('(CountUniqueSkills "repuser")')
        self.assertEqual(skill_diversity, 3)
        
        reputation = self.metta.space.parse_and_eval('(CalculateUserReputation "repuser")')
        self.assertGreater(reputation, 0)
```

### Performance Tests

```python
# backend/tests/test_metta_performance.py
import time
import pytest
from services.metta_reasoning import MeTTaReasoning

class TestMeTTaPerformance:
    """Test MeTTa reasoning engine performance"""
    
    def test_verification_latency(self):
        """Test verification response time"""
        metta = MeTTaReasoning()
        
        # Setup test data
        metta.add_user("perfuser", "Performance User", ["coding", "python"])
        metta.add_contribution("perfcontrib", "perfuser", "development")
        metta.add_evidence("perfcontrib", "github", "https://github.com/test/perf")
        
        # Measure verification time
        start_time = time.time()
        result = metta.verify_contribution_with_explanation("perfcontrib")
        execution_time = time.time() - start_time
        
        # Should complete within 100ms
        assert execution_time < 0.1
        assert 'verified' in result
        
    def test_batch_processing_performance(self):
        """Test batch verification performance"""
        metta = MeTTaReasoning()
        
        # Setup multiple contributions
        contribution_ids = []
        for i in range(100):
            user_id = f"user_{i}"
            contrib_id = f"contrib_{i}"
            
            metta.add_user(user_id, f"User {i}", ["skill1", "skill2"])
            metta.add_contribution(contrib_id, user_id, "development")
            metta.add_evidence(contrib_id, "github", f"https://github.com/user{i}/repo")
            contribution_ids.append(contrib_id)
        
        # Measure batch verification time
        start_time = time.time()
        results = metta.batch_verify_contributions(contribution_ids)
        execution_time = time.time() - start_time
        
        # Should process 100 contributions in under 5 seconds
        assert execution_time < 5.0
        assert len(results) == 100
        
    def test_memory_usage_stability(self):
        """Test memory usage doesn't grow unbounded"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        metta = MeTTaReasoning()
        
        # Add many entities and verify
        for i in range(1000):
            if i % 100 == 0:
                gc.collect()  # Force garbage collection
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be reasonable (< 100MB)
                assert memory_growth < 100 * 1024 * 1024
            
            metta.add_user(f"memuser_{i}", f"User {i}", ["skill"])
            metta.add_contribution(f"memcontrib_{i}", f"memuser_{i}", "test")
```

---

## 4. Frontend Testing

### Component Testing

**Framework:** Jest + Vue Test Utils
**Location:** `frontend/src/tests/`

```javascript
// frontend/src/tests/components/WalletConnect.test.js
import { mount } from '@vue/test-utils'
import WalletConnect from '@/components/WalletConnect.vue'
import { createPinia } from 'pinia'

describe('WalletConnect Component', () => {
  let wrapper
  let pinia
  
  beforeEach(() => {
    pinia = createPinia()
    wrapper = mount(WalletConnect, {
      global: {
        plugins: [pinia]
      }
    })
  })
  
  afterEach(() => {
    wrapper.unmount()
  })
  
  it('renders correctly when wallet not connected', () => {
    expect(wrapper.find('[data-test="connect-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="disconnect-button"]').exists()).toBe(false)
  })
  
  it('shows wallet info when connected', async () => {
    // Mock wallet connection
    const walletStore = useWalletStore()
    walletStore.isConnected = true
    walletStore.address = '0x1234567890123456789012345678901234567890'
    walletStore.balance = '1.5'
    
    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('[data-test="wallet-address"]').text()).toContain('0x1234')
    expect(wrapper.find('[data-test="wallet-balance"]').text()).toContain('1.5')
    expect(wrapper.find('[data-test="disconnect-button"]').exists()).toBe(true)
  })
  
  it('handles wallet connection error gracefully', async () => {
    // Mock wallet connection error
    const mockConnect = jest.fn().mockRejectedValue(new Error('User rejected'))
    wrapper.vm.connectWallet = mockConnect
    
    await wrapper.find('[data-test="connect-button"]').trigger('click')
    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('[data-test="error-message"]').text()).toContain('User rejected')
  })
})
```

### Integration Tests

```javascript
// frontend/src/tests/integration/ContributionFlow.test.js
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import ContributionsPage from '@/pages/ContributionsPage.vue'
import { contributionService } from '@/services'

// Mock API service
jest.mock('@/services', () => ({
  contributionService: {
    getContributions: jest.fn(),
    createContribution: jest.fn(),
    verifyContribution: jest.fn()
  }
}))

describe('Contribution Flow Integration', () => {
  let wrapper
  let router
  let pinia
  
  beforeEach(async () => {
    pinia = createPinia()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/contributions', component: ContributionsPage }
      ]
    })
    
    router.push('/contributions')
    await router.isReady()
    
    wrapper = mount(ContributionsPage, {
      global: {
        plugins: [pinia, router]
      }
    })
  })
  
  it('displays contributions list on load', async () => {
    const mockContributions = [
      {
        id: 1,
        title: 'Test Contribution',
        type: 'development',
        verified: false,
        created_at: '2025-01-15T10:00:00Z'
      }
    ]
    
    contributionService.getContributions.mockResolvedValue(mockContributions)
    
    await wrapper.vm.loadContributions()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.findAll('[data-test="contribution-item"]')).toHaveLength(1)
    expect(wrapper.find('[data-test="contribution-title"]').text()).toBe('Test Contribution')
  })
  
  it('handles contribution creation workflow', async () => {
    const newContribution = {
      title: 'New Contribution',
      description: 'Test description',
      type: 'education',
      evidence: {
        url: 'https://example.com/evidence',
        type: 'website'
      }
    }
    
    contributionService.createContribution.mockResolvedValue({
      id: 2,
      ...newContribution,
      created_at: new Date().toISOString()
    })
    
    // Open create modal
    await wrapper.find('[data-test="add-contribution-button"]').trigger('click')
    expect(wrapper.find('[data-test="create-modal"]').exists()).toBe(true)
    
    // Fill form
    await wrapper.find('[data-test="title-input"]').setValue(newContribution.title)
    await wrapper.find('[data-test="description-input"]').setValue(newContribution.description)
    await wrapper.find('[data-test="type-select"]').setValue(newContribution.type)
    await wrapper.find('[data-test="evidence-url-input"]').setValue(newContribution.evidence.url)
    
    // Submit form
    await wrapper.find('[data-test="submit-button"]').trigger('click')
    await wrapper.vm.$nextTick()
    
    expect(contributionService.createContribution).toHaveBeenCalledWith(newContribution)
    expect(wrapper.find('[data-test="success-message"]').exists()).toBe(true)
  })
})
```

### E2E Tests

**Framework:** Playwright
**Location:** `frontend/tests/e2e/`

```javascript
// frontend/tests/e2e/user-workflow.spec.js
const { test, expect } = require('@playwright/test')

test.describe('User Authentication and Contribution Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Setup test environment
    await page.goto('http://localhost:3000')
  })
  
  test('complete user workflow from registration to contribution', async ({ page }) => {
    // User Registration
    await page.click('[data-test="register-link"]')
    await page.fill('[data-test="email-input"]', 'test@example.com')
    await page.fill('[data-test="password-input"]', 'securepassword')
    await page.fill('[data-test="name-input"]', 'Test User')
    await page.click('[data-test="register-button"]')
    
    await expect(page).toHaveURL('/contributions')
    await expect(page.locator('[data-test="welcome-message"]')).toContainText('Welcome, Test User')
    
    // Create Contribution
    await page.click('[data-test="add-contribution-button"]')
    await page.fill('[data-test="title-input"]', 'E2E Test Contribution')
    await page.fill('[data-test="description-input"]', 'Created via E2E test')
    await page.selectOption('[data-test="type-select"]', 'development')
    await page.fill('[data-test="evidence-url"]', 'https://github.com/test/repo')
    await page.click('[data-test="submit-contribution"]')
    
    // Verify contribution appears in list
    await expect(page.locator('[data-test="contribution-item"]')).toHaveCount(1)
    await expect(page.locator('[data-test="contribution-title"]')).toContainText('E2E Test Contribution')
    
    // Check contribution status
    const status = page.locator('[data-test="contribution-status"]')
    await expect(status).toContainText('Pending Verification')
  })
  
  test('wallet connection and blockchain interaction', async ({ page }) => {
    // Mock wallet connection
    await page.addInitScript(() => {
      window.ethereum = {
        isMetaMask: true,
        request: async ({ method }) => {
          if (method === 'eth_requestAccounts') {
            return ['0x1234567890123456789012345678901234567890']
          }
          if (method === 'eth_chainId') {
            return '0x14a34' // Base Sepolia chain ID
          }
        }
      }
    })
    
    await page.goto('/profile')
    
    // Connect wallet
    await page.click('[data-test="connect-wallet-button"]')
    await expect(page.locator('[data-test="wallet-address"]')).toContainText('0x1234')
    
    // Test token balance display
    await expect(page.locator('[data-test="token-balance"]')).toBeVisible()
  })
  
  test('responsive design on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    
    await page.goto('/contributions')
    
    // Check mobile navigation
    await expect(page.locator('[data-test="mobile-menu-button"]')).toBeVisible()
    await page.click('[data-test="mobile-menu-button"]')
    await expect(page.locator('[data-test="mobile-menu"]')).toBeVisible()
    
    // Check responsive contribution cards
    const contributionCards = page.locator('[data-test="contribution-card"]')
    const cardWidth = await contributionCards.first().boundingBox()
    expect(cardWidth.width).toBeLessThan(400)
  })
})
```

---

## 5. Performance Testing

### Load Testing

**Framework:** k6
**Location:** `tests/performance/`

```javascript
// tests/performance/api-load-test.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

const errorRate = new Rate('errors')

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must be below 500ms
    errors: ['rate<0.1'],             // Error rate must be below 10%
  }
}

const BASE_URL = 'http://localhost:5000/api'

export function setup() {
  // Create test user and get auth token
  const registerResponse = http.post(`${BASE_URL}/auth/register`, JSON.stringify({
    email: `testuser${Date.now()}@example.com`,
    password: 'testpassword',
    name: 'Load Test User'
  }), {
    headers: { 'Content-Type': 'application/json' }
  })
  
  const loginResponse = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: registerResponse.json().email || `testuser${Date.now()}@example.com`,
    password: 'testpassword'
  }), {
    headers: { 'Content-Type': 'application/json' }
  })
  
  return {
    token: loginResponse.json().access_token
  }
}

export default function(data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`
  }
  
  // Test contribution endpoints
  const contributionsResponse = http.get(`${BASE_URL}/contribution/`, { headers })
  
  check(contributionsResponse, {
    'get contributions status 200': (r) => r.status === 200,
    'get contributions response time < 200ms': (r) => r.timings.duration < 200,
  }) || errorRate.add(1)
  
  // Test creating contribution
  const createResponse = http.post(`${BASE_URL}/contribution/`, JSON.stringify({
    title: `Load Test Contribution ${Date.now()}`,
    description: 'Performance test contribution',
    type: 'development',
    evidence: {
      url: 'https://github.com/test/load-test',
      type: 'repository'
    }
  }), { headers })
  
  check(createResponse, {
    'create contribution status 201': (r) => r.status === 201,
    'create contribution response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1)
  
  sleep(1)
}
```

### MeTTa Performance Testing

```javascript
// tests/performance/metta-performance.js
import http from 'k6/http'
import { check, sleep } from 'k6'

export let options = {
  scenarios: {
    verification_load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '5m',
    },
    fraud_detection_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 20 },
        { duration: '3m', target: 20 },
        { duration: '1m', target: 0 },
      ],
    }
  },
  thresholds: {
    'http_req_duration{scenario:verification_load}': ['p(95)<1000'],
    'http_req_duration{scenario:fraud_detection_load}': ['p(95)<2000'],
  }
}

export default function() {
  // Test MeTTa verification endpoint
  const verificationResponse = http.post(`${BASE_URL}/contribution/1/verify`, 
    JSON.stringify({
      organization: 'Performance Test Org',
      verifier_name: 'Load Tester'
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    }
  )
  
  check(verificationResponse, {
    'metta verification completes': (r) => r.status === 200,
    'metta verification under 1s': (r) => r.timings.duration < 1000,
    'metta returns confidence score': (r) => r.json().hasOwnProperty('confidence'),
  })
  
  sleep(2)
}
```

---

## 6. Security Testing

### Vulnerability Testing

**Framework:** Custom security test suite
**Location:** `tests/security/`

```python
# tests/security/test_auth_security.py
import pytest
import jwt
from datetime import datetime, timedelta

class TestAuthenticationSecurity:
    """Test authentication and authorization security"""
    
    def test_jwt_token_expiration(self, client):
        """Test JWT tokens expire correctly"""
        # Login and get token
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        
        token = response.json['access_token']
        
        # Decode token and check expiration
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Token should expire within 1 hour
        expected_expiry = datetime.utcnow() + timedelta(hours=1)
        assert abs((exp_datetime - expected_expiry).total_seconds()) < 60
    
    def test_password_hashing_security(self, client):
        """Test passwords are properly hashed"""
        from models.user import User
        
        user = User(email='test@example.com', password='plaintext', name='Test')
        
        # Password should be hashed, not stored as plaintext
        assert user.password_hash != 'plaintext'
        assert len(user.password_hash) > 50  # Hashed passwords are long
        assert user.verify_password('plaintext')
        assert not user.verify_password('wrongpassword')
    
    def test_sql_injection_protection(self, client, auth_header):
        """Test SQL injection protection"""
        # Attempt SQL injection in contribution search
        malicious_input = "'; DROP TABLE contributions; --"
        
        response = client.get(f'/api/contribution/?title={malicious_input}', 
                            headers=auth_header)
        
        # Should not cause server error (protected by SQLAlchemy ORM)
        assert response.status_code in [200, 400]
        
        # Database should still be intact
        contrib_response = client.get('/api/contribution/', headers=auth_header)
        assert contrib_response.status_code == 200
    
    def test_rate_limiting(self, client):
        """Test rate limiting on sensitive endpoints"""
        # Attempt multiple rapid login attempts
        for i in range(10):
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
        
        # After several attempts, should be rate limited
        assert response.status_code == 429  # Too Many Requests
```

### Smart Contract Security

```solidity
// contracts/test/SecurityTests.t.sol
contract SecurityTests is Test {
    NimoIdentity public nimoIdentity;
    
    function testAccessControlEnforcement() public {
        address attacker = address(0x999);
        
        // Attempt to verify contribution without VERIFIER_ROLE
        vm.prank(attacker);
        vm.expectRevert();
        nimoIdentity.verifyContribution(1, 100);
        
        // Attempt to execute MeTTa rule without METTA_AGENT_ROLE
        vm.prank(attacker);
        vm.expectRevert();
        nimoIdentity.executeMeTTaRule("malicious rule", 1, 1000);
    }
    
    function testOverflowProtection() public {
        // Test uint256 overflow protection
        vm.prank(user1);
        nimoIdentity.createIdentity("testuser", "ipfs://test");
        
        // Attempt to award maximum uint256 tokens (should not overflow)
        vm.prank(verifier);
        nimoIdentity.verifyContribution(1, type(uint256).max);
        
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentity(1);
        assertTrue(identity.tokenBalance > 0);
        assertTrue(identity.reputationScore > 0);
    }
    
    function testMaliciousMetadataHandling() public {
        string memory maliciousMetadata = "javascript:alert('xss')";
        
        vm.prank(user1);
        // Should not revert but should handle malicious input safely
        nimoIdentity.createIdentity("testuser", maliciousMetadata);
        
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentity(1);
        assertEq(identity.metadataURI, maliciousMetadata);
        // Frontend should sanitize display
    }
}
```

---

## 7. Testing Infrastructure

### CI/CD Pipeline

**File:** `.github/workflows/test.yml`

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: nimo_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/nimo_test
        FLASK_ENV: testing
      run: |
        cd backend
        pytest --cov=. --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  smart-contract-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        submodules: recursive
    
    - name: Install Foundry
      uses: foundry-rs/foundry-toolchain@v1
      with:
        version: nightly
    
    - name: Run contract tests
      run: |
        cd contracts
        forge test -vvv
        forge coverage --report lcov
    
    - name: Upload contract coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./contracts/lcov.info

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run unit tests
      run: |
        cd frontend
        npm run test:unit -- --coverage
    
    - name: Run E2E tests
      run: |
        cd frontend
        npm run test:e2e -- --headless

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security linting
      run: |
        cd backend
        pip install bandit safety
        bandit -r . -f json -o security-report.json
        safety check --json --output security-deps.json
    
    - name: Contract security analysis
      run: |
        cd contracts
        # Install slither for static analysis
        pip install slither-analyzer
        slither . --json security-analysis.json
```

### Test Data Management

```python
# tests/fixtures/test_data.py
import pytest
from backend.app import create_app, db
from backend.models.user import User
from backend.models.contribution import Contribution

@pytest.fixture(scope='session')
def test_app():
    """Create test application"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_users(test_app):
    """Create test users"""
    with test_app.app_context():
        users = [
            User(email='alice@example.com', password='password', name='Alice Smith'),
            User(email='bob@example.com', password='password', name='Bob Johnson'),
            User(email='charlie@example.com', password='password', name='Charlie Brown')
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        
        yield users
        
        # Cleanup
        for user in users:
            db.session.delete(user)
        db.session.commit()

@pytest.fixture
def test_contributions(test_app, test_users):
    """Create test contributions"""
    with test_app.app_context():
        contributions = [
            Contribution(
                user_id=test_users[0].id,
                title='Python Web Framework',
                description='Built a lightweight web framework',
                contribution_type='development',
                evidence={'url': 'https://github.com/alice/framework'}
            ),
            Contribution(
                user_id=test_users[1].id,
                title='Community Workshop',
                description='Organized coding workshop for beginners',
                contribution_type='education',
                evidence={'url': 'https://example.com/workshop', 'description': 'Workshop materials'}
            )
        ]
        
        for contrib in contributions:
            db.session.add(contrib)
        
        db.session.commit()
        yield contributions
        
        # Cleanup
        for contrib in contributions:
            db.session.delete(contrib)
        db.session.commit()
```

---

## 8. Test Environment Setup

### Docker Test Environment

**File:** `docker-compose.test.yml`

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres-test:
    image: postgres:13
    environment:
      POSTGRES_DB: nimo_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data
  
  backend-test:
    build: 
      context: ./backend
      dockerfile: Dockerfile.test
    depends_on:
      - postgres-test
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres-test:5432/nimo_test
      FLASK_ENV: testing
      USE_METTA_REASONING: "true"
    volumes:
      - ./backend:/app
      - ./backend/tests:/app/tests
    command: pytest --cov=. --cov-report=html --cov-report=term
  
  anvil-test:
    image: ghcr.io/foundry-rs/foundry:latest
    ports:
      - "8545:8545"
    command: anvil --host 0.0.0.0 --chain-id 31337
  
  frontend-test:
    build:
      context: ./frontend
      dockerfile: Dockerfile.test
    depends_on:
      - backend-test
    volumes:
      - ./frontend:/app
    environment:
      VITE_API_BASE_URL: http://backend-test:5000/api
    command: npm run test:unit
```

### Test Configuration

```python
# backend/config.py - Test configuration
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5433/nimo_test'
    
    # MeTTa testing configuration
    USE_METTA_REASONING = True
    METTA_DB_PATH = ':memory:'  # In-memory for tests
    METTA_CONFIDENCE_THRESHOLD = 0.5  # Lower threshold for tests
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
```

---

## 9. Test Execution

### Running Tests Locally

```bash
#!/bin/bash
# scripts/run-tests.sh

echo "Starting Nimo Platform Test Suite"

# Backend tests
echo "Running backend tests..."
cd backend
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term -v

# Smart contract tests
echo "Running smart contract tests..."
cd ../contracts
forge test -vv --gas-report

# Frontend tests
echo "Running frontend tests..."
cd ../frontend
npm run test:unit
npm run test:e2e:headless

# Performance tests
echo "Running performance tests..."
k6 run tests/performance/api-load-test.js

# Security tests
echo "Running security tests..."
cd ../backend
bandit -r . -f json -o security-report.json
safety check

echo "All tests completed!"
```

### Continuous Integration

```bash
# scripts/ci-test.sh
#!/bin/bash
set -e

echo "CI Test Pipeline Starting..."

# Setup test environment
docker-compose -f docker-compose.test.yml up -d postgres-test anvil-test

# Wait for services
sleep 10

# Run tests in parallel
docker-compose -f docker-compose.test.yml run --rm backend-test &
BACKEND_PID=$!

docker-compose -f docker-compose.test.yml run --rm frontend-test &
FRONTEND_PID=$!

# Smart contract tests
cd contracts && forge test --gas-report && cd .. &
CONTRACT_PID=$!

# Wait for all test suites
wait $BACKEND_PID
BACKEND_EXIT=$?

wait $FRONTEND_PID  
FRONTEND_EXIT=$?

wait $CONTRACT_PID
CONTRACT_EXIT=$?

# Cleanup
docker-compose -f docker-compose.test.yml down

# Check results
if [[ $BACKEND_EXIT -eq 0 && $FRONTEND_EXIT -eq 0 && $CONTRACT_EXIT -eq 0 ]]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed!"
    exit 1
fi
```

---

## 10. Test Metrics and Reporting

### Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|----------------|
| Backend API | 85% | 95% |
| MeTTa Rules | 90% | 100% |
| Smart Contracts | 95% | 100% |
| Frontend Components | 80% | 90% |
| Integration Flows | 75% | 85% |

### Quality Gates

```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
    - name: Check test coverage
      run: |
        # Backend coverage check
        BACKEND_COVERAGE=$(grep -o 'Total coverage: [0-9]*%' coverage-report.txt | grep -o '[0-9]*')
        if [ "$BACKEND_COVERAGE" -lt 85 ]; then
          echo "Backend coverage $BACKEND_COVERAGE% below required 85%"
          exit 1
        fi
        
        # Contract coverage check
        CONTRACT_COVERAGE=$(forge coverage --report summary | grep "Overall" | awk '{print $2}' | tr -d '%')
        if [ "$CONTRACT_COVERAGE" -lt 95 ]; then
          echo "Contract coverage $CONTRACT_COVERAGE% below required 95%"
          exit 1
        fi
    
    - name: Check test execution time
      run: |
        # Tests should complete within reasonable time
        if [ "$TEST_DURATION" -gt 300 ]; then  # 5 minutes
          echo "Test suite taking too long: ${TEST_DURATION}s"
          exit 1
        fi
```

### Test Reports

```python
# tests/utils/reporting.py
import json
import datetime
from pathlib import Path

class TestReporter:
    """Generate comprehensive test reports"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'summary': {},
            'details': {}
        }
    
    def add_test_suite_result(self, suite_name, passed, failed, skipped, duration):
        """Add test suite results"""
        self.results['details'][suite_name] = {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': duration,
            'success_rate': passed / (passed + failed) if (passed + failed) > 0 else 0
        }
    
    def generate_report(self, output_path='test-report.json'):
        """Generate final test report"""
        # Calculate summary
        total_passed = sum(r['passed'] for r in self.results['details'].values())
        total_failed = sum(r['failed'] for r in self.results['details'].values())
        total_duration = sum(r['duration'] for r in self.results['details'].values())
        
        self.results['summary'] = {
            'total_tests': total_passed + total_failed,
            'passed': total_passed,
            'failed': total_failed,
            'success_rate': total_passed / (total_passed + total_failed) if (total_passed + total_failed) > 0 else 0,
            'total_duration': total_duration
        }
        
        # Write report
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return self.results
```

---

## Conclusion

This comprehensive testing strategy ensures the Nimo Platform maintains high quality, security, and performance standards. The multi-layered approach covers:

✅ **Completed Testing Framework:**
- Unit tests for all components
- Integration tests for cross-component workflows
- Smart contract security and functionality tests
- Frontend component and E2E tests
- Performance and load testing
- Security vulnerability testing
- Automated CI/CD pipeline

🔄 **Continuous Improvement:**
- Regular test coverage analysis
- Performance benchmark tracking
- Security audit integration
- User acceptance testing
- Stress testing for scalability

The testing strategy supports rapid development while maintaining reliability and security, ensuring the platform can scale and evolve safely.

---

*Last Updated: January 26, 2025*  
*Author: John (Backend Developer)*  
*Status: Comprehensive testing framework ready for implementation*