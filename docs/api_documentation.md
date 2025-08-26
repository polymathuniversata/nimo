# Nimo Platform API Documentation

## Overview

The Nimo Platform API is a RESTful API built with Flask that enables social impact measurement, verification, and tokenization. The API integrates MeTTa reasoning for intelligent contribution verification and supports blockchain interactions for transparent impact tracking.

**Base URL:** `http://localhost:5000/api` (Development)  
**Authentication:** JWT Bearer Token  
**Content-Type:** `application/json`

---

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Auth Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "location": "New York, NY",
  "bio": "Software developer passionate about social impact",
  "skills": ["JavaScript", "Python", "Blockchain"]
}
```

**Response (201):**
```json
{
  "message": "User registered successfully"
}
```

**Errors:**
- `400`: Missing required field
- `409`: Email already registered

#### POST /auth/login
Authenticate and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "location": "New York, NY",
    "bio": "Software developer passionate about social impact",
    "skills": ["JavaScript", "Python", "Blockchain"],
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

**Errors:**
- `400`: Email and password required
- `401`: Invalid credentials

---

## User Management

### GET /user/me
Get current user profile information.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "location": "New York, NY",
  "bio": "Software developer passionate about social impact",
  "skills": ["JavaScript", "Python", "Blockchain"],
  "created_at": "2025-01-15T10:30:00Z"
}
```

### PUT /user/me
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "John Smith",
  "location": "San Francisco, CA",
  "bio": "Full-stack developer and blockchain enthusiast",
  "skills": ["React", "Node.js", "Solidity", "Web3"]
}
```

**Response (200):** Updated user object

### GET /user/{user_id}
Get specific user profile by ID.

**Headers:** `Authorization: Bearer <token>`

**Response (200):** User object
**Errors:** `404`: User not found

---

## Contribution Management

### GET /contribution/
Get user's contributions with optional filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `verified` (optional): `true` | `false` - Filter by verification status

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Open Source Library Development",
    "description": "Created a React component library for accessibility",
    "contribution_type": "development",
    "evidence": {
      "url": "https://github.com/user/accessibility-lib",
      "type": "repository"
    },
    "user_id": 1,
    "created_at": "2025-01-15T10:30:00Z",
    "verifications": []
  }
]
```

### POST /contribution/
Create a new contribution.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Educational Workshop Series",
  "description": "Conducted 5 workshops on Web3 development for underserved communities",
  "type": "education",
  "evidence": {
    "url": "https://example.com/workshop-materials",
    "type": "documentation",
    "additional_proof": ["participant_feedback.pdf", "attendance_records.xlsx"]
  }
}
```

**Response (201):**
```json
{
  "id": 2,
  "title": "Educational Workshop Series",
  "description": "Conducted 5 workshops on Web3 development for underserved communities",
  "contribution_type": "education",
  "evidence": {
    "url": "https://example.com/workshop-materials",
    "type": "documentation",
    "additional_proof": ["participant_feedback.pdf", "attendance_records.xlsx"]
  },
  "user_id": 1,
  "created_at": "2025-01-15T12:15:00Z",
  "verifications": []
}
```

**Errors:** `400`: Title is required

### GET /contribution/{contrib_id}
Get specific contribution details.

**Headers:** `Authorization: Bearer <token>`

**Response (200):** Contribution object  
**Errors:** `404`: Contribution not found

### GET /contribution/{contrib_id}/explain
Get MeTTa-powered explanation for contribution verification status.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "contribution": {
    "id": 1,
    "title": "Open Source Library Development",
    "type": "development",
    "impact_level": "moderate"
  },
  "verification_history": [
    {
      "verifier": "Jane Smith",
      "organization": "Nimo Platform",
      "date": "2025-01-15T14:30:00Z",
      "comments": "Verified through GitHub repository analysis and community feedback",
      "proof": "0x1234567890abcdef..."
    }
  ],
  "reasoning_factors": {
    "evidence_quality": "high",
    "skill_match": "verified",
    "impact_assessment": "moderate"
  },
  "detailed_explanation": "This contribution was verified based on multiple factors including the quality of the provided evidence, the match between the contributor's skills and the contribution type, and the assessed impact level."
}
```

**Errors:**
- `404`: Contribution not found
- `403`: Unauthorized to view explanation

### POST /contribution/{contrib_id}/verify
Verify a contribution (requires verification permissions).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "organization": "Impact Verification Council",
  "verifier_name": "Dr. Sarah Johnson",
  "comments": "Verified through code review and community impact assessment"
}
```

**Response (200) - With MeTTa Reasoning:**
```json
{
  "message": "Contribution verified successfully using MeTTa reasoning",
  "verification": {
    "id": 1,
    "organization": "Impact Verification Council",
    "verifier_name": "Dr. Sarah Johnson",
    "comments": "Automated verification: High confidence match based on evidence analysis and skill verification"
  },
  "metta_result": {
    "status": "verified",
    "confidence": 0.87,
    "reasoning": "GitHub repository shows substantial commits, positive community feedback, and matches declared skills",
    "verification_tx": "0x1234567890abcdef...",
    "token_tx": "0x9876543210fedcba..."
  }
}
```

**Response (200) - Fraud Detection:**
```json
{
  "message": "Contribution flagged for review",
  "reason": "Evidence mismatch detected",
  "confidence": 0.92
}
```

**Errors:**
- `403`: Unauthorized to verify contributions
- `404`: Contribution not found

---

## Token Management

### GET /token/balance
Get current user's token balance.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "balance": 150,
  "updated_at": "2025-01-15T16:45:00Z"
}
```

### GET /token/transactions
Get user's token transaction history.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "transactions": [
    {
      "id": 1,
      "amount": 50,
      "description": "Verification reward for Open Source Library Development",
      "type": "credit",
      "created_at": "2025-01-15T14:30:00Z"
    },
    {
      "id": 2,
      "amount": 25,
      "description": "Transfer to user #3",
      "type": "debit",
      "created_at": "2025-01-15T15:20:00Z"
    }
  ]
}
```

### POST /token/transfer
Transfer tokens to another user.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "recipient_id": 3,
  "amount": 25
}
```

**Response (200):**
```json
{
  "message": "Transfer successful",
  "new_balance": 125
}
```

**Errors:**
- `400`: Recipient ID and amount required / Amount must be positive / Insufficient balance
- `404`: Recipient not found

---

## Impact Bond Management

### GET /bond/
Get impact bonds with optional filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `cause` (optional): Filter by cause category
- `status` (optional): Filter by status (`active`, `completed`, `paused`) - Default: `active`
- `creator_id` (optional): Filter by creator ID

**Response (200):**
```json
[
  {
    "id": 1,
    "bond_id": "education-a1b2c3d4",
    "creator_id": 2,
    "title": "Community Coding Bootcamp",
    "description": "Intensive 12-week coding program for underserved youth",
    "cause": "education",
    "value": 5000,
    "status": "active",
    "image_url": "https://example.com/bootcamp-image.jpg",
    "created_at": "2025-01-10T09:00:00Z"
  }
]
```

### POST /bond/
Create a new impact bond.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Clean Water Initiative",
  "description": "Installing water filtration systems in rural communities",
  "cause": "environment",
  "value": 10000,
  "image_url": "https://example.com/water-project.jpg",
  "milestones": [
    {
      "milestone": "Complete feasibility study and site selection",
      "evidence": "Detailed report with community agreements"
    },
    {
      "milestone": "Install first 5 filtration systems",
      "evidence": "Installation photos and water quality test results"
    },
    {
      "milestone": "Complete all 20 installations and training",
      "evidence": "Final impact report with community testimonials"
    }
  ]
}
```

**Response (201):** Created bond object with generated `bond_id`

**Errors:** `400`: Missing required field (title, value)

### GET /bond/{bond_id}
Get specific impact bond with milestones and investments.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "bond_id": "environment-e5f6g7h8",
  "creator_id": 2,
  "title": "Clean Water Initiative",
  "description": "Installing water filtration systems in rural communities",
  "cause": "environment",
  "value": 10000,
  "status": "active",
  "image_url": "https://example.com/water-project.jpg",
  "created_at": "2025-01-10T09:00:00Z",
  "milestones": [
    {
      "id": 1,
      "milestone": "Complete feasibility study and site selection",
      "evidence": "Detailed report with community agreements",
      "is_verified": true,
      "verified_at": "2025-01-15T10:00:00Z",
      "verified_by": "Environmental Impact Council"
    }
  ],
  "investments": [
    {
      "id": 1,
      "investor_id": 4,
      "amount": 1500,
      "invested_at": "2025-01-12T14:30:00Z"
    }
  ]
}
```

**Errors:** `404`: Bond not found

### POST /bond/{bond_id}/invest
Invest tokens in an impact bond.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": 500
}
```

**Response (200):**
```json
{
  "message": "Investment successful",
  "investment": {
    "id": 2,
    "bond_id": 1,
    "investor_id": 1,
    "amount": 500,
    "invested_at": "2025-01-15T18:20:00Z"
  }
}
```

**Errors:**
- `400`: Amount required / Amount must be positive / Insufficient balance / Bond not active
- `404`: Bond not found

### POST /bond/{bond_id}/milestones/{milestone_id}/verify
Verify completion of a bond milestone (requires verification permissions).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "verifier": "Environmental Impact Council"
}
```

**Response (200):**
```json
{
  "message": "Milestone verified successfully",
  "milestone": {
    "id": 1,
    "milestone": "Complete feasibility study and site selection",
    "evidence": "Detailed report with community agreements",
    "is_verified": true,
    "verified_at": "2025-01-15T18:45:00Z",
    "verified_by": "Environmental Impact Council"
  },
  "all_completed": false
}
```

**Errors:**
- `404`: Milestone not found
- `400`: Milestone already verified

---

## Data Models

### User Object
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "location": "New York, NY",
  "bio": "Software developer passionate about social impact",
  "skills": ["JavaScript", "Python", "Blockchain"],
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Contribution Object
```json
{
  "id": 1,
  "title": "Open Source Library Development",
  "description": "Created a React component library for accessibility",
  "contribution_type": "development",
  "evidence": {
    "url": "https://github.com/user/accessibility-lib",
    "type": "repository",
    "additional_proof": []
  },
  "user_id": 1,
  "created_at": "2025-01-15T10:30:00Z",
  "verifications": [
    {
      "id": 1,
      "organization": "Nimo Platform",
      "verifier_name": "Jane Smith",
      "comments": "Verified through GitHub analysis",
      "verified_at": "2025-01-15T14:30:00Z"
    }
  ]
}
```

### Bond Object
```json
{
  "id": 1,
  "bond_id": "education-a1b2c3d4",
  "creator_id": 2,
  "title": "Community Coding Bootcamp",
  "description": "Intensive 12-week coding program for underserved youth",
  "cause": "education",
  "value": 5000,
  "status": "active",
  "image_url": "https://example.com/bootcamp-image.jpg",
  "created_at": "2025-01-10T09:00:00Z"
}
```

---

## Error Responses

All error responses follow this format:
```json
{
  "error": "Description of the error"
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid credentials)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `409`: Conflict (resource already exists)
- `500`: Internal Server Error

---

## MeTTa AI Integration

The API integrates MeTTa reasoning for intelligent verification and fraud detection. When `USE_METTA_REASONING` is enabled:

### Verification Features
- **Automated Evidence Analysis**: Analyzes GitHub repositories, documentation, and proof materials
- **Skill Matching**: Compares contributions against user's declared skills
- **Impact Assessment**: Evaluates potential social impact based on contribution type
- **Fraud Detection**: Identifies suspicious patterns or mismatched evidence

### Configuration
```python
USE_METTA_REASONING = True  # Enable MeTTa features
METTA_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for automated verification
METTA_DB_PATH = 'metta_store.db'  # MeTTa knowledge base location
```

---

## Blockchain Integration

The API supports blockchain interactions for transparent impact tracking:

### Supported Networks
- **Development**: Base Goerli Testnet
- **Production**: Base Mainnet

### Blockchain Features
- **Verification Proofs**: Contributions verified on-chain
- **Token Minting**: Automated token rewards for verified contributions
- **Impact Bonds**: Smart contract integration for milestone-based funding

### Configuration
```python
BLOCKCHAIN_NETWORK = 'base-goerli'
CONTRACT_ADDRESS = '0x...'  # Deployed contract address
PROVIDER_URL = 'https://goerli.base.org'
```

---

## Rate Limiting & Security

### Authentication Security
- JWT tokens expire after 1 hour
- Passwords hashed using Werkzeug security
- Secure cookies in production environment

### API Security
- CORS configuration for frontend integration
- Input validation on all endpoints
- SQL injection protection through SQLAlchemy ORM
- Environment-based configuration for sensitive data

---

## Development & Testing

### Local Development
```bash
# Start development server
flask run --debug

# Base URL
http://localhost:5000/api
```

### Testing Endpoints
Use tools like Postman, curl, or the frontend application to test endpoints.

Example curl request:
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Get contributions (with token)
curl -X GET http://localhost:5000/api/contribution/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- User authentication and management
- Contribution tracking and verification
- Token system with transfers
- Impact bond creation and investment
- MeTTa AI reasoning integration
- Basic blockchain connectivity

### Planned Features
- WebSocket real-time updates
- Advanced fraud detection algorithms  
- Multi-signature verification workflows
- DAO governance integration
- Enhanced impact metrics and reporting
- Mobile app API optimizations

---

*Last Updated: January 26, 2025*  
*Author: John (Backend Developer)*  
*For technical support, contact the development team.*