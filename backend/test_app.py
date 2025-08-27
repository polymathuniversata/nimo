#!/usr/bin/env python3
"""
Simple test script to verify the Flask application starts correctly
"""

from app import create_app

def test_app_creation():
    """Test that the Flask app can be created successfully"""
    try:
        app = create_app()
        print("[OK] Flask app created successfully!")
        
        print("\nAvailable routes:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
        
        print(f"\n[OK] App configuration loaded: {app.config.get('FLASK_ENV', 'default')}")
        print(f"[OK] Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        print(f"[OK] MeTTa integration: {'Enabled' if app.config.get('USE_METTA_REASONING') else 'Disabled'}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create Flask app: {e}")
        return False

if __name__ == "__main__":
    success = test_app_creation()
    exit(0 if success else 1)