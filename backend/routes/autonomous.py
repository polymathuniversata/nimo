"""
Autonomous System Routes for Nimo Platform

This module provides API endpoints for the autonomous MeTTa reasoning system,
including platform cycle execution, contribution processing, reward calculation,
predictive analytics, governance, and security management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
import logging

# Import autonomous services
try:
    from services.metta_reasoning import MeTTaReasoning
    from services.metta_integration_enhanced import MeTTaIntegrationService
    METTA_AVAILABLE = True
except ImportError:
    METTA_AVAILABLE = False
    print("Warning: MeTTa services not available for autonomous operations")

# Create blueprint
autonomous_bp = Blueprint('autonomous', __name__, url_prefix='/api/autonomous')

# Initialize logger
logger = logging.getLogger(__name__)

def get_metta_reasoning_service():
    """Get MeTTa reasoning service instance"""
    if not METTA_AVAILABLE:
        raise Exception("MeTTa services not available")

    # Try to get from app config first
    if hasattr(current_app, 'metta_reasoning_service'):
        return current_app.metta_reasoning_service

    # Create new instance
    service = MeTTaReasoning()
    if hasattr(current_app, 'metta_reasoning_service'):
        current_app.metta_reasoning_service = service
    return service

def get_metta_integration_service():
    """Get MeTTa integration service instance"""
    if not METTA_AVAILABLE:
        raise Exception("MeTTa services not available")

    # Try to get from app config first
    if hasattr(current_app, 'metta_integration_service'):
        return current_app.metta_integration_service

    # Create new instance
    service = MeTTaIntegrationService(force_mock=False)
    if hasattr(current_app, 'metta_integration_service'):
        current_app.metta_integration_service = service
    return service

@autonomous_bp.route('/health', methods=['GET'])
def autonomous_health():
    """Check autonomous system health"""
    try:
        reasoning_service = get_metta_reasoning_service()
        integration_service = get_metta_integration_service()

        health_data = {
            "status": "operational",
            "services": {
                "metta_reasoning": "available",
                "metta_integration": "available"
            },
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0.0"
        }

        return jsonify(health_data), 200

    except Exception as e:
        logger.error(f"Autonomous health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 503

@autonomous_bp.route('/cycle', methods=['POST'])
@jwt_required()
def execute_autonomous_cycle():
    """Execute a complete autonomous platform cycle"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get platform state from request
        data = request.get_json() or {}
        platform_state = data.get('platform_state', {
            "active_users": 1000,
            "total_contributions": 500,
            "platform_health": 0.85,
            "security_alerts": 2,
            "current_user": current_user_id
        })

        # Execute autonomous cycle
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.execute_autonomous_cycle(platform_state)

        if result and result.get('success'):
            return jsonify({
                "message": "Autonomous cycle executed successfully",
                "cycle_id": f"cycle-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Autonomous cycle execution failed",
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Autonomous cycle execution error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/contributions/<contribution_id>/process', methods=['POST'])
@jwt_required()
def process_contribution_autonomously(contribution_id):
    """Process a contribution autonomously using MeTTa reasoning"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get additional parameters
        data = request.get_json() or {}
        priority = data.get('priority', 'normal')
        include_fraud_detection = data.get('fraud_detection', True)

        # Process contribution autonomously
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.process_contribution_autonomously(contribution_id)

        if result and result.get('processed'):
            return jsonify({
                "message": "Contribution processed autonomously",
                "contribution_id": contribution_id,
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Autonomous contribution processing failed",
                "contribution_id": contribution_id,
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Autonomous contribution processing error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/contributions/<contribution_id>/reward', methods=['POST'])
@jwt_required()
def calculate_autonomous_reward(contribution_id):
    """Calculate autonomous reward for a contribution"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get quality and impact scores
        data = request.get_json() or {}
        quality_score = data.get('quality_score', 0.8)
        impact_score = data.get('impact_score', 0.7)

        # Validate scores
        if not (0.0 <= quality_score <= 1.0) or not (0.0 <= impact_score <= 1.0):
            return jsonify({"error": "Quality and impact scores must be between 0.0 and 1.0"}), 400

        # Calculate autonomous reward
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.calculate_autonomous_reward(
            contribution_id, quality_score, impact_score
        )

        if result and result.get('reward_calculated'):
            return jsonify({
                "message": "Autonomous reward calculated successfully",
                "contribution_id": contribution_id,
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Autonomous reward calculation failed",
                "contribution_id": contribution_id,
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Autonomous reward calculation error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/platform/optimize', methods=['POST'])
@jwt_required()
def optimize_platform_predictively():
    """Optimize platform using predictive analytics"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get platform state for optimization
        data = request.get_json() or {}
        platform_state = data.get('platform_state', {
            "user_growth_rate": 0.15,
            "contribution_trends": [100, 120, 140, 160],
            "system_load": 0.7,
            "current_user": current_user_id
        })

        # Execute predictive optimization
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.optimize_platform_predictively(platform_state)

        if result and result.get('optimization_completed'):
            return jsonify({
                "message": "Platform optimization completed",
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Platform optimization failed",
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Platform optimization error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/governance/execute', methods=['POST'])
@jwt_required()
def execute_autonomous_governance():
    """Execute autonomous governance cycle"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get governance state
        data = request.get_json() or {}
        governance_state = data.get('governance_state', {
            "active_proposals": 5,
            "stakeholder_count": 150,
            "voting_participation": 0.75,
            "recent_decisions": 12,
            "current_user": current_user_id
        })

        # Execute autonomous governance
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.execute_governance_autonomously(governance_state)

        if result and result.get('governance_executed'):
            return jsonify({
                "message": "Autonomous governance executed successfully",
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Autonomous governance execution failed",
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Autonomous governance error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/security/manage', methods=['POST'])
@jwt_required()
def manage_security_autonomously():
    """Manage security autonomously"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get security state
        data = request.get_json() or {}
        security_state = data.get('security_state', {
            "threat_level": "medium",
            "active_alerts": 3,
            "recent_incidents": 1,
            "security_score": 0.82,
            "current_user": current_user_id
        })

        # Execute autonomous security management
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.manage_security_autonomously(security_state)

        if result and result.get('security_managed'):
            return jsonify({
                "message": "Security managed autonomously",
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Autonomous security management failed",
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Autonomous security management error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/contributions/<contribution_id>/fraud-detect', methods=['POST'])
@jwt_required()
def detect_fraud_comprehensive(contribution_id):
    """Detect fraud comprehensively for a contribution"""
    try:
        current_user_id = int(get_jwt_identity())

        # Execute comprehensive fraud detection
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.detect_fraud_comprehensive(contribution_id)

        return jsonify({
            "message": "Fraud detection completed",
            "contribution_id": contribution_id,
            "result": result,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Fraud detection error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/analytics/predict', methods=['POST'])
@jwt_required()
def analyze_predictive_insights():
    """Generate predictive insights for an entity"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get prediction parameters
        data = request.get_json() or {}
        entity_id = data.get('entity_id', str(current_user_id))
        prediction_type = data.get('prediction_type', 'user-engagement')

        # Validate prediction type
        valid_types = [
            'user-engagement', 'contribution-quality', 'platform-growth',
            'security-threats', 'governance-outcomes', 'reward-optimization'
        ]

        if prediction_type not in valid_types:
            return jsonify({
                "error": f"Invalid prediction type. Must be one of: {', '.join(valid_types)}"
            }), 400

        # Execute predictive analysis
        reasoning_service = get_metta_reasoning_service()
        result = reasoning_service.analyze_predictive_insights(entity_id, prediction_type)

        if result and result.get('analysis_completed'):
            return jsonify({
                "message": "Predictive analysis completed",
                "entity_id": entity_id,
                "prediction_type": prediction_type,
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Predictive analysis failed",
                "entity_id": entity_id,
                "prediction_type": prediction_type,
                "details": result
            }), 500

    except Exception as e:
        logger.error(f"Predictive analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/batch/process', methods=['POST'])
@jwt_required()
def batch_process_contributions():
    """Batch process multiple contributions autonomously"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get batch parameters
        data = request.get_json() or {}
        contribution_ids = data.get('contribution_ids', [])
        operation_type = data.get('operation_type', 'process')  # process, reward, fraud_detect

        if not contribution_ids:
            return jsonify({"error": "contribution_ids is required"}), 400

        if len(contribution_ids) > 50:
            return jsonify({"error": "Maximum 50 contributions per batch"}), 400

        # Validate operation type
        valid_operations = ['process', 'reward', 'fraud_detect']
        if operation_type not in valid_operations:
            return jsonify({
                "error": f"Invalid operation type. Must be one of: {', '.join(valid_operations)}"
            }), 400

        # Execute batch operation
        reasoning_service = get_metta_reasoning_service()
        results = []

        for contrib_id in contribution_ids:
            try:
                if operation_type == 'process':
                    result = reasoning_service.process_contribution_autonomously(contrib_id)
                elif operation_type == 'reward':
                    # Use default quality/impact scores for batch processing
                    result = reasoning_service.calculate_autonomous_reward(contrib_id, 0.8, 0.7)
                elif operation_type == 'fraud_detect':
                    result = reasoning_service.detect_fraud_comprehensive(contrib_id)

                results.append({
                    'contribution_id': contrib_id,
                    'operation': operation_type,
                    'success': bool(result and 'error' not in result),
                    'result': result
                })

            except Exception as e:
                results.append({
                    'contribution_id': contrib_id,
                    'operation': operation_type,
                    'success': False,
                    'error': str(e)
                })

        # Calculate success statistics
        successful = sum(1 for r in results if r['success'])
        total = len(results)

        return jsonify({
            "message": f"Batch {operation_type} completed",
            "results": results,
            "statistics": {
                "total": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": successful / total if total > 0 else 0
            },
            "timestamp": datetime.datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/status', methods=['GET'])
@jwt_required()
def get_autonomous_status():
    """Get comprehensive autonomous system status"""
    try:
        current_user_id = int(get_jwt_identity())

        # Get service statuses
        reasoning_status = "available" if METTA_AVAILABLE else "unavailable"
        integration_status = "available" if METTA_AVAILABLE else "unavailable"

        # Get system metrics
        system_metrics = {
            "services": {
                "metta_reasoning": reasoning_status,
                "metta_integration": integration_status
            },
            "capabilities": [
                "autonomous_cycle_execution",
                "contribution_processing",
                "reward_calculation",
                "predictive_optimization",
                "governance_execution",
                "security_management",
                "fraud_detection",
                "predictive_analytics"
            ],
            "version": "1.0.0",
            "last_updated": datetime.datetime.now().isoformat()
        }

        return jsonify(system_metrics), 200

    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route('/rules/reload', methods=['POST'])
@jwt_required()
def reload_metta_rules():
    """Reload MeTTa rules (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())

        # Check if user has admin permissions (simplified check)
        # In production, you'd check against a proper admin role
        if current_user_id != 1:  # Simplified admin check
            return jsonify({"error": "Admin access required"}), 403

        # Reload MeTTa rules
        reasoning_service = get_metta_reasoning_service()
        integration_service = get_metta_integration_service()

        # Force reload by recreating services
        if hasattr(current_app, 'metta_reasoning_service'):
            current_app.metta_reasoning_service = MeTTaReasoning()
        if hasattr(current_app, 'metta_integration_service'):
            current_app.metta_integration_service = MeTTaIntegrationService(force_mock=False)

        return jsonify({
            "message": "MeTTa rules reloaded successfully",
            "timestamp": datetime.datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Rule reload error: {e}")
        return jsonify({"error": str(e)}), 500