# Nimo Platform Setup Script for Cardano Integration (Windows)
# This script sets up the complete backend environment with Cardano and MeTTa support

param(
    [switch]$SkipVirtualEnv,
    [switch]$SkipVerification
)

Write-Host "🚀 Nimo Platform Setup Script (Windows)" -ForegroundColor Blue
Write-Host "=======================================" -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if we're in the right directory
if (!(Test-Path "backend\requirements.txt")) {
    Write-Error "Please run this script from the Nimo project root directory"
    exit 1
}

Write-Status "Setting up Nimo Platform with Cardano and MeTTa integration..."

# Step 1: Create virtual environment
if (!$SkipVirtualEnv) {
    Write-Status "Step 1: Creating Python virtual environment..."
    if (!(Test-Path "nimo_env")) {
        python -m venv nimo_env
        Write-Success "Virtual environment created: nimo_env"
    } else {
        Write-Warning "Virtual environment already exists"
    }

    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & ".\nimo_env\Scripts\Activate.ps1"
}

# Step 2: Upgrade pip
Write-Status "Step 2: Upgrading pip..."
pip install --upgrade pip

# Step 3: Install base requirements
Write-Status "Step 3: Installing base requirements..."
pip install -r backend\requirements.txt
Write-Success "Base requirements installed"

# Step 4: Install Cardano dependencies
Write-Status "Step 4: Installing Cardano dependencies..."
pip install -r backend\requirements_cardano.txt
Write-Success "Cardano dependencies installed"

# Step 5: Install MeTTa/Hyperon
Write-Status "Step 5: Installing MeTTa/Hyperon..."
try {
    pip install hyperon
    Write-Success "MeTTa/Hyperon installed successfully"
} catch {
    Write-Warning "MeTTa/Hyperon installation failed. Will use mock mode."
    Write-Host "You can install MeTTa manually later or use mock mode for testing."
}

# Step 6: Verify installations
if (!$SkipVerification) {
    Write-Status "Step 6: Verifying installations..."

    # Check Flask
    try {
        python -c "import flask; print('Flask version:', flask.__version__)"
        Write-Success "Flask: OK"
    } catch {
        Write-Error "Flask: FAILED"
    }

    # Check PyCardano
    try {
        python -c "import pycardano; print('PyCardano: OK')"
        Write-Success "PyCardano: OK"
    } catch {
        Write-Error "PyCardano: FAILED"
    }

    # Check Blockfrost
    try {
        python -c "import blockfrost; print('Blockfrost: OK')"
        Write-Success "Blockfrost: OK"
    } catch {
        Write-Error "Blockfrost: FAILED"
    }

    # Check MeTTa/Hyperon
    try {
        python -c "import hyperon; print('MeTTa/Hyperon: OK')"
        Write-Success "MeTTa/Hyperon: OK"
    } catch {
        Write-Warning "MeTTa/Hyperon: NOT INSTALLED (will use mock mode)"
    }
}

# Step 7: Create environment file template
Write-Status "Step 7: Creating environment configuration template..."
if (!(Test-Path "backend\.env")) {
    @"
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
"@ | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Success "Environment template created: backend\.env"
} else {
    Write-Warning "Environment file already exists"
}

# Step 8: Create logs directory
Write-Status "Step 8: Creating logs directory..."
if (!(Test-Path "backend\logs")) {
    New-Item -ItemType Directory -Path "backend\logs" -Force
}
Write-Success "Logs directory created"

# Step 9: Create instance directory for Flask
Write-Status "Step 9: Creating instance directory..."
if (!(Test-Path "backend\instance")) {
    New-Item -ItemType Directory -Path "backend\instance" -Force
}
Write-Success "Instance directory created"

# Step 10: Initialize database (if using SQLite)
Write-Status "Step 10: Database setup..."
Push-Location backend
try {
    python -c "from app import db; db.create_all(); print('Database initialized')"
    Write-Success "Database initialized"
} catch {
    Write-Warning "Database initialization skipped (may need manual setup)"
}
Pop-Location

Write-Success "🎉 Nimo Platform setup completed!"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend\.env with your actual configuration values"
Write-Host "2. Get Blockfrost API keys from https://blockfrost.io/"
Write-Host "3. Set up your Cardano service wallet"
Write-Host "4. Run the application: cd backend; python app.py"
Write-Host "5. Test the API endpoints: python test_api_endpoints.py"
Write-Host ""
Write-Host "For detailed documentation, see:" -ForegroundColor Cyan
Write-Host "- docs\backend_implementation_status.md"
Write-Host "- docs\METTA_INTEGRATION_ANALYSIS.md"
Write-Host "- docs\CARDANO_MIGRATION_GUIDE.md"
Write-Host ""
Write-Status "Setup script finished. Happy coding! 🚀"