#!/usr/bin/env python3
"""
Run the Nimo Backend Server

This script starts the Flask development server for the Nimo Platform API.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

def main():
    """Main function to run the Flask app"""
    try:
        from app import create_app

        # Create Flask app
        app = create_app()

        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', 'localhost')

        print("🚀 Starting Nimo Backend Server...")
        print(f"🌐 Server will run on: http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/api")
        print(f"💓 Health Check: http://{host}:{port}/api/health")
        print("\nPress Ctrl+C to stop the server\n")

        # Run the app
        app.run(
            host=host,
            port=port,
            debug=os.environ.get('FLASK_ENV') == 'development'
        )

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("  pip install -r backend/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()