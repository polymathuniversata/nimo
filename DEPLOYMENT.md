# Nimo Platform Deployment Guide

This guide covers deployment of the Nimo Platform to production environments.

## Prerequisites

### System Requirements
- Python 3.9+ 
- Node.js 18+
- PostgreSQL 13+ (production database)
- Redis 6+ (caching and rate limiting)
- Nginx (reverse proxy)
- SSL certificate (Let's Encrypt recommended)

### Required Services
- **Base Network RPC** - For blockchain connectivity
- **USDC Contract Access** - For token operations
- **Email Service** - For notifications (SMTP)
- **Monitoring** - Sentry for error tracking (optional)

## Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Nimo
```

### 2. Configure Environment Variables

#### Backend Configuration
```bash
# Copy template and configure
cp .env.template .env

# Edit .env file with production values:
# - Set FLASK_ENV=production
# - Configure DATABASE_URL for PostgreSQL
# - Set strong SECRET_KEY and JWT_SECRET_KEY
# - Configure blockchain contracts for base-mainnet
# - Set up SENTRY_DSN for error tracking
# - Configure MAIL_* settings for email
# - Set REDIS_URL for caching
```

#### Frontend Configuration
```bash
cd frontend
cp .env.template .env

# Edit .env file with production values:
# - Set NODE_ENV=production
# - Configure REACT_APP_API_URL for production API
# - Set REACT_APP_BLOCKCHAIN_NETWORK=base-mainnet
# - Configure analytics and monitoring
```

### 3. Database Setup

```bash
# Install PostgreSQL and create database
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb nimo_production

# Create user and grant privileges
sudo -u postgres psql
postgres=# CREATE USER nimo_user WITH PASSWORD 'secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE nimo_production TO nimo_user;
postgres=# \q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://nimo_user:secure_password@localhost:5432/nimo_production
```

### 4. Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis (edit /etc/redis/redis.conf)
# Set password and memory limits
requirepass your_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server

# Update REDIS_URL in .env
REDIS_URL=redis://:your_redis_password@localhost:6379/0
```

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn psycopg2-binary redis sentry-sdk
```

### 2. Database Migration

```bash
# Initialize database
flask db upgrade

# Verify tables created
flask shell
>>> from models import User, Contribution, Token
>>> exit()
```

### 3. Create Production WSGI Server

Create `wsgi.py` in backend directory:
```python
import os
from app import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)

if __name__ == "__main__":
    app.run()
```

### 4. Create Systemd Service

Create `/etc/systemd/system/nimo-backend.service`:
```ini
[Unit]
Description=Nimo Platform Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/nimo/backend
Environment="PATH=/var/www/nimo/backend/venv/bin"
ExecStart=/var/www/nimo/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable nimo-backend
sudo systemctl start nimo-backend
sudo systemctl status nimo-backend
```

## Frontend Deployment

### 1. Build Production Bundle

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# This creates optimized build/ directory
```

### 2. Serve Static Files

The build directory contains static files that should be served by Nginx.

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt-get install nginx
```

### 2. Create Nginx Configuration

Create `/etc/nginx/sites-available/nimo`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Frontend (React app)
    location / {
        root /var/www/nimo/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location /api/auth {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable Site and SSL

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nimo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set up SSL with Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Set up auto-renewal
sudo systemctl enable certbot.timer
```

## Security Checklist

### Backend Security
- [ ] Strong SECRET_KEY and JWT_SECRET_KEY set
- [ ] Database credentials secured
- [ ] CORS origins restricted to your domains
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Security headers configured
- [ ] Logging enabled for security events
- [ ] Error details hidden in production

### Frontend Security
- [ ] API URLs point to HTTPS endpoints
- [ ] No sensitive data in client-side code
- [ ] Content Security Policy configured
- [ ] Analytics and tracking configured properly

### Infrastructure Security
- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Database not accessible from internet
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured

## Monitoring and Maintenance

### 1. Set up Log Rotation

Create `/etc/logrotate.d/nimo`:
```
/var/www/nimo/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nimo-backend
    endscript
}
```

### 2. Health Checks

Set up monitoring for:
- `/api/health` endpoint
- Database connectivity
- Redis connectivity
- SSL certificate expiry
- Disk space usage
- Application errors (via Sentry)

### 3. Backup Strategy

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U nimo_user -d nimo_production > /backups/nimo_${DATE}.sql
find /backups -name "nimo_*.sql" -mtime +30 -delete
```

### 4. Updates and Maintenance

```bash
# Update application
cd /var/www/nimo
git pull origin main

# Backend updates
cd backend
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart nimo-backend

# Frontend updates
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check logs: `sudo journalctl -u nimo-backend -f`
   - Verify database connection
   - Check environment variables

2. **Frontend not loading**
   - Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
   - Verify build files exist
   - Check proxy configuration

3. **Database connection issues**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check connection string in .env
   - Verify user permissions

4. **High memory usage**
   - Check Redis memory usage
   - Review application logs for memory leaks
   - Consider scaling with more workers

### Getting Help

- Check application logs in `/var/www/nimo/backend/logs/`
- Monitor Sentry dashboard for errors
- Review system logs with `journalctl`
- Check Nginx access/error logs

## Performance Optimization

### Backend Optimization
- Use database connection pooling
- Implement Redis caching for frequent queries  
- Configure gunicorn workers based on CPU cores
- Enable gzip compression in Nginx
- Use database indexes for common queries

### Frontend Optimization
- Implement code splitting
- Use CDN for static assets
- Enable browser caching
- Optimize images and assets
- Consider implementing service worker for offline functionality

This deployment guide provides a production-ready setup for the Nimo Platform with security best practices, monitoring, and maintenance procedures.