from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
import time

from app import db
from models.user import User, Skill, Token
from services.signature_verification import SignatureVerificationService, SignatureRateLimit
from middleware.security_middleware import rate_limit, validate_input, security_scan
from middleware.auth_middleware import rate_limit_auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/challenge', methods=['POST'])
@rate_limit(limit=20)  # 20 requests per 5-minute window
@validate_input({
    'wallet_address': {'type': 'wallet_address', 'required': True}
})
@security_scan
def get_challenge():
    """
    Generate a challenge message for wallet authentication.
    This endpoint provides a nonce and message for the wallet to sign.
    """
    # Get validated data from middleware
    data = g.validated_data
    wallet_address = data['wallet_address']
    
    # Get client IP for rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
    
    # Check rate limiting
    if SignatureRateLimit.is_rate_limited(client_ip):
        current_app.logger.warning(f"Challenge rate limit exceeded for IP: {client_ip}")
        return jsonify({"error": "Too many requests. Please try again later."}), 429
    
    # Generate nonce and challenge message
    nonce = SignatureVerificationService.get_nonce_for_challenge()
    message = SignatureVerificationService.create_challenge_message(wallet_address, nonce)
    
    return jsonify({
        "challenge": {
            "message": message,
            "nonce": nonce,
            "wallet_address": wallet_address
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
@rate_limit_auth
@validate_input({
    'auth_method': {'type': 'string', 'required': False},
    'name': {'type': 'string', 'max_length': 100, 'required': True},
    'email': {'type': 'email', 'required': False},
    'password': {'type': 'string', 'min_length': 6, 'required': False},
    'wallet_address': {'type': 'wallet_address', 'required': False},
    'signature': {'type': 'string', 'required': False},
    'message': {'type': 'string', 'required': False},
    'bio': {'type': 'string', 'max_length': 500, 'required': False},
    'location': {'type': 'string', 'max_length': 100, 'required': False},
    'skills': {'type': 'array', 'max_length': 20, 'required': False}
})
@security_scan
def register():
    # Get validated data from middleware
    data = g.validated_data
    auth_method = data.get('auth_method', 'traditional')

    if auth_method == 'wallet':
        # Wallet registration
        required_fields = ['wallet_address', 'signature', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        wallet_address = data['wallet_address']
        signature = data['signature']
        message = data['message']

        # Check if wallet is already registered
        if User.query.filter_by(wallet_address=wallet_address).first():
            return jsonify({"error": "Wallet address already registered"}), 409

        # Get client IP for rate limiting
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        
        # Check rate limiting
        if SignatureRateLimit.is_rate_limited(client_ip):
            current_app.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({"error": "Too many attempts. Please try again later."}), 429
        
        # Record the attempt
        SignatureRateLimit.record_attempt(client_ip)
        
        # Verify wallet address format
        if not SignatureVerificationService.is_valid_ethereum_address(wallet_address):
            return jsonify({"error": "Invalid wallet address format"}), 400
        
        # Verify signature
        verification_result = SignatureVerificationService.verify_signature(
            message=message,
            signature=signature,
            expected_address=wallet_address
        )
        
        if not verification_result['valid']:
            current_app.logger.warning(f"Signature verification failed for {wallet_address}: {verification_result['error']}")
            return jsonify({"error": f"Signature verification failed: {verification_result['error']}"}), 401

        try:
            # Create new wallet user
            new_user = User(
                email=f"{wallet_address}@wallet.local",
                name=data.get('name', f"Wallet User {wallet_address[:6]}...{wallet_address[-4:]}"),
                wallet_address=wallet_address,
                auth_method='wallet',
                bio=data.get('bio'),
                location=data.get('location')
            )
            db.session.add(new_user)
            db.session.flush()

            # Add skills if provided
            if data.get('skills'):
                for skill_name in data['skills']:
                    skill = Skill(user_id=new_user.id, name=skill_name)
                    db.session.add(skill)

            # Initialize token balance
            token = Token(user_id=new_user.id, initial_balance=0)
            db.session.add(token)

            db.session.commit()

            return jsonify({"message": "Wallet user registered successfully"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    else:
        # Traditional email/password registration
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already registered"}), 409

        try:
            # Create new user
            new_user = User(
                email=data['email'],
                password=data['password'],
                name=data['name'],
                location=data.get('location'),
                bio=data.get('bio'),
                auth_method='traditional'
            )
            db.session.add(new_user)
            db.session.flush()  # Flush to get the new user ID

            # Add skills if provided
            if data.get('skills'):
                for skill_name in data['skills']:
                    skill = Skill(user_id=new_user.id, name=skill_name)
                    db.session.add(skill)

            # Initialize token balance
            token = Token(user_id=new_user.id, initial_balance=0)
            db.session.add(token)

            db.session.commit()

            return jsonify({"message": "User registered successfully"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit_auth
@validate_input({
    'auth_method': {'type': 'string', 'required': False},
    'email': {'type': 'email', 'required': False},
    'password': {'type': 'string', 'required': False},
    'wallet_address': {'type': 'wallet_address', 'required': False},
    'signature': {'type': 'string', 'required': False},
    'message': {'type': 'string', 'required': False}
})
@security_scan
def login():
    # Get validated data from middleware
    data = g.validated_data
    auth_method = data.get('auth_method', 'traditional')

    if auth_method == 'wallet':
        # Wallet login
        required_fields = ['wallet_address', 'signature', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        wallet_address = data['wallet_address']
        signature = data['signature']
        message = data['message']

        # Find user by wallet address
        user = User.query.filter_by(wallet_address=wallet_address).first()

        if not user:
            return jsonify({"error": "Wallet address not registered"}), 401

        # Get client IP for rate limiting
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        
        # Check rate limiting
        if SignatureRateLimit.is_rate_limited(client_ip):
            current_app.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({"error": "Too many attempts. Please try again later."}), 429
        
        # Record the attempt
        SignatureRateLimit.record_attempt(client_ip)
        
        # Verify wallet address format
        if not SignatureVerificationService.is_valid_ethereum_address(wallet_address):
            return jsonify({"error": "Invalid wallet address format"}), 400
        
        # Verify signature
        verification_result = SignatureVerificationService.verify_signature(
            message=message,
            signature=signature,
            expected_address=wallet_address
        )
        
        if not verification_result['valid']:
            current_app.logger.warning(f"Signature verification failed for {wallet_address}: {verification_result['error']}")
            return jsonify({"error": f"Signature verification failed: {verification_result['error']}"}), 401

        # Generate access token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "message": "Wallet login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    else:
        # Traditional email/password login
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password required"}), 400

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        # Verify user and password
        if not user or not user.verify_password(data['password']):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate access token - JWT expects string identity
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200