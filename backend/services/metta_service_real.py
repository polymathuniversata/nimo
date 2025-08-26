"""
Real MeTTa Service Implementation for Nimo Platform
Uses the actual MeTTa Rust REPL for real reasoning
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
try:
    from .real_metta_runner import RealMeTTaRunner
except ImportError:
    from real_metta_runner import RealMeTTaRunner

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("real_metta_service")

class RealMeTTaService:
    """Real MeTTa service using the Rust REPL for actual reasoning"""
    
    def __init__(self, rules_dir=None, db_path=None, repl_path=None):
        """
        Initialize real MeTTa service
        
        Args:
            rules_dir: Directory containing MeTTa rule files
            db_path: Path to save/load MeTTa space serialization
            repl_path: Path to the MeTTa REPL executable
        """
        self.rules_dir = rules_dir or os.path.join(os.path.dirname(__file__), '../rules')
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '../metta_state/metta_database.json')
        
        # Initialize the real MeTTa runner
        try:
            self.runner = RealMeTTaRunner(repl_path)
            self.available = True
            logger.info("Real MeTTa service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize real MeTTa service: {e}")
            raise
        
        # Load core rules
        self._load_core_rules()
        
        # Initialize workspace tracking
        self.workspace = {}
    
    def _load_core_rules(self):
        """Load core MeTTa rules from files"""
        core_rules_file = os.path.join(self.rules_dir, 'core_rules.metta')
        
        if os.path.exists(core_rules_file):
            success = self.runner.load_core_rules(core_rules_file)
            if success:
                logger.info("Core rules loaded successfully")
            else:
                logger.warning("Failed to load core rules, using basic rules")
                self._add_basic_rules()
        else:
            logger.info("Core rules file not found, adding basic rules")
            self._add_basic_rules()
    
    def _add_basic_rules(self):
        """Add basic MeTTa rules for identity and contribution management"""
        basic_rules = """
; Basic identity and contribution rules
(= (UserSkill $user $skill) (User $user $skills) (member $skill $skills))
(= (ContributionValid $contrib) (and (Contribution $contrib) (User $user)))
(= (RewardTokens $user $contrib $amount) 
   (if (ContributionValid $contrib) 
       (TokenBalance $user $amount) 
       (TokenBalance $user 0)))
"""
        
        self.runner.execute_script(basic_rules)
        logger.info("Basic rules added to MeTTa space")
    
    def define_user(self, user_id: str, skills: List[str] = None) -> List[List[str]]:
        """
        Define a user in the MeTTa space
        
        Args:
            user_id: User identifier
            skills: List of user skills
            
        Returns:
            List of results from MeTTa execution
        """
        skills = skills or []
        
        try:
            success = self.runner.define_user(user_id, skills)
            if success:
                self.workspace[f"user_{user_id}"] = {"skills": skills}
                return [[f"User {user_id} defined successfully with skills: {skills}"]]
            else:
                return [[f"Failed to define user {user_id}"]]
        except Exception as e:
            logger.error(f"Error defining user {user_id}: {e}")
            return [[f"Error: {str(e)}"]]
    
    def add_skill(self, user_id: str, skill: str, level: int = 1) -> List[List[str]]:
        """
        Add a skill to a user
        
        Args:
            user_id: User identifier
            skill: Skill to add
            level: Skill level (1-5)
            
        Returns:
            List of results from MeTTa execution
        """
        try:
            # Get current user skills
            if f"user_{user_id}" in self.workspace:
                current_skills = self.workspace[f"user_{user_id}"]["skills"]
                if skill not in current_skills:
                    current_skills.append(skill)
                    # Redefine user with new skills
                    success = self.runner.define_user(user_id, current_skills)
                    if success:
                        return [[f"Skill {skill} added to user {user_id}"]]
            
            return [[f"Failed to add skill {skill} to user {user_id}"]]
        except Exception as e:
            logger.error(f"Error adding skill to user {user_id}: {e}")
            return [[f"Error: {str(e)}"]]
    
    def add_contribution(self, contribution_id: str, user_id: str, category: str, title: str = None) -> List[List[str]]:
        """
        Add a contribution to the MeTTa space
        
        Args:
            contribution_id: Unique contribution identifier
            user_id: User who made the contribution  
            category: Contribution category
            title: Optional contribution title
            
        Returns:
            List of results from MeTTa execution
        """
        try:
            description = title or category
            skills = [category]  # Use category as a skill for now
            
            success = self.runner.add_contribution(user_id, contribution_id, description, skills)
            if success:
                self.workspace[f"contribution_{contribution_id}"] = {
                    "user_id": user_id,
                    "category": category,
                    "title": title,
                    "skills": skills
                }
                return [[f"Contribution {contribution_id} added for user {user_id}"]]
            else:
                return [[f"Failed to add contribution {contribution_id}"]]
        except Exception as e:
            logger.error(f"Error adding contribution {contribution_id}: {e}")
            return [[f"Error: {str(e)}"]]
    
    def add_evidence(self, contribution_id: str, evidence_type: str, evidence_url: str, evidence_id: str = None) -> List[List[str]]:
        """
        Add evidence for a contribution
        
        Args:
            contribution_id: Contribution identifier
            evidence_type: Type of evidence
            evidence_url: URL to the evidence
            evidence_id: Optional evidence identifier
            
        Returns:
            List of results from MeTTa execution
        """
        try:
            evidence_id = evidence_id or f"evidence_{contribution_id}_{evidence_type}"
            
            evidence_code = f"""
; Add evidence for contribution {contribution_id}
(= (Evidence "{evidence_id}") ("{contribution_id}" "{evidence_type}" "{evidence_url}"))
!(Evidence "{evidence_id}")
"""
            
            stdout, stderr, return_code = self.runner.execute_script(evidence_code)
            
            if return_code == 0:
                return [[f"Evidence {evidence_id} added for contribution {contribution_id}"]]
            else:
                return [[f"Failed to add evidence: {stderr}"]]
        except Exception as e:
            logger.error(f"Error adding evidence: {e}")
            return [[f"Error: {str(e)}"]]
    
    def verify_contribution(self, contribution_id: str, organization: str, verifier_id: str = None) -> List[List[str]]:
        """
        Verify a contribution using MeTTa reasoning
        
        Args:
            contribution_id: Contribution to verify
            organization: Verifying organization
            verifier_id: Optional verifier identifier
            
        Returns:
            List of results from MeTTa execution
        """
        try:
            verifier = verifier_id or organization
            
            verification_result = self.runner.verify_contribution(contribution_id, verifier)
            
            if verification_result["verified"]:
                return [[f"Contribution {contribution_id} verified by {verifier}"]]
            else:
                return [[f"Contribution {contribution_id} could not be verified: {verification_result['explanation']}"]]
        except Exception as e:
            logger.error(f"Error verifying contribution {contribution_id}: {e}")
            return [[f"Error: {str(e)}"]]
    
    def set_token_balance(self, user_id: str, balance: int) -> List[List[str]]:
        """
        Set token balance for a user
        
        Args:
            user_id: User identifier
            balance: Token balance to set
            
        Returns:
            List of results from MeTTa execution
        """
        try:
            token_code = f"""
; Set token balance for user {user_id}
(= (TokenBalance "{user_id}") {balance})
!(TokenBalance "{user_id}")
"""
            
            stdout, stderr, return_code = self.runner.execute_script(token_code)
            
            if return_code == 0:
                return [[f"Token balance set to {balance} for user {user_id}"]]
            else:
                return [[f"Failed to set token balance: {stderr}"]]
        except Exception as e:
            logger.error(f"Error setting token balance: {e}")
            return [[f"Error: {str(e)}"]]
    
    def validate_contribution(self, contribution_id: str) -> Dict[str, Any]:
        """
        Validate a contribution using MeTTa reasoning
        
        Args:
            contribution_id: Contribution to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            verification = self.runner.verify_contribution(contribution_id)
            
            return {
                "valid": verification["verified"],
                "confidence": verification["confidence"],
                "explanation": verification["explanation"]
            }
        except Exception as e:
            logger.error(f"Error validating contribution {contribution_id}: {e}")
            return {
                "valid": False,
                "confidence": 0.0,
                "explanation": f"Validation error: {str(e)}"
            }
    
    def auto_award(self, user_id: str, contribution_id: str) -> Dict[str, Any]:
        """
        Automatically award tokens based on contribution validation
        
        Args:
            user_id: User identifier
            contribution_id: Contribution identifier
            
        Returns:
            Dictionary with award results
        """
        try:
            # First validate the contribution
            validation = self.validate_contribution(contribution_id)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "tokens_awarded": 0,
                    "reason": f"Contribution not valid: {validation['explanation']}",
                    "validation": validation
                }
            
            # Calculate tokens using MeTTa reasoning
            tokens = self.runner.calculate_tokens(user_id, contribution_id)
            
            if tokens > 0:
                # Set the new token balance
                self.set_token_balance(user_id, tokens)
                
                return {
                    "success": True,
                    "tokens_awarded": tokens,
                    "reason": f"Contribution {contribution_id} validated and rewarded",
                    "validation": validation
                }
            else:
                return {
                    "success": False,
                    "tokens_awarded": 0,
                    "reason": "No tokens calculated for this contribution",
                    "validation": validation
                }
        except Exception as e:
            logger.error(f"Error in auto_award: {e}")
            return {
                "success": False,
                "tokens_awarded": 0,
                "reason": f"Award error: {str(e)}",
                "validation": {"valid": False, "confidence": 0.0, "explanation": str(e)}
            }
    
    def query_user_contributions(self, user_id: str) -> List[str]:
        """
        Query all contributions by a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of contribution identifiers
        """
        try:
            contributions = []
            for key, value in self.workspace.items():
                if key.startswith("contribution_") and value.get("user_id") == user_id:
                    contribution_id = key.replace("contribution_", "")
                    contributions.append(contribution_id)
            
            return contributions
        except Exception as e:
            logger.error(f"Error querying user contributions: {e}")
            return []
    
    def query_token_balance(self, user_id: str) -> int:
        """
        Query token balance for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Token balance
        """
        try:
            query_code = f"""
; Query token balance for user {user_id}
!(TokenBalance "{user_id}")
"""
            
            results = self.runner.execute_query(f"!(TokenBalance \"{user_id}\")")
            
            # Try to extract balance from results
            for result in results:
                result_str = result.get("result", "")
                try:
                    if result_str.isdigit():
                        return int(result_str)
                    import re
                    numbers = re.findall(r'\d+', result_str)
                    if numbers:
                        return int(numbers[0])
                except:
                    pass
            
            return 0
        except Exception as e:
            logger.error(f"Error querying token balance: {e}")
            return 0
    
    def sync_user_to_metta(self, user) -> bool:
        """
        Sync a user object to MeTTa space
        
        Args:
            user: User object with id, username, skills
            
        Returns:
            True if successful
        """
        try:
            skills = getattr(user, 'skills', [])
            if isinstance(skills, str):
                skills = [skills]
            
            result = self.define_user(user.id, skills)
            return len(result) > 0 and "successfully" in result[0][0]
        except Exception as e:
            logger.error(f"Error syncing user to MeTTa: {e}")
            return False
    
    def sync_all_users(self, users) -> Dict[str, bool]:
        """
        Sync multiple users to MeTTa space
        
        Args:
            users: List of user objects
            
        Returns:
            Dictionary of user_id -> success status
        """
        results = {}
        for user in users:
            results[user.id] = self.sync_user_to_metta(user)
        
        logger.info(f"Synced {sum(results.values())} out of {len(users)} users")
        return results
    
    def save_to_file(self, path: str = None) -> bool:
        """
        Save MeTTa workspace state to file
        
        Args:
            path: Optional path to save to
            
        Returns:
            True if successful
        """
        try:
            save_path = path or self.db_path
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(self.workspace, f, indent=2)
            
            logger.info(f"MeTTa workspace saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving workspace: {e}")
            return False
    
    def load_from_file(self, path: str = None) -> bool:
        """
        Load MeTTa workspace state from file
        
        Args:
            path: Optional path to load from
            
        Returns:
            True if successful
        """
        try:
            load_path = path or self.db_path
            
            if os.path.exists(load_path):
                with open(load_path, 'r') as f:
                    self.workspace = json.load(f)
                
                logger.info(f"MeTTa workspace loaded from {load_path}")
                return True
            else:
                logger.info("No existing workspace file found")
                return False
        except Exception as e:
            logger.error(f"Error loading workspace: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize the service
        service = RealMeTTaService()
        
        print("Real MeTTa service initialized successfully!")
        
        # Test user definition
        result = service.define_user("alice", ["python", "blockchain", "ai"])
        print(f"Define user result: {result}")
        
        # Test contribution
        result = service.add_contribution("smart-contract-1", "alice", "blockchain", "Implemented ERC20 token")
        print(f"Add contribution result: {result}")
        
        # Test verification
        result = service.verify_contribution("smart-contract-1", "TrueAGI")
        print(f"Verify contribution result: {result}")
        
        # Test auto award
        result = service.auto_award("alice", "smart-contract-1")
        print(f"Auto award result: {result}")
        
        # Test token balance query
        balance = service.query_token_balance("alice")
        print(f"Token balance for alice: {balance}")
        
        # Save workspace
        service.save_to_file()
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")