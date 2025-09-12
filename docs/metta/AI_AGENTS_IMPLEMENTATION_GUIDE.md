# AI Agents Implementation Guide for Nimo Platform

## Overview

This guide provides step-by-step instructions for implementing the comprehensive AI agents architecture on the Nimo platform. The implementation builds on existing Cardano smart contracts and MeTTa reasoning capabilities to create a transparent, accountable, and fraud-resistant AI decision system.

## Prerequisites

### Existing Components (Already Available)
- ✅ Cardano smart contracts (contribution_validator.ak, identity_registry.ak, metta_bridge.ak)
- ✅ MeTTa integration service with enhanced fallback and caching
- ✅ Autonomous rule system with comprehensive reasoning
- ✅ Backend services with unified blockchain integration
- ✅ Performance monitoring and query optimization
- ✅ Cardano service with transaction handling

### New Components (Implemented)
- ✅ AI Agents Orchestrator (`backend/services/ai_agents_orchestrator.py`)
- ✅ AI Agents transparency rules (`backend/rules/ai_agents_transparency.metta`)
- ✅ AI Agents API routes (`backend/routes/ai_agents.py`)
- ✅ AI Agents smart contract (`contracts/cardano/ai_agents_validator.ak`)

## Implementation Steps

### Step 1: Deploy Smart Contracts

#### 1.1 Compile and Deploy AI Agents Validator

```bash
# Navigate to contracts directory
cd contracts/cardano

# Compile the AI agents validator
aiken build

# Generate deployment script
python deploy_ai_agents.py --network preprod
```

#### 1.2 Update Platform Configuration

Add the new contract addresses to your platform configuration:

```python
# In backend/config.py
AI_AGENTS_CONFIG = {
    'ai_agents_validator_address': 'addr_test1...',  # From deployment
    'decision_validator_address': 'addr_test1...',   # From deployment
    'challenge_validator_address': 'addr_test1...',  # From deployment
    'min_performance_bond': 1000 * 1000000,  # 1000 ADA in lovelace
    'challenge_period': 48 * 3600,           # 48 hours in seconds
    'base_challenge_stake': 100 * 1000000    # 100 ADA in lovelace
}
```

### Step 2: Initialize Backend Services

#### 2.1 Update Application Initialization

```python
# In backend/app.py
from routes.ai_agents import ai_agents_bp
from services.ai_agents_orchestrator import get_ai_agents_orchestrator
from services.metta_integration_enhanced import get_metta_service
from services.metta_reasoning import MeTTaReasoning

def create_app():
    app = Flask(__name__)
    
    # ... existing initialization ...
    
    # Initialize AI Agents system
    try:
        metta_integration = get_metta_service()
        metta_reasoning = MeTTaReasoning()
        
        # Get blockchain service
        if hasattr(app, 'cardano_service'):
            blockchain_service = app.cardano_service
        else:
            blockchain_service = CardanoService('preprod')
            app.cardano_service = blockchain_service
        
        # Initialize orchestrator
        app.ai_orchestrator = get_ai_agents_orchestrator(
            metta_integration, metta_reasoning, blockchain_service
        )
        
        logger.info("AI Agents system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI Agents system: {e}")
    
    # Register AI Agents blueprint
    app.register_blueprint(ai_agents_bp)
    
    return app
```

#### 2.2 Load AI Agents MeTTa Rules

```python
# In backend/services/metta_reasoning.py
def _initialize_core_rules(self):
    # ... existing rules loading ...
    
    # Load AI agents transparency rules
    ai_agents_rules_path = os.path.join(self.rules_dir, 'ai_agents_transparency.metta')
    if os.path.exists(ai_agents_rules_path):
        try:
            with open(ai_agents_rules_path, 'r') as f:
                ai_agents_rules = f.read()
                self._execute_metta(ai_agents_rules)
                logger.info("Loaded AI agents transparency rules")
        except Exception as e:
            logger.error(f"Error loading AI agents rules: {e}")
```

### Step 3: Register Core Agents

#### 3.1 Automatic Agent Registration

The orchestrator automatically registers core platform agents on initialization. These include:

- **Contribution Validation Agent**: Validates contribution submissions
- **Fraud Detection Agent**: Detects fraudulent activities
- **Reward Calculation Agent**: Calculates contribution rewards
- **Community Moderation Agent**: Moderates community content
- **Platform Governance Agent**: Coordinates governance decisions
- **Reputation Scoring Agent**: Calculates user reputation

#### 3.2 Custom Agent Registration

To register additional custom agents:

```bash
# Example API call to register a custom agent
curl -X POST http://localhost:5000/api/ai-agents/agents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "agent_id": "custom_validator_v1",
    "agent_type": "contribution_validation",
    "name": "Custom Validation Agent",
    "description": "Specialized validator for technical contributions",
    "performance_bond": 1500,
    "active": true
  }'
```

### Step 4: Configure Frontend Integration

#### 4.1 Add AI Agents Dashboard

Create a new Vue.js component for the AI agents dashboard:

```vue
<!-- In frontend/src/pages/AIAgentsDashboard.vue -->
<template>
  <q-page class="q-pa-md">
    <div class="q-mb-md">
      <h4>AI Agents Dashboard</h4>
      <p>Monitor and interact with platform AI agents</p>
    </div>
    
    <!-- Agents List -->
    <q-card class="q-mb-md">
      <q-card-section>
        <h6>Registered Agents</h6>
        <q-table
          :rows="agents"
          :columns="agentColumns"
          row-key="agent_id"
          :loading="loading"
        />
      </q-card-section>
    </q-card>
    
    <!-- Recent Decisions -->
    <q-card class="q-mb-md">
      <q-card-section>
        <h6>Recent Decisions</h6>
        <q-table
          :rows="recentDecisions"
          :columns="decisionColumns"
          row-key="decision_id"
          :loading="decisionsLoading"
        />
      </q-card-section>
    </q-card>
    
    <!-- Performance Metrics -->
    <q-card>
      <q-card-section>
        <h6>Platform Metrics</h6>
        <div class="row q-gutter-md">
          <div class="col">
            <q-statistic
              :value="metrics.totalAgents"
              label="Active Agents"
              color="primary"
            />
          </div>
          <div class="col">
            <q-statistic
              :value="metrics.totalDecisions"
              label="Total Decisions"
              color="secondary"
            />
          </div>
          <div class="col">
            <q-statistic
              :value="`${(metrics.challengeRate * 100).toFixed(1)}%`"
              label="Challenge Rate"
              color="accent"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'

// Reactive data
const agents = ref([])
const recentDecisions = ref([])
const metrics = ref({})
const loading = ref(false)
const decisionsLoading = ref(false)

// Table columns
const agentColumns = [
  { name: 'agent_id', label: 'Agent ID', field: 'agent_id', align: 'left' },
  { name: 'name', label: 'Name', field: 'name', align: 'left' },
  { name: 'agent_type', label: 'Type', field: 'agent_type', align: 'left' },
  { name: 'performance', label: 'Trust Score', field: (row) => row.performance?.trust_score?.toFixed(2) || 'N/A', align: 'center' }
]

const decisionColumns = [
  { name: 'decision_id', label: 'Decision ID', field: 'decision_id', align: 'left' },
  { name: 'agent_id', label: 'Agent', field: 'agent_id', align: 'left' },
  { name: 'confidence', label: 'Confidence', field: 'confidence', align: 'center' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' }
]

// Load data
async function loadAgents() {
  loading.value = true
  try {
    const response = await api.get('/ai-agents/agents')
    agents.value = response.data.agents
  } catch (error) {
    console.error('Error loading agents:', error)
  } finally {
    loading.value = false
  }
}

async function loadMetrics() {
  try {
    const response = await api.get('/ai-agents/analytics/performance')
    metrics.value = response.data.platform_metrics
  } catch (error) {
    console.error('Error loading metrics:', error)
  }
}

onMounted(() => {
  loadAgents()
  loadMetrics()
})
</script>
```

#### 4.2 Update Router

```typescript
// In frontend/src/router/routes.ts
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      // ... existing routes ...
      {
        path: 'ai-agents',
        component: () => import('pages/AIAgentsDashboard.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]
```

### Step 5: Testing and Validation

#### 5.1 Unit Tests

Create comprehensive unit tests for the AI agents system:

```python
# In backend/tests/test_ai_agents.py
import pytest
from services.ai_agents_orchestrator import AIAgentsOrchestrator, AgentType
from services.metta_integration_enhanced import MeTTaIntegrationService
from services.metta_reasoning import MeTTaReasoning

class MockBlockchainService:
    def register_agent(self, agent_spec):
        return {'success': True, 'tx_hash': f"mock_tx_{agent_spec['agent_id']}"}
    
    def create_decision_proof(self, decision):
        return {'success': True, 'tx_hash': f"mock_proof_{decision['decision_id']}"}

@pytest.fixture
def orchestrator():
    metta_integration = MeTTaIntegrationService(force_mock=True)
    metta_reasoning = MeTTaReasoning()
    blockchain_service = MockBlockchainService()
    
    return AIAgentsOrchestrator(
        metta_integration, metta_reasoning, blockchain_service
    )

def test_agent_registration(orchestrator):
    """Test agent registration"""
    agent_spec = {
        'agent_id': 'test_agent_v1',
        'agent_type': AgentType.CONTRIBUTION_VALIDATION,
        'name': 'Test Agent',
        'description': 'Test agent for validation',
        'performance_bond': 1000,
        'owner': 'test_user',
        'active': True
    }
    
    result = orchestrator.register_agent(agent_spec)
    
    assert result['success'] == True
    assert result['agent_id'] == 'test_agent_v1'
    assert 'test_agent_v1' in orchestrator.registered_agents

def test_decision_making(orchestrator):
    """Test decision making process"""
    # Use a pre-registered agent
    agent_id = 'contribution_validator_v1'
    input_data = {
        'contribution_id': 'test_contrib_123',
        'user_id': 'test_user_456',
        'evidence': {'type': 'github', 'url': 'https://github.com/test/repo'}
    }
    
    decision = orchestrator.make_decision(agent_id, input_data)
    
    assert decision.agent_id == agent_id
    assert decision.decision_id is not None
    assert 0.0 <= decision.confidence <= 1.0
    assert decision.metta_proof is not None

def test_challenge_system(orchestrator):
    """Test decision challenge system"""
    # First make a decision
    agent_id = 'fraud_detector_v1'
    input_data = {'contribution_id': 'test_contrib_789', 'user_id': 'test_user_999'}
    
    decision = orchestrator.make_decision(agent_id, input_data)
    
    # Then challenge it
    result = orchestrator.challenge_decision(
        decision.decision_id,
        'challenger_123',
        'Insufficient evidence',
        {'additional_evidence': 'proof_of_error'}
    )
    
    assert result['success'] == True
    assert 'challenge_id' in result
    assert result['stake_amount'] > 0
```

#### 5.2 Integration Tests

```python
# In backend/tests/test_ai_agents_integration.py
import pytest
import requests
from flask import Flask
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_agents_health_endpoint(client):
    """Test AI agents health endpoint"""
    response = client.get('/api/ai-agents/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'status' in data
    assert data['ai_agents_available'] is True

def test_list_agents_endpoint(client, auth_token):
    """Test list agents endpoint"""
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/api/ai-agents/agents', headers=headers)
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'agents' in data
    assert len(data['agents']) > 0

def test_make_decision_endpoint(client, auth_token):
    """Test make decision endpoint"""
    headers = {'Authorization': f'Bearer {auth_token}'}
    payload = {
        'contribution_id': 'test_contrib_999',
        'user_id': 'test_user_888',
        'evidence': {'type': 'github', 'url': 'https://github.com/test/repo'}
    }
    
    response = client.post(
        '/api/ai-agents/agents/contribution_validator_v1/decisions',
        json=payload,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'decision' in data
    assert 'decision_id' in data['decision']
```

### Step 6: Monitoring and Operations

#### 6.1 Logging Configuration

Update logging configuration to include AI agents:

```python
# In backend/config.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        # ... existing loggers ...
        'services.ai_agents_orchestrator': {
            'level': 'INFO',
            'handlers': ['file_handler', 'console_handler'],
            'propagate': False
        },
        'routes.ai_agents': {
            'level': 'INFO', 
            'handlers': ['file_handler', 'console_handler'],
            'propagate': False
        }
    }
}
```

#### 6.2 Performance Monitoring

Set up monitoring for AI agents performance:

```python
# In backend/monitoring/ai_agents_monitor.py
import time
from typing import Dict, Any
from services.ai_agents_orchestrator import get_ai_agents_orchestrator

class AIAgentsMonitor:
    def __init__(self):
        self.orchestrator = get_ai_agents_orchestrator()
        self.metrics_history = []
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current AI agents metrics"""
        metrics = {
            'timestamp': time.time(),
            'total_agents': len(self.orchestrator.registered_agents),
            'total_decisions': len(self.orchestrator.decision_history),
            'pending_challenges': len([
                c for c in self.orchestrator.challenge_history.values()
                if c.status == 'pending'
            ]),
            'agent_performance': {}
        }
        
        # Collect per-agent metrics
        for agent_id in self.orchestrator.registered_agents.keys():
            performance = self.orchestrator.get_agent_performance(agent_id)
            metrics['agent_performance'][agent_id] = performance
        
        self.metrics_history.append(metrics)
        return metrics
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        current_metrics = self.collect_metrics()
        
        # Calculate trends if we have historical data
        trends = {}
        if len(self.metrics_history) > 1:
            previous = self.metrics_history[-2]
            trends = {
                'decisions_growth': current_metrics['total_decisions'] - previous['total_decisions'],
                'challenges_growth': current_metrics['pending_challenges'] - previous['pending_challenges']
            }
        
        return {
            'current_metrics': current_metrics,
            'trends': trends,
            'recommendations': self._generate_recommendations(current_metrics)
        }
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate operational recommendations"""
        recommendations = []
        
        # Check challenge rate
        if metrics['total_decisions'] > 0:
            challenge_rate = metrics['pending_challenges'] / metrics['total_decisions']
            if challenge_rate > 0.1:  # More than 10% challenge rate
                recommendations.append("High challenge rate detected - review agent performance")
        
        # Check agent performance
        for agent_id, performance in metrics['agent_performance'].items():
            trust_score = performance.get('metrics', {}).get('trust_score', 1.0)
            if trust_score < 0.7:
                recommendations.append(f"Agent {agent_id} has low trust score - consider retraining")
        
        return recommendations
```

#### 6.3 Health Checks

Implement comprehensive health checks:

```python
# In backend/routes/health_routes.py (update existing)
@health_bp.route('/ai-agents', methods=['GET'])
def ai_agents_health():
    """Comprehensive AI agents health check"""
    try:
        orchestrator = get_ai_agents_orchestrator()
        
        # Basic service health
        health_status = {
            'service': 'ai_agents',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check orchestrator
        health_status['checks']['orchestrator'] = {
            'status': 'pass',
            'registered_agents': len(orchestrator.registered_agents),
            'active_agents': len([
                a for a in orchestrator.registered_agents.values() 
                if a['active']
            ])
        }
        
        # Check MeTTa integration
        try:
            metta_service = get_metta_service()
            metta_health = metta_service.health_check()
            health_status['checks']['metta_integration'] = {
                'status': 'pass' if metta_health.get('status') == 'operational' else 'fail',
                'details': metta_health
            }
        except Exception as e:
            health_status['checks']['metta_integration'] = {
                'status': 'fail',
                'error': str(e)
            }
        
        # Check blockchain integration
        try:
            if hasattr(orchestrator.blockchain, 'health_check'):
                blockchain_health = orchestrator.blockchain.health_check()
                health_status['checks']['blockchain'] = {
                    'status': 'pass',
                    'details': blockchain_health
                }
            else:
                health_status['checks']['blockchain'] = {
                    'status': 'pass',
                    'note': 'Using mock blockchain service'
                }
        except Exception as e:
            health_status['checks']['blockchain'] = {
                'status': 'fail',
                'error': str(e)
            }
        
        # Determine overall status
        failed_checks = [
            check for check in health_status['checks'].values()
            if check.get('status') == 'fail'
        ]
        
        if failed_checks:
            health_status['status'] = 'unhealthy'
            return jsonify(health_status), 503
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'service': 'ai_agents',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
```

## Deployment Checklist

### Pre-deployment
- [ ] Smart contracts compiled and tested
- [ ] Backend services initialized and tested
- [ ] MeTTa rules loaded and validated
- [ ] Database migrations completed
- [ ] Configuration files updated
- [ ] Unit tests passing
- [ ] Integration tests passing

### Deployment
- [ ] Deploy smart contracts to testnet
- [ ] Update backend configuration with contract addresses
- [ ] Deploy backend services
- [ ] Update frontend with new dashboard
- [ ] Run smoke tests
- [ ] Monitor logs for errors

### Post-deployment
- [ ] Verify agent registration
- [ ] Test decision making flow
- [ ] Test challenge mechanism
- [ ] Monitor performance metrics
- [ ] Set up alerting
- [ ] Document any issues

## Maintenance and Operations

### Regular Tasks
- Monitor agent performance metrics
- Review challenge resolution outcomes
- Update MeTTa rules based on community feedback
- Perform security audits
- Optimize gas usage and transaction costs

### Emergency Procedures
- Agent pause/resume procedures
- Challenge escalation process
- Performance bond slashing
- Governance intervention protocols

## Security Considerations

### Access Control
- Multi-signature requirements for critical operations
- Role-based access control for administrative functions
- Rate limiting on API endpoints
- Input validation and sanitization

### Data Protection
- Encrypt sensitive decision data
- Secure storage of MeTTa proofs
- Audit trail immutability
- Privacy-preserving challenge evidence

### Monitoring
- Real-time fraud detection
- Anomaly detection in agent behavior
- Performance degradation alerts
- Security incident response procedures

## Support and Documentation

### User Guides
- How to interact with AI agents
- Understanding decision transparency
- Challenge submission process
- Appeal procedures

### Developer Documentation
- API reference documentation
- Smart contract interfaces
- MeTTa rule development guide
- Integration examples

### Community Resources
- Governance participation guide
- Agent performance interpretation
- Best practices for evidence submission
- Community moderation guidelines

This implementation guide provides a comprehensive roadmap for deploying the AI agents architecture on the Nimo platform while maintaining the highest standards of transparency, accountability, and fraud prevention.