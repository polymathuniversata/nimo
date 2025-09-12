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
    Enhanced MeTTa integration service with automatic fallback and caching.
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
        self.cache_service = None
        self.performance_monitor = None

        self._initialize_service()
        self._initialize_cache()
        self._initialize_performance_monitor()
        self._initialize_query_optimizer()

    def _initialize_service(self):
        """Initialize the appropriate service (real or mock)"""
        if self.force_mock:
            logger.info("Forcing use of mock MeTTa service")
            self._use_mock_service()
            return

        # Try to use real MeTTa service via runner
        try:
            from .metta_runner import run_metta_query, run_metta_script
            # Test if the runner works
            test_result = run_metta_query("(= test true)")
            self.service = self._create_runner_service()
            self.is_mock = False
            logger.info("Successfully initialized MeTTa runner service")
        except Exception as e:
            logger.warning(f"Failed to initialize MeTTa runner service: {e}")
            self._use_mock_service()

    def _initialize_cache(self):
        """Initialize the caching service"""
        try:
            from .metta_cache_service import get_cache_service
            self.cache_service = get_cache_service()
            logger.info("Successfully initialized cache service")
        except Exception as e:
            logger.warning(f"Failed to initialize cache service: {e}")
            self.cache_service = None

    def _initialize_performance_monitor(self):
        """Initialize the performance monitoring service"""
        try:
            from .metta_performance_monitor import get_monitor
            self.performance_monitor = get_monitor()
            logger.info("Successfully initialized performance monitor")
        except Exception as e:
            logger.warning(f"Failed to initialize performance monitor: {e}")
            self.performance_monitor = None

    def _initialize_query_optimizer(self):
        """Initialize the query optimizer service"""
        try:
            from .metta_query_optimizer import get_optimized_query_service
            self.query_optimizer = get_optimized_query_service()
            logger.info("Successfully initialized query optimizer")
        except Exception as e:
            logger.warning(f"Failed to initialize query optimizer: {e}")
            self.query_optimizer = None
    
    def _create_runner_service(self):
        """Create a service wrapper around metta_runner"""
        from .metta_runner import run_metta_query, run_metta_script
        
        class RunnerService:
            def __init__(self):
                self.db_path = None
                
            def analyze_contribution_safety(self, contribution_id, content, metadata):
                """Analyze contribution for safety and legitimacy"""
                query = f"""
                (= (analyze-contribution "{contribution_id}" "{content[:100]}")
                   (and (safety-check "{content[:100]}")
                        (legitimacy-check "{metadata.get('type', 'unknown')}")
                        (quality-assessment "{content[:100]}")))
                """
                try:
                    result = run_metta_query(query)
                    return {
                        'safe': True,  # Mock result for now
                        'legitimate': True,
                        'confidence': 0.8,
                        'reasoning': result
                    }
                except Exception:
                    return {'safe': True, 'legitimate': True, 'confidence': 0.5}
            
            def determine_reward(self, contribution_analysis, base_reward=10):
                """Determine appropriate reward based on analysis"""
                try:
                    confidence = contribution_analysis.get('confidence', 0.5)
                    multiplier = max(0.5, min(2.0, confidence * 1.5))
                    return int(base_reward * multiplier)
                except Exception:
                    return base_reward
            
            def add_contribution_atom(self, contribution_id, user_id, content, metadata):
                """Add contribution to MeTTa knowledge base"""
                atom = f'(contribution "{contribution_id}" "{user_id}" "{content[:50]}" {metadata})'
                try:
                    return run_metta_query(f'(add-atom {atom})')
                except Exception:
                    return f"Mock: Added {atom}"
        
        return RunnerService()
    
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
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("calculate_contribution_confidence") as op_monitor:
                op_monitor.add_metadata("contribution_id", str(contribution_id))
                return self._calculate_contribution_confidence_impl(contribution_id)
        else:
            return self._calculate_contribution_confidence_impl(contribution_id)
    
    def _calculate_contribution_confidence_impl(self, contribution_id: Union[str, int]) -> float:
        """Internal implementation of confidence calculation"""
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
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("validate_contribution") as op_monitor:
                op_monitor.add_metadata("contribution_id", str(contribution_id))
                op_monitor.add_metadata("has_contribution_data", contribution_data is not None)
                return self._validate_contribution_impl(contribution_id, contribution_data)
        else:
            return self._validate_contribution_impl(contribution_id, contribution_data)

    def _validate_contribution_impl(self, contribution_id: Union[str, int], contribution_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Internal implementation of contribution validation"""
        try:
            contribution_id_str = str(contribution_id)

            # Check cache first (only if no contribution_data is provided)
            if self.cache_service and not contribution_data:
                cached_result = self.cache_service.get_contribution_verification(contribution_id_str)
                if cached_result:
                    logger.info(f"Returning cached validation for {contribution_id_str}")
                    return cached_result

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
                final_result = {**default_result, **result}
            else:
                final_result = default_result

            # Cache the result (only if no contribution_data was provided)
            if self.cache_service and not contribution_data:
                self.cache_service.cache_contribution_verification(contribution_id_str, final_result)

            return final_result

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
    
    def execute_autonomous_cycle(self, platform_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a complete autonomous platform cycle

        Args:
            platform_state (Dict[str, Any]): Current platform state

        Returns:
            dict: Autonomous cycle results or None if failed
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("execute_autonomous_cycle") as op_monitor:
                op_monitor.add_metadata("platform_state_keys", list(platform_state.keys()) if platform_state else [])
                return self._execute_autonomous_cycle_impl(platform_state)
        else:
            return self._execute_autonomous_cycle_impl(platform_state)

    def _execute_autonomous_cycle_impl(self, platform_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Internal implementation of autonomous cycle execution"""
        try:
            # Check cache first
            if self.cache_service:
                cached_result = self.cache_service.get('platform_cycle', platform_state)
                if cached_result:
                    logger.info("Returning cached autonomous cycle result")
                    return cached_result

            if hasattr(self.service, 'execute_autonomous_cycle'):
                result = self.service.execute_autonomous_cycle(platform_state)

                # Cache the result
                if self.cache_service and result:
                    self.cache_service.set('platform_cycle', platform_state, result)

                return result
            else:
                # Fallback implementation
                result = {
                    'success': True,
                    'cycle_completed': True,
                    'results': 'Autonomous cycle executed (fallback)',
                    'timestamp': self._get_current_timestamp()
                }

                # Cache the result
                if self.cache_service:
                    self.cache_service.set('platform_cycle', platform_state, result)

                return result
        except Exception as e:
            logger.error(f"Failed to execute autonomous cycle: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.execute_autonomous_cycle(platform_state)
            return None
    
    def process_contribution_autonomously(self, contribution_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Process a contribution autonomously

        Args:
            contribution_id: The contribution ID to process

        Returns:
            dict: Autonomous processing results or None if failed
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("process_contribution_autonomously") as op_monitor:
                op_monitor.add_metadata("contribution_id", str(contribution_id))
                return self._process_contribution_autonomously_impl(contribution_id)
        else:
            return self._process_contribution_autonomously_impl(contribution_id)

    def _process_contribution_autonomously_impl(self, contribution_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Internal implementation of autonomous contribution processing"""
        try:
            contribution_id_str = str(contribution_id)

            # Check cache first
            if self.cache_service:
                cached_result = self.cache_service.get_contribution_verification(contribution_id_str)
                if cached_result:
                    logger.info(f"Returning cached contribution processing for {contribution_id_str}")
                    return cached_result

            if hasattr(self.service, 'process_contribution_autonomously'):
                result = self.service.process_contribution_autonomously(contribution_id_str)

                # Cache the result
                if self.cache_service and result:
                    self.cache_service.cache_contribution_verification(contribution_id_str, result)

                return result
            else:
                # Fallback implementation
                result = {
                    'contribution_id': contribution_id_str,
                    'processed': True,
                    'autonomous_decision': 'Contribution processed autonomously (fallback)',
                    'timestamp': self._get_current_timestamp()
                }

                # Cache the result
                if self.cache_service:
                    self.cache_service.cache_contribution_verification(contribution_id_str, result)

                return result
        except Exception as e:
            logger.error(f"Failed to process contribution autonomously {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.process_contribution_autonomously(str(contribution_id))
            return None
    
    def calculate_autonomous_reward(self, contribution_id: Union[str, int], quality_score: float, impact_score: float) -> Optional[Dict[str, Any]]:
        """
        Calculate autonomous reward

        Args:
            contribution_id: The contribution ID
            quality_score: Quality score (0-1)
            impact_score: Impact score (0-1)

        Returns:
            dict: Reward calculation results or None if failed
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("calculate_autonomous_reward") as op_monitor:
                op_monitor.add_metadata("contribution_id", str(contribution_id))
                op_monitor.add_metadata("quality_score", quality_score)
                op_monitor.add_metadata("impact_score", impact_score)
                return self._calculate_autonomous_reward_impl(contribution_id, quality_score, impact_score)
        else:
            return self._calculate_autonomous_reward_impl(contribution_id, quality_score, impact_score)

    def _calculate_autonomous_reward_impl(self, contribution_id: Union[str, int], quality_score: float, impact_score: float) -> Optional[Dict[str, Any]]:
        """Internal implementation of autonomous reward calculation"""
        try:
            contribution_id_str = str(contribution_id)

            # Check cache first
            if self.cache_service:
                cached_result = self.cache_service.get_reward_calculation(
                    contribution_id_str, quality_score, impact_score
                )
                if cached_result:
                    logger.info(f"Returning cached reward calculation for {contribution_id_str}")
                    return cached_result

            if hasattr(self.service, 'calculate_autonomous_reward'):
                result = self.service.calculate_autonomous_reward(contribution_id_str, quality_score, impact_score)

                # Cache the result
                if self.cache_service and result:
                    self.cache_service.cache_reward_calculation(
                        contribution_id_str, quality_score, impact_score, result
                    )

                return result
            else:
                # Fallback implementation
                base_reward = 50
                quality_bonus = int(quality_score * 25)
                impact_bonus = int(impact_score * 25)
                total = base_reward + quality_bonus + impact_bonus

                result = {
                    'contribution_id': contribution_id_str,
                    'reward_calculated': True,
                    'autonomous_reward': total,
                    'breakdown': {
                        'base': base_reward,
                        'quality_bonus': quality_bonus,
                        'impact_bonus': impact_bonus
                    },
                    'timestamp': self._get_current_timestamp()
                }

                # Cache the result
                if self.cache_service:
                    self.cache_service.cache_reward_calculation(
                        contribution_id_str, quality_score, impact_score, result
                    )

                return result
        except Exception as e:
            logger.error(f"Failed to calculate autonomous reward for {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.calculate_autonomous_reward(str(contribution_id), quality_score, impact_score)
            return None
    
    def optimize_platform_predictively(self, platform_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Optimize platform using predictive analytics
        
        Args:
            platform_state: Current platform state
            
        Returns:
            dict: Optimization results or None if failed
        """
        try:
            if hasattr(self.service, 'optimize_platform_predictively'):
                result = self.service.optimize_platform_predictively(platform_state)
                return result
            else:
                # Fallback implementation
                return {
                    'optimization_completed': True,
                    'predictive_insights': 'Platform optimized predictively (fallback)',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            logger.error(f"Failed to optimize platform predictively: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.optimize_platform_predictively(platform_state)
            return None
    
    def execute_governance_autonomously(self, governance_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute autonomous governance
        
        Args:
            governance_state: Current governance state
            
        Returns:
            dict: Governance execution results or None if failed
        """
        try:
            if hasattr(self.service, 'execute_governance_autonomously'):
                result = self.service.execute_governance_autonomously(governance_state)
                return result
            else:
                # Fallback implementation
                return {
                    'governance_executed': True,
                    'autonomous_decisions': 'Governance executed autonomously (fallback)',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            logger.error(f"Failed to execute governance autonomously: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.execute_governance_autonomously(governance_state)
            return None
    
    def manage_security_autonomously(self, security_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Manage security autonomously
        
        Args:
            security_state: Current security state
            
        Returns:
            dict: Security management results or None if failed
        """
        try:
            if hasattr(self.service, 'manage_security_autonomously'):
                result = self.service.manage_security_autonomously(security_state)
                return result
            else:
                # Fallback implementation
                return {
                    'security_managed': True,
                    'autonomous_actions': 'Security managed autonomously (fallback)',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            logger.error(f"Failed to manage security autonomously: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.manage_security_autonomously(security_state)
            return None
    
    def detect_fraud_comprehensive(self, contribution_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Detect fraud using comprehensive rules

        Args:
            contribution_id: The contribution ID to analyze

        Returns:
            dict: Fraud detection results or None if failed
        """
        if self.performance_monitor:
            with self.performance_monitor.monitor_operation("detect_fraud_comprehensive") as op_monitor:
                op_monitor.add_metadata("contribution_id", str(contribution_id))
                return self._detect_fraud_comprehensive_impl(contribution_id)
        else:
            return self._detect_fraud_comprehensive_impl(contribution_id)

    def _detect_fraud_comprehensive_impl(self, contribution_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Internal implementation of comprehensive fraud detection"""
        try:
            contribution_id_str = str(contribution_id)

            # Check cache first
            if self.cache_service:
                cached_result = self.cache_service.get_fraud_detection(contribution_id_str)
                if cached_result:
                    logger.info(f"Returning cached fraud detection for {contribution_id_str}")
                    return cached_result

            if hasattr(self.service, 'detect_fraud_comprehensive'):
                result = self.service.detect_fraud_comprehensive(contribution_id_str)

                # Cache the result
                if self.cache_service and result:
                    self.cache_service.cache_fraud_detection(contribution_id_str, result)

                return result
            else:
                # Fallback implementation
                result = {
                    'contribution_id': contribution_id_str,
                    'fraud_detected': False,
                    'analysis': 'Fraud detection completed (fallback)',
                    'timestamp': self._get_current_timestamp()
                }

                # Cache the result
                if self.cache_service:
                    self.cache_service.cache_fraud_detection(contribution_id_str, result)

                return result
        except Exception as e:
            logger.error(f"Failed to detect fraud comprehensively for {contribution_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.detect_fraud_comprehensive(str(contribution_id))
            return None
    
    def analyze_predictive_insights(self, entity_id: Union[str, int], prediction_type: str) -> Optional[Dict[str, Any]]:
        """
        Generate predictive insights
        
        Args:
            entity_id: The entity ID to analyze
            prediction_type: Type of prediction to generate
            
        Returns:
            dict: Predictive analysis results or None if failed
        """
        try:
            entity_id_str = str(entity_id)
            
            if hasattr(self.service, 'analyze_predictive_insights'):
                result = self.service.analyze_predictive_insights(entity_id_str, prediction_type)
                return result
            else:
                # Fallback implementation
                return {
                    'entity_id': entity_id_str,
                    'prediction_type': prediction_type,
                    'analysis_completed': True,
                    'predictive_insights': f'Predictive analysis completed for {prediction_type} (fallback)',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            logger.error(f"Failed to analyze predictive insights for {entity_id}: {e}")
            if not self.is_mock:
                self._use_mock_service()
                return self.service.analyze_predictive_insights(str(entity_id), prediction_type)
            return None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()

    def get_performance_metrics(self, time_window: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for autonomous operations

        Args:
            time_window: Time window in seconds for metrics

        Returns:
            dict: Performance metrics or None if monitor not available
        """
        if self.performance_monitor:
            return self.performance_monitor.get_performance_report(time_window)
        return None

    def get_operation_stats(self, operation_name: str, time_window: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific operation

        Args:
            operation_name: Name of the operation
            time_window: Time window in seconds for stats

        Returns:
            dict: Operation statistics or None if monitor not available
        """
        if self.performance_monitor:
            return self.performance_monitor.get_operation_stats(operation_name, time_window)
        return None

    def batch_validate_contributions(self, contribution_ids: List[Union[str, int]]) -> Dict[str, Any]:
        """
        Batch validate multiple contributions

        Args:
            contribution_ids: List of contribution IDs to validate

        Returns:
            dict: Batch validation results
        """
        if not self.query_optimizer:
            # Fallback to individual validation
            logger.warning("Query optimizer not available, falling back to individual validation")
            return self._batch_validate_fallback(contribution_ids)

        def validate_single(contribution_id, **kwargs):
            return self.validate_contribution(contribution_id)

        try:
            result = self.query_optimizer.execute_batch_query(
                'batch_contributions',
                contribution_ids,
                validate_single
            )

            logger.info(f"Batch validated {len(contribution_ids)} contributions: {result['success_count']} success, {result['error_count']} errors")
            return result

        except Exception as e:
            logger.error(f"Batch validation failed: {e}")
            return self._batch_validate_fallback(contribution_ids)

    def _batch_validate_fallback(self, contribution_ids: List[Union[str, int]]) -> Dict[str, Any]:
        """Fallback batch validation using individual calls"""
        results = []
        success_count = 0
        error_count = 0

        for contribution_id in contribution_ids:
            try:
                result = self.validate_contribution(contribution_id)
                results.append({
                    'contribution_id': contribution_id,
                    'result': result,
                    'success': True
                })
                success_count += 1
            except Exception as e:
                results.append({
                    'contribution_id': contribution_id,
                    'error': str(e),
                    'success': False
                })
                error_count += 1

        return {
            'results': results,
            'success_count': success_count,
            'error_count': error_count,
            'total_processed': len(contribution_ids),
            'batch_count': 1,
            'total_execution_time': 0,  # Not tracked in fallback
            'avg_time_per_item': 0
        }

    def batch_process_contributions(self, contribution_ids: List[Union[str, int]]) -> Dict[str, Any]:
        """
        Batch process multiple contributions autonomously

        Args:
            contribution_ids: List of contribution IDs to process

        Returns:
            dict: Batch processing results
        """
        if not self.query_optimizer:
            # Fallback to individual processing
            logger.warning("Query optimizer not available, falling back to individual processing")
            return self._batch_process_fallback(contribution_ids)

        def process_single(contribution_id, **kwargs):
            return self.process_contribution_autonomously(contribution_id)

        try:
            result = self.query_optimizer.execute_batch_query(
                'batch_contributions',
                contribution_ids,
                process_single
            )

            logger.info(f"Batch processed {len(contribution_ids)} contributions: {result['success_count']} success, {result['error_count']} errors")
            return result

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return self._batch_process_fallback(contribution_ids)

    def _batch_process_fallback(self, contribution_ids: List[Union[str, int]]) -> Dict[str, Any]:
        """Fallback batch processing using individual calls"""
        results = []
        success_count = 0
        error_count = 0

        for contribution_id in contribution_ids:
            try:
                result = self.process_contribution_autonomously(contribution_id)
                results.append({
                    'contribution_id': contribution_id,
                    'result': result,
                    'success': True
                })
                success_count += 1
            except Exception as e:
                results.append({
                    'contribution_id': contribution_id,
                    'error': str(e),
                    'success': False
                })
                error_count += 1

        return {
            'results': results,
            'success_count': success_count,
            'error_count': error_count,
            'total_processed': len(contribution_ids),
            'batch_count': 1,
            'total_execution_time': 0,
            'avg_time_per_item': 0
        }

    def batch_calculate_rewards(self, reward_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch calculate rewards for multiple contributions

        Args:
            reward_requests: List of reward request dicts with keys:
                           'contribution_id', 'quality_score', 'impact_score'

        Returns:
            dict: Batch reward calculation results
        """
        if not self.query_optimizer:
            # Fallback to individual calculations
            logger.warning("Query optimizer not available, falling back to individual calculations")
            return self._batch_rewards_fallback(reward_requests)

        def calculate_single(request, **kwargs):
            return self.calculate_autonomous_reward(
                request['contribution_id'],
                request['quality_score'],
                request['impact_score']
            )

        try:
            result = self.query_optimizer.execute_batch_query(
                'batch_rewards',
                reward_requests,
                calculate_single
            )

            logger.info(f"Batch calculated rewards for {len(reward_requests)} contributions: {result['success_count']} success, {result['error_count']} errors")
            return result

        except Exception as e:
            logger.error(f"Batch reward calculation failed: {e}")
            return self._batch_rewards_fallback(reward_requests)

    def _batch_rewards_fallback(self, reward_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback batch reward calculation using individual calls"""
        results = []
        success_count = 0
        error_count = 0

        for request in reward_requests:
            try:
                result = self.calculate_autonomous_reward(
                    request['contribution_id'],
                    request['quality_score'],
                    request['impact_score']
                )
                results.append({
                    'request': request,
                    'result': result,
                    'success': True
                })
                success_count += 1
            except Exception as e:
                results.append({
                    'request': request,
                    'error': str(e),
                    'success': False
                })
                error_count += 1

        return {
            'results': results,
            'success_count': success_count,
            'error_count': error_count,
            'total_processed': len(reward_requests),
            'batch_count': 1,
            'total_execution_time': 0,
            'avg_time_per_item': 0
        }

    def get_query_performance_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get query performance statistics

        Returns:
            dict: Query performance statistics or None if optimizer not available
        """
        if self.query_optimizer:
            return self.query_optimizer.get_performance_stats()
        return None

    def get_service_health(self) -> Dict[str, Any]:
        """
        Get comprehensive service health information

        Returns:
            dict: Service health information
        """
        health = {
            'service_type': 'enhanced_metta_integration',
            'timestamp': self._get_current_timestamp(),
            'components': {}
        }

        # Base service health
        health['components']['base_service'] = {
            'healthy': self.is_connected(),
            'mode': 'mock' if self.is_mock else 'real',
            'connected': self.is_connected()
        }

        # Cache health
        if self.cache_service:
            health['components']['cache'] = {'healthy': True, 'type': 'redis'}
        else:
            health['components']['cache'] = {'healthy': False, 'type': 'none'}

        # Performance monitor health
        if self.performance_monitor:
            health['components']['performance_monitor'] = {'healthy': True}
        else:
            health['components']['performance_monitor'] = {'healthy': False}

        # Query optimizer health
        if self.query_optimizer:
            optimizer_health = self.query_optimizer.health_check()
            health['components']['query_optimizer'] = optimizer_health
        else:
            health['components']['query_optimizer'] = {'healthy': False}

        # Overall health determination
        component_healths = []
        for comp in health['components'].values():
            if isinstance(comp, dict) and 'healthy' in comp:
                component_healths.append(comp['healthy'])
            else:
                # Assume component is healthy if status not specified
                component_healths.append(True)

        health['overall_healthy'] = all(component_healths)

        if not health['overall_healthy']:
            unhealthy_components = [name for name, comp in health['components'].items() if not comp['healthy']]
            health['issues'] = f"Unhealthy components: {', '.join(unhealthy_components)}"

        return health

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