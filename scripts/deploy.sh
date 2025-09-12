#!/bin/bash

# Nimo Backend Production Deployment Script

set -e

echo "Starting Nimo Backend Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
