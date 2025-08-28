from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging

try:
    from config import active_config
except ImportError:
    print("Warning: config.py not found. Using default configuration.")
    
    class DefaultConfig:
        SECRET_KEY = 'dev-secret-key-change-in-production'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_SECRET_KEY = 'jwt-secret-change-in-production'
    
    active_config = DefaultConfig

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=active_config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    from utils.logging_config import setup_logging, add_request_logging
    setup_logging(
        app_name="nimo",
        log_level=config_class.LOG_LEVEL,
        log_dir=config_class.LOG_DIR,
        enable_file_logging=config_class.ENABLE_FILE_LOGGING,
        enable_json_logging=config_class.ENABLE_JSON_LOGGING,
        max_bytes=config_class.MAX_LOG_SIZE,
        backup_count=config_class.LOG_BACKUP_COUNT
    )
    add_request_logging(app)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Initialize security middleware
    from middleware.security_middleware import init_security
    init_security(app)
    
    # Initialize error handling
    from utils.error_handling import init_error_handling
    init_error_handling(app)
    
    # JWT token blacklist callback
    from middleware.auth_middleware import check_if_token_revoked
    jwt.token_in_blocklist_loader(check_if_token_revoked)
    
    # Initialize Sentry for production error tracking
    if app.config.get('SENTRY_DSN') and not app.config.get('TESTING'):
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                integrations=[FlaskIntegration(), sentry_logging],
                traces_sample_rate=0.1,
                environment=os.environ.get('FLASK_ENV', 'development')
            )
            
            app.logger.info("Sentry error tracking initialized")
        except ImportError:
            app.logger.warning("Sentry SDK not installed, skipping error tracking setup")

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.contribution import contribution_bp
    from routes.token import token_bp
    from routes.bond import bond_bp
    from routes.identity import identity_bp
    from routes.usdc import usdc_bp
    from routes.blockchain import blockchain_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(contribution_bp, url_prefix='/api/contributions')
    app.register_blueprint(token_bp, url_prefix='/api/tokens')
    app.register_blueprint(bond_bp, url_prefix='/api/bonds')
    app.register_blueprint(identity_bp)  # Identity routes have their own url_prefix
    app.register_blueprint(usdc_bp)  # USDC routes have their own url_prefix
    app.register_blueprint(blockchain_bp, url_prefix='/api')

    # Enhanced error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": "Access denied"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": "The requested resource was not found"}), 404

    @app.errorhandler(413)
    def request_too_large(e):
        return jsonify({"error": "Request too large", "message": "The request payload is too large"}), 413

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Rate limit exceeded", "message": "Too many requests. Please try again later."}), 429

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

    # Root endpoint
    @app.route('/')
    def root():
        return {
            "message": "Nimo Platform API Server",
            "version": "1.0.0",
            "status": "operational",
            "metta_integration": "active",
            "endpoints": {
                "health": "/api/health",
                "auth": "/api/auth/*",
                "users": "/api/user/*", 
                "contributions": "/api/contributions/*",
                "tokens": "/api/tokens/*",
                "bonds": "/api/bonds/*",
                "usdc": "/api/usdc/*"
            }
        }, 200

    @app.route('/api')
    def api_info():
        return {
            "message": "Nimo Platform API",
            "version": "1.0.0",
            "metta_integration": "operational",
            "available_endpoints": [
                "GET /api/health - Health check",
                "POST /api/auth/register - User registration", 
                "POST /api/auth/login - User login",
                "POST /api/contributions - Create contribution",
                "POST /api/contributions/verify - MeTTa verification",
                "GET /api/tokens/balance/{user_id} - Token balance",
                "POST /api/bonds - Create bond",
                "POST /api/identity/verify-did - Verify DID",
                "POST /api/identity/verify-ens - Verify ENS name",
                "GET /api/identity/supported-methods - Get supported DID methods",
                "GET /api/usdc/status - USDC integration status",
                "GET /api/usdc/balance/{address} - Check USDC balance",
                "POST /api/usdc/calculate-reward - Calculate USDC rewards",
                "POST /api/usdc/contribution-reward-preview - Preview complete reward"
            ]
        }, 200

    @app.route('/api/health')
    def health_check():
        return {"status": "ok", "metta": "operational"}, 200

    # Public demo endpoints for frontend (no auth required)
    @app.route('/api/contributions', methods=['GET'])
    def get_public_contributions():
        """Public endpoint to get sample contributions for demo"""
        # Return sample data for demo purposes
        sample_contributions = [
            {
                "id": 1,
                "title": "Community Water Project",
                "description": "Built a water well for 200 families in rural Kenya",
                "contribution_type": "infrastructure",
                "impact_level": "significant",
                "created_at": "2024-01-15T10:00:00Z",
                "user_id": 1,
                "evidence": {"type": "photo", "url": "/images/water-well.jpg"},
                "verifications": [
                    {
                        "id": 1,
                        "verifier_name": "Kenya Water Alliance",
                        "organization": "Non-profit",
                        "comments": "Verified impact on community health",
                        "created_at": "2024-01-16T14:30:00Z"
                    }
                ]
            },
            {
                "id": 2,
                "title": "Solar Panel Installation",
                "description": "Installed solar panels for local school providing clean energy",
                "contribution_type": "sustainability",
                "impact_level": "moderate",
                "created_at": "2024-02-01T09:00:00Z",
                "user_id": 2,
                "evidence": {"type": "video", "url": "/videos/solar-install.mp4"},
                "verifications": []
            },
            {
                "id": 3,
                "title": "Mobile Health Clinic",
                "description": "Organized mobile health services reaching 500+ people monthly",
                "contribution_type": "healthcare",
                "impact_level": "transformative", 
                "created_at": "2024-02-15T16:45:00Z",
                "user_id": 3,
                "evidence": {"type": "report", "url": "/reports/health-impact.pdf"},
                "verifications": [
                    {
                        "id": 2,
                        "verifier_name": "WHO Africa",
                        "organization": "International",
                        "comments": "Outstanding community health impact",
                        "created_at": "2024-02-20T11:00:00Z"
                    }
                ]
            }
        ]
        
        return {
            "contributions": sample_contributions,
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total": len(sample_contributions),
                "pages": 1,
                "has_next": False,
                "has_prev": False
            }
        }, 200

    @app.route('/api/bonds', methods=['GET']) 
    def get_public_bonds():
        """Public endpoint to get sample bonds for demo"""
        sample_bonds = [
            {
                "id": 1,
                "bond_id": "education-001",
                "creator_id": 1,
                "title": "Girls Education Initiative",
                "description": "Fund scholarships and school supplies for 100 girls in Tanzania",
                "cause": "Education",
                "value": 25000,
                "status": "active",
                "image_url": "/images/girls-education.jpg",
                "created_at": "2024-01-10T08:00:00Z",
                "milestones": [
                    {
                        "id": 1,
                        "title": "Purchase School Supplies",
                        "description": "Books, uniforms, and materials for all students",
                        "target_amount": 10000,
                        "completed": True,
                        "completion_date": "2024-02-01T00:00:00Z"
                    },
                    {
                        "id": 2,
                        "title": "Scholarship Distribution",
                        "description": "Direct payments to cover school fees",
                        "target_amount": 15000,
                        "completed": False,
                        "completion_date": None
                    }
                ]
            },
            {
                "id": 2,
                "bond_id": "agriculture-002",
                "creator_id": 2,
                "title": "Sustainable Farming Co-op",
                "description": "Support 50 farmers to transition to organic farming practices",
                "cause": "Agriculture",
                "value": 40000,
                "status": "active",
                "image_url": "/images/organic-farming.jpg", 
                "created_at": "2024-01-20T12:00:00Z",
                "milestones": [
                    {
                        "id": 3,
                        "title": "Training Programs",
                        "description": "Organic farming certification for all participants",
                        "target_amount": 15000,
                        "completed": True,
                        "completion_date": "2024-02-15T00:00:00Z"
                    }
                ]
            },
            {
                "id": 3,
                "bond_id": "healthcare-003",
                "creator_id": 3,
                "title": "Rural Health Center",
                "description": "Build and equip a health center serving 5 villages",
                "cause": "Healthcare",
                "value": 75000,
                "status": "active",
                "image_url": "/images/health-center.jpg",
                "created_at": "2024-02-01T10:30:00Z",
                "milestones": []
            }
        ]
        
        return sample_bonds, 200

    @app.route('/api/tokens/balance', methods=['GET'])
    def get_public_token_balance():
        """Public endpoint to get sample token balance for demo"""
        return {
            "balance": 1250.75,
            "updated_at": "2024-02-20T15:30:00Z"
        }, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)