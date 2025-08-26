# Nimo Backend Testing Suite

This directory contains comprehensive tests for the Nimo backend implementation, including MeTTa reasoning, blockchain integration, and API endpoints.

## Test Structure

```
tests/
├── README.md                    # This file
├── test_runner.py              # Main test runner with reporting
├── test_metta_reasoning.py     # Tests for MeTTa AI integration
├── test_blockchain_service.py  # Tests for Base network integration
└── test_api_routes.py          # Tests for Flask API endpoints
```

## Running Tests

### Quick Start

Run all tests:
```bash
cd backend/tests
python test_runner.py
```

Run with verbose output:
```bash
python test_runner.py --verbose
```

### Specific Test Suites

Run specific test suites:
```bash
python test_runner.py --suite metta      # MeTTa reasoning tests
python test_runner.py --suite blockchain # Blockchain service tests
python test_runner.py --suite routes     # API route tests
python test_runner.py --suite security   # Security feature tests
```

### Integration Tests

Run integration tests (tests that span multiple components):
```bash
python test_runner.py --integration
```

### Coverage Analysis

Run tests with coverage analysis (requires `coverage.py`):
```bash
pip install coverage
python test_runner.py --coverage
```

### Generate Reports

Generate JSON test report:
```bash
python test_runner.py --report test_results.json
```

## Test Categories

### 1. MeTTa Reasoning Tests (`test_metta_reasoning.py`)

Tests for the MeTTa AI integration:
- ✅ Contribution verification with different evidence types
- ✅ Fraud detection functionality
- ✅ Reputation calculation
- ✅ Batch verification processing
- ✅ Reasoning trace export
- ✅ Performance analytics

**Key Test Cases:**
- GitHub evidence verification (should have high confidence)
- Website evidence verification (medium confidence)
- Document evidence with signatures
- Fraud pattern detection
- User reputation scoring with temporal decay

### 2. Blockchain Service Tests (`test_blockchain_service.py`)

Tests for Base network integration:
- ✅ Network configuration (Base Sepolia/Mainnet)
- ✅ Gas price optimization for Base L2
- ✅ Transaction building and sending
- ✅ Smart contract interactions
- ✅ Batch transaction processing
- ✅ Event listener setup
- ✅ Transaction status monitoring

**Key Test Cases:**
- Identity NFT creation on Base
- Contribution recording on-chain
- Token minting for verified contributions
- Batch verification for gas efficiency
- Transaction cost estimation
- Network connection status

### 3. MeTTa-Blockchain Bridge Tests

Tests for the integration between MeTTa reasoning and blockchain:
- ✅ Verification workflow (MeTTa → Blockchain)
- ✅ Fraud detection integration
- ✅ Token award calculation
- ✅ Batch processing coordination
- ✅ Analytics and reporting

### 4. API Route Tests (`test_api_routes.py`)

Tests for Flask API endpoints:
- ✅ Contribution CRUD operations
- ✅ Pagination and filtering
- ✅ Input validation and sanitization
- ✅ Authentication and authorization
- ✅ Rate limiting
- ✅ Batch operations
- ✅ Analytics endpoints

**Key Test Cases:**
- Contribution creation with validation
- Paginated contribution listing
- Batch verification API
- Analytics calculation
- Security input sanitization
- Permission checking

### 5. Security Tests

Comprehensive security testing:
- ✅ Input validation (XSS, SQL injection prevention)
- ✅ Authentication bypass attempts
- ✅ Rate limiting effectiveness
- ✅ Permission boundary testing
- ✅ Data sanitization

## Mock Strategy

The tests use extensive mocking to isolate components:

### MeTTa Mocking
- Mock PyMeTTa space operations
- Simulated reasoning results
- Controlled test scenarios

### Blockchain Mocking
- Mock Web3 provider connections
- Simulated transaction results
- Gas estimation mocking
- Event filter simulation

### Database Mocking
- SQLAlchemy model mocking
- Query result simulation
- Transaction rollback testing

### Flask Mocking
- Request/response mocking
- JWT token simulation
- Session management mocking

## Test Data

### Sample Users
```python
{
    "id": "test_user",
    "skills": ["python", "web_development", "community_building"],
    "reputation": 75,
    "blockchain_address": "0x1234...abcd"
}
```

### Sample Contributions
```python
{
    "id": "test_contrib",
    "title": "Python Web Application",
    "type": "coding",
    "impact": "significant",
    "evidence": {
        "url": "https://github.com/user/project",
        "type": "github_repo"
    }
}
```

### Sample Evidence Types
- **GitHub Repository**: High confidence verification
- **Website with Proof**: Medium confidence
- **Signed Documents**: High confidence with signature validation
- **Video Evidence**: Medium-high confidence
- **Image Evidence**: Medium confidence

## Performance Benchmarks

The tests include performance benchmarks for:
- MeTTa reasoning speed (target: <2s per verification)
- Batch processing efficiency (target: 50+ contributions/batch)
- API response times (target: <500ms for most endpoints)
- Blockchain transaction confirmation (Base network: ~2s)

## Continuous Integration

### GitHub Actions Integration

Add to `.github/workflows/backend-tests.yml`:
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install coverage
      - name: Run tests
        run: |
          cd backend/tests
          python test_runner.py --coverage --report results.json
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: backend/tests/results.json
```

## Debugging Test Failures

### Common Issues

1. **MeTTa Import Errors**
   - Ensure PyMeTTa is installed: `pip install pymetta`
   - Check PYTHONPATH includes backend directory

2. **Blockchain Connection Failures**
   - Verify Base network RPC URLs are accessible
   - Check private key format in environment variables

3. **Database Model Errors**
   - Ensure SQLAlchemy models are properly defined
   - Check foreign key relationships

### Debug Mode

Run tests with Python debugger:
```bash
python -m pdb test_runner.py --verbose
```

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Adding New Tests

### 1. Create Test Class
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        pass
    
    def test_feature_functionality(self):
        # Test the feature
        self.assertTrue(condition)
    
    def tearDown(self):
        # Cleanup
        pass
```

### 2. Add to Test Runner
Add your test class to `test_runner.py`:
```python
from test_new_feature import TestNewFeature

test_suites = [
    # ... existing suites
    ('New Feature', TestNewFeature)
]
```

### 3. Mock Dependencies
Use appropriate mocking for external dependencies:
```python
@patch('module.dependency')
def test_with_mocked_dependency(self, mock_dep):
    mock_dep.return_value = expected_result
    # Run test
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (network, filesystem, database)
3. **Assertions**: Use specific assertions with clear error messages
4. **Cleanup**: Always clean up resources in tearDown()
5. **Coverage**: Aim for >90% code coverage
6. **Performance**: Include performance assertions for critical paths
7. **Security**: Test security boundaries and input validation

## Troubleshooting

### Windows-Specific Issues
- Use `python` instead of `python3`
- Ensure path separators are handled correctly
- Check file permissions for test artifacts

### macOS/Linux Issues
- Use `python3` explicitly
- Check virtual environment activation
- Verify file permissions

### Docker Testing
Run tests in isolated Docker container:
```bash
docker run -v $(pwd):/app -w /app/backend/tests python:3.8 python test_runner.py
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Add integration tests for multi-component features
4. Update this README with new test descriptions
5. Maintain >90% test coverage

For questions about testing, refer to the main project documentation or open an issue.