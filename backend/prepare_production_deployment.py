"""
Production Deployment Preparation for Nimo Backend

This script prepares the Nimo backend for production deployment
by setting up Docker, environment configuration, and deployment scripts.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_dockerfile():
    """Create optimized Dockerfile for production"""
    dockerfile_content = '''# Multi-stage build for optimized production image
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash nimo

# Set work directory
WORKDIR /app

# Install Python dependencies in a virtual environment
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy virtual environment from dependencies stage
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs instance metta_state && \\
    chown -R nimo:nimo /app

# Switch to non-root user
USER nimo

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health/live || exit 1

# Expose port
EXPOSE 5000

# Start application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "app:create_app()"]
'''

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)

    print("✅ Dockerfile created")

def create_docker_compose():
    """Create Docker Compose configuration for production"""
    docker_compose_content = '''version: '3.8'

services:
  nimo-backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - METTA_DATABASE_PATH=/app/metta_state
      - LOG_DIR=/app/logs
      - SENTRY_DSN=${SENTRY_DSN}
    volumes:
      - ./logs:/app/logs
      - ./metta_state:/app/metta_state
      - ./instance:/app/instance
    depends_on:
      - redis
      - postgres
    networks:
      - nimo-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - nimo-network
    restart: unless-stopped
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - nimo-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - nimo-backend
    networks:
      - nimo-network
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:

networks:
  nimo-network:
    driver: bridge
'''

    # Create docker-compose directory if it doesn't exist
    os.makedirs('docker-compose', exist_ok=True)

    with open('docker-compose/docker-compose.prod.yml', 'w') as f:
        f.write(docker_compose_content)

    print("✅ Docker Compose configuration created")

def create_nginx_config():
    """Create Nginx configuration for production"""
    nginx_config = '''events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    upstream nimo_backend {
        server nimo-backend:5000;
    }

    server {
        listen 80;
        server_name localhost;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Handle API requests
        location /api/ {
            proxy_pass http://nimo_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check endpoint (no auth required)
        location /api/health/ {
            proxy_pass http://nimo_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            access_log off;
        }

        # Static files (if any)
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Default location
        location / {
            proxy_pass http://nimo_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # SSL configuration (uncomment when SSL certificates are available)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_session_timeout 1d;
    #     ssl_session_cache shared:MozTLS:10m;
    #     ssl_session_tickets off;
    #
    #     # Modern configuration
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    #     ssl_prefer_server_ciphers off;
    #
    #     # HSTS
    #     add_header Strict-Transport-Security "max-age=63072000" always;
    #
    #     # Rest of the configuration same as HTTP server block
    #     location /api/ {
    #         proxy_pass http://nimo_backend;
    #         # ... proxy settings ...
    #     }
    #
    #     location / {
    #         proxy_pass http://nimo_backend;
    #         # ... proxy settings ...
    #     }
    # }
}
'''

    # Create nginx directory
    os.makedirs('nginx', exist_ok=True)

    with open('nginx/nginx.conf', 'w') as f:
        f.write(nginx_config)

    print("✅ Nginx configuration created")

def create_environment_template():
    """Create environment variables template"""
    env_template = '''# Nimo Backend Production Environment Variables

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Database Configuration
DATABASE_URL=postgresql://nimo_user:nimo_password@postgres:5432/nimo_db
POSTGRES_DB=nimo_db
POSTGRES_USER=nimo_user
POSTGRES_PASSWORD=your-secure-postgres-password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# MeTTa Configuration
METTA_DATABASE_PATH=/app/metta_state

# Logging Configuration
LOG_DIR=/app/logs
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
ENABLE_JSON_LOGGING=false
MAX_LOG_SIZE=10485760
LOG_BACKUP_COUNT=5

# Security Configuration
SENTRY_DSN=your-sentry-dsn-here
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cardano Configuration
CARDANO_NETWORK=mainnet
BLOCKFROST_API_KEY=your-blockfrost-api-key
CARDANO_WALLET_SEED=your-wallet-seed-24-words

# External API Keys (if needed)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@nimo-platform.com

# Monitoring and Metrics
ENABLE_PROMETHEUS_METRICS=false
PROMETHEUS_PORT=9090
ENABLE_HEALTH_CHECKS=true

# CORS Configuration
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# File Upload Configuration
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=/app/uploads
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,jpeg,png,gif
'''

    with open('.env.template', 'w') as f:
        f.write(env_template)

    print("✅ Environment template created")

def create_deployment_scripts():
    """Create deployment scripts"""
    # Create deploy script
    deploy_script = '''#!/bin/bash

# Nimo Backend Production Deployment Script

set -e

echo "Starting Nimo Backend Deployment"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please copy .env.template to .env and configure your environment variables."
    exit 1
fi

print_status "Building Docker images..."
docker-compose -f docker-compose/docker-compose.prod.yml build

print_status "Starting services..."
docker-compose -f docker-compose/docker-compose.prod.yml up -d

print_status "Waiting for services to be healthy..."
sleep 30

# Check if services are healthy
if docker-compose -f docker-compose/docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "Deployment successful!"
    print_status "Services are running:"
    docker-compose -f docker-compose/docker-compose.prod.yml ps

    print_status "Health check endpoints:"
    echo "  - Basic Health: http://localhost/api/health/"
    echo "  - Detailed Health: http://localhost/api/health/detailed"
    echo "  - System Metrics: http://localhost/api/health/metrics"
    echo "  - Performance: http://localhost/api/health/performance"
else
    print_error "Deployment failed. Check logs:"
    docker-compose -f docker-compose/docker-compose.prod.yml logs
    exit 1
fi

print_status "Nimo Backend is now running in production mode!"
'''

    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)

    # Make deploy script executable with secure permissions
    # Security: Use restrictive permissions (owner read/write/execute only)
    os.chmod('deploy.sh', 0o700)

    # Create development setup script
    dev_setup_script = '''#!/bin/bash

# Nimo Backend Development Setup Script

set -e

echo "Setting up Nimo Backend for Development"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python &> /dev/null; then
    print_error "Python is not installed. Please install Python 3.12 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.12"

if [ "$(printf '%s\\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or later is required. Current version: $PYTHON_VERSION"
    exit 1
fi

print_status "Creating virtual environment..."
python -m venv venv

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Upgrading pip..."
pip install --upgrade pip

print_status "Installing dependencies..."
pip install -r requirements.txt

print_status "Creating necessary directories..."
mkdir -p logs instance metta_state

print_status "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.template .env
    print_warning "Please edit .env file with your configuration before running the application."
fi

print_status "Running database migrations..."
flask db upgrade

print_status "Development setup complete!"
print_status "To start the development server:"
echo "  source venv/bin/activate"
echo "  flask run"
echo ""
print_status "Or use the run script:"
echo "  ./run_dev.sh"
'''

    with open('setup_dev.sh', 'w') as f:
        f.write(dev_setup_script)

    # Security: Use restrictive permissions for setup script
    os.chmod('setup_dev.sh', 0o700)

    # Create development run script
    run_dev_script = '''#!/bin/bash

# Nimo Backend Development Run Script

set -e

echo "Starting Nimo Backend in Development Mode"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup_dev.sh
fi

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=app.py

# Start the application (SECURITY: Bind to localhost only by default)
echo "Starting Flask development server..."
echo "WARNING: This development script binds to localhost only for security."
echo "For production, use a proper WSGI server and reverse proxy."
flask run --host=127.0.0.1 --port=5000
'''

    with open('run_dev.sh', 'w') as f:
        f.write(run_dev_script)

    # Security: Use restrictive permissions for run script
    os.chmod('run_dev.sh', 0o700)

    print("Deployment scripts created")

def create_monitoring_config():
    """Create monitoring configuration files"""
    # Prometheus configuration
    prometheus_config = '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'nimo-backend'
    static_configs:
      - targets: ['nimo-backend:5000']
    metrics_path: '/api/health/metrics'
    scrape_interval: 5s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
'''

    # Create monitoring directory
    os.makedirs('monitoring', exist_ok=True)

    with open('monitoring/prometheus.yml', 'w') as f:
        f.write(prometheus_config)

    # Grafana dashboard configuration
    grafana_dashboard = {
        "dashboard": {
            "title": "Nimo Backend Dashboard",
            "tags": ["nimo", "backend"],
            "timezone": "browser",
            "panels": [
                {
                    "title": "System CPU Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "cpu_percent",
                            "legendFormat": "CPU %"
                        }
                    ]
                },
                {
                    "title": "System Memory Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "memory_percent",
                            "legendFormat": "Memory %"
                        }
                    ]
                },
                {
                    "title": "API Response Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "flask_http_request_duration_seconds",
                            "legendFormat": "Response Time"
                        }
                    ]
                }
            ]
        }
    }

    with open('monitoring/grafana-dashboard.json', 'w') as f:
        json.dump(grafana_dashboard, f, indent=2)

    print("✅ Monitoring configuration created")

def create_dockerignore():
    """Create .dockerignore file"""
    dockerignore_content = '''# Version control
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
venv
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Documentation
*.md
docs/
README.md

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Logs
logs/
*.log

# Testing
tests/
test_*.py
*_test.py
conftest.py

# Development
debug_*.py
validate_*.py
*.development
'''

    with open('.dockerignore', 'w') as f:
        f.write(dockerignore_content)

    print("✅ .dockerignore created")

def create_production_readme():
    """Create production deployment README"""
    readme_content = '''# Nimo Backend - Production Deployment

This document provides instructions for deploying the Nimo Backend to production.

## Prerequisites

- Docker and Docker Compose
- At least 4GB RAM
- At least 20GB disk space
- Domain name (optional, but recommended)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nimo-backend
   ```

2. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your production values
   ```

3. **Deploy with Docker Compose**
   ```bash
   ./deploy.sh
   ```

4. **Verify deployment**
   ```bash
   curl http://localhost/api/health/
   ```

## Environment Configuration

Copy `.env.template` to `.env` and configure the following variables:

### Required Variables
- `SECRET_KEY`: Flask secret key (generate a secure random key)
- `JWT_SECRET_KEY`: JWT secret key (generate a secure random key)
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL

### Optional Variables
- `SENTRY_DSN`: Sentry DSN for error tracking
- `CARDANO_NETWORK`: Cardano network (mainnet/testnet)
- `BLOCKFROST_API_KEY`: Blockfrost API key for Cardano

## Services

The production deployment includes:

- **Nimo Backend**: Main Flask application
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Nginx**: Reverse proxy and load balancer

## Health Checks

The application provides comprehensive health check endpoints:

- `GET /api/health/` - Basic health check
- `GET /api/health/detailed` - Detailed health with metrics
- `GET /api/health/services/{name}` - Service-specific health
- `GET /api/health/metrics` - System metrics
- `GET /api/health/performance` - Performance statistics
- `GET /api/health/autonomous` - Autonomous operations health
- `GET /api/health/ready` - Kubernetes readiness probe
- `GET /api/health/live` - Kubernetes liveness probe

## Monitoring

### Prometheus Metrics
The application exposes metrics at `/api/health/metrics` for Prometheus scraping.

### Logging
- Application logs are stored in the `logs/` directory
- Nginx logs are available in `logs/nginx/`
- All logs are configured with structured JSON format

## Scaling

### Horizontal Scaling
To scale the application horizontally:

1. Update the `docker-compose.prod.yml` file
2. Increase the number of backend workers
3. Add a load balancer in front of Nginx

### Vertical Scaling
For vertical scaling, increase the resources allocated to containers in the Docker Compose file.

## Backup and Recovery

### Database Backup
```bash
# Backup PostgreSQL database
docker exec nimo_postgres pg_dump -U nimo_user nimo_db > backup.sql

# Restore from backup
docker exec -i nimo_postgres psql -U nimo_user nimo_db < backup.sql
```

### Redis Backup
Redis data is automatically persisted to the `redis_data` Docker volume.

## Security Considerations

1. **Change default passwords** in the `.env` file
2. **Use HTTPS** in production (configure SSL certificates)
3. **Restrict database access** to application containers only
4. **Regular security updates** for all Docker images
5. **Monitor logs** for suspicious activity

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 5000
   lsof -i :5000
   # Kill the process or change the port in docker-compose.prod.yml
   ```

2. **Database connection failed**
   - Check PostgreSQL container logs
   - Verify database credentials in `.env`
   - Ensure PostgreSQL is healthy

3. **Redis connection failed**
   - Check Redis container logs
   - Verify Redis URL in `.env`

### Logs

View application logs:
```bash
docker-compose -f docker-compose/docker-compose.prod.yml logs nimo-backend
```

View all logs:
```bash
docker-compose -f docker-compose/docker-compose.prod.yml logs
```

## Development

For development setup, see `setup_dev.sh` and `run_dev.sh` scripts.

## Support

For support and issues, please check:
- Application logs in `logs/` directory
- Docker container logs
- Health check endpoints for system status
'''

    with open('PRODUCTION_README.md', 'w') as f:
        f.write(readme_content)

    print("✅ Production README created")

def main():
    """Main deployment preparation function"""
    print("Nimo Backend Production Deployment Preparation")
    print("=" * 60)

    # Create all deployment files
    create_dockerfile()
    create_docker_compose()
    create_nginx_config()
    create_environment_template()
    create_deployment_scripts()
    create_monitoring_config()
    create_dockerignore()
    create_production_readme()

    print("\n" + "=" * 60)
    print("Production deployment preparation complete!")
    print("\nFiles created:")
    print("  • Dockerfile - Multi-stage production Docker image")
    print("  • docker-compose/docker-compose.prod.yml - Production services")
    print("  • nginx/nginx.conf - Nginx reverse proxy configuration")
    print("  • .env.template - Environment variables template")
    print("  • deploy.sh - Production deployment script")
    print("  • setup_dev.sh - Development setup script")
    print("  • run_dev.sh - Development run script")
    print("  • monitoring/ - Prometheus and Grafana configurations")
    print("  • .dockerignore - Docker ignore file")
    print("  • PRODUCTION_README.md - Deployment documentation")

    print("\nNext Steps:")
    print("1. Review and configure .env.template")
    print("2. Run ./deploy.sh for production deployment")
    print("3. Or run ./setup_dev.sh for development setup")
    print("4. Check PRODUCTION_README.md for detailed instructions")

    print("\nHealth Check Endpoints:")
    print("  • Basic: http://localhost/api/health/")
    print("  • Detailed: http://localhost/api/health/detailed")
    print("  • Metrics: http://localhost/api/health/metrics")
    print("  • Performance: http://localhost/api/health/performance")

if __name__ == "__main__":
    main()