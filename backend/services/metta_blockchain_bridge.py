"""
MeTTa Blockchain Bridge for Nimo Platform

This service bridges the MeTTa reasoning engine with blockchain operations,
enabling verification of contributions and minting of tokens based on
MeTTa's autonomous decisions.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List

from services.metta_reasoning import MeTTaReasoning
from services.blockchain_service import BlockchainService
from models.user import User
from models.contribution import Contribution, Verification
from models.bond import BlockchainTransaction

class MeTTaBlockchainBridge:
    def __init__(self, metta_service: MeTTaReasoning, blockchain_service: BlockchainService):
        """Initialize the bridge between MeTTa and blockchain services"""
        self.metta_service = metta_service
        self.blockchain_service = blockchain_service
    
    async def verify_contribution_on_chain(self, user_id: int, contribution_id: int, 
                                        evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify contribution using MeTTa reasoning and record on blockchain
        
        Args:
            user_id: ID of the user who made the contribution
            contribution_id: ID of the contribution to verify
            evidence: Evidence supporting the contribution
            
        Returns:
            Dict with verification result, tokens awarded, and transaction hashes
        """
        # Get verification decision from MeTTa
        result = self.metta_service.verify_contribution(
            str(user_id), str(contribution_id), evidence
        )
        
        if not result['verified']:
            return {
                'status': 'rejected',
                'reason': result['explanation'],
                'confidence': result['confidence'],
                'metta_proof': result['metta_proof']
            }
        
        # Check for fraud
        fraud_check = self.metta_service.detect_fraudulent_activity(
            str(user_id), str(contribution_id)
        )
        
        if fraud_check['is_fraud']:
            return {
                'status': 'flagged_for_fraud',
                'reason': fraud_check['reason'],
                'confidence': fraud_check['confidence'],
                'metta_proof': result['metta_proof']
            }
        
        # Get user's blockchain address
        user = User.query.get(user_id)
        if not user or not user.blockchain_address:
            return {
                'status': 'error',
                'reason': 'User does not exist or has no blockchain address',
            }
        
        blockchain_address = user.blockchain_address
        
        # Get contribution data
        contribution = Contribution.query.get(contribution_id)
        if not contribution:
            return {
                'status': 'error',
                'reason': 'Contribution not found',
            }
        
        # Execute verification on blockchain
        try:
            # Record verification on blockchain
            tx_hash = await self.blockchain_service.verify_contribution_on_chain(
                contribution_id=contribution_id,
                user_address=blockchain_address,
                tokens_to_award=result['tokens'],
                proof_hash=result['metta_proof']
            )
            
            # Mint tokens for the verified contribution
            token_tx = await self.blockchain_service.mint_tokens_for_contribution(
                to_address=blockchain_address,
                amount=result['tokens'],
                reason=f"Verified contribution: {contribution.title}",
                metta_proof=result['metta_proof']
            )
            
            return {
                'status': 'verified',
                'tokens_awarded': result['tokens'],
                'explanation': result['explanation'],
                'confidence': result['confidence'],
                'verification_tx': tx_hash,
                'token_tx': token_tx,
                'metta_proof': result['metta_proof']
            }
        
        except Exception as e:
            return {
                'status': 'blockchain_error',
                'reason': str(e),
                'metta_proof': result['metta_proof']
            }
    
    async def record_contribution_with_reputation(self, user_id: int, contribution_data: Dict[str, Any],
                                             evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a new contribution, calculate reputation, and trigger verification
        
        Args:
            user_id: ID of the user making the contribution
            contribution_data: Data about the contribution
            evidence: Evidence supporting the contribution
            
        Returns:
            Dict with contribution status and reputation impact
        """
        # Calculate user reputation before and after
        old_reputation = self.metta_service.calculate_reputation(str(user_id))
        
        # Create the contribution in database
        # This would be implemented to use SQLAlchemy models
        
        # Calculate new reputation
        new_reputation = self.metta_service.calculate_reputation(str(user_id))
        reputation_change = new_reputation - old_reputation
        
        # Trigger asynchronous verification
        # This avoids blocking the API response
        asyncio.create_task(self.verify_contribution_on_chain(
            user_id=user_id,
            contribution_id=contribution_data['id'],  # Would be the newly created ID
            evidence=evidence
        ))
        
        return {
            'status': 'recorded',
            'message': 'Contribution recorded and verification in progress',
            'reputation_before': old_reputation,
            'reputation_after': new_reputation,
            'reputation_change': reputation_change
        }
    
    async def link_user_impact_to_bond(self, user_id: int, bond_id: int, 
                                  contribution_ids: List[int]) -> Dict[str, Any]:
        """
        Link user contributions to a diaspora bond for impact verification
        
        Args:
            user_id: ID of the user
            bond_id: ID of the diaspora bond
            contribution_ids: List of contribution IDs to link
            
        Returns:
            Dict with linking status and impact assessment
        """
        # Get total verified impact
        total_impact = 0
        verified_contributions = 0
        
        # Calculate impact from each contribution
        for contrib_id in contribution_ids:
            # Get contribution verification status
            contribution = Contribution.query.get(contrib_id)
            if not contribution:
                continue
                
            if contribution.is_verified:
                verified_contributions += 1
                total_impact += self._calculate_contribution_impact(contribution)
        
        # Only record on chain if there are verified contributions
        if verified_contributions > 0:
            # Record impact link on blockchain
            tx_hash = await self.blockchain_service.link_contributions_to_bond(
                bond_id=bond_id,
                user_id=user_id,
                contribution_count=verified_contributions,
                impact_score=total_impact
            )
            
            return {
                'status': 'linked',
                'verified_contributions': verified_contributions,
                'total_impact': total_impact,
                'transaction_hash': tx_hash
            }
        
        return {
            'status': 'no_verified_contributions',
            'verified_contributions': 0,
            'total_impact': 0
        }
    
    def _calculate_contribution_impact(self, contribution: Contribution) -> float:
        """Calculate the impact score of a contribution"""
        # Use MeTTa to calculate more sophisticated impact
        try:
            impact_score = self.metta_service.space.parse_and_eval(
                f'(CalculateImpactScore "{contribution.id}")'
            )
            if impact_score:
                return float(impact_score)
        except Exception:
            pass
        
        # Fallback to simple mapping
        impact_mapping = {
            "minimal": 1.0,
            "moderate": 2.5,
            "significant": 5.0,
            "transformative": 10.0
        }
        
        # Default to moderate if not specified
        return impact_mapping.get(getattr(contribution, 'impact_level', 'moderate'), 2.5)
    
    async def batch_verify_contributions(self, verification_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch verify multiple contributions for efficiency
        
        Args:
            verification_batch: List of contributions to verify
            
        Returns:
            List of verification results
        """
        # Use MeTTa batch verification
        metta_results = self.metta_service.batch_verify_contributions(verification_batch)
        
        # Process blockchain transactions for verified contributions
        blockchain_results = []
        verified_contributions = []
        
        for i, result in enumerate(metta_results):
            if result.get('verified'):
                verified_contributions.append({
                    'id': result['contribution_id'],
                    'tokens': result.get('tokens', 50),
                    'user_address': verification_batch[i].get('user_address')
                })
        
        # Execute batch blockchain verification if available
        if verified_contributions:
            try:
                blockchain_tx_hashes = await self.blockchain_service.batch_verify_contributions(
                    verified_contributions
                )
                
                # Combine results
                for i, result in enumerate(metta_results):
                    if result.get('verified'):
                        blockchain_results.append({
                            **result,
                            'blockchain_status': 'pending',
                            'transaction_hash': blockchain_tx_hashes[i] if i < len(blockchain_tx_hashes) else None
                        })
                    else:
                        blockchain_results.append({
                            **result,
                            'blockchain_status': 'not_verified'
                        })
            
            except Exception as e:
                # Handle blockchain batch failure
                for result in metta_results:
                    blockchain_results.append({
                        **result,
                        'blockchain_status': 'error',
                        'blockchain_error': str(e)
                    })
        else:
            blockchain_results = metta_results
        
        return blockchain_results
    
    async def get_verification_analytics(self, user_id: Optional[int] = None, 
                                       time_period: str = '30d') -> Dict[str, Any]:
        """
        Get analytics about verification performance
        
        Args:
            user_id: Optional user ID to filter analytics
            time_period: Time period for analytics ('7d', '30d', '90d', 'all')
            
        Returns:
            Dict with verification analytics
        """
        # Get MeTTa verification statistics
        metta_stats = self.metta_service.get_verification_stats()
        
        # Get blockchain network information
        network_info = self.blockchain_service.get_network_info()
        
        # Calculate cost analytics
        cost_estimates = {
            'create_identity': self.blockchain_service.estimate_transaction_cost('create_identity'),
            'add_contribution': self.blockchain_service.estimate_transaction_cost('add_contribution'),
            'verify_contribution': self.blockchain_service.estimate_transaction_cost('verify_contribution')
        }
        
        return {
            'verification_stats': metta_stats,
            'network_info': network_info,
            'cost_estimates': cost_estimates,
            'time_period': time_period,
            'user_id': user_id
        }
    
    async def sync_verification_data(self) -> Dict[str, Any]:
        """
        Synchronize verification data between MeTTa, database, and blockchain
        
        Returns:
            Dict with sync status and statistics
        """
        try:
            # Get pending verifications from database
            # This would query the database for unverified contributions
            
            # Sync blockchain data
            await self.blockchain_service.sync_blockchain_data()
            
            # Update reputation scores for all users
            # This would iterate through users and update their reputation
            
            return {
                'status': 'success',
                'synced_at': self._get_current_timestamp(),
                'items_synced': {
                    'pending_verifications': 0,  # Would be actual count
                    'reputation_updates': 0,     # Would be actual count
                    'blockchain_events': 0       # Would be actual count
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'synced_at': self._get_current_timestamp()
            }
    
    def generate_verification_report(self, contribution_id: int) -> Dict[str, Any]:
        """
        Generate a detailed verification report for a contribution
        
        Args:
            contribution_id: ID of the contribution
            
        Returns:
            Dict with detailed verification report
        """
        # Get MeTTa reasoning trace
        reasoning_trace = self.metta_service.export_reasoning_trace(str(contribution_id))
        
        # Get blockchain transaction status if available
        contribution = Contribution.query.get(contribution_id)
        blockchain_status = None
        
        if contribution and hasattr(contribution, 'verification_tx_hash'):
            blockchain_status = self.blockchain_service.get_transaction_status(
                contribution.verification_tx_hash
            )
        
        # Get cost analysis
        cost_analysis = self.blockchain_service.estimate_transaction_cost('verify_contribution')
        
        return {
            'contribution_id': contribution_id,
            'metta_reasoning': reasoning_trace,
            'blockchain_status': blockchain_status,
            'cost_analysis': cost_analysis,
            'generated_at': self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    async def handle_blockchain_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Handle blockchain events and update local state
        
        Args:
            event_type: Type of blockchain event
            event_data: Event data from blockchain
        """
        try:
            if event_type == 'ContributionVerified':
                # Update local contribution status
                contribution_id = event_data.get('contributionId')
                if contribution_id:
                    contribution = Contribution.query.get(contribution_id)
                    if contribution:
                        contribution.is_verified = True
                        contribution.verification_tx_hash = event_data.get('transactionHash')
                        # Would commit to database here
                        
            elif event_type == 'TokensMinted':
                # Update local token balance
                user_address = event_data.get('to')
                amount = event_data.get('amount')
                if user_address and amount:
                    user = User.query.filter_by(blockchain_address=user_address).first()
                    if user:
                        # Update user's token balance
                        # Would update database here
                        pass
                        
        except Exception as e:
            # Log error but don't fail
            import logging
            logging.error(f"Error handling blockchain event {event_type}: {e}")
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """
        Get status of the MeTTa-Blockchain bridge
        
        Returns:
            Dict with bridge operational status
        """
        metta_status = 'operational' if self.metta_service else 'unavailable'
        blockchain_status = 'operational' if self.blockchain_service and self.blockchain_service.is_connected() else 'unavailable'
        
        return {
            'bridge_status': 'operational' if metta_status == 'operational' and blockchain_status == 'operational' else 'degraded',
            'metta_service': metta_status,
            'blockchain_service': blockchain_status,
            'network': getattr(self.blockchain_service, 'network', 'unknown'),
            'checked_at': self._get_current_timestamp()
        }