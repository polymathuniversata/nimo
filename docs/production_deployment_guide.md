# Nimo Platform - Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Nimo platform to production environments. The platform consists of three main components:
- **Smart Contracts** (deployed to Base Mainnet)
- **Backend API** (Flask application)
- **Frontend Application** (React.js SPA)

## Prerequisites

### System Requirements
- **Node.js**: v18.0.0 or higher
- **Python**: 3.9 or higher
- **PostgreSQL**: 14.0 or higher
- **Redis**: 6.0 or higher (for caching and rate limiting)
- **Nginx**: For reverse proxy and SSL termination
- **SSL Certificate**: Valid SSL certificate for HTTPS

### Required Accounts and API Keys
- **Base Mainnet RPC**: Alchemy, Infura, or similar
- **Basescan API Key**: For contract verification
- **Domain and SSL**: Configured DNS and SSL certificates
- **Email Service**: For notifications (SendGrid, AWS SES, etc.)

## Security Checklist

Before deployment, ensure all security measures are in place:

### ✅ Environment Security
- [ ] All sensitive data stored in environment variables
- [ ] No hardcoded private keys or API keys in code
- [ ] Environment files excluded from version control
- [ ] Separate environment configurations for staging/production

### ✅ Infrastructure Security
- [ ] SSL/TLS certificates properly configured
- [ ] Firewall rules configured (only necessary ports open)
- [ ] Database access restricted to application servers
- [ ] Regular security updates applied to all systems

### ✅ Application Security
- [ ] Input validation implemented on all endpoints
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Security headers implemented
- [ ] Authentication and authorization working
- [ ] Logging and monitoring configured

## Step 1: Infrastructure Setup

### 1.1 Server Requirements

**Recommended Minimum Specifications:**
- **CPU**: 2 cores (4 recommended)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 50GB SSD
- **Bandwidth**: 100 Mbps

### 1.2 Database Setup

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE nimo_production;
CREATE USER nimo_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nimo_production TO nimo_user;
\q

# Install Redis
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 1.3 Nginx Configuration

Create `/etc/nginx/sites-available/nimo`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://mainnet.base.org https://sepolia.base.org wss://mainnet.base.org wss://sepolia.base.org;";
    
    # Frontend
    location / {
        root /var/www/nimo/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }
}

# Rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}
```

## Step 2: Smart Contract Deployment

### 2.1 Prepare Environment

```bash
cd contracts/
cp .env.example .env
```

Configure `.env` file:
```env
# Production Configuration
PRIVATE_KEY=YOUR_DEPLOYMENT_PRIVATE_KEY_HERE
BASESCAN_API_KEY=YOUR_BASESCAN_API_KEY_HERE
BASE_RPC_URL=https://mainnet.base.org
```

### 2.2 Deploy to Base Mainnet

```bash
# Compile contracts
forge build

# Deploy to Base Mainnet
forge script script/Deploy.s.sol:DeployScript \
  --rpc-url https://mainnet.base.org \
  --private-key $PRIVATE_KEY \
  --verify \
  --etherscan-api-key $BASESCAN_API_KEY \
  --broadcast

# Save deployment addresses
echo "NIMO_IDENTITY_CONTRACT=$(cat deployments/mainnet/NimoIdentity.json | jq -r '.address')" >> ../backend/.env.production
echo "NIMO_TOKEN_CONTRACT=$(cat deployments/mainnet/NimoToken.json | jq -r '.address')" >> ../backend/.env.production
```

### 2.3 Verify Contracts

```bash
# Verify NimoIdentity contract
forge verify-contract \
  --chain-id 8453 \
  --constructor-args-path constructor-args.txt \
  --etherscan-api-key $BASESCAN_API_KEY \
  CONTRACT_ADDRESS \
  src/NimoIdentity.sol:NimoIdentity

# Verify NimoToken contract
forge verify-contract \
  --chain-id 8453 \
  --constructor-args-path token-constructor-args.txt \
  --etherscan-api-key $BASESCAN_API_KEY \
  TOKEN_CONTRACT_ADDRESS \
  src/NimoToken.sol:NimoToken
```

## Step 3: Backend Deployment

### 3.1 Environment Configuration

Create `/var/www/nimo/backend/.env.production`:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=YOUR_SUPER_SECRET_KEY_HERE
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://nimo_user:your_secure_password@localhost/nimo_production

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Blockchain Configuration
WEB3_PROVIDER_URL=https://mainnet.base.org
BASE_RPC_URL=https://mainnet.base.org
NIMO_IDENTITY_CONTRACT=CONTRACT_ADDRESS_FROM_DEPLOYMENT
NIMO_TOKEN_CONTRACT=TOKEN_CONTRACT_ADDRESS_FROM_DEPLOYMENT
BLOCKCHAIN_SERVICE_PRIVATE_KEY=YOUR_BLOCKCHAIN_SERVICE_PRIVATE_KEY_HERE

# API Configuration
CORS_ORIGINS=https://your-domain.com
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY_HERE
JWT_ACCESS_TOKEN_EXPIRES=86400

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=1000 per hour

# MeTTa Configuration
METTA_RUNTIME_PATH=/usr/local/bin/metta
METTA_KNOWLEDGE_BASE=/var/www/nimo/metta_knowledge/

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/nimo/backend.log

# Email Configuration (if using)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=YOUR_EMAIL_USERNAME
MAIL_PASSWORD=YOUR_EMAIL_PASSWORD
```

### 3.2 Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/nimo
sudo chown -R $USER:$USER /var/www/nimo

# Clone and setup backend
cd /var/www/nimo
git clone YOUR_REPOSITORY_URL .
cd backend

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Create log directory
sudo mkdir -p /var/log/nimo
sudo chown $USER:$USER /var/log/nimo
```

### 3.3 Systemd Service

Create `/etc/systemd/system/nimo-backend.service`:

```ini
[Unit]
Description=Nimo Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/nimo/backend
Environment=PATH=/var/www/nimo/backend/venv/bin
EnvironmentFile=/var/www/nimo/backend/.env.production
ExecStart=/var/www/nimo/backend/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nimo-backend
sudo systemctl start nimo-backend
```

## Step 4: Frontend Deployment

### 4.1 Environment Configuration

Create `/var/www/nimo/frontend/.env.production`:

```env
VITE_API_BASE_URL=https://your-domain.com/api
VITE_WEB3_PROVIDER_URL=https://mainnet.base.org
VITE_CHAIN_ID=8453
VITE_NIMO_IDENTITY_CONTRACT=CONTRACT_ADDRESS_FROM_DEPLOYMENT
VITE_NIMO_TOKEN_CONTRACT=TOKEN_CONTRACT_ADDRESS_FROM_DEPLOYMENT
VITE_ENVIRONMENT=production
```

### 4.2 Build and Deploy

```bash
cd /var/www/nimo/frontend

# Install dependencies
npm ci --production

# Build for production
npm run build

# Move build files
sudo mkdir -p /var/www/nimo/frontend/dist
sudo cp -r dist/* /var/www/nimo/frontend/dist/
sudo chown -R www-data:www-data /var/www/nimo/frontend/dist
```

## Step 5: Monitoring and Logging

### 5.1 Log Configuration

Create log rotation config `/etc/logrotate.d/nimo`:

```
/var/log/nimo/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nimo-backend
    endscript
}
```

### 5.2 Health Check Endpoints

The backend provides health check endpoints:
- `GET /health` - Basic health check
- `GET /health/db` - Database connectivity check
- `GET /health/blockchain` - Blockchain connectivity check

### 5.3 Monitoring Setup

Consider implementing:
- **Application Performance Monitoring**: New Relic, DataDog, or similar
- **Error Tracking**: Sentry for error monitoring
- **Uptime Monitoring**: Pingdom, UptimeRobot, or similar
- **Log Aggregation**: ELK Stack or similar

## Step 6: SSL and Security

### 6.1 SSL Certificate Installation

Using Let's Encrypt with Certbot:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 6.2 Security Hardening

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Step 7: Backup Strategy

### 7.1 Database Backup

Create backup script `/usr/local/bin/backup-nimo.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/nimo"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="nimo_production"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump $DB_NAME | gzip > $BACKUP_DIR/database_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "database_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-nimo.sh
```

### 7.2 Application Backup

```bash
# Create application backup
tar -czf /var/backups/nimo/application_$(date +%Y%m%d).tar.gz \
  /var/www/nimo \
  --exclude=/var/www/nimo/backend/venv \
  --exclude=/var/www/nimo/frontend/node_modules
```

## Step 8: Deployment Verification

### 8.1 Post-Deployment Checklist

- [ ] All services running (`systemctl status nimo-backend nginx postgresql redis`)
- [ ] SSL certificate valid and auto-renewal configured
- [ ] API endpoints responding correctly
- [ ] Frontend loading and connecting to API
- [ ] Smart contracts deployed and verified on Basescan
- [ ] Database migrations completed successfully
- [ ] Logs being written correctly
- [ ] Backup system functioning
- [ ] Monitoring and alerts configured

### 8.2 Testing Production Deployment

```bash
# Test API health
curl -k https://your-domain.com/api/health

# Test frontend loading
curl -I https://your-domain.com

# Test database connection
curl -k https://your-domain.com/api/health/db

# Test blockchain connection
curl -k https://your-domain.com/api/health/blockchain
```

## Step 9: Maintenance and Updates

### 9.1 Update Process

1. **Test updates in staging environment first**
2. **Create backup before updates**
3. **Use blue-green or rolling deployment strategies**
4. **Monitor application after updates**

### 9.2 Emergency Procedures

**Service Recovery:**
```bash
# Restart services
sudo systemctl restart nimo-backend
sudo systemctl restart nginx

# Check logs
sudo journalctl -u nimo-backend -f
tail -f /var/log/nimo/backend.log
```

**Database Recovery:**
```bash
# Restore from backup
gunzip < /var/backups/nimo/database_YYYYMMDD_HHMMSS.sql.gz | psql nimo_production
```

## Troubleshooting

### Common Issues

**502 Bad Gateway:**
- Check if backend service is running
- Verify Nginx proxy configuration
- Check backend logs for errors

**Smart Contract Issues:**
- Verify contract addresses in environment
- Check RPC provider connectivity
- Ensure sufficient gas for transactions

**Database Connection Issues:**
- Verify database credentials
- Check PostgreSQL service status
- Review connection pool settings

### Log Locations

- **Backend Logs**: `/var/log/nimo/backend.log`
- **Nginx Logs**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **System Logs**: `journalctl -u nimo-backend`
- **Database Logs**: `/var/log/postgresql/postgresql-14-main.log`

## Support and Maintenance

For ongoing support and maintenance:

1. **Monitor system resources regularly**
2. **Keep all components updated**
3. **Review logs for anomalies**
4. **Test backup and restore procedures monthly**
5. **Review and update security measures quarterly**

---

**Last Updated**: August 2025  
**Version**: 1.0  
**Contact**: support@nimo-platform.com