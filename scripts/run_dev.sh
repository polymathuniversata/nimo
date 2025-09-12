#!/bin/bash

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

# Start the application
echo "Starting Flask development server..."
flask run --host=0.0.0.0 --port=5000
