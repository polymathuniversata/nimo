# MeTTa Integration Guide for Nimo Platform

## Overview

MeTTa (Meta Type Talk) is the AI reasoning engine powering the Nimo platform's autonomous verification system. It provides intelligent contribution verification, fraud detection, and token award calculations through symbolic reasoning.

## Quick Start

### Installation

Use the automated setup script:
```powershell
# From project root
.\setup_metta.ps1
```

Or install manually:
```powershell
# Create virtual environment
python -m venv hyperon-venv
.\hyperon-venv\Scripts\Activate.ps1

# Install from PyPI (recommended)
python -m pip install --upgrade pip==23.1.2
python -m pip install hyperon
```

### Verification

Test your installation:
```powershell
# Check Python module
python -c "import hyperon; print('MeTTa available!')"

# Run integration test
python backend\tests\test_metta_installation.py
```

## Architecture

### Core Components

1. **MeTTa Service** (`services/metta_service_hyperon.py`)
   - Direct interface with Hyperon API
   - Fallback to mock mode when unavailable

2. **Integration Layer** (`services/metta_integration.py`) 
   - Connects Flask API with MeTTa service
   - Provides verification and reputation methods

3. **Core Rules** (`rules/core_rules.metta`)
   - Identity verification rules
   - Contribution validation logic
   - Token award calculations

4. **API Routes** (`routes/contribution.py`)
   - HTTP endpoints using MeTTa verification

### Data Flow

```
API Request → MeTTa Integration → MeTTa Service → Hyperon Engine
     ↓              ↓                 ↓              ↓
Database   →   Rule Processing  →  Reasoning   →   Results
```

## Basic Usage

### Python Service

```python
from services.metta_service_hyperon import MeTTaService

# Initialize service
service = MeTTaService()

# Define entities
service.define_user("user-123", "Alice")
service.add_skill("user-123", "programming", 5)
service.add_contribution("contrib-456", "user-123", "coding", "DID System")
service.add_evidence("contrib-456", "github", "https://github.com/alice/did")

# Verify contribution
result = service.verify_contribution("contrib-456")
print(f"Verified: {result['valid']}, Confidence: {result['confidence']}")
```

### API Integration

```python
from services.metta_integration import MeTTaIntegration

integration = MeTTaIntegration()
result = integration.validate_contribution(
    contribution_id="contrib-123",
    contribution_data={
        "user_id": "user-456",
        "category": "education", 
        "title": "Programming Tutorial",
        "evidence": [{"type": "github", "url": "https://github.com/user/repo"}]
    }
)
```

## MeTTa Rules

Core verification logic in `backend/rules/core_rules.metta`:

```metta
;; Main verification rule
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))

;; Evidence validation
(= (ValidEvidence $contrib-id)
   (let* (($evidence-count (CountEvidence $contrib-id))
          ($min-evidence 1))
     (>= $evidence-count $min-evidence)))

;; Token calculation  
(= (CalculateTokenAward $contrib-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($confidence (CalculateConfidence $contrib-id))
          ($total-amount (+ $base-amount (* $confidence 50))))
     $total-amount))
```

## Configuration

### Environment Variables

```bash
# .env file
USE_METTA_REASONING=True
METTA_CONFIDENCE_THRESHOLD=0.7
METTA_DB_PATH=backend/metta_state.json
```

### Flask Config

```python
# config.py
class Config:
    USE_METTA_REASONING = os.environ.get('USE_METTA_REASONING', 'False').lower() == 'true'
    METTA_CONFIDENCE_THRESHOLD = float(os.environ.get('METTA_CONFIDENCE_THRESHOLD', '0.7'))
```

## Testing

### Unit Tests

```powershell
# Test MeTTa installation
python backend\tests\test_metta_installation.py

# Test service integration
python backend\tests\test_metta_service.py

# Test API integration
python backend\tests\test_metta_integration.py
```

### Manual Testing

```powershell
# Run MeTTa script directly
.\run_metta.ps1 backend\tests\simple_test.metta

# Test with REPL
metta-py
```

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure hyperon package is installed in the correct virtual environment
2. **Mock Mode**: If MeTTa unavailable, system automatically uses mock responses
3. **Rule Errors**: Check syntax in `core_rules.metta` file
4. **Performance**: Clear MeTTa space periodically for large datasets

### Debug Mode

```python
# Enable detailed logging
service = MeTTaService(debug=True)

# Check system status
print(f"MeTTa Available: {service.hyperon_available}")
print(f"Rules Loaded: {len(service.added_atoms)}")
```

## API Endpoints

### Verify Contribution

```http
POST /api/contributions/{id}/verify
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "organization": "Nimo Platform"
}
```

### Get Explanation

```http
GET /api/contributions/{id}/explain
Authorization: Bearer {jwt_token}
```

## Advanced Features

### Custom Rules

Add specialized validation rules:

```metta
;; Custom skill validation
(= (ValidateSpecializedSkill $contrib-id $skill-type)
   (let* (($user-id (GetContributorId $contrib-id))
          ($required-level 3))
     (HasSkillLevel $user-id $skill-type $required-level)))
```

### External API Integration

Connect to external services for verification:

```python
def validate_github_contribution(self, repo_url, username):
    # Fetch GitHub data via API
    # Validate commits and contributions
    # Return MeTTa-compatible result
    pass
```

### Performance Optimization

```python
# Implement caching for expensive queries
def cached_query(self, query_key, query_func, *args):
    if query_key in self.cache:
        return self.cache[query_key]
    result = query_func(*args)
    self.cache[query_key] = result
    return result
```

## Production Deployment

### Configuration

```python
# Production settings
class ProductionConfig(Config):
    USE_METTA_REASONING = True
    METTA_CONFIDENCE_THRESHOLD = 0.8
    METTA_CACHE_SIZE = 10000
```

### Monitoring

```python
# Health check endpoint
@app.route('/health/metta')
def metta_health():
    try:
        service = MeTTaService()
        test = service.space.parse_and_eval('(+ 1 1)')
        return jsonify({
            'status': 'healthy' if test == 2 else 'unhealthy',
            'rules_loaded': len(service.added_atoms)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500
```

## Resources

- [MeTTa Website](https://metta-lang.dev/)
- [Hyperon GitHub](https://github.com/trueagi-io/hyperon-experimental)
- [Project Rules](../backend/rules/core_rules.metta)

---

*Last Updated: August 27, 2025*