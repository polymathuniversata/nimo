from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import active_config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=active_config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.contribution import contribution_bp
    from routes.token import token_bp
    from routes.bond import bond_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(contribution_bp, url_prefix='/api/contributions')
    app.register_blueprint(token_bp, url_prefix='/api/tokens')
    app.register_blueprint(bond_bp, url_prefix='/api/bonds')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Server error"}, 500

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
                "bonds": "/api/bonds/*"
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
                "POST /api/bonds - Create bond"
            ]
        }, 200

    @app.route('/api/health')
    def health_check():
        return {"status": "ok", "metta": "operational"}, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)