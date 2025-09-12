#!/bin/bash
# Nimo Platform Setup Script for Cardano Integration
# This script sets up the complete backend environment with Cardano and MeTTa support

set -e  # Exit on any error

echo "🚀 Nimo Platform Setup Script"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    print_error "Please run this script from the Nimo project root directory"
    exit 1
fi

print_status "Setting up Nimo Platform with Cardano and MeTTa integration..."

# Step 1: Create virtual environment
print_status "Step 1: Creating Python virtual environment..."
if [ ! -d "nimo_env" ]; then
    python -m venv nimo_env
    print_success "Virtual environment created: nimo_env"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source nimo_env/bin/activate

# Step 2: Upgrade pip
print_status "Step 2: Upgrading pip..."
pip install --upgrade pip

# Step 3: Install base requirements
print_status "Step 3: Installing base requirements..."
pip install -r backend/requirements.txt
print_success "Base requirements installed"

# Step 4: Install Cardano dependencies
print_status "Step 4: Installing Cardano dependencies..."
pip install -r backend/requirements_cardano.txt
print_success "Cardano dependencies installed"

# Step 5: Install MeTTa/Hyperon
print_status "Step 5: Installing MeTTa/Hyperon..."
if pip install hyperon; then
    print_success "MeTTa/Hyperon installed successfully"
else
    print_warning "MeTTa/Hyperon installation failed. Will use mock mode."
    echo "You can install MeTTa manually later or use mock mode for testing."
fi

# Step 6: Verify installations
print_status "Step 6: Verifying installations..."

# Check Flask
if python -c "import flask; print('Flask version:', flask.__version__)" 2>/dev/null; then
    print_success "Flask: OK"
else
    print_error "Flask: FAILED"
fi

# Check PyCardano
if python -c "import pycardano; print('PyCardano: OK')" 2>/dev/null; then
    print_success "PyCardano: OK"
else
    print_error "PyCardano: FAILED"
fi

# Check Blockfrost
if python -c "import blockfrost; print('Blockfrost: OK')" 2>/dev/null; then
    print_success "Blockfrost: OK"
else
    print_error "Blockfrost: FAILED"
fi

# Check MeTTa/Hyperon
if python -c "import hyperon; print('MeTTa/Hyperon: OK')" 2>/dev/null; then
    print_success "MeTTa/Hyperon: OK"
else
    print_warning "MeTTa/Hyperon: NOT INSTALLED (will use mock mode)"
fi

# Step 7: Create environment file template
print_status "Step 7: Creating environment configuration template..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
# Nimo Platform Environment Configuration
# Copy this file and update with your actual values

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///nimo.db

# Cardano Network Configuration
CARDANO_NETWORK=preview
BLOCKFROST_PROJECT_ID_PREVIEW=your_preview_api_key
BLOCKFROST_PROJECT_ID_PREPROD=your_preprod_api_key
BLOCKFROST_PROJECT_ID_MAINNET=your_mainnet_api_key

# Service Wallet (for automated operations)
CARDANO_SERVICE_PRIVATE_KEY=your_service_wallet_private_key
CARDANO_SERVICE_KEY_FILE=service_key.skey

# MeTTa Configuration
USE_METTA_REASONING=true
METTA_MODE=real  # or 'mock' for testing
METTA_CONFIDENCE_THRESHOLD=0.7

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nimo.log
EOF
    print_success "Environment template created: backend/.env"
else
    print_warning "Environment file already exists"
fi

# Step 8: Create logs directory
print_status "Step 8: Creating logs directory..."
mkdir -p backend/logs
print_success "Logs directory created"

# Step 9: Create instance directory for Flask
print_status "Step 9: Creating instance directory..."
mkdir -p backend/instance
print_success "Instance directory created"

# Step 10: Initialize database (if using SQLite)
print_status "Step 10: Database setup..."
cd backend
if python -c "from app import db; db.create_all(); print('Database initialized')" 2>/dev/null; then
    print_success "Database initialized"
else
    print_warning "Database initialization skipped (may need manual setup)"
fi
cd ..

print_success "🎉 Nimo Platform setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your actual configuration values"
echo "2. Get Blockfrost API keys from https://blockfrost.io/"
echo "3. Set up your Cardano service wallet"
echo "4. Run the application: cd backend && python app.py"
echo "5. Test the API endpoints: python test_api_endpoints.py"
echo ""
echo "For detailed documentation, see:"
echo "- docs/backend_implementation_status.md"
echo "- docs/METTA_INTEGRATION_ANALYSIS.md"
echo "- docs/CARDANO_MIGRATION_GUIDE.md"
echo ""
print_status "Setup script finished. Happy coding! 🚀"