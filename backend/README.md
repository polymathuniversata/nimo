# Flask Backend for Nimo Platform

This directory contains the Flask backend for the Nimo platform, providing RESTful APIs for the Vue.js frontend.

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

### Authentication
- `POST /api/auth/register`
  - Body: `{"username": "string", "email": "string", "password": "string"}`
  - Response: `{"message": "User created", "user_id": "integer"}`

- `POST /api/auth/login`
  - Body: `{"username": "string", "password": "string"}`
  - Response: `{"access_token": "jwt_token", "user": {...}}`

### User Management
- `GET /api/user/<id>`
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"id": 1, "username": "string", "skills": [...], "token_balance": 100}`

### Contributions
- `GET /api/contributions`
  - Headers: `Authorization: Bearer <token>`
  - Response: `[{"id": 1, "title": "string", "verified": true, "tokens_awarded": 50}]`

- `POST /api/contributions`
  - Headers: `Authorization: Bearer <token>`
  - Body: `{"title": "string", "description": "string", "evidence_url": "string"}`
  - Response: `{"message": "Contribution added", "contribution_id": 1}`

### Tokens
- `GET /api/tokens`
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"balance": 320, "recent_awards": [...]}`

### Impact Bonds
- `GET /api/bonds`
  - Response: `[{"id": "string", "title": "string", "target_amount": 10000, "current_amount": 5000}]`

- `POST /api/bonds`
  - Headers: `Authorization: Bearer <token>`
  - Body: `{"title": "string", "description": "string", "target_amount": 10000, "cause": "string"}`
  - Response: `{"message": "Bond created", "bond_id": "string"}`

## Environment Variables

Create a `.env` file in the backend directory:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///nimo.db
JWT_SECRET_KEY=your-jwt-secret
```