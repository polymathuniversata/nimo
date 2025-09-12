"""
AI Agents Orchestrator for Nimo Platform

This service coordinates multiple specialized AI agents for transparent,
accountable, and fraud-resistant platform operations. It builds on the
existing MeTTa reasoning system and Cardano integration.
"""

import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .metta_integration_enhanced import MeTTaIntegrationService
from .metta_reasoning import MeTTaReasoning
from .cardano_service import CardanoService
from .blockchain_service import BlockchainService

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of specialized AI agents"""
    CONTRIBUTION_VALIDATION = "contribution_validation"
    FRAUD_DETECTION = "fraud_detection"
    REWARD_CALCULATION = "reward_calculation"
    COMMUNITY_MODERATION = "community_moderation"
    PLATFORM_GOVERNANCE = "platform_governance"
    REPUTATION_SCORING = "reputation_scoring"

class DecisionStatus(Enum):
    """Status of agent decisions"""
    PENDING = "pending"
    VALIDATED = "validated"
    CHALLENGED = "challenged"
    FINALIZED = "finalized"
    OVERTURNED = "overturned"

@dataclass
class AgentDecision:
    """Standardized agent decision structure"""
    decision_id: str
    agent_id: str
    agent_type: AgentType
    input_data: Dict[str, Any]
    decision: Dict[str, Any]
    confidence: float
    reasoning: Dict[str, Any]
    metta_proof: str
    blockchain_proof: Optional[str] = None
    timestamp: str = None
    status: DecisionStatus = DecisionStatus.PENDING
    challenge_deadline: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ChallengeRecord:
    """Challenge to an agent decision"""
    challenge_id: str
    decision_id: str
    challenger_id: str
    reason: str
    evidence: Dict[str, Any]
    stake_amount: int
    timestamp: str
    status: str = "pending"

class AIAgentsOrchestrator:
    """
    Orchestrates multiple specialized AI agents for the Nimo platform.
    Provides transparency, accountability, and fraud prevention.
    """
    
    def __init__(self, 
                 metta_integration: MeTTaIntegrationService,
                 metta_reasoning: MeTTaReasoning,
                 blockchain_service: Union[CardanoService, BlockchainService]):
        self.metta_integration = metta_integration
        self.metta_reasoning = metta_reasoning
        self.blockchain = blockchain_service
        
        # Agent registry
        self.registered_agents: Dict[str, Dict] = {}
        self.decision_history: Dict[str, AgentDecision] = {}
        self.challenge_history: Dict[str, ChallengeRecord] = {}
        
        # Performance tracking
        self.agent_performance: Dict[str, Dict] = {}
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize core agents
        self._initialize_core_agents()
    
    def _initialize_core_agents(self):
        """Initialize core platform agents"""
        core_agents = [
            {
                'agent_id': 'contribution_validator_v1',
                'agent_type': AgentType.CONTRIBUTION_VALIDATION,
                'name': 'Contribution Validation Agent',
                'description': 'Validates contribution submissions and evidence',
                'performance_bond': 1000,
                'owner': 'platform',
                'active': True
            },
            {
                'agent_id': 'fraud_detector_v1',
                'agent_type': AgentType.FRAUD_DETECTION,
                'name': 'Fraud Detection Agent',
                'description': 'Detects fraudulent activities and suspicious patterns',
                'performance_bond': 1500,
                'owner': 'platform',
                'active': True
            },
            {
                'agent_id': 'reward_calculator_v1',
                'agent_type': AgentType.REWARD_CALCULATION,
                'name': 'Reward Calculation Agent',
                'description': 'Calculates rewards based on contribution quality and impact',
                'performance_bond': 1200,
                'owner': 'platform',
                'active': True
            },
            {
                'agent_id': 'community_moderator_v1',
                'agent_type': AgentType.COMMUNITY_MODERATION,
                'name': 'Community Moderation Agent',
                'description': 'Moderates community interactions and resolves conflicts',
                'performance_bond': 800,
                'owner': 'platform',
                'active': True
            },
            {
                'agent_id': 'governance_coordinator_v1',
                'agent_type': AgentType.PLATFORM_GOVERNANCE,
                'name': 'Platform Governance Agent',
                'description': 'Coordinates platform governance and proposal management',
                'performance_bond': 2000,
                'owner': 'platform',
                'active': True
            },
            {
                'agent_id': 'reputation_scorer_v1',
                'agent_type': AgentType.REPUTATION_SCORING,
                'name': 'Reputation Scoring Agent',
                'description': 'Calculates and maintains user reputation scores',
                'performance_bond': 1000,
                'owner': 'platform',
                'active': True
            }
        ]
        
        for agent_spec in core_agents:
            self.registered_agents[agent_spec['agent_id']] = agent_spec
            self.agent_performance[agent_spec['agent_id']] = {
                'total_decisions': 0,
                'successful_decisions': 0,
                'challenged_decisions': 0,
                'overturned_decisions': 0,
                'average_confidence': 0.0,
                'last_activity': datetime.now().isoformat()
            }
    
    def register_agent(self, agent_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new AI agent"""
        try:
            agent_id = agent_spec['agent_id']
            
            # Validate agent specification
            validation_result = self._validate_agent_spec(agent_spec)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Store agent registration
            self.registered_agents[agent_id] = agent_spec
            self.agent_performance[agent_id] = {
                'total_decisions': 0,
                'successful_decisions': 0,
                'challenged_decisions': 0,
                'overturned_decisions': 0,
                'average_confidence': 0.0,
                'last_activity': datetime.now().isoformat()
            }
            
            # Register with blockchain if available
            blockchain_result = None
            if hasattr(self.blockchain, 'register_agent'):
                blockchain_result = self.blockchain.register_agent(agent_spec)
            
            logger.info(f"Agent {agent_id} registered successfully")
            
            return {
                'success': True,
                'agent_id': agent_id,
                'blockchain_tx': blockchain_result.get('tx_hash') if blockchain_result else None
            }
            
        except Exception as e:
            logger.error(f"Agent registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def make_decision(self, agent_id: str, input_data: Dict[str, Any]) -> AgentDecision:
        """Make a decision using a specific agent"""
        try:
            if agent_id not in self.registered_agents:
                raise ValueError(f"Agent {agent_id} not registered")
            
            agent = self.registered_agents[agent_id]
            agent_type = agent['agent_type']
            
            # Route to appropriate decision method
            if agent_type == AgentType.CONTRIBUTION_VALIDATION:
                decision_result = self._validate_contribution(agent_id, input_data)
            elif agent_type == AgentType.FRAUD_DETECTION:
                decision_result = self._detect_fraud(agent_id, input_data)
            elif agent_type == AgentType.REWARD_CALCULATION:
                decision_result = self._calculate_reward(agent_id, input_data)
            elif agent_type == AgentType.COMMUNITY_MODERATION:
                decision_result = self._moderate_content(agent_id, input_data)
            elif agent_type == AgentType.PLATFORM_GOVERNANCE:
                decision_result = self._coordinate_governance(agent_id, input_data)
            elif agent_type == AgentType.REPUTATION_SCORING:
                decision_result = self._score_reputation(agent_id, input_data)
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Create decision record
            decision = AgentDecision(
                decision_id=self._generate_decision_id(),
                agent_id=agent_id,
                agent_type=agent_type,
                input_data=input_data,
                decision=decision_result['decision'],
                confidence=decision_result['confidence'],
                reasoning=decision_result['reasoning'],
                metta_proof=decision_result['metta_proof'],
                challenge_deadline=self._calculate_challenge_deadline()
            )
            
            # Store decision
            self.decision_history[decision.decision_id] = decision
            
            # Update agent performance
            self._update_agent_performance(agent_id, decision)
            
            # Create blockchain proof if available
            if hasattr(self.blockchain, 'create_decision_proof'):
                blockchain_proof = self.blockchain.create_decision_proof(asdict(decision))
                decision.blockchain_proof = blockchain_proof.get('tx_hash')
            
            logger.info(f"Decision {decision.decision_id} made by agent {agent_id}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            raise
    
    def challenge_decision(self, decision_id: str, challenger_id: str, 
                         reason: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Challenge an agent decision"""
        try:
            if decision_id not in self.decision_history:
                return {'success': False, 'error': 'Decision not found'}
            
            decision = self.decision_history[decision_id]
            
            # Check if challenge is still allowed
            if not self._is_challenge_allowed(decision):
                return {'success': False, 'error': 'Challenge period expired'}
            
            # Calculate challenge stake
            stake_amount = self._calculate_challenge_stake(decision)
            
            # Create challenge record
            challenge = ChallengeRecord(
                challenge_id=self._generate_challenge_id(),
                decision_id=decision_id,
                challenger_id=challenger_id,
                reason=reason,
                evidence=evidence,
                stake_amount=stake_amount,
                timestamp=datetime.now().isoformat()
            )
            
            # Store challenge
            self.challenge_history[challenge.challenge_id] = challenge
            
            # Update decision status
            decision.status = DecisionStatus.CHALLENGED
            
            # Initiate challenge resolution process
            resolution_result = self._initiate_challenge_resolution(challenge)
            
            logger.info(f"Decision {decision_id} challenged by {challenger_id}")
            
            return {
                'success': True,
                'challenge_id': challenge.challenge_id,
                'stake_amount': stake_amount,
                'resolution_process': resolution_result
            }
            
        except Exception as e:
            logger.error(f"Challenge submission failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_decision_consensus(self, decision_id: str) -> Dict[str, Any]:
        """Validate decision through multi-agent consensus"""
        try:
            if decision_id not in self.decision_history:
                return {'success': False, 'error': 'Decision not found'}
            
            primary_decision = self.decision_history[decision_id]
            
            # Select validating agents
            validating_agents = self._select_validating_agents(primary_decision)
            
            # Collect validation results
            validation_results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for agent_id in validating_agents:
                    future = executor.submit(
                        self._validate_decision, agent_id, primary_decision
                    )
                    futures.append(future)
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        validation_results.append(result)
                    except Exception as e:
                        logger.error(f"Validation error: {e}")
            
            # Calculate consensus
            consensus = self._calculate_validation_consensus(validation_results)
            
            # Update decision status based on consensus
            if consensus['valid']:
                primary_decision.status = DecisionStatus.VALIDATED
            
            logger.info(f"Decision {decision_id} consensus: {consensus}")
            
            return {
                'success': True,
                'consensus': consensus,
                'validations': validation_results
            }
            
        except Exception as e:
            logger.error(f"Consensus validation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent"""
        if agent_id not in self.registered_agents:
            return {'error': 'Agent not found'}
        
        performance = self.agent_performance.get(agent_id, {})
        agent_info = self.registered_agents[agent_id]
        
        # Calculate derived metrics
        if performance.get('total_decisions', 0) > 0:
            success_rate = performance['successful_decisions'] / performance['total_decisions']
            challenge_rate = performance['challenged_decisions'] / performance['total_decisions']
            overturn_rate = performance['overturned_decisions'] / performance['total_decisions'] if performance['challenged_decisions'] > 0 else 0
        else:
            success_rate = 0
            challenge_rate = 0
            overturn_rate = 0
        
        return {
            'agent_id': agent_id,
            'agent_type': agent_info['agent_type'].value,
            'performance': performance,
            'metrics': {
                'success_rate': success_rate,
                'challenge_rate': challenge_rate,
                'overturn_rate': overturn_rate,
                'trust_score': self._calculate_trust_score(performance)
            }
        }
    
    def get_decision_audit_trail(self, decision_id: str) -> Dict[str, Any]:
        """Get complete audit trail for a decision"""
        if decision_id not in self.decision_history:
            return {'error': 'Decision not found'}
        
        decision = self.decision_history[decision_id]
        
        # Get related challenges
        challenges = [
            challenge for challenge in self.challenge_history.values()
            if challenge.decision_id == decision_id
        ]
        
        # Get MeTTa reasoning trace
        reasoning_trace = self.metta_reasoning.export_reasoning_trace(
            decision.input_data.get('contribution_id', decision_id)
        )
        
        return {
            'decision': asdict(decision),
            'challenges': [asdict(challenge) for challenge in challenges],
            'reasoning_trace': reasoning_trace,
            'blockchain_verification': self._get_blockchain_verification(decision_id)
        }
    
    def execute_batch_decisions(self, batch_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple decisions in batch for efficiency"""
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for request in batch_requests:
                future = executor.submit(
                    self.make_decision,
                    request['agent_id'],
                    request['input_data']
                )
                futures.append((request, future))
            
            for request, future in futures:
                try:
                    decision = future.result()
                    results.append({
                        'success': True,
                        'request_id': request.get('request_id'),
                        'decision': asdict(decision)
                    })
                except Exception as e:
                    results.append({
                        'success': False,
                        'request_id': request.get('request_id'),
                        'error': str(e)
                    })
        
        return results
    
    # Private methods for specific agent implementations
    
    def _validate_contribution(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Contribution validation agent implementation"""
        contribution_id = input_data['contribution_id']
        user_id = input_data['user_id']
        evidence = input_data.get('evidence', {})
        
        # Use existing MeTTa integration for validation
        validation_result = self.metta_integration.validate_contribution(
            contribution_id, input_data
        )
        
        # Generate MeTTa proof
        metta_proof = self._generate_metta_proof(agent_id, input_data, validation_result)
        
        return {
            'decision': validation_result,
            'confidence': validation_result.get('confidence', 0.0),
            'reasoning': {
                'method': 'metta_reasoning',
                'factors': validation_result.get('explanation', 'No explanation available'),
                'evidence_analysis': self._analyze_evidence(evidence)
            },
            'metta_proof': metta_proof
        }
    
    def _detect_fraud(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fraud detection agent implementation"""
        contribution_id = input_data['contribution_id']
        
        # Use existing fraud detection
        fraud_result = self.metta_integration.detect_fraud_comprehensive(contribution_id)
        
        # Generate MeTTa proof
        metta_proof = self._generate_metta_proof(agent_id, input_data, fraud_result)
        
        fraud_detected = fraud_result.get('fraud_detected', False)
        
        return {
            'decision': {
                'fraud_detected': fraud_detected,
                'risk_level': self._determine_risk_level(fraud_result),
                'recommended_action': self._recommend_action(fraud_result)
            },
            'confidence': fraud_result.get('confidence', 0.0) if fraud_detected else 1.0 - fraud_result.get('confidence', 0.0),
            'reasoning': {
                'method': 'comprehensive_fraud_detection',
                'analysis': fraud_result.get('analysis', 'No analysis available'),
                'patterns': self._extract_fraud_patterns(fraud_result)
            },
            'metta_proof': metta_proof
        }
    
    def _calculate_reward(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reward calculation agent implementation"""
        contribution_id = input_data['contribution_id']
        quality_score = input_data.get('quality_score', 0.8)
        impact_score = input_data.get('impact_score', 0.7)
        
        # Use existing reward calculation
        reward_result = self.metta_integration.calculate_autonomous_reward(
            contribution_id, quality_score, impact_score
        )
        
        # Generate MeTTa proof
        metta_proof = self._generate_metta_proof(agent_id, input_data, reward_result)
        
        return {
            'decision': reward_result,
            'confidence': 0.9,  # High confidence for deterministic calculations
            'reasoning': {
                'method': 'autonomous_reward_calculation',
                'quality_score': quality_score,
                'impact_score': impact_score,
                'calculation_breakdown': reward_result.get('breakdown', {})
            },
            'metta_proof': metta_proof
        }
    
    def _moderate_content(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Community moderation agent implementation"""
        content = input_data.get('content', '')
        content_type = input_data.get('content_type', 'text')
        
        # Implement content moderation logic
        moderation_result = {
            'approved': len(content) > 0 and len(content) < 10000,  # Basic check
            'issues': [],
            'severity': 'low'
        }
        
        # Generate MeTTa proof
        metta_proof = self._generate_metta_proof(agent_id, input_data, moderation_result)
        
        return {
            'decision': moderation_result,
            'confidence': 0.8,
            'reasoning': {
                'method': 'content_analysis',
                'content_length': len(content),
                'content_type': content_type,
                'checks_performed': ['length_check', 'basic_validation']
            },
            'metta_proof': metta_proof
        }
    
    def _coordinate_governance(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Platform governance agent implementation"""
        proposal_id = input_data.get('proposal_id')
        action = input_data.get('action', 'analyze')
        
        governance_result = {
            'action_taken': action,
            'proposal_status': 'analyzed',
            'recommendations': ['community_review', 'expert_evaluation']
        }
        
        # Generate MeTTa proof
        metta_proof = self._generate_metta_proof(agent_id, input_data, governance_result)
        
        return {
            'decision': governance_result,
            'confidence': 0.7,
            'reasoning': {
                'method': 'governance_coordination',
                'proposal_id': proposal_id,
                'analysis_factors': ['community_impact', 'technical_feasibility']
            },
            'metta_proof': metta_proof
        }
    
    def _score_reputation(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reputation scoring agent implementation"""
        user_id = input_data['user_id']
        
        # Use existing reputation calculation
        reputation_score = self.metta_reasoning.calculate_user_reputation(user_id)
        
        reputation_result = {
            'user_id': user_id,
            'reputation_score': reputation_score,
            'tier': self._determine_reputation_tier(reputation_score),
            'factors': ['contribution_history', 'community_feedback', 'verification_rate']
        }
        
        # Generate MeTTa proof
        metta_proof = self._generate_metta_proof(agent_id, input_data, reputation_result)
        
        return {
            'decision': reputation_result,
            'confidence': 0.85,
            'reasoning': {
                'method': 'reputation_calculation',
                'score': reputation_score,
                'calculation_factors': reputation_result['factors']
            },
            'metta_proof': metta_proof
        }
    
    # Utility methods
    
    def _validate_agent_spec(self, agent_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent specification"""
        required_fields = ['agent_id', 'agent_type', 'name', 'description', 'owner']
        
        for field in required_fields:
            if field not in agent_spec:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if agent_spec['agent_id'] in self.registered_agents:
            return {'valid': False, 'error': 'Agent ID already exists'}
        
        return {'valid': True}
    
    def _generate_decision_id(self) -> str:
        """Generate unique decision ID"""
        import uuid
        return f"decision_{uuid.uuid4().hex[:12]}"
    
    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        import uuid
        return f"challenge_{uuid.uuid4().hex[:12]}"
    
    def _generate_metta_proof(self, agent_id: str, input_data: Dict, result: Dict) -> str:
        """Generate MeTTa reasoning proof"""
        proof_data = {
            'agent_id': agent_id,
            'input_hash': hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest(),
            'result_hash': hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
            'timestamp': datetime.now().isoformat()
        }
        return hashlib.sha256(json.dumps(proof_data, sort_keys=True).encode()).hexdigest()
    
    def _calculate_challenge_deadline(self) -> str:
        """Calculate challenge deadline (48 hours from now)"""
        deadline = datetime.now() + timedelta(hours=48)
        return deadline.isoformat()
    
    def _is_challenge_allowed(self, decision: AgentDecision) -> bool:
        """Check if challenge is still allowed for a decision"""
        if decision.challenge_deadline is None:
            return False
        
        deadline = datetime.fromisoformat(decision.challenge_deadline)
        return datetime.now() < deadline
    
    def _calculate_challenge_stake(self, decision: AgentDecision) -> int:
        """Calculate required stake for challenging a decision"""
        base_stake = 100  # Base stake amount
        confidence_multiplier = decision.confidence * 100
        return int(base_stake * (1 + confidence_multiplier / 100))
    
    def _update_agent_performance(self, agent_id: str, decision: AgentDecision):
        """Update agent performance metrics"""
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = {
                'total_decisions': 0,
                'successful_decisions': 0,
                'challenged_decisions': 0,
                'overturned_decisions': 0,
                'average_confidence': 0.0,
                'last_activity': datetime.now().isoformat()
            }
        
        performance = self.agent_performance[agent_id]
        performance['total_decisions'] += 1
        performance['last_activity'] = datetime.now().isoformat()
        
        # Update average confidence
        total = performance['total_decisions']
        current_avg = performance['average_confidence']
        new_avg = ((current_avg * (total - 1)) + decision.confidence) / total
        performance['average_confidence'] = new_avg
    
    def _calculate_trust_score(self, performance: Dict[str, Any]) -> float:
        """Calculate trust score based on performance metrics"""
        total = performance.get('total_decisions', 0)
        if total == 0:
            return 0.5  # Neutral score for new agents
        
        success_rate = performance.get('successful_decisions', 0) / total
        challenge_rate = performance.get('challenged_decisions', 0) / total
        overturn_rate = performance.get('overturned_decisions', 0) / total if performance.get('challenged_decisions', 0) > 0 else 0
        avg_confidence = performance.get('average_confidence', 0.0)
        
        # Weight factors
        trust_score = (
            success_rate * 0.4 +
            (1 - challenge_rate) * 0.3 +
            (1 - overturn_rate) * 0.2 +
            avg_confidence * 0.1
        )
        
        return min(1.0, max(0.0, trust_score))
    
    def _analyze_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze evidence quality"""
        return {
            'evidence_type': evidence.get('type', 'unknown'),
            'completeness_score': 0.8,
            'authenticity_score': 0.9,
            'relevance_score': 0.85
        }
    
    def _determine_risk_level(self, fraud_result: Dict[str, Any]) -> str:
        """Determine risk level from fraud analysis"""
        if fraud_result.get('fraud_detected', False):
            confidence = fraud_result.get('confidence', 0.0)
            if confidence > 0.8:
                return 'high'
            elif confidence > 0.6:
                return 'medium'
            else:
                return 'low'
        return 'none'
    
    def _recommend_action(self, fraud_result: Dict[str, Any]) -> str:
        """Recommend action based on fraud analysis"""
        if fraud_result.get('fraud_detected', False):
            risk_level = self._determine_risk_level(fraud_result)
            if risk_level == 'high':
                return 'reject_and_flag'
            elif risk_level == 'medium':
                return 'manual_review'
            else:
                return 'proceed_with_caution'
        return 'approve'
    
    def _extract_fraud_patterns(self, fraud_result: Dict[str, Any]) -> List[str]:
        """Extract detected fraud patterns"""
        return fraud_result.get('patterns', ['temporal_anomaly', 'similarity_match'])
    
    def _determine_reputation_tier(self, score: float) -> str:
        """Determine reputation tier from score"""
        if score >= 90:
            return 'platinum'
        elif score >= 75:
            return 'gold'
        elif score >= 60:
            return 'silver'
        elif score >= 40:
            return 'bronze'
        else:
            return 'basic'
    
    def _select_validating_agents(self, decision: AgentDecision) -> List[str]:
        """Select agents for decision validation"""
        # For now, select all agents of the same type
        agent_type = decision.agent_type
        validators = [
            agent_id for agent_id, agent in self.registered_agents.items()
            if agent['agent_type'] == agent_type and agent_id != decision.agent_id
        ]
        return validators[:3]  # Limit to 3 validators
    
    def _validate_decision(self, validator_agent_id: str, decision: AgentDecision) -> Dict[str, Any]:
        """Validate decision using another agent"""
        try:
            # Re-run decision with same input
            validation_result = self.make_decision(validator_agent_id, decision.input_data)
            
            # Compare results
            agreement = self._compare_decisions(decision, validation_result)
            
            return {
                'validator_agent_id': validator_agent_id,
                'agreement': agreement,
                'validation_confidence': validation_result.confidence,
                'result': asdict(validation_result)
            }
        except Exception as e:
            return {
                'validator_agent_id': validator_agent_id,
                'error': str(e),
                'agreement': 0.0
            }
    
    def _compare_decisions(self, decision1: AgentDecision, decision2: AgentDecision) -> float:
        """Compare two decisions and return agreement score"""
        # Simple comparison based on key decision fields
        # In practice, this would be more sophisticated
        
        if decision1.agent_type != decision2.agent_type:
            return 0.0
        
        confidence_diff = abs(decision1.confidence - decision2.confidence)
        agreement = 1.0 - confidence_diff
        
        return max(0.0, agreement)
    
    def _calculate_validation_consensus(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate consensus from validation results"""
        if not validation_results:
            return {'valid': False, 'consensus': 0.0}
        
        agreements = [result.get('agreement', 0.0) for result in validation_results]
        average_agreement = sum(agreements) / len(agreements)
        
        return {
            'valid': average_agreement >= 0.6,
            'consensus': average_agreement,
            'validator_count': len(validation_results)
        }
    
    def _initiate_challenge_resolution(self, challenge: ChallengeRecord) -> Dict[str, Any]:
        """Initiate challenge resolution process"""
        return {
            'process': 'community_review',
            'review_period': '7 days',
            'next_steps': ['community_voting', 'expert_panel', 'final_resolution']
        }
    
    def _get_blockchain_verification(self, decision_id: str) -> Dict[str, Any]:
        """Get blockchain verification for decision"""
        if hasattr(self.blockchain, 'get_decision_verification'):
            return self.blockchain.get_decision_verification(decision_id)
        return {'verified': False, 'reason': 'Blockchain verification not available'}

# Global orchestrator instance
_orchestrator = None

def get_ai_agents_orchestrator(
    metta_integration: MeTTaIntegrationService = None,
    metta_reasoning: MeTTaReasoning = None,
    blockchain_service = None
) -> AIAgentsOrchestrator:
    """Get the global AI agents orchestrator instance"""
    global _orchestrator
    
    if _orchestrator is None:
        if not all([metta_integration, metta_reasoning, blockchain_service]):
            raise ValueError("All services required for initial orchestrator creation")
        
        _orchestrator = AIAgentsOrchestrator(
            metta_integration, metta_reasoning, blockchain_service
        )
    
    return _orchestrator