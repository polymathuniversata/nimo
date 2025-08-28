"""
Enhanced MeTTa Integration Service with automatic fallback to mock service.
This service provides seamless operation whether MeTTa is available or not.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from flask import current_app

# Set up logger
logger = logging.getLogger(__name__)

class MeTTaIntegrationService:
    """
    Enhanced MeTTa integration service with automatic fallback.
    Attempts to use real MeTTa service first, then falls back to mock service.
    """
    
    def __init__(self, db_path: Optional[str] = None, force_mock: bool = False):
        """
        Initialize MeTTa integration service.
        
        Args:
            db_path: Optional path for persistent storage
            force_mock: Force use of mock service for testing
        """
        self.db_path = db_path
        self.force_mock = force_mock
        self.service = None
        self.is_mock = False
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the appropriate service (real or mock)"""
        if self.force_mock:
            logger.info("Forcing use of mock MeTTa service")
            self._use_mock_service()
            return
        
        # Try to use real MeTTa service first
        try:
            from .metta_service import MeTTaIntegration
            self.service = MeTTaIntegration(db_path=self.db_path)
            self.is_mock = False
            logger.info("Successfully initialized real MeTTa service")
        except Exception as e:
            logger.warning(f"Failed to initialize real MeTTa service: {e}")
            self._use_mock_service()
    
    def _use_mock_service(self):
        """Use the mock MeTTa service"""
        try:
            from .metta_mock_service import MockMeTTaService
            self.service = MockMeTTaService(db_path=self.db_path)
            self.is_mock = True
            logger.info("Successfully initialized mock MeTTa service")
        except Exception as e:
            logger.error(f"Failed to initialize mock MeTTa service: {e}")
            raise RuntimeError("Could not initialize any MeTTa service")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the MeTTa service.
        
        Returns:
            dict: Health status information
        """
        try:
            if hasattr(self.service, 'health_check'):
                return self.service.health_check()
            else:
                return {
                    "status": "operational" if self.service else "error",
                    "mode": "mock" if self.is_mock else "real",
                    "connected": self.is_connected()
                }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "mode": "mock" if self.is_mock else "real",
                "error": str(e),
                "connected": False
            }
    
    def is_connected(self) -> bool:
        """Check if the service is connected and operational"""
        try:
            if hasattr(self.service, 'is_connected'):
                return self.service.is_connected()
            return self.service is not None
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
    
    def define_user(self, user_id: Union[str, int], username: Optional[str] = None) -> str:
        """Define a user in MeTTa"""
        try:
            user_id_str = str(user_id)
            return self.service.define_user(user_id_str, username)
        except Exception as e:
            logger.error(f"Failed to define user {user_id}: {e}")
            if not self.is_mock:
                logger.info("Attempting fallback to mock service")
                self._use_mock_service()
                return self.service.define_user(str(user_id), username)
            raise
    
    def add_skill(self, user_id: Union[str, int], skill: str, level: int = 1) -> str:
        """Add a skill to a user's profile"""
        try:
            user_id_str = str(user_id)
            return self.service.add_skill(user_id_str, skill, level)
        except Exception as e:
            logger.error(f"Failed to add skill for user {user_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.add_skill(str(user_id), skill, level)
            raise
    
    def add_contribution(
        self, 
        contribution_id: Union[str, int], 
        user_id: Union[str, int], 
        category: str, 
        title: Optional[str] = None
    ) -> str:
        """Record a contribution"""
        try:
            contribution_id_str = str(contribution_id)
            user_id_str = str(user_id)
            return self.service.add_contribution(contribution_id_str, user_id_str, category, title)
        except Exception as e:
            logger.error(f"Failed to add contribution {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.add_contribution(str(contribution_id), str(user_id), category, title)
            raise
    
    def add_evidence(
        self, 
        contribution_id: Union[str, int], 
        evidence_type: str, 
        evidence_url: str, 
        evidence_id: Optional[Union[str, int]] = None
    ) -> str:
        """Add evidence for a contribution"""
        try:
            contribution_id_str = str(contribution_id)
            evidence_id_str = str(evidence_id) if evidence_id else None
            return self.service.add_evidence(contribution_id_str, evidence_type, evidence_url, evidence_id_str)
        except Exception as e:
            logger.error(f"Failed to add evidence for contribution {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.add_evidence(str(contribution_id), evidence_type, evidence_url, str(evidence_id) if evidence_id else None)
            raise
    
    def verify_contribution(
        self, 
        contribution_id: Union[str, int], 
        organization: str, 
        verifier_id: Optional[Union[str, int]] = None
    ) -> str:
        """Record a contribution verification"""
        try:
            contribution_id_str = str(contribution_id)
            verifier_id_str = str(verifier_id) if verifier_id else None
            return self.service.verify_contribution(contribution_id_str, organization, verifier_id_str)
        except Exception as e:
            logger.error(f"Failed to verify contribution {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.verify_contribution(str(contribution_id), organization, str(verifier_id) if verifier_id else None)
            raise
    
    def set_token_balance(self, user_id: Union[str, int], balance: int) -> str:
        """Set token balance for a user"""
        try:
            user_id_str = str(user_id)
            return self.service.set_token_balance(user_id_str, balance)
        except Exception as e:
            logger.error(f"Failed to set token balance for user {user_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.set_token_balance(str(user_id), balance)
            raise
    
    def calculate_contribution_confidence(self, contribution_id: Union[str, int]) -> float:
        """Calculate confidence score for a contribution"""
        try:
            contribution_id_str = str(contribution_id)
            return self.service.calculate_contribution_confidence(contribution_id_str)
        except Exception as e:
            logger.error(f"Failed to calculate confidence for contribution {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.calculate_contribution_confidence(str(contribution_id))
            return 0.5  # Default fallback
    
    def validate_contribution(self, contribution_id: Union[str, int], contribution_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a contribution using MeTTa reasoning.
        
        Args:
            contribution_id: The contribution ID to validate
            contribution_data: Optional contribution data
            
        Returns:
            dict: Validation result with confidence and explanation
        """
        try:
            contribution_id_str = str(contribution_id)
            
            # If contribution data is provided, add it to MeTTa space first
            if contribution_data and hasattr(self.service, '_add_contribution_from_data'):
                self.service._add_contribution_from_data(contribution_id_str, contribution_data)
            
            result = self.service.validate_contribution(contribution_id_str)
            
            # Ensure result has required fields
            default_result = {
                "valid": False,
                "confidence": 0.0,
                "explanation": "Validation failed"
            }
            
            if isinstance(result, dict):
                return {**default_result, **result}
            else:
                return default_result
                
        except Exception as e:
            logger.error(f"Failed to validate contribution {contribution_id}: {e}")
            
            if not self.is_mock:
                logger.info("Attempting fallback to mock service")
                self._use_mock_service()
                return self.service.validate_contribution(str(contribution_id))
            
            return {
                "valid": False,
                "confidence": 0.0,
                "explanation": f"Validation error: {str(e)}"
            }
    
    def auto_award(self, user_id: Union[str, int], contribution_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Apply automatic token award logic.
        
        Args:
            user_id: The user ID
            contribution_id: The contribution ID
            
        Returns:
            dict: Award result or None if failed
        """
        try:
            user_id_str = str(user_id)
            contribution_id_str = str(contribution_id)
            
            if hasattr(self.service, 'auto_award'):
                result = self.service.auto_award(user_id_str, contribution_id_str)
                return result
            else:
                # Fallback calculation if method doesn't exist
                validation = self.validate_contribution(contribution_id_str)
                if validation.get('valid', False):
                    confidence = validation.get('confidence', 0.5)
                    base_award = 50
                    bonus = int(confidence * 50)
                    total = base_award + bonus
                    
                    # Update balance if possible
                    if hasattr(self.service, 'query_token_balance') and hasattr(self.service, 'set_token_balance'):
                        current_balance = self.service.query_token_balance(user_id_str)
                        self.service.set_token_balance(user_id_str, current_balance + total)
                        
                        return {
                            "awarded": total,
                            "breakdown": {"base": base_award, "confidence_bonus": bonus},
                            "old_balance": current_balance,
                            "new_balance": current_balance + total
                        }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to auto award for user {user_id}, contribution {contribution_id}: {e}")
            
            if not self.is_mock:
                self._use_mock_service()
                return self.service.auto_award(str(user_id), str(contribution_id))
            
            return None
    
    def query_user_contributions(self, user_id: Union[str, int]) -> List[str]:
        """Query all contributions for a user"""
        try:
            user_id_str = str(user_id)
            return self.service.query_user_contributions(user_id_str)
        except Exception as e:
            logger.error(f"Failed to query contributions for user {user_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.query_user_contributions(str(user_id))
            return []
    
    def query_token_balance(self, user_id: Union[str, int]) -> int:
        """Query token balance for a user"""
        try:
            user_id_str = str(user_id)
            return self.service.query_token_balance(user_id_str)
        except Exception as e:
            logger.error(f"Failed to query token balance for user {user_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.query_token_balance(str(user_id))
            return 0
    
    def sync_user_to_metta(self, user_data: Union[Dict[str, Any], Any]):
        """
        Sync a user to MeTTa representation.
        
        Args:
            user_data: User data (dict or model instance)
        """
        try:
            # Convert user model to dict if needed
            if hasattr(user_data, 'to_dict'):
                user_dict = user_data.to_dict()
            elif hasattr(user_data, '__dict__'):
                user_dict = user_data.__dict__.copy()
            else:
                user_dict = user_data
            
            # Use service-specific sync method if available
            if hasattr(self.service, 'sync_user_to_metta'):
                if self.is_mock:
                    # Mock service expects dict
                    self.service.sync_user_to_metta(user_dict)
                else:
                    # Real service expects model instance
                    self.service.sync_user_to_metta(user_data)
            else:
                # Manual sync for services without this method
                user_id = str(user_dict.get('id'))
                username = user_dict.get('name') or user_dict.get('username')
                
                self.define_user(user_id, username)
                
                # Sync skills
                skills = user_dict.get('skills', [])
                for skill in skills:
                    if isinstance(skill, dict):
                        skill_name = skill.get('name')
                        skill_level = skill.get('level', 1)
                    else:
                        skill_name = str(skill)
                        skill_level = 1
                    
                    if skill_name:
                        self.add_skill(user_id, skill_name, skill_level)
                
                # Sync token balance
                token_balance = user_dict.get('token_balance', 0)
                if isinstance(token_balance, dict):
                    token_balance = token_balance.get('balance', 0)
                self.set_token_balance(user_id, token_balance)
                
        except Exception as e:
            logger.error(f"Failed to sync user to MeTTa: {e}")
            if not self.is_mock:
                self._use_mock_service()
                self.sync_user_to_metta(user_data)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the current service"""
        return {
            "is_mock": self.is_mock,
            "service_type": "mock" if self.is_mock else "real",
            "connected": self.is_connected(),
            "service_class": self.service.__class__.__name__ if self.service else None
        }

# Global instance
_metta_service = None

def get_metta_service(force_mock: bool = False) -> MeTTaIntegrationService:
    """
    Get the global MeTTa service instance.
    
    Args:
        force_mock: Force use of mock service
        
    Returns:
        MeTTaIntegrationService: The service instance
    """
    global _metta_service
    
    if _metta_service is None or force_mock:
        db_path = None
        
        # Try to get database path from config
        try:
            if current_app:
                db_path = current_app.config.get('METTA_DATABASE_PATH')
        except RuntimeError:
            pass  # Outside application context
        
        _metta_service = MeTTaIntegrationService(db_path=db_path, force_mock=force_mock)
    
    return _metta_service

def reset_metta_service():
    """Reset the global service instance (useful for testing)"""
    global _metta_service
    _metta_service = None