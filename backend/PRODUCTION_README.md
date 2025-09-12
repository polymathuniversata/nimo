# Nimo Backend - Production Deployment

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
