# Flask Backend for Nimo Platform

This directory contains the Flask backend for the Nimo platform, providing RESTful APIs for the React frontend with core MeTTa Identity and automated Reward system functionality.

## Structure

- `app.py`: Main application entry point
- `config.py`: Configuration settings
- `models/`: Database models
- `routes/`: API route definitions
- `services/`: Business logic implementation
- `utils/`: Utility functions

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
```

5. Initialize the database:

```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the development server:

```bash
flask run
```

## API Endpoints

### Core System Status
- `GET /api/health` - Health check endpoint
- `GET /api` - API information and version

### Authentication & MeTTa Identity System
- `POST /api/auth/register` - User registration
  - Body: `{"username": "string", "email": "string", "password": "string"}`
  - Response: `{"message": "User created", "user_id": "integer"}`

- `POST /api/auth/login` - User login
  - Body: `{"username": "string", "password": "string"}`
  - Response: `{"access_token": "jwt_token", "user": {...}}`

- `POST /api/identity/verify-did` - Verify DID (Decentralized Identity)
- `POST /api/identity/verify-ens` - Verify ENS name
- `GET /api/identity/supported-methods` - Get supported DID methods

### User Management
- `GET /api/user/<id>` - Get user profile
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"id": 1, "username": "string", "skills": [...], "token_balance": 100}`

### Contributions & MeTTa Verification
- `POST /api/contributions` - Create contribution
  - Headers: `Authorization: Bearer <token>`
  - Body: `{"title": "string", "description": "string", "evidence_url": "string"}`

- `POST /api/contributions/verify` - MeTTa verification of contributions

### Automated Reward System & Tokens
- `GET /api/tokens/balance/{user_id}` - Get token balance
- `GET /api/usdc/status` - USDC integration status
- `GET /api/usdc/balance/{address}` - Check USDC balance
- `POST /api/usdc/calculate-reward` - Calculate USDC rewards
- `POST /api/usdc/contribution-reward-preview` - Preview complete reward calculation

### Impact Bonds
- `POST /api/bonds` - Create bond
  - Headers: `Authorization: Bearer <token>`
  - Body: `{"title": "string", "description": "string", "target_amount": 10000, "cause": "string"}`

## Environment Variables

Create a `.env` file in the backend directory:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///nimo.db
JWT_SECRET_KEY=your-jwt-secret
```