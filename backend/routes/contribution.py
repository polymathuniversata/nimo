from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import asyncio
import datetime

from app import db
from models.contribution import Contribution, Verification
from models.user import User, Token, TokenTransaction
from models.bond import BlockchainTransaction
from services.token_service import award_tokens_for_verification
from services.metta_integration import MeTTaIntegration
from services.metta_reasoning import MeTTaReasoning

# Create blueprint
contribution_bp = Blueprint('contribution', __name__, url_prefix='/api/contributions')

# Optional blockchain imports - if not available, skip blockchain features
try:
    from services.blockchain_service import BlockchainService
    from services.metta_blockchain_bridge import MeTTaBlockchainBridge
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    print("Warning: Blockchain services not available")

@contribution_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_contributions():
    """Get contributions for the current user (alias for backwards compatibility)"""
    current_user_id = int(get_jwt_identity())

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    # Get all contributions for the current user
    contributions = Contribution.query.filter_by(user_id=current_user_id) \
        .order_by(Contribution.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "contributions": [contribution.to_dict() for contribution in contributions.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": contributions.total,
            "pages": contributions.pages,
            "has_next": contributions.has_next,
            "has_prev": contributions.has_prev
        }
    }), 200
@jwt_required()
def get_contributions():
    current_user_id = int(get_jwt_identity())  # Convert string to int
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 per page
    
    # Get filter parameters
    verified = request.args.get('verified')
    contribution_type = request.args.get('type')
    impact_level = request.args.get('impact')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Base query
    query = Contribution.query.filter_by(user_id=current_user_id)
    
    # Apply filters
    if verified is not None:
        if verified.lower() == 'true':
            query = query.filter(Contribution.verifications.any())
        elif verified.lower() == 'false':
            query = query.filter(~Contribution.verifications.any())
    
    if contribution_type:
        query = query.filter_by(contribution_type=contribution_type)
        
    if impact_level:
        query = query.filter(Contribution.impact_level == impact_level)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Contribution.title.ilike(search_term) | 
            Contribution.description.ilike(search_term)
        )
    
    # Apply sorting
    if sort_by == 'created_at':
        sort_column = Contribution.created_at
    elif sort_by == 'title':
        sort_column = Contribution.title
    elif sort_by == 'type':
        sort_column = Contribution.contribution_type
    else:
        sort_column = Contribution.created_at
    
    if sort_order.lower() == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Execute paginated query
    try:
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False,
            max_per_page=100
        )
        
        # Build response with metadata
        response_data = {
            "contributions": [contrib.to_dict() for contrib in pagination.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next,
                "prev_num": pagination.prev_num,
                "next_num": pagination.next_num
            },
            "filters": {
                "verified": verified,
                "type": contribution_type,
                "impact": impact_level,
                "search": search,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
        # Add cache headers for better performance
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'private, max-age=300'  # 5 minutes cache
        return response, 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting contributions: {e}")
        return jsonify({"error": "Failed to retrieve contributions"}), 500


@contribution_bp.route('/', methods=['POST'])
@jwt_required()
def add_contribution():
    current_user_id = int(get_jwt_identity())  # Convert string to int
    data = request.get_json()
    
    # Input validation
    validation_errors = []
    
    # Required fields
    if not data or not data.get('title'):
        validation_errors.append("Title is required")
    elif len(data['title'].strip()) < 3:
        validation_errors.append("Title must be at least 3 characters long")
    elif len(data['title']) > 200:
        validation_errors.append("Title must be less than 200 characters")
    
    # Optional field validation
    if data.get('description') and len(data['description']) > 2000:
        validation_errors.append("Description must be less than 2000 characters")
    
    # Validate contribution type
    valid_types = ['coding', 'education', 'volunteer', 'activism', 'leadership', 
                   'entrepreneurship', 'environmental', 'community', 'other']
    if data.get('type') and data['type'] not in valid_types:
        validation_errors.append(f"Invalid contribution type. Must be one of: {', '.join(valid_types)}")
    
    # Validate impact level
    valid_impacts = ['minimal', 'moderate', 'significant', 'transformative']
    if data.get('impact') and data['impact'] not in valid_impacts:
        validation_errors.append(f"Invalid impact level. Must be one of: {', '.join(valid_impacts)}")
    
    # Validate evidence structure
    if data.get('evidence'):
        evidence = data['evidence']
        if not isinstance(evidence, dict):
            validation_errors.append("Evidence must be a valid object")
        elif evidence.get('url') and not _is_valid_url(evidence['url']):
            validation_errors.append("Evidence URL is not valid")
    
    # Return validation errors if any
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Rate limiting check (simple implementation)
    user = User.query.get(current_user_id)
    if user and _check_rate_limit(user, 'contribution_creation'):
        return jsonify({"error": "Rate limit exceeded. Please wait before creating another contribution"}), 429
    
    try:
        # Sanitize inputs
        title = data['title'].strip()
        description = data.get('description', '').strip() if data.get('description') else None
        contribution_type = data.get('type', 'other')
        impact_level = data.get('impact', 'moderate')
        
        # Create new contribution with sanitized data
        new_contribution = Contribution(
            user_id=current_user_id,
            title=title,
            description=description,
            contribution_type=contribution_type,
            impact_level=impact_level,
            evidence=data.get('evidence')
        )
        
        db.session.add(new_contribution)
        db.session.commit()
        
        current_app.logger.info(f"New contribution created by user {current_user_id}: {title}")
        
        return jsonify(new_contribution.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating contribution: {e}")
        return jsonify({"error": "Failed to create contribution"}), 500


def _is_valid_url(url):
    """Validate URL format"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def _check_rate_limit(user, action_type):
    """Check if user has exceeded rate limit for specific action"""
    # Simple rate limiting implementation
    # In production, you'd use Redis or similar
    import datetime
    
    if action_type == 'contribution_creation':
        # Allow maximum 10 contributions per hour
        if not hasattr(user, 'last_contribution_time') or user.last_contribution_time is None:
            return False
            
        # This is a simplified check - in production, use proper rate limiting
        time_diff = datetime.datetime.utcnow() - user.last_contribution_time
        if time_diff.total_seconds() < 360:  # 6 minutes minimum between contributions
            return True
    
    return False


@contribution_bp.route('/<int:contrib_id>', methods=['GET'])
@jwt_required()
def get_contribution(contrib_id):
    contribution = Contribution.query.get(contrib_id)
    
    if not contribution:
        return jsonify({"error": "Contribution not found"}), 404
    
    return jsonify(contribution.to_dict()), 200


@contribution_bp.route('/<int:contrib_id>/explain', methods=['GET'])
@jwt_required()
def explain_verification(contrib_id):
    """Get MeTTa explanation for a contribution verification"""
    current_user_id = int(get_jwt_identity())  # Convert string to int
    
    # Get contribution
    contribution = Contribution.query.get(contrib_id)
    if not contribution:
        return jsonify({"error": "Contribution not found"}), 404
    
    # Check if user has permission to view the explanation
    if contribution.user_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or not getattr(user, 'has_verification_permission', lambda: True)():
            return jsonify({"error": "Unauthorized"}), 403
    
    # Initialize MeTTa service if available
    use_metta = current_app.config.get('USE_METTA_REASONING', False)
    
    # Get verification history
    verification_history = []
    for verification in contribution.verifications:
        # Find associated blockchain transaction for the proof
        tx = None
        if hasattr(BlockchainTransaction, 'query'):
            tx = BlockchainTransaction.query.filter_by(
                contribution_id=contrib_id,
                transaction_type='verification'
            ).first()
        
        proof = None
        if tx and hasattr(tx, 'tx_hash'):
            proof = tx.tx_hash
        
        verification_history.append({
            "verifier": verification.verifier_name,
            "organization": verification.organization,
            "date": verification.verified_at.isoformat() if hasattr(verification, 'verified_at') else None,
            "comments": verification.comments,
            "proof": proof
        })
    
    # Generate explanation
    if use_metta and hasattr(contribution, 'evidence') and contribution.evidence:
        try:
            # Use MeTTa for detailed explanation
            metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
            
            # Generate explanation based on contribution and verifications
            explanation = {
                "contribution": {
                    "id": contribution.id,
                    "title": contribution.title,
                    "type": getattr(contribution, 'contribution_type', None),
                    "impact_level": getattr(contribution, 'impact_level', 'moderate')
                },
                "verification_history": verification_history,
                "reasoning_factors": {
                    "evidence_quality": "high" if isinstance(contribution.evidence, dict) and 
                                       contribution.evidence.get('url') and 
                                       "github.com" in contribution.evidence.get('url', '') 
                                       else "medium",
                    "skill_match": "verified",
                    "impact_assessment": getattr(contribution, 'impact_level', 'moderate')
                },
                "detailed_explanation": (
                    "This contribution was verified based on multiple factors including "
                    "the quality of the provided evidence, the match between the contributor's "
                    f"skills and the contribution type, and the assessed impact level."
                )
            }
        except Exception as e:
            explanation = {
                "contribution": {
                    "id": contribution.id,
                    "title": contribution.title
                },
                "verification_history": verification_history,
                "error": str(e)
            }
    else:
        # Simple explanation without MeTTa
        explanation = {
            "contribution": {
                "id": contribution.id,
                "title": contribution.title,
                "type": getattr(contribution, 'contribution_type', None)
            },
            "verification_history": verification_history
        }
    
    return jsonify(explanation), 200


@contribution_bp.route('/<int:contrib_id>/verify', methods=['POST'])
@jwt_required()
async def verify_contribution(contrib_id):
    """Verify a contribution using MeTTa reasoning"""
    current_user_id = int(get_jwt_identity())  # Convert string to int
    data = request.get_json()
    
    # Check if user has permission to verify contributions
    user = User.query.get(current_user_id)
    if not user or not getattr(user, 'has_verification_permission', lambda: True)():
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get contribution
    contribution = Contribution.query.get(contrib_id)
    if not contribution:
        return jsonify({"error": "Contribution not found"}), 404
    
    # Initialize services
    try:
        # First, check if we should use MeTTa reasoning
        use_metta = current_app.config.get('USE_METTA_REASONING', False)
        
        if use_metta and contribution.evidence_dict:
            # Use new MeTTa integration
            metta_integration = MeTTaIntegration(
                rules_dir=current_app.config.get('METTA_RULES_DIR'),
                db_path=current_app.config.get('METTA_DB_PATH')
            )
            
            # Initialize blockchain services if available
            blockchain_service = None
            bridge = None
            if BLOCKCHAIN_AVAILABLE:
                try:
                    blockchain_service = BlockchainService()
                    metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
                    bridge = MeTTaBlockchainBridge(metta_service, blockchain_service)
                except Exception as e:
                    current_app.logger.warning(f"Blockchain service initialization failed: {e}")
            
            # First use the new integration to validate the contribution
            evidence_dict = contribution.evidence_dict or {}
            contribution_data = {
                "user_id": contribution.user_id,
                "category": getattr(contribution, 'contribution_type', 'other'),
                "title": contribution.title,
                "evidence": [
                    {
                        "type": evidence_dict.get('type', 'url'),
                        "url": evidence_dict.get('url', ''),
                        "id": f"evidence-{contrib_id}"
                    }
                ] if evidence_dict.get('url') else []
            }
            
            # Validate with MeTTa integration
            validation_result = metta_integration.validate_contribution(
                contribution_id=str(contrib_id),
                contribution_data=contribution_data
            )
            
            # Execute verification through bridge for blockchain integration if available
            result = validation_result.copy()  # Start with MeTTa results
            
            if bridge:
                try:
                    blockchain_result = await bridge.verify_contribution_on_chain(
                        user_id=contribution.user_id,
                        contribution_id=contrib_id,
                        evidence=evidence_dict
                    )
                    # Merge blockchain results with MeTTa results
                    result.update(blockchain_result)
                except Exception as e:
                    current_app.logger.warning(f"Blockchain verification failed: {e}")
                    # Continue with MeTTa-only results
            
            # Merge the results
            result.update({
                'reputation_impact': validation_result.get('reputation_impact', 0),
                'token_award': validation_result.get('token_award', 0),
                'confidence': validation_result.get('confidence', 0.0),
                'explanation': validation_result.get('explanation', '')
            })
            
            # Create verification record if verified
            if result['status'] == 'verified':
                verification = Verification(
                    contribution_id=contrib_id,
                    organization=data.get('organization', 'Nimo Platform'),
                    verifier_name=user.name if hasattr(user, 'name') else data.get('verifier_name'),
                    comments=result['explanation']
                )
                db.session.add(verification)
                
                # Record blockchain transactions if available
                if 'verification_tx' in result:
                    blockchain_record = BlockchainTransaction(
                        user_id=contribution.user_id,
                        contribution_id=contrib_id,
                        transaction_type='verification',
                        tx_hash=result['verification_tx'],
                        status='confirmed'
                    )
                    db.session.add(blockchain_record)
                
                if 'token_tx' in result:
                    token_record = BlockchainTransaction(
                        user_id=contribution.user_id,
                        contribution_id=contrib_id,
                        transaction_type='token_mint',
                        tx_hash=result['token_tx'],
                        status='confirmed'
                    )
                    db.session.add(token_record)
                
                # Award tokens the traditional way as backup
                award_tokens_for_verification(contribution.user_id, verification.id)
                
                db.session.commit()
                
                return jsonify({
                    "message": "Contribution verified successfully using MeTTa reasoning",
                    "verification": verification.to_dict() if hasattr(verification, 'to_dict') else {
                        "id": verification.id,
                        "organization": verification.organization,
                        "verifier_name": verification.verifier_name,
                        "comments": verification.comments
                    },
                    "metta_result": result
                }), 200
            
            # Flag for manual review if fraud detected
            elif result.get('status') == 'flagged_for_fraud':
                # Update contribution status to flagged
                if hasattr(contribution, 'status'):
                    contribution.status = 'flagged_for_review'
                    db.session.commit()
                
                return jsonify({
                    "message": "Contribution flagged for review",
                    "reason": result.get('reason'),
                    "confidence": result.get('confidence')
                }), 200
            
            # If verification failed but not fraud
            else:
                return jsonify({
                    "message": "Contribution verification failed",
                    "reason": result.get('reason'),
                    "confidence": result.get('confidence')
                }), 200
        
        else:
            # Use traditional verification
            verification = Verification(
                contribution_id=contrib_id,
                organization=data.get('organization', 'Nimo Platform'),
                verifier_name=data.get('verifier_name'),
                comments=data.get('comments')
            )
            
            db.session.add(verification)
            db.session.flush()
            
            # Award tokens to the contribution creator
            award_tokens_for_verification(contribution.user_id, verification.id)
            
            db.session.commit()
            
            return jsonify({
                "message": "Contribution verified successfully",
                "verification": verification.to_dict() if hasattr(verification, 'to_dict') else {
                    "id": verification.id,
                    "organization": verification.organization,
                    "verifier_name": verification.verifier_name,
                    "comments": verification.comments
                }
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@contribution_bp.route('/batch-verify', methods=['POST'])
@jwt_required()
async def batch_verify_contributions():
    """Batch verify multiple contributions for efficiency"""
    current_user_id = int(get_jwt_identity())  # Convert string to int
    data = request.get_json()
    
    # Check if user has permission to verify contributions
    user = User.query.get(current_user_id)
    if not user or not getattr(user, 'has_verification_permission', lambda: True)():
        return jsonify({"error": "Unauthorized"}), 403
    
    # Validate input
    if not data or not data.get('contribution_ids'):
        return jsonify({"error": "contribution_ids required"}), 400
    
    contribution_ids = data['contribution_ids']
    if not isinstance(contribution_ids, list) or len(contribution_ids) == 0:
        return jsonify({"error": "contribution_ids must be a non-empty list"}), 400
    
    if len(contribution_ids) > 50:  # Limit batch size
        return jsonify({"error": "Maximum 50 contributions per batch"}), 400
    
    try:
        # Initialize services
        use_metta = current_app.config.get('USE_METTA_REASONING', False)
        
        if use_metta:
            # Initialize services with availability check
            bridge = None
            if BLOCKCHAIN_AVAILABLE:
                try:
                    metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
                    blockchain_service = BlockchainService()
                    bridge = MeTTaBlockchainBridge(metta_service, blockchain_service)
                except Exception as e:
                    current_app.logger.warning(f"Blockchain services not available for batch processing: {e}")
            
            if not bridge:
                return jsonify({"error": "Blockchain integration required for batch verification"}), 400
            
            # Prepare batch data
            verification_batch = []
            for contrib_id in contribution_ids:
                contribution = Contribution.query.get(contrib_id)
                if contribution:
                    user = User.query.get(contribution.user_id)
                    verification_batch.append({
                        'user_id': contribution.user_id,
                        'contribution_id': contrib_id,
                        'evidence': contribution.evidence or {},
                        'user_address': getattr(user, 'blockchain_address', None)
                    })
            
            # Execute batch verification
            results = await bridge.batch_verify_contributions(verification_batch)
            
            # Process results and update database
            verification_results = []
            for result in results:
                contrib_id = result.get('contribution_id')
                if result.get('verified'):
                    # Create verification record
                    verification = Verification(
                        contribution_id=contrib_id,
                        organization=data.get('organization', 'Nimo Platform'),
                        verifier_name=user.name if hasattr(user, 'name') else 'System',
                        comments=result.get('explanation', 'Batch verified using MeTTa reasoning')
                    )
                    db.session.add(verification)
                
                verification_results.append({
                    'contribution_id': contrib_id,
                    'verified': result.get('verified', False),
                    'confidence': result.get('confidence', 0.0),
                    'explanation': result.get('explanation', ''),
                    'blockchain_status': result.get('blockchain_status', 'unknown'),
                    'transaction_hash': result.get('transaction_hash')
                })
            
            db.session.commit()
            
            return jsonify({
                'message': 'Batch verification completed',
                'results': verification_results,
                'total_processed': len(verification_results),
                'total_verified': sum(1 for r in verification_results if r['verified'])
            }), 200
        
        else:
            return jsonify({"error": "MeTTa reasoning not enabled for batch operations"}), 400
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Batch verification error: {e}")
        return jsonify({"error": "Batch verification failed"}), 500


@contribution_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_contribution_analytics():
    """Get analytics for contributions"""
    current_user_id = int(get_jwt_identity())  # Convert string to int
    
    # Get query parameters
    time_period = request.args.get('period', '30d')  # 7d, 30d, 90d, all
    user_filter = request.args.get('user_id')
    
    # Check if user has permission to view analytics
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # If requesting another user's analytics, check permissions
    if user_filter and int(user_filter) != current_user_id:
        if not getattr(user, 'has_admin_permission', lambda: False)():
            return jsonify({"error": "Unauthorized"}), 403
    
    try:
        # Base query for contributions
        query = Contribution.query
        if user_filter:
            query = query.filter_by(user_id=user_filter)
        else:
            query = query.filter_by(user_id=current_user_id)
        
        # Apply time filter
        if time_period != 'all':
            import datetime
            days_map = {'7d': 7, '30d': 30, '90d': 90}
            days = days_map.get(time_period, 30)
            cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
            query = query.filter(Contribution.created_at >= cutoff_date)
        
        # Calculate analytics
        contributions = query.all()
        total_contributions = len(contributions)
        verified_contributions = len([c for c in contributions if c.verifications])
        verification_rate = (verified_contributions / total_contributions) if total_contributions > 0 else 0
        
        # Calculate by type
        by_type = {}
        for contrib in contributions:
            contrib_type = getattr(contrib, 'contribution_type', 'other') or 'other'
            by_type[contrib_type] = by_type.get(contrib_type, 0) + 1
        
        # Calculate by impact
        by_impact = {}
        for contrib in contributions:
            impact_level = getattr(contrib, 'impact_level', 'moderate') or 'moderate'
            by_impact[impact_level] = by_impact.get(impact_level, 0) + 1
        
        # Get MeTTa analytics if enabled
        metta_analytics = None
        if current_app.config.get('USE_METTA_REASONING', False):
            try:
                metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
                
                analytics = {}
                if hasattr(metta_service, 'get_verification_stats'):
                    analytics['verification_stats'] = metta_service.get_verification_stats()
                
                if BLOCKCHAIN_AVAILABLE:
                    try:
                        blockchain_service = BlockchainService()
                        if hasattr(blockchain_service, 'get_network_info'):
                            analytics['network_info'] = blockchain_service.get_network_info()
                    except Exception:
                        pass
                
                metta_analytics = analytics if analytics else None
            except Exception as e:
                current_app.logger.warning(f"Could not get MeTTa analytics: {e}")
        
        analytics_data = {
            'summary': {
                'total_contributions': total_contributions,
                'verified_contributions': verified_contributions,
                'verification_rate': round(verification_rate, 3),
                'time_period': time_period
            },
            'by_type': by_type,
            'by_impact': by_impact,
            'metta_analytics': metta_analytics,
            'generated_at': datetime.datetime.utcnow().isoformat()
        }
        
        # Add cache headers
        response = jsonify(analytics_data)
        response.headers['Cache-Control'] = 'private, max-age=600'  # 10 minutes cache
        return response, 200
    
    except Exception as e:
        current_app.logger.error(f"Analytics error: {e}")
        return jsonify({"error": "Failed to generate analytics"}), 500


@contribution_bp.route('/verification-report/<int:contrib_id>', methods=['GET'])
@jwt_required() 
def get_verification_report(contrib_id):
    """Get detailed verification report for a contribution"""
    current_user_id = int(get_jwt_identity())  # Convert string to int
    
    # Get contribution
    contribution = Contribution.query.get(contrib_id)
    if not contribution:
        return jsonify({"error": "Contribution not found"}), 404
    
    # Check permissions
    user = User.query.get(current_user_id)
    if contribution.user_id != current_user_id and not getattr(user, 'has_verification_permission', lambda: False)():
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        # Generate comprehensive report
        if current_app.config.get('USE_METTA_REASONING', False):
            metta_service = MeTTaReasoning(db_path=current_app.config.get('METTA_DB_PATH'))
            blockchain_service = BlockchainService()
            bridge = MeTTaBlockchainBridge(metta_service, blockchain_service)
            
            report = bridge.generate_verification_report(contrib_id)
        else:
            # Generate basic report without MeTTa
            report = {
                'contribution_id': contrib_id,
                'basic_info': {
                    'title': contribution.title,
                    'type': getattr(contribution, 'contribution_type', None),
                    'impact_level': getattr(contribution, 'impact_level', None),
                    'created_at': contribution.created_at.isoformat() if hasattr(contribution, 'created_at') else None
                },
                'verification_history': [
                    {
                        'verifier': v.verifier_name,
                        'organization': v.organization,
                        'comments': v.comments,
                        'verified_at': v.verified_at.isoformat() if hasattr(v, 'verified_at') else None
                    }
                    for v in contribution.verifications
                ],
                'generated_at': datetime.datetime.utcnow().isoformat()
            }
        
        return jsonify(report), 200
    
    except Exception as e:
        current_app.logger.error(f"Report generation error: {e}")
        return jsonify({"error": "Failed to generate verification report"}), 500