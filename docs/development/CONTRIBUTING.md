# Contributing to Nimo

Thank you for considering contributing to Nimo! This document outlines the process for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct (be respectful, inclusive, and collaborative).

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists in the GitHub issues.
2. If not, create a new issue with a descriptive title and detailed description.
3. Include steps to reproduce, expected behavior, and actual behavior.
4. Include screenshots or logs if applicable.

### Suggesting Features

1. Check if the feature has already been suggested in the GitHub issues.
2. If not, create a new issue with a descriptive title.
3. Provide a detailed description of the feature and its benefits.

### Pull Requests

1. Fork the repository.
2. Create a new branch from `main`: `git checkout -b feature/your-feature-name`.
3. **MANDATORY**: Write tests FIRST using Test-Driven Development (TDD)
4. Make your changes - **NEVER write production code without tests**
5. Run ALL tests to ensure they pass (backend, frontend, contracts)
6. Commit your changes with a descriptive commit message.
7. Push your branch to your fork.
8. Create a pull request to the `main` branch of the original repository.

## ⚠️ **TESTING REQUIREMENTS - NON-NEGOTIABLE**

### Test-Driven Development (TDD) - REQUIRED
- **RED**: Write failing tests first
- **GREEN**: Write minimal code to pass tests  
- **REFACTOR**: Improve code while keeping tests passing
- **REPEAT**: Never write code without tests

### Coverage Requirements
- **Backend**: Minimum 85% coverage (pytest)
- **Frontend**: Minimum 80% coverage (Vitest)
- **Smart Contracts**: Minimum 95% coverage (Foundry)
- **Integration Tests**: Required for all major features

### Testing Commands
- **Backend**: `cd backend && python -m pytest tests/ -v --cov=.`
- **Frontend**: `cd frontend && npm run test:unit`
- **Smart Contracts**: `cd contracts && forge test`
- **E2E Tests**: `cd frontend && npm run test:e2e`

**🚨 NO CODE WILL BE MERGED WITHOUT COMPREHENSIVE TESTS**

## Development Setup

See the README.md file for detailed instructions on setting up the development environment.

## Testing

**CRITICAL**: All contributions MUST include comprehensive tests. We practice strict Test-Driven Development (TDD).

### Testing Frameworks
- **Backend**: pytest with coverage reporting
- **Frontend**: Vitest with Vue Test Utils
- **Smart Contracts**: Foundry (Forge)
- **E2E**: Playwright for critical user flows

### Test Structure
```
backend/tests/          # Backend unit/integration tests
frontend/src/test/      # Frontend component tests  
contracts/test/         # Smart contract tests
tests/e2e/             # End-to-end tests
```

### Running Tests
```bash
# Backend tests
cd backend && python -m pytest tests/ -v --cov=.

# Frontend tests  
cd frontend && npm run test:unit

# Smart contract tests
cd contracts && forge test

# E2E tests
cd frontend && npm run test:e2e
```

### Test Requirements
- ✅ Unit tests for all functions/methods
- ✅ Integration tests for API endpoints
- ✅ Component tests for UI elements
- ✅ E2E tests for critical user flows
- ✅ Minimum 85% code coverage
- ✅ All tests must pass before merge

## MeTTa Style Guide

When contributing MeTTa code, please follow these guidelines:

- Use descriptive atom names
- Comment complex logic
- Follow the pattern established in the backend/main.metta file

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally

## License

By contributing to Nimo, you agree that your contributions will be licensed under the project's MIT License.