# MeTTa Reasoning Engine Implementation Guide

## Overview

The Nimo Platform utilizes MeTTa (Meta Type Talking), a symbolic reasoning language developed by SingularityNET, to provide autonomous verification, fraud detection, and reputation scoring. This implementation enables the platform to make intelligent decisions about contributions, calculate token awards, and maintain trust without human intervention.

**Key Features:**
- Autonomous contribution verification
- Confidence scoring for decisions
- Fraud detection and pattern recognition
- Dynamic token award calculation
- Reputation scoring system
- Explainable AI decisions

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    MeTTa Reasoning Engine                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐│
│  │   Core Rules    │    │  Python Service  │    │ Blockchain  ││
│  │   (core_rules.  │    │  (metta_reasoning │    │   Bridge    ││
│  │    metta)       │◄──►│      .py)        │◄──►│             ││
│  └─────────────────┘    └──────────────────┘    └─────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              MeTTa Space (PyMeTTa)                          ││
│  │  - User atoms                                               ││
│  │  - Contribution atoms                                       ││
│  │  - Evidence atoms                                           ││
│  │  - Reasoning rules                                          ││
│  │  - Verification decisions                                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

1. **MeTTa Rules Engine (`core_rules.metta`)**
   - Define verification logic
   - Implement confidence scoring algorithms
   - Provide fraud detection patterns
   - Calculate token awards

2. **Python Service (`metta_reasoning.py`)**
   - Interface with PyMeTTa library
   - Convert database data to MeTTa atoms
   - Execute reasoning queries
   - Manage rule serialization

3. **Blockchain Bridge (`metta_blockchain_bridge.py`)**
   - Connect MeTTa decisions to blockchain
   - Execute on-chain verification
   - Mint tokens based on MeTTa awards
   - Record verification proofs

---

## Implementation Details

### 1. MeTTa Space Management

#### Atom-Based Architecture

The implementation uses an atom-based approach rather than object-based for better performance and readability:

```python
# Adding entities to MeTTa space
def _add_user_to_space(self, user_id: str, user_data: Dict[str, Any]) -> None:
    """Add user to MeTTa space as atoms"""
    # User atom
    atom = f'(User "{user_id}" "{username}")'
    self.space.parse_and_eval(atom)
    
    # Skills atoms
    for skill in user_data.get('skills', []):
        skill_atom = f'(HasSkill "{user_id}" "{skill_name}" {skill_level})'
        self.space.parse_and_eval(skill_atom)
```

#### Data Persistence

```python
def save_to_file(self, path: str = None) -> None:
    """Save MeTTa space to JSON for persistence"""
    serialized = {
        "atoms": self.added_atoms,
        "version": "1.0"
    }
    with open(save_path, 'w') as f:
        json.dump(serialized, f, indent=2)
```

### 2. Verification System

#### Core Verification Logic

The verification system uses multiple criteria in MeTTa:

```metta
;; Main verification rule
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))
```

#### Evidence Validation

```metta
;; Evidence validation with different types
(= (ValidEvidence $contrib-id)
   (let* (($evidence-count (CountEvidence $contrib-id))
          ($min-evidence 1))
     (>= $evidence-count $min-evidence)))

;; GitHub repository validation
(= (HasGithubEvidence $contrib-id)
   (Evidence $_ $contrib-id "github" $_))
```

#### Skill Matching

```metta
;; Skill matching logic
(= (SkillMatch $contrib-id $user-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($required-skills (RequiredSkillsForCategory $category)))
     (UserHasAnySkill $user-id $required-skills)))
```

### 3. Confidence Scoring

#### Multi-Factor Confidence Calculation

```python
def verify_contribution(self, user_id: str, contribution_id: str, 
                       evidence: Dict[str, Any] = None) -> Dict[str, Any]:
    """Verify contribution with confidence scoring"""
    # Execute MeTTa verification with confidence
    result = self.space.parse_and_eval(f'(VerifyWithConfidence "{contribution_id}")')
    
    return {
        'verified': bool(result.get_args()[1]),
        'confidence': float(result.get_args()[2]),
        'explanation': str(result.get_args()[3]),
        'tokens': self._calculate_token_award(contribution_id),
        'metta_proof': self._generate_proof(result)
    }
```

#### Confidence Factors

```metta
;; Calculate confidence based on multiple factors
(= (CalculateConfidence $contrib-id)
   (let* (($evidence-score (EvidenceScore $contrib-id))
          ($reputation-score (ReputationScore $contrib-id))
          ($consistency-score (ConsistencyScore $contrib-id)))
     (/ (+ $evidence-score $reputation-score $consistency-score) 3.0)))
```

### 4. Fraud Detection

#### Pattern Recognition

```metta
;; Main fraud detection rule
(= (DetectFraud $contrib-id)
   (let* (($user-id (GetContributorId $contrib-id)))
     (or (DuplicateSubmission $contrib-id $user-id)
         (SuspiciousActivityPattern $user-id)
         (EvidenceInconsistency $contrib-id))))
```

#### Duplicate Detection

```python
def detect_fraudulent_activity(self, user_id: str, contribution_id: str) -> Dict[str, Any]:
    """Detect potentially fraudulent activity"""
    is_fraud = self.space.parse_and_eval(f'(DetectFraud "{contribution_id}")')
    
    if is_fraud:
        return {
            'is_fraud': True,
            'reason': self._determine_fraud_reason(user_id, contribution_id),
            'confidence': self._calculate_fraud_confidence(user_id, contribution_id)
        }
    return {'is_fraud': False}
```

### 5. Token Award System

#### Dynamic Award Calculation

```metta
;; Dynamic token awards based on confidence and category
(= (CalculateTokenAward $contrib-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($confidence (CalculateConfidence $contrib-id))
          ($quality-bonus (* $confidence 50))
          ($total-amount (+ $base-amount $quality-bonus)))
     $total-amount))
```

#### Category-Based Base Awards

```metta
;; Base token amounts by contribution category
(= (BaseTokenAmount $category)
   (match $category
     ("coding" 75)
     ("education" 60)
     ("volunteer" 50)
     ("activism" 65)
     ("leadership" 70)
     ("entrepreneurship" 80)
     ("environmental" 70)
     ("community" 60)
     (_ 50)))
```

---

## Configuration & Setup

### 1. Environment Configuration

```python
# backend/config.py
class Config:
    # MeTTa configuration
    METTA_DB_PATH = os.environ.get('METTA_DB_PATH', 'metta_store.db')
    USE_METTA_REASONING = os.environ.get('USE_METTA_REASONING', 'False').lower() == 'true'
    METTA_CONFIDENCE_THRESHOLD = float(os.environ.get('METTA_CONFIDENCE_THRESHOLD', '0.7'))
```

### 2. Service Initialization

```python
# Initialize MeTTa service
from backend.services.metta_reasoning import MeTTaReasoning

metta_service = MeTTaReasoning(
    rules_dir='backend/rules',
    db_path='metta_store.db'
)
```

### 3. Dependencies

```bash
# Install PyMeTTa
pip install pymetta

# Alternative: Install from source
git clone https://github.com/singularitynet/metta-py
cd metta-py
pip install -e .
```

---

## API Integration

### 1. Contribution Verification Endpoint

```python
@contribution_bp.route('/<int:contrib_id>/verify', methods=['POST'])
@jwt_required()
async def verify_contribution(contrib_id):
    """Verify contribution using MeTTa reasoning"""
    # Initialize MeTTa service
    metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
    blockchain_service = BlockchainService()
    bridge = MeTTaBlockchainBridge(metta_service, blockchain_service)
    
    # Execute verification through bridge
    result = await bridge.verify_contribution_on_chain(
        user_id=contribution.user_id,
        contribution_id=contrib_id,
        evidence=contribution.evidence
    )
    
    return jsonify(result), 200
```

### 2. Explanation Endpoint

```python
@contribution_bp.route('/<int:contrib_id>/explain', methods=['GET'])
@jwt_required()
def explain_verification(contrib_id):
    """Get MeTTa explanation for verification"""
    metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
    
    explanation = metta_service.verify_contribution_with_explanation(str(contrib_id))
    
    return jsonify({
        "reasoning_factors": explanation,
        "detailed_explanation": explanation.get('explanation', '')
    }), 200
```

---

## Rule Development

### 1. Adding New Rules

Create rules in `backend/rules/core_rules.metta`:

```metta
;; Example: New skill validation rule
(= (ValidateSpecializedSkill $contrib-id $skill-type)
   (let* (($user-id (GetContributorId $contrib-id))
          ($user-skills (GetUserSkills $user-id))
          ($required-level 3))
     (HasSkillLevel $user-id $skill-type $required-level)))

;; Helper rule for skill levels
(= (HasSkillLevel $user-id $skill $level)
   (let* (($skill-atom (HasSkill $user-id $skill $user-level)))
     (>= $user-level $level)))
```

### 2. Testing Rules

```python
def test_new_rule():
    """Test new MeTTa rules"""
    metta = MeTTaReasoning()
    
    # Add test data
    metta.add_user("user123", "testuser", [
        {"name": "blockchain", "level": 4}
    ])
    metta.add_contribution("contrib456", "user123", "development")
    
    # Test rule
    result = metta.space.parse_and_eval('(ValidateSpecializedSkill "contrib456" "blockchain")')
    assert result == True
```

### 3. Rule Optimization

```metta
;; Optimized rule with caching
(= (CachedCalculateConfidence $contrib-id)
   (let* (($cache-key (JoinStrings "confidence-" $contrib-id))
          ($cached-result (GetFromCache $cache-key)))
     (if $cached-result
         $cached-result
         (let* (($result (CalculateConfidence $contrib-id)))
           (SetCache $cache-key $result)
           $result))))
```

---

## Performance Optimization

### 1. Caching Strategy

```python
def cached_query(self, query_key: str, query_func, *args, **kwargs):
    """Cache expensive MeTTa queries"""
    if query_key in self.cache:
        return self.cache[query_key]
    
    result = query_func(*args, **kwargs)
    self.cache[query_key] = result
    return result
```

### 2. Batch Processing

```python
def batch_verify_contributions(self, contribution_ids: List[str]) -> Dict[str, Any]:
    """Batch verify multiple contributions"""
    results = {}
    
    # Ensure all entities are in space first
    for contrib_id in contribution_ids:
        self._ensure_entities_in_space(contrib_id.split('-')[1], contrib_id)
    
    # Execute batch verification
    for contrib_id in contribution_ids:
        results[contrib_id] = self.verify_contribution_with_explanation(contrib_id)
    
    return results
```

### 3. Memory Management

```python
def clear_space(self) -> None:
    """Clear MeTTa space and reinitialize"""
    self.space = pymetta.MeTTa()
    self.added_atoms = []
    self._initialize_core_rules()
```

---

## Error Handling

### 1. Rule Execution Errors

```python
def safe_metta_query(self, query: str, fallback=None):
    """Execute MeTTa query with error handling"""
    try:
        result = self.space.parse_and_eval(query)
        return result if result else fallback
    except Exception as e:
        logger.error(f"MeTTa query failed: {query}, error: {e}")
        return fallback
```

### 2. Fallback Mechanisms

```python
def verify_contribution(self, user_id: str, contribution_id: str, evidence: Dict[str, Any] = None):
    """Verify with fallback to traditional methods"""
    try:
        # Try atom-based approach first
        result = self.space.parse_and_eval(f'(VerifyWithConfidence "{contribution_id}")')
        if result:
            return self._parse_verification_result(result)
    except Exception as e:
        logger.warning(f"Atom-based verification failed: {e}, using fallback")
    
    # Fallback to object-based approach
    return self._fallback_verification(user_id, contribution_id, evidence)
```

### 3. Validation

```python
def validate_metta_space(self) -> Dict[str, Any]:
    """Validate MeTTa space consistency"""
    issues = []
    
    # Check for orphaned atoms
    contributions = self.space.parse_and_eval('(Contribution $_ $_ $_)')
    for contrib in contributions:
        user_exists = self.space.parse_and_eval(f'(User "{contrib.user_id}" $_)')
        if not user_exists:
            issues.append(f"Orphaned contribution: {contrib.id}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }
```

---

## Monitoring & Debugging

### 1. Logging

```python
import logging

logger = logging.getLogger(__name__)

def verify_contribution(self, user_id: str, contribution_id: str, evidence: Dict[str, Any] = None):
    """Verify with comprehensive logging"""
    logger.info(f"Starting verification for contribution {contribution_id}")
    
    start_time = time.time()
    result = self._execute_verification(user_id, contribution_id, evidence)
    execution_time = time.time() - start_time
    
    logger.info(f"Verification completed in {execution_time:.3f}s: {result['verified']}")
    return result
```

### 2. Metrics Collection

```python
class MeTTaMetrics:
    def __init__(self):
        self.verification_count = 0
        self.fraud_detection_count = 0
        self.average_confidence = 0.0
        
    def record_verification(self, confidence: float, verified: bool):
        self.verification_count += 1
        self.average_confidence = (
            (self.average_confidence * (self.verification_count - 1) + confidence) 
            / self.verification_count
        )
```

### 3. Debug Mode

```python
def debug_verification(self, contribution_id: str) -> Dict[str, Any]:
    """Debug verification process step by step"""
    debug_info = {}
    
    # Check entity existence
    debug_info['user_exists'] = bool(self.space.parse_and_eval(
        f'(Contribution "{contribution_id}" $user-id $_)'
    ))
    
    # Check evidence
    debug_info['evidence_count'] = self.space.parse_and_eval(
        f'(CountEvidence "{contribution_id}")'
    )
    
    # Check confidence factors
    debug_info['confidence'] = self.space.parse_and_eval(
        f'(CalculateConfidence "{contribution_id}")'
    )
    
    return debug_info
```

---

## Testing

### 1. Unit Tests

```python
import unittest
from backend.services.metta_reasoning import MeTTaReasoning

class TestMeTTaReasoning(unittest.TestCase):
    def setUp(self):
        self.metta = MeTTaReasoning()
        
    def test_user_creation(self):
        """Test user atom creation"""
        self.metta.add_user("test_user", "testuser", ["python", "web_dev"])
        
        user_exists = self.metta.space.parse_and_eval('(User "test_user" "testuser")')
        self.assertTrue(user_exists)
        
    def test_contribution_verification(self):
        """Test contribution verification"""
        # Setup test data
        self.metta.add_user("user1", "contributor", ["coding"])
        self.metta.add_contribution("contrib1", "user1", "development")
        self.metta.add_evidence("contrib1", "github", "https://github.com/test/repo")
        
        # Test verification
        result = self.metta.verify_contribution_with_explanation("contrib1")
        self.assertIn('verified', result)
        self.assertIn('confidence', result)
```

### 2. Integration Tests

```python
def test_end_to_end_verification():
    """Test complete verification workflow"""
    from backend.services.metta_blockchain_bridge import MeTTaBlockchainBridge
    
    # Mock blockchain service
    blockchain_service = MockBlockchainService()
    metta_service = MeTTaReasoning()
    bridge = MeTTaBlockchainBridge(metta_service, blockchain_service)
    
    # Test verification
    result = await bridge.verify_contribution_on_chain(
        user_id=1,
        contribution_id=1,
        evidence={"url": "https://github.com/test/repo"}
    )
    
    assert result['status'] == 'verified'
    assert 'tokens_awarded' in result
```

### 3. Performance Tests

```python
def test_verification_performance():
    """Test MeTTa verification performance"""
    import time
    
    metta = MeTTaReasoning()
    
    # Setup test data
    for i in range(100):
        metta.add_user(f"user{i}", f"user{i}", ["skill1", "skill2"])
        metta.add_contribution(f"contrib{i}", f"user{i}", "development")
    
    # Measure verification time
    start_time = time.time()
    for i in range(100):
        metta.verify_contribution_with_explanation(f"contrib{i}")
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    assert avg_time < 0.1  # Should verify in under 100ms
```

---

## Deployment Considerations

### 1. Production Configuration

```python
# config.py
class ProductionConfig(Config):
    # MeTTa Production Settings
    USE_METTA_REASONING = True
    METTA_CONFIDENCE_THRESHOLD = 0.8  # Higher threshold for production
    METTA_DB_PATH = '/app/data/metta_store.db'
    
    # Performance settings
    METTA_CACHE_SIZE = 10000
    METTA_BATCH_SIZE = 50
```

### 2. Scaling

```python
# Distributed MeTTa processing
from celery import Celery

app = Celery('metta_worker')

@app.task
def verify_contribution_async(user_id: str, contribution_id: str, evidence: dict):
    """Async MeTTa verification task"""
    metta = MeTTaReasoning()
    return metta.verify_contribution(user_id, contribution_id, evidence)
```

### 3. Monitoring

```python
# Health check endpoint
@app.route('/health/metta')
def metta_health():
    """Check MeTTa service health"""
    try:
        metta = MeTTaReasoning()
        test_result = metta.space.parse_and_eval('(+ 1 1)')
        
        return jsonify({
            'status': 'healthy' if test_result == 2 else 'unhealthy',
            'version': metta.get_version(),
            'rules_loaded': len(metta.added_atoms)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
```

---

## Advanced Features

### 1. Rule Evolution

```python
def evolve_rules_based_on_feedback(self, feedback_data: List[Dict]):
    """Evolve MeTTa rules based on user feedback"""
    # Analyze feedback patterns
    patterns = self._analyze_feedback_patterns(feedback_data)
    
    # Generate new rules
    for pattern in patterns:
        if pattern['confidence'] > 0.9:
            new_rule = self._generate_rule_from_pattern(pattern)
            self.space.parse_and_eval(new_rule)
            self._track_atom(new_rule)
```

### 2. Multi-Agent Verification

```python
def multi_agent_verification(self, contribution_id: str) -> Dict[str, Any]:
    """Use multiple MeTTa agents for verification"""
    agents = ['strict_agent', 'lenient_agent', 'balanced_agent']
    results = {}
    
    for agent in agents:
        agent_service = MeTTaReasoning(rules_dir=f'rules/{agent}')
        results[agent] = agent_service.verify_contribution_with_explanation(contribution_id)
    
    # Aggregate results
    return self._aggregate_agent_results(results)
```

### 3. Continuous Learning

```python
def update_confidence_models(self, verified_data: List[Dict]):
    """Update confidence calculation based on historical data"""
    # Train confidence model
    model_updates = self._train_confidence_model(verified_data)
    
    # Update MeTTa rules
    for update in model_updates:
        updated_rule = self._generate_updated_rule(update)
        self.space.parse_and_eval(updated_rule)
```

---

## Troubleshooting

### Common Issues

**1. PyMeTTa Installation Issues**
```bash
# If pip install fails
git clone https://github.com/singularitynet/metta-py
cd metta-py
pip install -e .
```

**2. Rule Parsing Errors**
```python
# Add rule validation
def validate_rule_syntax(rule: str) -> bool:
    try:
        self.space.parse_and_eval(rule)
        return True
    except Exception as e:
        logger.error(f"Rule syntax error: {e}")
        return False
```

**3. Memory Usage**
```python
# Monitor memory usage
import psutil

def check_memory_usage(self):
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    if memory_mb > 1000:  # 1GB threshold
        self.clear_cache()
        logger.warning(f"High memory usage: {memory_mb:.1f}MB, cleared cache")
```

**4. Performance Issues**
```python
# Profile MeTTa queries
def profile_verification(self, contribution_id: str):
    import cProfile
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = self.verify_contribution_with_explanation(contribution_id)
    
    profiler.disable()
    profiler.dump_stats(f'metta_profile_{contribution_id}.prof')
    
    return result
```

---

## Conclusion

The MeTTa reasoning engine provides Nimo Platform with powerful autonomous decision-making capabilities. This implementation offers:

✅ **Completed Features:**
- Autonomous contribution verification
- Confidence-based scoring
- Fraud detection patterns
- Dynamic token awards
- Reputation calculation
- Explainable AI decisions

🔄 **Future Enhancements:**
- Machine learning integration
- Multi-agent verification
- Rule evolution mechanisms
- Advanced fraud patterns
- Cross-platform compatibility

The system is designed for scalability, maintainability, and extensibility, allowing for continuous improvement of the reasoning capabilities.

---

*Last Updated: January 26, 2025*  
*Author: John (Backend Developer)*  
*Status: Production ready with ongoing improvements*