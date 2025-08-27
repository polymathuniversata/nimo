# Development Guide
**Updated: August 26, 2025 - React.js Migration Complete**

This guide covers the development workflow, testing, and deployment processes for the Nimo platform.

## 🚀 **MAJOR UPDATE: Frontend Stack Completely Modernized**
- **Vue.js/Quasar** → **React.js/Vite/Tailwind CSS**
- **Modern Development Experience** with lightning-fast builds
- **All backend MeTTa integration preserved**

## Development Workflow

### Setting Up the Development Environment

1. **System Requirements**
   - Python 3.8+ with pip
   - Node.js 18+ with npm (updated for React 19.1.1)
   - Git for version control
   - MeTTa runtime (optional, for core logic testing)
   - Modern browser for React DevTools

2. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Nimo
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   
   # Environment setup
   cp .env.example .env
   # Edit .env with your configuration
   
   # Database setup
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **Frontend Setup** ✅ **NEW REACT.JS STACK**
   ```bash
   cd frontend/client
   npm install
   ```
   
   **New Frontend Stack:**
   - React 19.1.1 + Vite 7.1.2
   - Tailwind CSS 3.3.4 + PostCSS
   - React Router DOM 7.8.2
   - ESLint + React DevTools

### Daily Development Workflow

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   flask run
   # Backend runs on http://127.0.0.1:5000
   ```

2. **Start React Frontend** (Terminal 2) 🎆 **NEW**
   ```bash
   cd frontend/client
   npm run dev
   # React app runs on http://localhost:5173 with hot reload
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test MeTTa Logic** (Terminal 3)
   ```bash
   # From project root
   metta main.metta
   ```

### Code Organization

- **Backend (Flask)**
  - `models/`: Database models using SQLAlchemy
  - `routes/`: API endpoint definitions
  - `services/`: Business logic and MeTTa integration
  - `utils/`: Helper functions and utilities

- **Frontend (Vue/Quasar)**
  - `components/`: Reusable UI components
  - `pages/`: Application pages/views
  - `services/`: API service layer
  - `stores/`: Pinia state management

## Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

Test structure:
- `test_models.py`: Database model tests
- `test_api.py`: API endpoint tests
- `test_services.py`: Business logic tests

### Frontend Tests

```bash
cd frontend
npm run test:unit
```

### MeTTa Tests

```bash
# Run MeTTa test file
metta tests/nimo_test.metta
```

### Integration Testing

Run both backend and frontend, then test API endpoints:
```bash
# Test API health
curl http://localhost:5000/api/health

# Test authentication
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass"}'
```

## Database Management

### Migrations

```bash
cd backend
source venv/bin/activate

# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback (if needed)
flask db downgrade
```

### Development Data

```bash
# Seed database with test data
python seed_data.py
```

## Code Quality

### Python (Backend)

```bash
# Code formatting
black backend/

# Import sorting
isort backend/

# Linting
flake8 backend/
```

### JavaScript (Frontend)

```bash
cd frontend

# Linting
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

## Environment Configuration

### Backend Environment Variables
```bash
# backend/.env
FLASK_ENV=development
SECRET_KEY=your-development-secret-key
DATABASE_URL=sqlite:///nimo.db
JWT_SECRET_KEY=your-jwt-secret-key
METTA_RUNTIME_PATH=/path/to/metta
```

### Frontend Environment Variables
```bash
# frontend/.env.development
VUE_APP_API_URL=http://localhost:5000/api
VUE_APP_ENVIRONMENT=development
```

## Debugging

### Backend Debugging
- Use Flask's debug mode: `FLASK_ENV=development`
- Add breakpoints with `import pdb; pdb.set_trace()`
- Check logs in terminal running Flask

### Frontend Debugging
- Use browser dev tools
- Vue dev tools extension
- Console.log statements
- Network tab for API calls

### MeTTa Debugging
- Add print statements in MeTTa code
- Use step-by-step evaluation
- Check atom/relation definitions

## Performance Monitoring

### API Performance
```bash
# Load testing
pip install locust
locust -f load_tests.py --host=http://localhost:5000
```

### Frontend Performance
- Use Chrome DevTools Performance tab
- Lighthouse audits for web vitals
- Bundle size analysis: `npm run build --report`

## Deployment Preparation

### Production Build

```bash
# Backend
cd backend
pip install gunicorn
gunicorn app:app

# Frontend
cd frontend
npm run build
# Files ready in dist/spa/
```

### Docker Containers

```dockerfile
# Dockerfile.backend
FROM python:3.9-slim
COPY backend/ /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

```dockerfile
# Dockerfile.frontend  
FROM nginx:alpine
COPY frontend/dist/spa/ /usr/share/nginx/html/
```

### Environment-Specific Configs

- `config/development.py`: Development settings
- `config/production.py`: Production settings  
- `config/testing.py`: Test environment settings

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check Flask-CORS configuration
   - Verify frontend API_URL environment variable

2. **Database Connection Issues**
   - Check DATABASE_URL in .env
   - Ensure database exists and is accessible

3. **JWT Token Issues**
   - Verify JWT_SECRET_KEY consistency
   - Check token expiration settings

4. **MeTTa Runtime Issues**
   - Ensure MeTTa runtime is properly installed
   - Check METTA_RUNTIME_PATH environment variable

### Getting Help

- Check existing documentation in `docs/`
- Review error logs in backend console
- Use browser dev tools for frontend issues
- Check network requests in browser