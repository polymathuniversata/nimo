#!/usr/bin/env python3
"""
Nimo Backend Server Entry Point
Properly configures and runs the Flask application with all integrations
"""

from app import create_app
import os

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    print("Starting Nimo Backend Server...")
    print("API will be available at: http://127.0.0.1:5000")
    print("Frontend should connect to: http://localhost:5000")
    print("API Documentation: http://127.0.0.1:5000/api")
    print("Health Check: http://127.0.0.1:5000/api/health")
    
    # Run the application
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )