"""
MeTTa Integration Service for Nimo Platform

This service provides integration with MeTTa language for representing
decentralized identities and contributions in the Nimo platform.

This is the main MeTTa integration class that brings together various MeTTa
implementations and provides a unified interface for the rest of the application.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
try:
    from .metta_runner import run_metta_script, run_metta_query
    METTA_AVAILABLE = True
except ImportError:
    print("Warning: No MeTTa implementation available. Using mock implementation.")
    METTA_AVAILABLE = False
    
    # Mock implementations
    def run_metta_script(script):
        return "Mock MeTTa result"
    
    def run_metta_query(query):
        return "Mock MeTTa query result"
from .metta_service import MeTTaIntegration as BaseMeTTaIntegration
from .metta_security import MeTTaSanitizer, MeTTaSecurityError, create_safe_metta_atom, MeTTaAuditor
from .did_verification import DIDVerifier, MeTTaDIDIntegration, DIDVerificationError

class MeTTaIntegration(BaseMeTTaIntegration):
    """
    Enhanced MeTTa Integration service for Nimo Platform
    
    This extends the base MeTTa service with additional capabilities
    for contribution validation, token awards, and DID verification
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with DID integration support"""
        super().__init__(*args, **kwargs)
        self.did_integration = MeTTaDIDIntegration()
        
        # Load DID verification rules into MeTTa space
        did_rules = self.did_integration.generate_identity_metta_rules()
        run_metta_query(did_rules)
        self._track_atom(did_rules)
    
    def validate_contribution(self, contribution_id: str, contribution_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate a contribution using MeTTa reasoning and determine token awards
        
        Args:
            contribution_id (str): Contribution ID
            contribution_data (Dict[str, Any], optional): Contribution data
                If provided, this will be used instead of querying the contribution
            
        Returns:
            dict: Validation result with confidence, token award, and explanation
        """
        # If contribution data is provided, add it to MeTTa space first
        if contribution_data:
            self._add_contribution_from_data(contribution_id, contribution_data)
        
        # Base validation from parent class
        validation_result = super().validate_contribution(contribution_id)
        
        # Calculate reputation impact
        reputation_impact = self._calculate_reputation_impact(contribution_id, validation_result)
        
        # Calculate token award
        token_award = self._calculate_token_award(contribution_id, validation_result)
        
        # Enhanced result
        return {
            "status": "verified" if validation_result["valid"] else "rejected",
            "confidence": validation_result["confidence"],
            "explanation": validation_result["explanation"],
            "reputation_impact": reputation_impact,
            "token_award": token_award,
            "verification_timestamp": self._get_current_timestamp()
        }
    
    def _add_contribution_from_data(self, contribution_id: str, data: Dict[str, Any]) -> None:
        """
        Add contribution data to MeTTa space from dictionary
        
        Args:
            contribution_id (str): Contribution ID
            data (Dict[str, Any]): Contribution data
        """
        try:
            # Sanitize input parameters
            sanitized_contribution_id = MeTTaSanitizer.sanitize_id(contribution_id, "contribution_id")
            user_id = MeTTaSanitizer.sanitize_id(data.get('user_id', ''), "user_id")
            category = MeTTaSanitizer.sanitize_category(data.get('category', 'other'))
            title = MeTTaSanitizer.sanitize_string(data.get('title', ''), "title", 200)
        except MeTTaSecurityError as e:
            print(f"Security error in contribution data: {e}")
            return
        
        # Add the contribution to MeTTa space
        self.add_contribution(sanitized_contribution_id, user_id, category, title)
        
        # Add any evidence
        evidence_list = data.get('evidence', [])
        if isinstance(evidence_list, list):
            for i, evidence in enumerate(evidence_list):
                if isinstance(evidence, dict):
                    evidence_type = evidence.get('type', 'url')
                    evidence_url = evidence.get('url', '')
                    evidence_id = evidence.get('id', f"evidence-{contribution_id}-{i}")
                    
                    if evidence_url:
                        try:
                            sanitized_url = MeTTaSanitizer.sanitize_url(evidence_url)
                            self.add_evidence(sanitized_contribution_id, evidence_type, sanitized_url, evidence_id)
                        except MeTTaSecurityError as e:
                            print(f"Skipping invalid evidence URL: {e}")
        
        # Add metadata if available (with security validation)
        if 'metadata' in data and isinstance(data['metadata'], dict):
            try:
                # Validate and sanitize metadata first
                metadata = MeTTaSanitizer.validate_metadata(data['metadata'])
            except MeTTaSecurityError as e:
                print(f"Security error in metadata validation: {e}")
                return  # Skip adding potentially malicious metadata
            
            if 'impact' in metadata:
                impact_atom = create_safe_metta_atom(
                    '(ContributionImpact "{contribution_id}" "{impact}")',
                    contribution_id=sanitized_contribution_id,
                    impact=metadata['impact']
                )
                run_metta_query(impact_atom)
                self._track_atom(impact_atom)
            
            if 'skills' in metadata and isinstance(metadata['skills'], list):
                for skill in metadata['skills']:
                    try:
                        sanitized_skill = MeTTaSanitizer.sanitize_skill(skill)
                        skill_atom = create_safe_metta_atom(
                            '(RequiresSkill "{contribution_id}" "{skill}")',
                            contribution_id=sanitized_contribution_id,
                            skill=sanitized_skill
                        )
                        run_metta_query(skill_atom)
                        self._track_atom(skill_atom)
                    except MeTTaSecurityError as e:
                        print(f"Skipping invalid skill '{skill}': {e}")
    
    def _calculate_reputation_impact(self, contribution_id: str, validation_result: Dict[str, Any]) -> int:
        """
        Calculate reputation impact for a contribution
        
        Args:
            contribution_id (str): Contribution ID
            validation_result (Dict[str, Any]): Validation result
            
        Returns:
            int: Reputation impact (positive or negative)
        """
        # Query MeTTa for reputation impact
        try:
            result = run_metta_query(
                f'!(CalculateReputationImpact "{contribution_id}")'
            )
            
            if result:
                # Extract numeric value from result
                match = re.search(r'(-?\d+)', result)
                if match:
                    return int(match.group(0))
        except Exception:
            pass
        
        # Default calculation if MeTTa query fails
        if validation_result["valid"]:
            # Base reputation impact based on confidence
            confidence = validation_result["confidence"]
            if confidence >= 0.8:
                return 10  # High confidence verification
            elif confidence >= 0.6:
                return 5   # Medium confidence verification
            else:
                return 2   # Low confidence verification
        else:
            # Negative reputation for rejected contributions with high confidence
            if validation_result["confidence"] >= 0.8:
                return -3  # High confidence rejection
            else:
                return 0   # No impact for low confidence rejections
    
    def _calculate_token_award(self, contribution_id: str, validation_result: Dict[str, Any]) -> int:
        """
        Calculate token award for a verified contribution
        
        Args:
            contribution_id (str): Contribution ID
            validation_result (Dict[str, Any]): Validation result
            
        Returns:
            int: Token award amount
        """
        if not validation_result["valid"]:
            return 0
        
        # Query category first
        category_result = run_metta_query(
            f'!(match &self (Contribution "{contribution_id}" $_ $category) $category)'
        )
        
        category = "other"
        if category_result:
            # Extract category from result
            match = re.search(r'"([^"]+)"', category_result)
            if match:
                category = match.group(1)
        
        # Try to get token award from MeTTa first
        try:
            result = run_metta_query(
                f'!(CalculateTokenAward "{category}")'
            )
            
            if result:
                # Extract numeric value from result
                match = re.search(r'(\d+)', result)
                if match:
                    return int(match.group(0))
        except Exception:
            pass
        
        # Default calculation if MeTTa query fails
        base_awards = {
            "coding": 75,
            "education": 60,
            "volunteer": 50,
            "activism": 65,
            "leadership": 70,
            "entrepreneurship": 80,
            "environmental": 70,
            "community": 60
        }
        
        # Get base award by category or default to 50
        base_award = base_awards.get(category.lower(), 50)
        
        # Apply confidence multiplier
        confidence = validation_result["confidence"]
        confidence_multiplier = 0.5 + (confidence * 0.5)  # Scale from 0.5 to 1.0
        
        return int(base_award * confidence_multiplier)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for reporting"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def verify_user_did(self, user_id: str, did: str, proof: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify user's decentralized identity and integrate with MeTTa reasoning
        
        Args:
            user_id (str): User ID
            did (str): Decentralized identifier
            proof (Dict[str, Any], optional): Cryptographic proof
            
        Returns:
            Dict[str, Any]: DID verification result with MeTTa integration
        """
        try:
            # Perform DID verification and MeTTa integration
            result = self.did_integration.verify_user_identity(user_id, did, proof)
            
            # Add MeTTa atoms to the reasoning space
            for atom in result['metta_atoms']:
                run_metta_query(atom)
                self._track_atom(atom)
            
            # Enhance result with identity-based reputation
            if result['identity_verified']:
                # Query for identity reputation bonus
                try:
                    bonus_query = f'!(IdentityReputationBonus "{user_id}")'
                    bonus_result = run_metta_query(bonus_query)
                    result['reputation_bonus'] = int(bonus_result) if bonus_result else 0
                except Exception:
                    result['reputation_bonus'] = 0
            else:
                result['reputation_bonus'] = 0
            
            return result
            
        except DIDVerificationError as e:
            return {
                'user_id': user_id,
                'did': did,
                'identity_verified': False,
                'error': str(e),
                'verification_timestamp': self._get_current_timestamp()
            }
    
    def verify_contribution_with_identity(self, contribution_id: str, contribution_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhanced contribution verification that considers user's verified identity
        
        Args:
            contribution_id (str): Contribution ID
            contribution_data (Dict[str, Any], optional): Contribution data
            
        Returns:
            Dict[str, Any]: Enhanced verification result considering identity
        """
        # First perform standard contribution validation
        base_result = self.validate_contribution(contribution_id, contribution_data)
        
        # Add identity-enhanced verification
        try:
            identity_verification_query = f'!(VerifyWithIdentity "{contribution_id}")'
            identity_result = run_metta_query(identity_verification_query)
            
            if identity_result:
                # Identity verification enhances confidence
                base_result['identity_enhanced'] = True
                base_result['confidence'] = min(1.0, base_result.get('confidence', 0.5) + 0.2)
                base_result['explanation'] += " Identity verification provides additional trust."
            else:
                base_result['identity_enhanced'] = False
                base_result['explanation'] += " No verified identity found for user."
                
        except Exception as e:
            base_result['identity_enhanced'] = False
            base_result['identity_error'] = str(e)
        
        return base_result