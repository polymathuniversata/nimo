"""
Automated Reward Distribution Service for Nimo Platform.
Handles automatic calculation and distribution of rewards for contributions.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from .metta_integration_enhanced import get_metta_service
from models.user import User, Token
from models.contribution import Contribution, Verification

logger = logging.getLogger(__name__)

class RewardType(Enum):
    """Types of rewards that can be distributed"""
    CONTRIBUTION_BASE = "contribution_base"
    VERIFICATION_BONUS = "verification_bonus"
    EVIDENCE_BONUS = "evidence_bonus"
    QUALITY_BONUS = "quality_bonus"
    COMMUNITY_BONUS = "community_bonus"

@dataclass
class RewardCalculation:
    """Result of a reward calculation"""
    user_id: int
    contribution_id: int
    total_amount: int
    breakdown: Dict[str, int]
    confidence_score: float
    reasoning: str
    eligible: bool

@dataclass
class RewardTransaction:
    """A reward transaction record"""
    id: str
    user_id: int
    contribution_id: int
    amount: int
    reward_type: RewardType
    timestamp: float
    metta_confidence: float
    auto_processed: bool

class RewardDistributionService:
    """
    Service for automated reward calculation and distribution.
    Uses MeTTa reasoning for intelligent reward decisions.
    """
    
    def __init__(self):
        """Initialize the reward distribution service"""
        self.metta_service = get_metta_service()
        
        # Reward configuration
        self.config = {
            "base_contribution_reward": 50,
            "max_total_reward": 500,
            "confidence_threshold": 0.6,
            "verification_multiplier": 2.0,
            "evidence_bonus_per_item": 10,
            "quality_score_multiplier": 1.5,
            "community_engagement_bonus": 25,
            "auto_award_enabled": True,
            "manual_review_threshold": 200
        }
        
        # Track processed rewards to avoid duplicates
        self._processed_rewards = set()
    
    def calculate_reward(
        self, 
        contribution: Contribution, 
        include_metta_reasoning: bool = True
    ) -> RewardCalculation:
        """
        Calculate reward for a contribution using MeTTa reasoning.
        
        Args:
            contribution: The contribution to calculate rewards for
            include_metta_reasoning: Whether to use MeTTa for reasoning
            
        Returns:
            RewardCalculation: Complete reward calculation
        """
        try:
            user_id = contribution.user_id
            contribution_id = contribution.id
            
            # Initialize calculation
            breakdown = {
                "base": self.config["base_contribution_reward"],
                "verification_bonus": 0,
                "evidence_bonus": 0,
                "quality_bonus": 0,
                "community_bonus": 0
            }
            
            # Get MeTTa confidence and validation if enabled
            confidence_score = 0.5
            metta_valid = False
            reasoning = "Basic calculation without MeTTa reasoning"
            
            if include_metta_reasoning and self.metta_service.is_connected():
                try:
                    # Sync contribution to MeTTa if needed
                    self._sync_contribution_to_metta(contribution)
                    
                    # Get MeTTa validation
                    validation = self.metta_service.validate_contribution(contribution_id)
                    confidence_score = validation.get('confidence', 0.5)
                    metta_valid = validation.get('valid', False)
                    reasoning = validation.get('explanation', 'MeTTa validation completed')
                    
                    logger.info(f"MeTTa validation for contribution {contribution_id}: valid={metta_valid}, confidence={confidence_score}")
                    
                except Exception as e:
                    logger.warning(f"MeTTa reasoning failed for contribution {contribution_id}: {e}")
                    reasoning = f"MeTTa reasoning failed: {str(e)}"
            
            # Calculate verification bonus
            verification_count = len(contribution.verifications) if hasattr(contribution, 'verifications') else 0
            if verification_count > 0:
                breakdown["verification_bonus"] = int(
                    breakdown["base"] * self.config["verification_multiplier"] * min(verification_count / 2, 1.0)
                )
            
            # Calculate evidence bonus
            evidence_items = []
            if hasattr(contribution, 'evidence') and contribution.evidence:
                if isinstance(contribution.evidence, dict):
                    evidence_items = contribution.evidence.get('items', [])
                elif isinstance(contribution.evidence, list):
                    evidence_items = contribution.evidence
            
            breakdown["evidence_bonus"] = len(evidence_items) * self.config["evidence_bonus_per_item"]
            
            # Quality bonus based on contribution details
            quality_score = self._calculate_quality_score(contribution)
            breakdown["quality_bonus"] = int(breakdown["base"] * quality_score * self.config["quality_score_multiplier"])
            
            # Community engagement bonus
            if self._has_community_engagement(contribution):
                breakdown["community_bonus"] = self.config["community_engagement_bonus"]
            
            # Apply confidence multiplier
            if include_metta_reasoning and confidence_score > 0:
                for key in ["verification_bonus", "evidence_bonus", "quality_bonus"]:
                    breakdown[key] = int(breakdown[key] * confidence_score)
            
            # Calculate total
            total_amount = sum(breakdown.values())
            
            # Apply maximum cap
            if total_amount > self.config["max_total_reward"]:
                scale_factor = self.config["max_total_reward"] / total_amount
                for key in breakdown:
                    breakdown[key] = int(breakdown[key] * scale_factor)
                total_amount = sum(breakdown.values())
            
            # Determine eligibility
            eligible = (
                total_amount > 0 and 
                confidence_score >= self.config["confidence_threshold"] and
                (not include_metta_reasoning or metta_valid or confidence_score > 0.7)
            )
            
            return RewardCalculation(
                user_id=user_id,
                contribution_id=contribution_id,
                total_amount=total_amount,
                breakdown=breakdown,
                confidence_score=confidence_score,
                reasoning=reasoning,
                eligible=eligible
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate reward for contribution {contribution.id}: {e}")
            return RewardCalculation(
                user_id=contribution.user_id,
                contribution_id=contribution.id,
                total_amount=0,
                breakdown={},
                confidence_score=0.0,
                reasoning=f"Calculation failed: {str(e)}",
                eligible=False
            )
    
    def _sync_contribution_to_metta(self, contribution: Contribution):
        """Sync a contribution to MeTTa service"""
        try:
            # Add contribution to MeTTa
            self.metta_service.add_contribution(
                contribution.id,
                contribution.user_id,
                contribution.contribution_type or 'general',
                contribution.title
            )
            
            # Add evidence if available
            if hasattr(contribution, 'evidence') and contribution.evidence:
                evidence_items = []
                if isinstance(contribution.evidence, dict):
                    evidence_items = contribution.evidence.get('items', [])
                elif isinstance(contribution.evidence, list):
                    evidence_items = contribution.evidence
                
                for i, evidence in enumerate(evidence_items):
                    if isinstance(evidence, dict):
                        evidence_type = evidence.get('type', 'link')
                        evidence_url = evidence.get('url', '')
                    else:
                        evidence_type = 'link'
                        evidence_url = str(evidence)
                    
                    if evidence_url:
                        self.metta_service.add_evidence(
                            contribution.id,
                            evidence_type,
                            evidence_url,
                            f"evidence_{contribution.id}_{i}"
                        )
            
            # Add verifications if available
            if hasattr(contribution, 'verifications'):
                for verification in contribution.verifications:
                    self.metta_service.verify_contribution(
                        contribution.id,
                        verification.organization or 'Unknown',
                        verification.id if hasattr(verification, 'id') else None
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to sync contribution {contribution.id} to MeTTa: {e}")
    
    def _calculate_quality_score(self, contribution: Contribution) -> float:
        """Calculate quality score based on contribution properties"""
        score = 0.0
        
        # Title and description quality
        if contribution.title and len(contribution.title) > 10:
            score += 0.2
        
        if contribution.description and len(contribution.description) > 50:
            score += 0.3
        
        # Impact level consideration
        impact_scores = {
            'low': 0.1,
            'medium': 0.3,
            'high': 0.5,
            'very_high': 0.7
        }
        
        impact_level = contribution.impact_level or 'medium'
        score += impact_scores.get(impact_level.lower(), 0.3)
        
        # Contribution type bonus
        type_scores = {
            'code': 0.4,
            'research': 0.5,
            'documentation': 0.3,
            'community': 0.3,
            'education': 0.4,
            'open_source': 0.5
        }
        
        contrib_type = contribution.contribution_type or 'general'
        score += type_scores.get(contrib_type.lower(), 0.2)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _has_community_engagement(self, contribution: Contribution) -> bool:
        """Check if contribution has community engagement indicators"""
        # Check for community-related keywords or types
        community_indicators = [
            'community', 'mentoring', 'teaching', 'volunteer', 
            'outreach', 'workshop', 'presentation', 'collaboration'
        ]
        
        text_content = f"{contribution.title or ''} {contribution.description or ''}".lower()
        
        for indicator in community_indicators:
            if indicator in text_content:
                return True
        
        # Check contribution type
        community_types = ['community', 'education', 'mentoring', 'volunteer']
        contrib_type = (contribution.contribution_type or '').lower()
        
        return contrib_type in community_types
    
    def distribute_reward(
        self, 
        calculation: RewardCalculation,
        auto_process: bool = True,
        commit_to_db: bool = True
    ) -> Optional[RewardTransaction]:
        """
        Distribute reward based on calculation.
        
        Args:
            calculation: The reward calculation
            auto_process: Whether this is an automatic distribution
            commit_to_db: Whether to commit changes to database
            
        Returns:
            RewardTransaction: The transaction record or None if failed
        """
        try:
            if not calculation.eligible:
                logger.info(f"Reward for contribution {calculation.contribution_id} not eligible: {calculation.reasoning}")
                return None
            
            # Check if already processed
            reward_key = f"{calculation.user_id}:{calculation.contribution_id}"
            if reward_key in self._processed_rewards:
                logger.info(f"Reward already processed for {reward_key}")
                return None
            
            # Check if manual review required
            if calculation.total_amount > self.config["manual_review_threshold"] and auto_process:
                logger.info(f"Reward amount {calculation.total_amount} exceeds threshold, requires manual review")
                return None
            
            # Get or create user token record
            from app import db
            
            user = User.query.get(calculation.user_id)
            if not user:
                logger.error(f"User {calculation.user_id} not found")
                return None
            
            # Get or create token balance
            token_record = Token.query.filter_by(user_id=calculation.user_id).first()
            if not token_record:
                token_record = Token(user_id=calculation.user_id, balance=0)
                db.session.add(token_record)
            
            # Update balance
            old_balance = token_record.balance
            token_record.balance += calculation.total_amount
            
            # Update MeTTa service if connected
            if self.metta_service.is_connected():
                try:
                    self.metta_service.set_token_balance(calculation.user_id, token_record.balance)
                except Exception as e:
                    logger.warning(f"Failed to update MeTTa token balance: {e}")
            
            # Create transaction record
            transaction = RewardTransaction(
                id=f"reward_{calculation.contribution_id}_{int(time.time())}",
                user_id=calculation.user_id,
                contribution_id=calculation.contribution_id,
                amount=calculation.total_amount,
                reward_type=RewardType.CONTRIBUTION_BASE,
                timestamp=time.time(),
                metta_confidence=calculation.confidence_score,
                auto_processed=auto_process
            )
            
            # Commit to database if requested
            if commit_to_db:
                db.session.commit()
                logger.info(f"Distributed {calculation.total_amount} tokens to user {calculation.user_id} for contribution {calculation.contribution_id}")
            
            # Mark as processed
            self._processed_rewards.add(reward_key)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to distribute reward: {e}")
            if commit_to_db:
                from app import db
                db.session.rollback()
            return None
    
    def process_contribution_rewards(
        self, 
        contribution_id: int,
        force_reprocess: bool = False
    ) -> Optional[RewardTransaction]:
        """
        Process rewards for a specific contribution.
        
        Args:
            contribution_id: The contribution ID
            force_reprocess: Force reprocessing even if already done
            
        Returns:
            RewardTransaction: The transaction or None
        """
        try:
            contribution = Contribution.query.get(contribution_id)
            if not contribution:
                logger.error(f"Contribution {contribution_id} not found")
                return None
            
            # Check if already processed
            reward_key = f"{contribution.user_id}:{contribution_id}"
            if reward_key in self._processed_rewards and not force_reprocess:
                logger.info(f"Reward already processed for contribution {contribution_id}")
                return None
            
            # Calculate reward
            calculation = self.calculate_reward(contribution, include_metta_reasoning=True)
            
            # Distribute reward
            return self.distribute_reward(calculation, auto_process=True)
            
        except Exception as e:
            logger.error(f"Failed to process contribution rewards for {contribution_id}: {e}")
            return None
    
    def batch_process_pending_rewards(self, max_contributions: int = 50) -> List[RewardTransaction]:
        """
        Process rewards for multiple pending contributions.
        
        Args:
            max_contributions: Maximum number to process in this batch
            
        Returns:
            List of successful transactions
        """
        transactions = []
        
        try:
            # Get contributions that might need reward processing
            # For now, get recent contributions that don't have processed rewards
            contributions = Contribution.query.limit(max_contributions).all()
            
            logger.info(f"Processing rewards for {len(contributions)} contributions")
            
            for contribution in contributions:
                try:
                    transaction = self.process_contribution_rewards(contribution.id)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    logger.error(f"Failed to process reward for contribution {contribution.id}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(transactions)} reward transactions")
            
        except Exception as e:
            logger.error(f"Batch reward processing failed: {e}")
        
        return transactions
    
    def get_reward_preview(
        self, 
        contribution_id: int
    ) -> Dict[str, Any]:
        """
        Get a preview of reward calculation without processing.
        
        Args:
            contribution_id: The contribution ID
            
        Returns:
            dict: Reward preview information
        """
        try:
            contribution = Contribution.query.get(contribution_id)
            if not contribution:
                return {
                    "error": "Contribution not found",
                    "contribution_id": contribution_id
                }
            
            # Calculate reward
            calculation = self.calculate_reward(contribution, include_metta_reasoning=True)
            
            return {
                "contribution_id": contribution_id,
                "user_id": calculation.user_id,
                "eligible": calculation.eligible,
                "total_amount": calculation.total_amount,
                "breakdown": calculation.breakdown,
                "confidence_score": calculation.confidence_score,
                "reasoning": calculation.reasoning,
                "metta_service_active": self.metta_service.is_connected(),
                "service_info": self.metta_service.get_service_info()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate reward preview for {contribution_id}: {e}")
            return {
                "error": str(e),
                "contribution_id": contribution_id
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        try:
            metta_health = self.metta_service.health_check()
            
            return {
                "service_active": True,
                "auto_awards_enabled": self.config["auto_award_enabled"],
                "processed_rewards": len(self._processed_rewards),
                "metta_service": metta_health,
                "config": self.config.copy(),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "service_active": False,
                "error": str(e),
                "timestamp": time.time()
            }

# Global service instance
_reward_service = None

def get_reward_service() -> RewardDistributionService:
    """Get the global reward distribution service instance"""
    global _reward_service
    if _reward_service is None:
        _reward_service = RewardDistributionService()
    return _reward_service