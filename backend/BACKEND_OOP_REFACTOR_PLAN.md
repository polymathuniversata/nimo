# Backend OOP Refactor Plan

## Executive Summary

This document outlines a comprehensive Object-Oriented Programming (OOP) refactor plan for the Nimo backend codebase. The refactor aims to address architectural deficiencies identified in the security audit, improve code maintainability, and establish scalable development patterns.

## Current Architecture Assessment

### Identified Issues

1. **Mixed Concerns**: Business logic, data access, and infrastructure code are tightly coupled
2. **Procedural Patterns**: Many functions operate on global state rather than encapsulated objects
3. **Inconsistent Interfaces**: Services lack common interfaces and contracts
4. **Tight Coupling**: Direct dependencies between components without abstraction layers
5. **Configuration Scattering**: Configuration values hardcoded throughout the codebase

### Current Architecture Overview

```
Current Structure:
├── app.py (Flask app with mixed concerns)
├── config.py (Global configuration)
├── services/ (Mixed service implementations)
├── models/ (Data models with business logic)
├── routes/ (Route handlers with embedded logic)
└── utils/ (Utility functions)
```

## Target Architecture

### Proposed OOP Architecture

```
Target Structure:
├── app/
│   ├── core/
│   │   ├── application.py (Main application class)
│   │   ├── container.py (Dependency injection container)
│   │   └── config.py (Configuration management)
│   ├── domain/
│   │   ├── entities/ (Business entities)
│   │   ├── services/ (Domain services)
│   │   ├── repositories/ (Data access interfaces)
│   │   └── value_objects/ (Value objects)
│   ├── infrastructure/
│   │   ├── persistence/ (Repository implementations)
│   │   ├── external/ (External service integrations)
│   │   └── messaging/ (Event handling)
│   ├── presentation/
│   │   ├── controllers/ (Request handlers)
│   │   ├── middleware/ (Cross-cutting concerns)
│   │   └── dto/ (Data transfer objects)
│   └── shared/
│       ├── interfaces/ (Common interfaces)
│       ├── exceptions/ (Custom exceptions)
│       └── utilities/ (Shared utilities)
```

## Refactor Strategy

### Phase 1: Foundation (Week 1-2)

#### 1.1 Abstract Base Classes and Interfaces

**Objective**: Establish common interfaces and contracts

**Deliverables**:
- `BaseService` abstract class for all services
- `BaseRepository` interface for data access
- `BaseController` for request handling
- `BaseException` hierarchy for error handling

**Implementation**:

```python
# shared/interfaces/base_service.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..exceptions import ServiceException

class BaseService(ABC):
    """Abstract base class for all service classes."""

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._logger = self._setup_logger()

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        pass

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process business logic."""
        pass

    def _setup_logger(self):
        """Setup service-specific logger."""
        # Implementation
        pass
```

#### 1.2 Configuration Management

**Objective**: Centralized, type-safe configuration

**Deliverables**:
- `ConfigurationManager` class
- Environment-specific configurations
- Configuration validation

**Implementation**:

```python
# core/config.py
from typing import Dict, Any, Optional
from pydantic import BaseSettings, validator
import os

class DatabaseConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "nimo"
    user: str = ""
    password: str = ""

    @validator('password', pre=True)
    def validate_password(cls, v):
        if not v and os.getenv('DB_PASSWORD'):
            return os.getenv('DB_PASSWORD')
        return v

class AppConfig(BaseSettings):
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 5000
    secret_key: str = ""
    jwt_secret: str = ""

    database: DatabaseConfig = DatabaseConfig()

class ConfigurationManager:
    """Centralized configuration management."""

    def __init__(self, env_file: Optional[str] = None):
        self._config = AppConfig(_env_file=env_file)

    def get(self, key: str) -> Any:
        """Get configuration value by key."""
        return self._config.dict().get(key)

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self._config.database
```

#### 1.3 Dependency Injection Container

**Objective**: Loose coupling through dependency injection

**Deliverables**:
- `Container` class for service registration
- Service locator pattern
- Automatic dependency resolution

**Implementation**:

```python
# core/container.py
from typing import Dict, Type, Any, TypeVar
from ..domain.services.user_service import UserService
from ..infrastructure.persistence.user_repository import UserRepository

T = TypeVar('T')

class Container:
    """Dependency injection container."""

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type[T], implementation: Type[T],
                 singleton: bool = False):
        """Register a service implementation."""
        if singleton:
            self._singletons[interface] = implementation
        else:
            self._services[interface] = implementation

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        if interface in self._singletons:
            if not hasattr(self._singletons[interface], '_instance'):
                self._singletons[interface]._instance = (
                    self._singletons[interface]()
                )
            return self._singletons[interface]._instance

        if interface in self._services:
            return self._services[interface]()

        raise ValueError(f"No registration for {interface}")
```

### Phase 2: Domain Layer (Week 3-4)

#### 2.1 Entity Classes

**Objective**: Rich domain entities with business logic

**Deliverables**:
- `User` entity with validation and business rules
- `Contribution` entity with state management
- `Token` entity with balance operations

**Implementation**:

```python
# domain/entities/user.py
from typing import Optional, List
from datetime import datetime
from ..value_objects.email import Email
from ..value_objects.user_id import UserId

class User:
    """User domain entity."""

    def __init__(self,
                 user_id: UserId,
                 email: Email,
                 username: str,
                 created_at: Optional[datetime] = None):
        self._user_id = user_id
        self._email = email
        self._username = username
        self._created_at = created_at or datetime.utcnow()
        self._skills: List[str] = []
        self._is_active = True

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def email(self) -> Email:
        return self._email

    def add_skill(self, skill: str) -> None:
        """Add a skill to the user."""
        if skill not in self._skills:
            self._skills.append(skill)

    def remove_skill(self, skill: str) -> None:
        """Remove a skill from the user."""
        if skill in self._skills:
            self._skills.remove(skill)

    def can_contribute(self, skill_required: str) -> bool:
        """Check if user can contribute with required skill."""
        return skill_required in self._skills and self._is_active
```

#### 2.2 Repository Pattern

**Objective**: Abstract data access layer

**Deliverables**:
- Repository interfaces
- Repository implementations
- Unit of Work pattern

**Implementation**:

```python
# domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User
from ..value_objects.user_id import UserId

class UserRepository(ABC):
    """Abstract user repository interface."""

    @abstractmethod
    def save(self, user: User) -> None:
        """Save user entity."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """Find all users."""
        pass
```

#### 2.3 Domain Services

**Objective**: Complex business logic coordination

**Deliverables**:
- `ContributionService` for contribution processing
- `RewardCalculationService` for token rewards
- `VerificationService` for contribution verification

**Implementation**:

```python
# domain/services/contribution_service.py
from typing import Dict, Any
from ..entities.contribution import Contribution
from ..entities.user import User
from ..repositories.contribution_repository import ContributionRepository
from ..repositories.user_repository import UserRepository
from ...shared.interfaces.base_service import BaseService

class ContributionService(BaseService):
    """Domain service for contribution management."""

    def __init__(self,
                 contribution_repo: ContributionRepository,
                 user_repo: UserRepository,
                 config: Dict[str, Any]):
        super().__init__(config)
        self._contribution_repo = contribution_repo
        self._user_repo = user_repo

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate contribution data."""
        required_fields = ['user_id', 'type', 'content']
        return all(field in data for field in required_fields)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process contribution submission."""
        # Validate input
        if not self.validate(data):
            raise ValueError("Invalid contribution data")

        # Get user
        user = self._user_repo.find_by_id(data['user_id'])
        if not user:
            raise ValueError("User not found")

        # Create contribution
        contribution = Contribution(
            user_id=user.user_id,
            contribution_type=data['type'],
            content=data['content']
        )

        # Save contribution
        self._contribution_repo.save(contribution)

        return {
            'contribution_id': contribution.contribution_id,
            'status': 'submitted',
            'user_id': user.user_id
        }
```

### Phase 3: Infrastructure Layer (Week 5-6)

#### 3.1 Repository Implementations

**Objective**: Concrete data access implementations

**Deliverables**:
- SQLAlchemy repository implementations
- IPFS integration repository
- Blockchain repository implementations

**Implementation**:

```python
# infrastructure/persistence/user_repository_impl.py
from typing import List, Optional
from sqlalchemy.orm import Session
from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_id import UserId
from ..models.user_model import UserModel

class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, user: User) -> None:
        """Save user entity."""
        user_model = UserModel.from_entity(user)
        self._session.add(user_model)
        self._session.commit()

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        user_model = self._session.query(UserModel).filter(
            UserModel.id == user_id.value
        ).first()

        return user_model.to_entity() if user_model else None
```

#### 3.2 External Service Integrations

**Objective**: Encapsulated external service interactions

**Deliverables**:
- `IPFSService` with proper error handling
- `BlockchainService` with retry logic
- `CardanoService` with connection management

**Implementation**:

```python
# infrastructure/external/ipfs_service.py
import requests
from typing import Optional, Dict, Any
from ...shared.interfaces.base_service import BaseService
from ...shared.exceptions import ExternalServiceException

class IPFSService(BaseService):
    """IPFS integration service."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._base_url = config.get('ipfs_url', 'http://localhost:5001')
        self._timeout = config.get('timeout', 30)

    def store_content(self, content: str) -> str:
        """Store content on IPFS."""
        try:
            response = requests.post(
                f"{self._base_url}/api/v0/add",
                files={'file': content},
                timeout=self._timeout
            )
            response.raise_for_status()

            result = response.json()
            return result['Hash']

        except requests.RequestException as e:
            self._logger.error(f"IPFS storage failed: {e}")
            raise ExternalServiceException("Failed to store content on IPFS")

    def retrieve_content(self, cid: str) -> str:
        """Retrieve content from IPFS."""
        try:
            response = requests.post(
                f"{self._base_url}/api/v0/cat",
                params={'arg': cid},
                timeout=self._timeout
            )
            response.raise_for_status()

            return response.text

        except requests.RequestException as e:
            self._logger.error(f"IPFS retrieval failed: {e}")
            raise ExternalServiceException("Failed to retrieve content from IPFS")
```

### Phase 4: Presentation Layer (Week 7-8)

#### 4.1 Controller Classes

**Objective**: Clean request handling with proper separation

**Deliverables**:
- REST API controllers
- Request/response DTOs
- Input validation and sanitization

**Implementation**:

```python
# presentation/controllers/contribution_controller.py
from typing import Dict, Any
from flask import request, jsonify
from ...domain.services.contribution_service import ContributionService
from ...shared.interfaces.base_controller import BaseController
from ...shared.exceptions import ValidationException

class ContributionController(BaseController):
    """REST controller for contribution endpoints."""

    def __init__(self, contribution_service: ContributionService):
        self._contribution_service = contribution_service

    def create_contribution(self) -> Dict[str, Any]:
        """Handle contribution creation request."""
        try:
            data = request.get_json()

            # Validate request
            self._validate_contribution_data(data)

            # Process contribution
            result = self._contribution_service.process(data)

            return jsonify(result), 201

        except ValidationException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            self._logger.error(f"Contribution creation failed: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    def _validate_contribution_data(self, data: Dict[str, Any]) -> None:
        """Validate contribution request data."""
        if not data:
            raise ValidationException("Request body is required")

        required_fields = ['user_id', 'type', 'content']
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Field '{field}' is required")
```

#### 4.2 Middleware Classes

**Objective**: Cross-cutting concerns as reusable components

**Deliverables**:
- Authentication middleware
- Rate limiting middleware
- Logging middleware
- Error handling middleware

**Implementation**:

```python
# presentation/middleware/authentication_middleware.py
from typing import Callable, Any
from flask import request, g
from functools import wraps
from ...domain.services.auth_service import AuthService
from ...shared.exceptions import AuthenticationException

class AuthenticationMiddleware:
    """Authentication middleware."""

    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    def __call__(self, f: Callable) -> Callable:
        """Middleware decorator."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                raise AuthenticationException("Authorization header required")

            # Extract token
            token = self._extract_token(auth_header)

            # Validate token
            user = self._auth_service.validate_token(token)
            if not user:
                raise AuthenticationException("Invalid token")

            # Set user context
            g.user = user

            return f(*args, **kwargs)

        return decorated_function

    def _extract_token(self, auth_header: str) -> str:
        """Extract token from authorization header."""
        if not auth_header.startswith('Bearer '):
            raise AuthenticationException("Invalid authorization header format")

        return auth_header[7:]  # Remove 'Bearer ' prefix
```

### Phase 5: Testing and Validation (Week 9-10)

#### 5.1 Unit Testing Strategy

**Objective**: Comprehensive test coverage for OOP components

**Deliverables**:
- Unit tests for all domain entities
- Service layer testing with mocks
- Repository testing with test database
- Integration tests for service interactions

**Implementation**:

```python
# tests/domain/test_contribution_service.py
import pytest
from unittest.mock import Mock
from ...domain.services.contribution_service import ContributionService
from ...domain.entities.user import User
from ...domain.value_objects.user_id import UserId

class TestContributionService:
    """Unit tests for ContributionService."""

    @pytest.fixture
    def mock_contribution_repo(self):
        return Mock()

    @pytest.fixture
    def mock_user_repo(self):
        return Mock()

    @pytest.fixture
    def contribution_service(self, mock_contribution_repo, mock_user_repo):
        config = {'timeout': 30}
        return ContributionService(
            mock_contribution_repo,
            mock_user_repo,
            config
        )

    def test_validate_valid_data(self, contribution_service):
        """Test validation with valid data."""
        data = {
            'user_id': 'user123',
            'type': 'github',
            'content': 'https://github.com/user/repo'
        }

        assert contribution_service.validate(data) is True

    def test_validate_invalid_data(self, contribution_service):
        """Test validation with invalid data."""
        data = {'user_id': 'user123'}  # Missing required fields

        assert contribution_service.validate(data) is False
```

#### 5.2 Integration Testing

**Objective**: End-to-end testing of OOP architecture

**Deliverables**:
- API integration tests
- Database integration tests
- External service integration tests

## Implementation Timeline

### Week 1-2: Foundation
- [ ] Create abstract base classes
- [ ] Implement configuration management
- [ ] Setup dependency injection container
- [ ] Create custom exception hierarchy

### Week 3-4: Domain Layer
- [ ] Implement domain entities
- [ ] Create repository interfaces
- [ ] Implement domain services
- [ ] Add value objects

### Week 5-6: Infrastructure Layer
- [ ] Implement repository classes
- [ ] Create external service integrations
- [ ] Add proper error handling
- [ ] Implement caching layer

### Week 7-8: Presentation Layer
- [ ] Create controller classes
- [ ] Implement middleware
- [ ] Add request/response DTOs
- [ ] Setup routing

### Week 9-10: Testing and Validation
- [ ] Write comprehensive unit tests
- [ ] Create integration tests
- [ ] Performance testing
- [ ] Documentation

## Success Metrics

### Code Quality Metrics
- **Cyclomatic Complexity**: <10 for all service methods
- **Test Coverage**: >90% for domain and service layers
- **Maintainability Index**: >85 for all modules
- **Technical Debt**: <5% of total codebase

### Architecture Metrics
- **Coupling**: Low coupling between layers
- **Cohesion**: High cohesion within modules
- **Abstraction**: Proper use of interfaces and abstract classes
- **Modularity**: Clear separation of concerns

### Performance Metrics
- **Response Time**: <100ms for API endpoints
- **Memory Usage**: <10% increase from current baseline
- **Error Rate**: <0.1% for production operations

## Risk Mitigation

### Technical Risks
1. **Learning Curve**: Team training on OOP patterns
2. **Breaking Changes**: Gradual migration strategy
3. **Performance Impact**: Performance testing throughout refactor

### Operational Risks
1. **Downtime**: Zero-downtime deployment strategy
2. **Rollback Plan**: Complete rollback procedures
3. **Monitoring**: Enhanced monitoring during transition

## Migration Strategy

### Incremental Migration
1. **Start Small**: Begin with isolated services
2. **Parallel Implementation**: Run old and new implementations in parallel
3. **Gradual Rollout**: Feature-by-feature migration
4. **Complete Transition**: Full migration with comprehensive testing

### Compatibility Layer
1. **Adapter Pattern**: Create adapters for legacy code
2. **Facade Pattern**: Provide unified interfaces
3. **Bridge Pattern**: Connect old and new architectures

## Conclusion

This OOP refactor plan provides a comprehensive roadmap for transforming the Nimo backend from a procedural, tightly-coupled architecture to a maintainable, scalable, object-oriented system. The phased approach ensures minimal disruption while delivering significant improvements in code quality, maintainability, and security.

The refactor addresses all critical issues identified in the security audit while establishing patterns for sustainable long-term development. Success will be measured by improved code metrics, enhanced testability, and reduced technical debt.

---

**Document Version**: 1.0
**Last Updated**: Current Session
**Estimated Duration**: 10 weeks
**Risk Level**: Medium
**Business Impact**: High (Improved maintainability and security)