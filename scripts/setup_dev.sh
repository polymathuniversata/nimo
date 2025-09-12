#!/bin/bash

# Nimo Backend Development Setup Script

set -e

echo "Setting up Nimo Backend for Development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
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
