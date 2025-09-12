"""
AI Agents API Routes for Nimo Platform

This module provides RESTful API endpoints for interacting with the AI agents
system, including agent registration, decision-making, challenge submission,
and transparency features.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
import logging
from typing import Dict, List, Any, Optional

# Import AI agents services
try:
    from services.ai_agents_orchestrator import get_ai_agents_orchestrator, AgentType, DecisionStatus
    from services.metta_integration_enhanced import get_metta_service
    from services.metta_reasoning import MeTTaReasoning
    from services.cardano_service import CardanoService
    AI_AGENTS_AVAILABLE = True
except ImportError as e:
    AI_AGENTS_AVAILABLE = False
    print(f"Warning: AI Agents services not available: {e}")

# Create blueprint
ai_agents_bp = Blueprint('ai_agents', __name__, url_prefix='/api/ai-agents')

# Initialize logger
logger = logging.getLogger(__name__)

def get_orchestrator():
    """Get AI agents orchestrator instance"""
    if not AI_AGENTS_AVAILABLE:
        raise Exception("AI Agents services not available")
    
    # Try to get from app context
    if hasattr(current_app, 'ai_orchestrator'):
        return current_app.ai_orchestrator
    
    # Create new instance
    metta_integration = get_metta_service()
    metta_reasoning = MeTTaReasoning()
    
    # Get blockchain service (prefer Cardano if available)
    blockchain_service = None
    if hasattr(current_app, 'cardano_service'):
        blockchain_service = current_app.cardano_service
    elif hasattr(current_app, 'blockchain_service'):
        blockchain_service = current_app.blockchain_service
    else:
        # Create mock blockchain service for development
        blockchain_service = MockBlockchainService()
    
    orchestrator = get_ai_agents_orchestrator(
        metta_integration, metta_reasoning, blockchain_service
    )
    
    # Cache in app context
    current_app.ai_orchestrator = orchestrator
    
    return orchestrator

class MockBlockchainService:
    """Mock blockchain service for development"""
    def register_agent(self, agent_spec):
        return {'success': True, 'tx_hash': 'mock_tx_' + agent_spec['agent_id']}
    
    def create_decision_proof(self, decision):
        return {'success': True, 'tx_hash': 'mock_proof_' + decision['decision_id']}

@ai_agents_bp.route('/health', methods=['GET'])
def ai_agents_health():
    """Check AI agents system health"""
    try:
        orchestrator = get_orchestrator()
        
        health_data = {
            "status": "operational",
            "ai_agents_available": AI_AGENTS_AVAILABLE,
            "registered_agents": len(orchestrator.registered_agents),
            "active_decisions": len([
                d for d in orchestrator.decision_history.values() 
                if d.status in [DecisionStatus.PENDING, DecisionStatus.VALIDATED]
            ]),
            "pending_challenges": len([
                c for c in orchestrator.challenge_history.values()
                if c.status == "pending"
            ]),
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        logger.error(f"AI agents health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "ai_agents_available": AI_AGENTS_AVAILABLE,
            "timestamp": datetime.datetime.now().isoformat()
        }), 503

@ai_agents_bp.route('/agents', methods=['GET'])
@jwt_required()
def list_agents():
    """List all registered agents"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        # Get agent list with performance metrics
        agents_list = []
        for agent_id, agent_spec in orchestrator.registered_agents.items():
            performance = orchestrator.get_agent_performance(agent_id)
            
            agent_info = {
                'agent_id': agent_id,
                'name': agent_spec['name'],
                'agent_type': agent_spec['agent_type'].value,
                'description': agent_spec['description'],
                'owner': agent_spec['owner'],
                'active': agent_spec['active'],
                'performance': performance.get('metrics', {}),
                'last_activity': performance.get('performance', {}).get('last_activity')
            }
            agents_list.append(agent_info)
        
        return jsonify({
            "agents": agents_list,
            "total_count": len(agents_list),
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"List agents error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/agents', methods=['POST'])
@jwt_required()
def register_agent():
    """Register a new AI agent"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        # Get agent specification from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Agent specification required"}), 400
        
        # Add owner information
        data['owner'] = str(current_user_id)
        data['created_at'] = datetime.datetime.now().isoformat()
        
        # Validate required fields
        required_fields = ['agent_id', 'agent_type', 'name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Convert agent_type string to enum
        try:
            data['agent_type'] = AgentType(data['agent_type'])
        except ValueError:
            valid_types = [t.value for t in AgentType]
            return jsonify({
                "error": f"Invalid agent_type. Must be one of: {', '.join(valid_types)}"
            }), 400
        
        # Register the agent
        result = orchestrator.register_agent(data)
        
        if result['success']:
            return jsonify({
                "message": "Agent registered successfully",
                "agent_id": result['agent_id'],
                "blockchain_tx": result.get('blockchain_tx'),
                "timestamp": datetime.datetime.now().isoformat()
            }), 201
        else:
            return jsonify({
                "error": "Agent registration failed",
                "details": result.get('error')
            }), 400
            
    except Exception as e:
        logger.error(f"Agent registration error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/agents/<agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    """Get detailed information about a specific agent"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        if agent_id not in orchestrator.registered_agents:
            return jsonify({"error": "Agent not found"}), 404
        
        agent_spec = orchestrator.registered_agents[agent_id]
        performance = orchestrator.get_agent_performance(agent_id)
        
        # Get recent decisions by this agent
        recent_decisions = [
            {
                'decision_id': d.decision_id,
                'timestamp': d.timestamp,
                'confidence': d.confidence,
                'status': d.status.value
            }
            for d in orchestrator.decision_history.values()
            if d.agent_id == agent_id
        ][-10:]  # Last 10 decisions
        
        agent_details = {
            'agent_id': agent_id,
            'specification': agent_spec,
            'performance': performance,
            'recent_decisions': recent_decisions,
            'decision_count': len([
                d for d in orchestrator.decision_history.values()
                if d.agent_id == agent_id
            ])
        }
        
        return jsonify(agent_details), 200
        
    except Exception as e:
        logger.error(f"Get agent error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/agents/<agent_id>/decisions', methods=['POST'])
@jwt_required()
def make_agent_decision(agent_id):
    """Make a decision using a specific agent"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        if agent_id not in orchestrator.registered_agents:
            return jsonify({"error": "Agent not found"}), 404
        
        # Get input data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Input data required"}), 400
        
        # Add requester information to input
        data['requester_id'] = str(current_user_id)
        data['request_timestamp'] = datetime.datetime.now().isoformat()
        
        # Make decision
        decision = orchestrator.make_decision(agent_id, data)
        
        # Convert decision to JSON-serializable format
        decision_dict = {
            'decision_id': decision.decision_id,
            'agent_id': decision.agent_id,
            'agent_type': decision.agent_type.value,
            'decision': decision.decision,
            'confidence': decision.confidence,
            'reasoning': decision.reasoning,
            'metta_proof': decision.metta_proof,
            'blockchain_proof': decision.blockchain_proof,
            'timestamp': decision.timestamp,
            'status': decision.status.value,
            'challenge_deadline': decision.challenge_deadline
        }
        
        return jsonify({
            "message": "Decision made successfully",
            "decision": decision_dict,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Make decision error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/decisions/<decision_id>', methods=['GET'])
@jwt_required()
def get_decision(decision_id):
    """Get detailed information about a specific decision"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        if decision_id not in orchestrator.decision_history:
            return jsonify({"error": "Decision not found"}), 404
        
        # Get complete audit trail
        audit_trail = orchestrator.get_decision_audit_trail(decision_id)
        
        return jsonify({
            "decision_id": decision_id,
            "audit_trail": audit_trail,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Get decision error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/decisions/<decision_id>/challenge', methods=['POST'])
@jwt_required()
def challenge_decision(decision_id):
    """Challenge an agent decision"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        if decision_id not in orchestrator.decision_history:
            return jsonify({"error": "Decision not found"}), 404
        
        # Get challenge data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Challenge data required"}), 400
        
        reason = data.get('reason', '')
        evidence = data.get('evidence', {})
        
        if not reason:
            return jsonify({"error": "Challenge reason required"}), 400
        
        # Submit challenge
        result = orchestrator.challenge_decision(
            decision_id, str(current_user_id), reason, evidence
        )
        
        if result['success']:
            return jsonify({
                "message": "Challenge submitted successfully",
                "challenge_id": result['challenge_id'],
                "stake_amount": result['stake_amount'],
                "resolution_process": result['resolution_process'],
                "timestamp": datetime.datetime.now().isoformat()
            }), 201
        else:
            return jsonify({
                "error": "Challenge submission failed",
                "details": result.get('error')
            }), 400
            
    except Exception as e:
        logger.error(f"Challenge decision error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/decisions/<decision_id>/validate', methods=['POST'])
@jwt_required()
def validate_decision(decision_id):
    """Validate decision through multi-agent consensus"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        if decision_id not in orchestrator.decision_history:
            return jsonify({"error": "Decision not found"}), 404
        
        # Validate decision through consensus
        result = orchestrator.validate_decision_consensus(decision_id)
        
        if result['success']:
            return jsonify({
                "message": "Decision validation completed",
                "decision_id": decision_id,
                "consensus": result['consensus'],
                "validations": result['validations'],
                "timestamp": datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Decision validation failed",
                "details": result.get('error')
            }), 500
            
    except Exception as e:
        logger.error(f"Validate decision error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/batch/decisions', methods=['POST'])
@jwt_required()
def batch_decisions():
    """Execute multiple decisions in batch"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        # Get batch requests from request
        data = request.get_json()
        if not data or 'requests' not in data:
            return jsonify({"error": "Batch requests required"}), 400
        
        requests = data['requests']
        if len(requests) > 50:
            return jsonify({"error": "Maximum 50 requests per batch"}), 400
        
        # Add requester information to each request
        for req in requests:
            req['input_data']['requester_id'] = str(current_user_id)
            req['input_data']['batch_timestamp'] = datetime.datetime.now().isoformat()
        
        # Execute batch decisions
        results = orchestrator.execute_batch_decisions(requests)
        
        # Calculate statistics
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        return jsonify({
            "message": "Batch decisions completed",
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
        logger.error(f"Batch decisions error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/challenges', methods=['GET'])
@jwt_required()
def list_challenges():
    """List all challenges in the system"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        # Get query parameters
        status_filter = request.args.get('status', None)
        challenger_filter = request.args.get('challenger', None)
        limit = min(int(request.args.get('limit', 50)), 100)
        
        # Filter challenges
        challenges = list(orchestrator.challenge_history.values())
        
        if status_filter:
            challenges = [c for c in challenges if c.status == status_filter]
        
        if challenger_filter:
            challenges = [c for c in challenges if c.challenger_id == challenger_filter]
        
        # Sort by timestamp (most recent first) and limit
        challenges.sort(key=lambda c: c.timestamp, reverse=True)
        challenges = challenges[:limit]
        
        # Convert to JSON-serializable format
        challenges_list = []
        for challenge in challenges:
            challenge_dict = {
                'challenge_id': challenge.challenge_id,
                'decision_id': challenge.decision_id,
                'challenger_id': challenge.challenger_id,
                'reason': challenge.reason,
                'stake_amount': challenge.stake_amount,
                'timestamp': challenge.timestamp,
                'status': challenge.status
            }
            challenges_list.append(challenge_dict)
        
        return jsonify({
            "challenges": challenges_list,
            "total_count": len(challenges_list),
            "filters_applied": {
                "status": status_filter,
                "challenger": challenger_filter,
                "limit": limit
            },
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"List challenges error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/analytics/performance', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Get performance analytics for all agents"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        # Collect performance data for all agents
        agent_analytics = {}
        total_decisions = 0
        total_challenges = 0
        
        for agent_id in orchestrator.registered_agents.keys():
            performance = orchestrator.get_agent_performance(agent_id)
            agent_analytics[agent_id] = performance
            
            perf_data = performance.get('performance', {})
            total_decisions += perf_data.get('total_decisions', 0)
            total_challenges += perf_data.get('challenged_decisions', 0)
        
        # Calculate platform-wide metrics
        platform_metrics = {
            'total_agents': len(orchestrator.registered_agents),
            'total_decisions': total_decisions,
            'total_challenges': total_challenges,
            'challenge_rate': total_challenges / total_decisions if total_decisions > 0 else 0,
            'active_agents': len([
                agent_id for agent_id, agent in orchestrator.registered_agents.items()
                if agent['active']
            ])
        }
        
        return jsonify({
            "platform_metrics": platform_metrics,
            "agent_analytics": agent_analytics,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Performance analytics error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/transparency/report', methods=['GET'])
@jwt_required()
def get_transparency_report():
    """Get comprehensive transparency report"""
    try:
        orchestrator = get_orchestrator()
        current_user_id = int(get_jwt_identity())
        
        # Get query parameters
        agent_id = request.args.get('agent_id', None)
        time_period = request.args.get('period', '30d')  # 7d, 30d, 90d
        
        # Calculate time range
        from datetime import timedelta
        now = datetime.datetime.now()
        
        if time_period == '7d':
            start_date = now - timedelta(days=7)
        elif time_period == '30d':
            start_date = now - timedelta(days=30)
        elif time_period == '90d':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=30)
        
        # Filter decisions by time period
        recent_decisions = [
            d for d in orchestrator.decision_history.values()
            if datetime.datetime.fromisoformat(d.timestamp) >= start_date
        ]
        
        # Filter by agent if specified
        if agent_id:
            recent_decisions = [d for d in recent_decisions if d.agent_id == agent_id]
        
        # Calculate transparency metrics
        total_decisions = len(recent_decisions)
        decisions_with_proofs = len([d for d in recent_decisions if d.metta_proof])
        decisions_challenged = len([d for d in recent_decisions if d.status == DecisionStatus.CHALLENGED])
        decisions_validated = len([d for d in recent_decisions if d.status == DecisionStatus.VALIDATED])
        
        transparency_metrics = {
            'total_decisions': total_decisions,
            'proof_coverage': decisions_with_proofs / total_decisions if total_decisions > 0 else 0,
            'challenge_rate': decisions_challenged / total_decisions if total_decisions > 0 else 0,
            'validation_rate': decisions_validated / total_decisions if total_decisions > 0 else 0,
            'average_confidence': sum(d.confidence for d in recent_decisions) / total_decisions if total_decisions > 0 else 0
        }
        
        # Decision status breakdown
        status_breakdown = {}
        for status in DecisionStatus:
            count = len([d for d in recent_decisions if d.status == status])
            status_breakdown[status.value] = count
        
        return jsonify({
            "transparency_report": {
                "period": time_period,
                "agent_filter": agent_id,
                "metrics": transparency_metrics,
                "status_breakdown": status_breakdown,
                "generated_at": datetime.datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Transparency report error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/governance/proposals', methods=['POST'])
@jwt_required()
def create_governance_proposal():
    """Create a governance proposal for agent-related decisions"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get proposal data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Proposal data required"}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'proposal_type', 'technical_specs']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create proposal
        proposal = {
            'proposal_id': f"prop_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user_id}",
            'title': data['title'],
            'description': data['description'],
            'proposal_type': data['proposal_type'],
            'technical_specs': data['technical_specs'],
            'proposer_id': str(current_user_id),
            'created_at': datetime.datetime.now().isoformat(),
            'status': 'draft',
            'voting_period': data.get('voting_period', 7),
            'minimum_quorum': data.get('minimum_quorum', 0.1)
        }
        
        # In a real implementation, this would be stored in a governance system
        # For now, we'll just return the proposal
        
        return jsonify({
            "message": "Governance proposal created successfully",
            "proposal": proposal,
            "timestamp": datetime.datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Governance proposal error: {e}")
        return jsonify({"error": str(e)}), 500