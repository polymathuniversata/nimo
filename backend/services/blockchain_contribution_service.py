"""
Blockchain-First Contribution Service

Handles contribution management operations using blockchain as the primary data source
with database caching for performance optimization.
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import current_app

from app import db
from models.contribution import Contribution, Verification
from models.user import User
from services.blockchain_service import BlockchainService
from services.ipfs_service import IPFSService
from services.metta_integration_enhanced import get_metta_service

class BlockchainContributionService:
    """Service for managing contributions on blockchain with database caching"""

    def __init__(self):
        """Initialize blockchain contribution service"""
        self.blockchain_service = BlockchainService()
        self.ipfs_service = IPFSService()
        self.cache_enabled = True

    def create_contribution_on_chain(self, user_id: int, contribution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contribution on blockchain"""
        try:
            # Validate required fields
            if not contribution_data.get('title'):
                return self._error_response("Title is required")

            # Get user
            user = User.query.get(user_id)
            if not user:
                return self._error_response("User not found")

            # Prepare contribution metadata
            metadata = {
                'title': contribution_data['title'],
                'description': contribution_data.get('description'),
                'contribution_type': contribution_data.get('contribution_type', 'other'),
                'impact_level': contribution_data.get('impact_level', 'moderate'),
                'evidence': contribution_data.get('evidence', {}),
                'user_id': user_id,
                'user_email': user.email,
                'created_at': datetime.utcnow().isoformat(),
                'version': '1.0'
            }

            # Store metadata on IPFS
            ipfs_hash = self.ipfs_service.store_json(metadata)
            if not ipfs_hash:
                return self._error_response("Failed to store contribution metadata on IPFS")

            # Create contribution on blockchain
            contribution_type = contribution_data.get('contribution_type', 'other')
            description = contribution_data.get('description', '')
            evidence_uri = f"ipfs://{ipfs_hash}"

            # Generate MeTTa proof for the contribution
            metta_proof = self._generate_metta_proof(contribution_data)

            tx_hash = self.blockchain_service.add_contribution_on_chain(
                contribution_type=contribution_type,
                description=description,
                evidence_uri=evidence_uri,
                metta_hash=metta_proof
            )

            if not tx_hash:
                return self._error_response("Failed to create contribution on blockchain")

            # Create local cache record
            new_contribution = Contribution(
                user_id=user_id,
                title=contribution_data['title'],
                description=contribution_data.get('description'),
                contribution_type=contribution_type,
                impact_level=contribution_data.get('impact_level', 'moderate'),
                evidence=contribution_data.get('evidence')
            )

            db.session.add(new_contribution)
            db.session.commit()

            return {
                'success': True,
                'contribution_id': new_contribution.id,
                'tx_hash': tx_hash,
                'ipfs_hash': ipfs_hash,
                'metta_proof': metta_proof,
                'message': 'Contribution created successfully on blockchain'
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating contribution on chain: {e}")
            return self._error_response(str(e))

    def get_contributions_from_chain(self, user_id: int, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get contributions from blockchain with database cache"""
        try:
            filters = filters or {}

            # Try database cache first
            if self.cache_enabled:
                query = Contribution.query.filter_by(user_id=user_id)

                # Apply filters
                if filters.get('verified') is not None:
                    if filters['verified']:
                        query = query.filter(Contribution.verifications.any())
                    else:
                        query = query.filter(~Contribution.verifications.any())

                if filters.get('contribution_type'):
                    query = query.filter_by(contribution_type=filters['contribution_type'])

                if filters.get('impact_level'):
                    query = query.filter_by(impact_level=filters['impact_level'])

                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        Contribution.title.ilike(search_term) |
                        Contribution.description.ilike(search_term)
                    )

                # Apply sorting
                sort_by = filters.get('sort_by', 'created_at')
                sort_order = filters.get('sort_order', 'desc')

                if sort_by == 'created_at':
                    sort_column = Contribution.created_at
                elif sort_by == 'title':
                    sort_column = Contribution.title
                else:
                    sort_column = Contribution.created_at

                if sort_order.lower() == 'asc':
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())

                # Apply pagination
                page = filters.get('page', 1)
                per_page = min(filters.get('per_page', 10), 100)

                pagination = query.paginate(page=page, per_page=per_page, error_out=False)

                contributions = [contrib.to_dict() for contrib in pagination.items]

                return {
                    'success': True,
                    'contributions': contributions,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev
                    },
                    'source': 'cache'
                }

            return self._error_response("Cache disabled and blockchain query not implemented")

        except Exception as e:
            current_app.logger.error(f"Error getting contributions from chain: {e}")
            return self._error_response(str(e))

    def verify_contribution_on_chain(self, contribution_id: int, verifier_user_id: int) -> Dict[str, Any]:
        """Verify contribution using MeTTa reasoning and record on blockchain"""
        try:
            # Get contribution
            contribution = Contribution.query.get(contribution_id)
            if not contribution:
                return self._error_response("Contribution not found")

            # Get verifier
            verifier = User.query.get(verifier_user_id)
            if not verifier:
                return self._error_response("Verifier not found")

            # Use MeTTa service for verification
            metta_service = get_metta_service()

            evidence_dict = contribution.evidence_dict or {}
            contribution_data = {
                "user_id": contribution.user_id,
                "category": contribution.contribution_type or 'other',
                "title": contribution.title,
                "evidence": [
                    {
                        "type": evidence_dict.get('type', 'url'),
                        "url": evidence_dict.get('url', ''),
                        "id": f"evidence-{contribution_id}"
                    }
                ] if evidence_dict.get('url') else []
            }

            # Validate with MeTTa
            validation_result = metta_service.validate_contribution(
                contribution_id=str(contribution_id),
                contribution_data=contribution_data
            )

            if not validation_result.get('status') == 'verified':
                return {
                    'success': False,
                    'error': 'Contribution failed MeTTa validation',
                    'reason': validation_result.get('reason', 'Unknown')
                }

            # Calculate token award
            token_award = validation_result.get('token_award', 0)

            # Verify on blockchain
            tx_hash = self.blockchain_service.verify_contribution_on_chain(
                contribution_id=contribution_id,
                tokens_to_award=token_award
            )

            if not tx_hash:
                return self._error_response("Failed to verify contribution on blockchain")

            # Create verification record
            verification = Verification(
                contribution_id=contribution_id,
                organization='Nimo Platform',
                verifier_name=verifier.name,
                comments=validation_result.get('explanation', 'Verified using MeTTa reasoning')
            )

            db.session.add(verification)
            db.session.commit()

            return {
                'success': True,
                'verification_id': verification.id,
                'tx_hash': tx_hash,
                'token_award': token_award,
                'message': 'Contribution verified successfully on blockchain'
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error verifying contribution on chain: {e}")
            return self._error_response(str(e))

    def get_contribution_analytics(self, user_id: int, time_period: str = '30d') -> Dict[str, Any]:
        """Get contribution analytics from blockchain data"""
        try:
            # Get analytics from database cache
            query = Contribution.query.filter_by(user_id=user_id)

            # Apply time filter
            if time_period != 'all':
                import datetime
                days_map = {'7d': 7, '30d': 30, '90d': 90}
                days = days_map.get(time_period, 30)
                cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
                query = query.filter(Contribution.created_at >= cutoff_date)

            contributions = query.all()

            # Calculate analytics
            total_contributions = len(contributions)
            verified_contributions = len([c for c in contributions if c.verifications])
            verification_rate = (verified_contributions / total_contributions) if total_contributions > 0 else 0

            # Group by type and impact
            by_type = {}
            by_impact = {}

            for contrib in contributions:
                contrib_type = contrib.contribution_type or 'other'
                impact_level = contrib.impact_level or 'moderate'

                by_type[contrib_type] = by_type.get(contrib_type, 0) + 1
                by_impact[impact_level] = by_impact.get(impact_level, 0) + 1

            return {
                'success': True,
                'analytics': {
                    'summary': {
                        'total_contributions': total_contributions,
                        'verified_contributions': verified_contributions,
                        'verification_rate': round(verification_rate, 3),
                        'time_period': time_period
                    },
                    'by_type': by_type,
                    'by_impact': by_impact,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            current_app.logger.error(f"Error getting contribution analytics: {e}")
            return self._error_response(str(e))

    def batch_verify_contributions(self, contribution_ids: List[int], verifier_user_id: int) -> Dict[str, Any]:
        """Batch verify multiple contributions for efficiency"""
        try:
            results = []

            for contrib_id in contribution_ids:
                result = self.verify_contribution_on_chain(contrib_id, verifier_user_id)
                results.append({
                    'contribution_id': contrib_id,
                    'success': result.get('success', False),
                    'error': result.get('error'),
                    'tx_hash': result.get('tx_hash'),
                    'token_award': result.get('token_award', 0)
                })

            successful = sum(1 for r in results if r['success'])

            return {
                'success': True,
                'results': results,
                'total_processed': len(contribution_ids),
                'total_successful': successful,
                'total_failed': len(contribution_ids) - successful
            }

        except Exception as e:
            current_app.logger.error(f"Error in batch verification: {e}")
            return self._error_response(str(e))

    def _generate_metta_proof(self, contribution_data: Dict[str, Any]) -> str:
        """Generate MeTTa proof for contribution"""
        try:
            # Create a simple hash-based proof for now
            # In production, this would use actual MeTTa reasoning
            proof_data = {
                'title': contribution_data.get('title'),
                'type': contribution_data.get('contribution_type'),
                'timestamp': datetime.utcnow().isoformat()
            }

            proof_string = json.dumps(proof_data, sort_keys=True)
            return hashlib.sha256(proof_string.encode()).hexdigest()

        except Exception as e:
            current_app.logger.warning(f"Error generating MeTTa proof: {e}")
            return hashlib.sha256(str(contribution_data).encode()).hexdigest()

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'success': False,
            'error': message
        }