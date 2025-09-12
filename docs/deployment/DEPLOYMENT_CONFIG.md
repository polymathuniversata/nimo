# Nimo Platform - Deployment Configuration Guide
**Production Deployment Configuration - August 28, 2025**

## 🚀 **Production Deployment Configuration**

Based on the comprehensive audit results, this guide provides the complete configuration needed for production deployment of the Nimo platform.

### **Environment Variables for Production**

#### **Core Application Settings**
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_production_secret_key_here_minimum_32_chars
JWT_SECRET_KEY=your_jwt_secret_key_here_minimum_32_chars
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/nimo_production
SQLALCHEMY_DATABASE_URI=postgresql://user:password@host:port/nimo_production

# Server Configuration
SERVER_NAME=api.nimo.app
TRUSTED_HOSTS=api.nimo.app,nimo.app,www.nimo.app
SSL_REDIRECT=true
PREFERRED_URL_SCHEME=https
```

#### **Cardano Blockchain Configuration**
```bash
# Network Selection
CARDANO_NETWORK=mainnet

# Blockfrost API Keys (Get from https://blockfrost.io)
BLOCKFROST_PROJECT_ID_MAINNET=mainnet_your_api_key_here
BLOCKFROST_PROJECT_ID_PREVIEW=preview_your_api_key_here
BLOCKFROST_PROJECT_ID_PREPROD=preprod_your_api_key_here

# Service Wallet Configuration
CARDANO_SERVICE_PRIVATE_KEY=your_cardano_service_private_key
CARDANO_SERVICE_KEY_FILE=/secure/path/service_key.skey

# NIMO Token Configuration (Deploy contracts first)
NIMO_TOKEN_POLICY_ID_MAINNET=your_deployed_nimo_policy_id
NIMO_TOKEN_POLICY_ID_PREVIEW=your_preview_policy_id
NIMO_TOKEN_POLICY_ID_PREPROD=your_preprod_policy_id
NIMO_TOKEN_ASSET_NAME=NIMO
```

#### **MeTTa AI Configuration**
```bash
# MeTTa Service Configuration
USE_METTA_REASONING=true
METTA_MODE=enhanced
METTA_CONFIDENCE_THRESHOLD=0.75
METTA_FRAUD_DETECTION_THRESHOLD=0.85
METTA_BATCH_SIZE=100
METTA_CACHE_TTL=3600
METTA_ENABLE_PERFORMANCE_MONITORING=true
METTA_QUERY_TIMEOUT=30
METTA_ENABLE_CACHE=true

# MeTTa File Paths
METTA_DATABASE_PATH=/app/data/metta_state/metta_database.json
METTA_CORE_RULES_PATH=/app/rules/core_rules.metta
```

#### **Feature Flags**
```bash
# Core Features (All enabled for production)
FEATURE_WALLET_AUTH=true
FEATURE_METTA_INTEGRATION=true
FEATURE_AUTO_REWARDS=true
FEATURE_ADA_REWARDS=true
FEATURE_NIMO_REWARDS=true
FEATURE_IDENTITY_VERIFICATION=true
FEATURE_AUTONOMOUS_SYSTEM=true
FEATURE_FRAUD_DETECTION=true
FEATURE_BATCH_PROCESSING=true
FEATURE_PERFORMANCE_MONITORING=true
FEATURE_CACHE_OPTIMIZATION=true
```

#### **Reward System Configuration**
```bash
# Token Rates and Limits
ADA_TO_NIMO_RATE=100
NIMO_DECIMAL_PLACES=6
NIMO_MIN_MINT_AMOUNT=1
NIMO_MAX_MINT_AMOUNT=1000000

# Reward Limits
MIN_ADA_REWARD=1000000
MAX_ADA_REWARD=10000000
MIN_NIMO_REWARD=10
MAX_NIMO_REWARD=1000
CONFIDENCE_REWARD_MULTIPLIER=1.5
```

#### **Autonomous System Configuration**
```bash
# Autonomous Operations
AUTONOMOUS_SYSTEM_ENABLED=true
AUTONOMOUS_CYCLE_INTERVAL=300
AUTONOMOUS_BATCH_SIZE=50
AUTONOMOUS_MAX_CONCURRENT=10
AUTONOMOUS_RETRY_ATTEMPTS=3
AUTONOMOUS_RETRY_DELAY=5
```

#### **Redis Configuration**
```bash
# Redis Connection
REDIS_URL=redis://your-redis-host:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_SSL=true
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_CONNECTION_POOL_SIZE=50
```

#### **Performance Optimization**
```bash
# Database Performance
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600

# Query Optimization
QUERY_OPTIMIZER_ENABLED=true
QUERY_CACHE_TTL=300
BATCH_PROCESSING_ENABLED=true
```

#### **Security Configuration**
```bash
# Security Headers
SECURITY_HEADERS_ENABLED=true
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';

# CORS Configuration
CORS_ORIGINS=https://nimo.app,https://www.nimo.app,https://app.nimo.io

# Rate Limiting
DEFAULT_RATE_LIMIT=1000
AUTH_RATE_LIMIT=20
RATE_LIMIT_WINDOW=300
```

#### **Monitoring and Logging**
```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=/app/logs
ENABLE_FILE_LOGGING=true
ENABLE_JSON_LOGGING=true
MAX_LOG_SIZE=50485760
LOG_BACKUP_COUNT=10

# Monitoring Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
PERFORMANCE_MONITORING_ENABLED=true
```

#### **Email Configuration** (Optional)
```bash
# Email Service
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@nimo.app
MAIL_PASSWORD=your_email_password
```

---

## 🐳 **Docker Configuration**

### **Production Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p logs data/metta_state rules

# Set proper permissions
RUN chmod +x setup_backend.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

### **Docker Compose for Production**
```yaml
version: '3.8'

services:
  nimo-backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://nimo_user:nimo_password@db:5432/nimo_production
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./rules:/app/rules
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=nimo_production
      - POSTGRES_USER=nimo_user
      - POSTGRES_PASSWORD=nimo_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass your_redis_password
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - nimo-backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

## ⚙️ **Kubernetes Configuration**

### **Production Kubernetes Manifests**

#### **Namespace**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: nimo-production
```

#### **ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nimo-config
  namespace: nimo-production
data:
  FLASK_ENV: "production"
  CARDANO_NETWORK: "mainnet"
  METTA_MODE: "enhanced"
  USE_METTA_REASONING: "true"
  AUTONOMOUS_SYSTEM_ENABLED: "true"
  FEATURE_METTA_INTEGRATION: "true"
  FEATURE_ADA_REWARDS: "true"
  FEATURE_NIMO_REWARDS: "true"
```

#### **Secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: nimo-secrets
  namespace: nimo-production
type: Opaque
data:
  SECRET_KEY: base64_encoded_secret_key
  JWT_SECRET_KEY: base64_encoded_jwt_key
  DATABASE_URL: base64_encoded_database_url
  CARDANO_SERVICE_PRIVATE_KEY: base64_encoded_private_key
  BLOCKFROST_PROJECT_ID_MAINNET: base64_encoded_api_key
  REDIS_PASSWORD: base64_encoded_redis_password
  SENTRY_DSN: base64_encoded_sentry_dsn
```

#### **Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nimo-backend
  namespace: nimo-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nimo-backend
  template:
    metadata:
      labels:
        app: nimo-backend
    spec:
      containers:
      - name: nimo-backend
        image: nimo/backend:latest
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: nimo-config
        - secretRef:
            name: nimo-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
```

---

## 🚀 **Deployment Steps**

### **Phase 1: Infrastructure Setup**
1. **Set up PostgreSQL database**
   ```bash
   # Create production database
   psql -c "CREATE DATABASE nimo_production;"
   psql -c "CREATE USER nimo_user WITH PASSWORD 'secure_password';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE nimo_production TO nimo_user;"
   ```

2. **Set up Redis cache**
   ```bash
   # Install and configure Redis
   redis-server --daemonize yes --requirepass your_redis_password
   ```

3. **Configure SSL certificates**
   ```bash
   # Obtain SSL certificates (Let's Encrypt recommended)
   certbot --nginx -d api.nimo.app -d nimo.app
   ```

### **Phase 2: Cardano Smart Contract Deployment**
1. **Deploy NIMO token policy**
   ```bash
   cd contracts/cardano
   python deploy_nimo_token.py --network mainnet --initial-mint 1000000
   ```

2. **Deploy contribution validator**
   ```bash
   python deploy_contribution_validator.py --network mainnet
   ```

3. **Update environment variables**
   ```bash
   # Set deployed contract addresses
   export NIMO_TOKEN_POLICY_ID_MAINNET="your_deployed_policy_id"
   ```

### **Phase 3: Application Deployment**
1. **Build and deploy backend**
   ```bash
   # Build Docker image
   docker build -t nimo/backend:latest .
   
   # Deploy to production
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Run database migrations**
   ```bash
   # Initialize database schema
   flask db upgrade
   ```

3. **Start services**
   ```bash
   # Start all services
   systemctl start nimo-backend
   systemctl enable nimo-backend
   ```

### **Phase 4: Verification and Testing**
1. **Health checks**
   ```bash
   # Verify service health
   curl https://api.nimo.app/api/health
   curl https://api.nimo.app/api/autonomous/health
   ```

2. **End-to-end testing**
   ```bash
   # Run production tests
   python -m pytest tests/integration/ --env=production
   ```

3. **Performance testing**
   ```bash
   # Load testing
   artillery run load-test-config.yml
   ```

---

## 📊 **Monitoring Configuration**

### **Prometheus Configuration**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'nimo-backend'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

### **Grafana Dashboard Configuration**
- **API Performance**: Response times, error rates, throughput
- **MeTTa AI Metrics**: Verification accuracy, fraud detection rates
- **Cardano Integration**: Transaction success rates, costs
- **Autonomous System**: Processing rates, optimization results
- **System Health**: CPU, memory, database performance

---

## 🔒 **Security Checklist**

### **Pre-Deployment Security**
- [ ] **SSL/TLS certificates** configured and valid
- [ ] **Database encryption** at rest and in transit
- [ ] **Redis authentication** and SSL enabled
- [ ] **API rate limiting** configured
- [ ] **CORS policy** restrictive to production domains
- [ ] **Input validation** on all endpoints
- [ ] **JWT token expiration** set appropriately
- [ ] **Secrets management** using environment variables
- [ ] **Private key security** with hardware wallets
- [ ] **Network security** with firewalls and VPCs

### **Post-Deployment Security**
- [ ] **Security audit** by third-party
- [ ] **Penetration testing** completed
- [ ] **Vulnerability scanning** automated
- [ ] **Log monitoring** for security events
- [ ] **Backup strategy** implemented
- [ ] **Incident response plan** documented
- [ ] **Access controls** reviewed
- [ ] **Regular security updates** scheduled

---

## 🎯 **Production Readiness Checklist**

### **Infrastructure**
- [ ] **Load balancer** configured with SSL termination
- [ ] **Database** with read replicas and backups
- [ ] **Redis cluster** for high availability
- [ ] **CDN** for static assets
- [ ] **Monitoring** with alerts and dashboards

### **Application**
- [ ] **Environment variables** all configured
- [ ] **Database migrations** completed
- [ ] **MeTTa rules** loaded and tested
- [ ] **Cardano contracts** deployed and funded
- [ ] **Service wallet** funded with ADA
- [ ] **Cache warming** completed
- [ ] **Performance testing** passed

### **Operations**
- [ ] **CI/CD pipeline** configured
- [ ] **Backup procedures** tested
- [ ] **Rollback strategy** documented
- [ ] **Monitoring alerts** configured
- [ ] **Log aggregation** setup
- [ ] **Performance baselines** established
- [ ] **Capacity planning** completed

---

**Last Updated**: August 28, 2025  
**Platform**: Nimo - Decentralized Youth Identity & Proof of Contribution Network  
**Deployment Status**: Production Ready (90% Complete)