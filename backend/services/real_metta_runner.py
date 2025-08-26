"""
Real MeTTa Runner Implementation
Uses the Rust MeTTa REPL directly for actual MeTTa execution
"""

import os
import sys
import json
import subprocess
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("real_metta_runner")

class RealMeTTaRunner:
    """Real MeTTa runner using the Rust REPL"""
    
    def __init__(self, repl_path: str = None):
        """
        Initialize the real MeTTa runner
        
        Args:
            repl_path: Path to the metta-repl.exe executable
        """
        if repl_path is None:
            # Try to find the REPL executable
            possible_paths = [
                "E:\\Polymath Universata\\Projects\\Nimo\\hyperon-experimental\\target\\debug\\metta-repl.exe",
                os.path.join(os.path.dirname(__file__), "../../../hyperon-experimental/target/debug/metta-repl.exe"),
                os.path.join(os.path.dirname(__file__), "../../../hyperon-experimental/target/release/metta-repl.exe"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    repl_path = path
                    break
        
        if not repl_path or not os.path.exists(repl_path):
            raise RuntimeError("MeTTa REPL executable not found. Please build hyperon-experimental first.")
        
        self.repl_path = repl_path
        self.workspace = {}  # Store workspace data
        logger.info(f"Real MeTTa runner initialized with REPL at: {repl_path}")
    
    def execute_script(self, metta_code: str) -> Tuple[str, str, int]:
        """
        Execute MeTTa code using the Rust REPL
        
        Args:
            metta_code: MeTTa code to execute
            
        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        try:
            # Create a temporary file with the MeTTa code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.metta', delete=False) as f:
                f.write(metta_code)
                temp_file = f.name
            
            # Execute the MeTTa REPL with the script
            cmd = [self.repl_path, temp_file]
            
            logger.debug(f"Executing: {' '.join(cmd)}")
            logger.debug(f"MeTTa code:\\n{metta_code}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(self.repl_path)
            )
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            logger.debug(f"STDOUT: {result.stdout}")
            logger.debug(f"STDERR: {result.stderr}")
            logger.debug(f"Return code: {result.returncode}")
            
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            logger.error("MeTTa execution timed out")
            return "", "Execution timed out", 1
        except Exception as e:
            logger.error(f"Error executing MeTTa code: {e}")
            return "", str(e), 1
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a MeTTa query and parse the results
        
        Args:
            query: MeTTa query to execute
            
        Returns:
            List of result dictionaries
        """
        # Wrap the query in a script that prints the results
        metta_code = f"""
; Execute query and display result
{query}
"""
        
        stdout, stderr, return_code = self.execute_script(metta_code)
        
        if return_code != 0:
            logger.error(f"Query failed: {stderr}")
            return []
        
        # Parse the output
        results = []
        lines = stdout.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(';') and not line.startswith('metta>'):
                # Try to parse as a result
                try:
                    # Simple parsing for now - can be enhanced
                    if line.startswith('(') and line.endswith(')'):
                        results.append({"result": line, "type": "atom"})
                    elif line:
                        results.append({"result": line, "type": "value"})
                except Exception as e:
                    logger.debug(f"Failed to parse line: {line}, error: {e}")
        
        logger.info(f"Query '{query}' returned {len(results)} results")
        return results
    
    def define_user(self, user_id: str, skills: List[str]) -> bool:
        """
        Define a user in the MeTTa space
        
        Args:
            user_id: User identifier
            skills: List of user skills
            
        Returns:
            True if successful
        """
        skills_str = " ".join([f'"{skill}"' for skill in skills])
        metta_code = f"""
; Define user {user_id}
(= (User "{user_id}") ({skills_str}))
!(User "{user_id}")
"""
        
        stdout, stderr, return_code = self.execute_script(metta_code)
        success = return_code == 0
        
        if success:
            self.workspace[f"user_{user_id}"] = {"skills": skills}
            logger.info(f"User {user_id} defined successfully")
        else:
            logger.error(f"Failed to define user {user_id}: {stderr}")
        
        return success
    
    def add_contribution(self, user_id: str, contribution_id: str, description: str, skills: List[str]) -> bool:
        """
        Add a contribution to the MeTTa space
        
        Args:
            user_id: User who made the contribution
            contribution_id: Unique contribution identifier
            description: Contribution description
            skills: Skills demonstrated by the contribution
            
        Returns:
            True if successful
        """
        skills_str = " ".join([f'"{skill}"' for skill in skills])
        metta_code = f"""
; Add contribution {contribution_id}
(= (Contribution "{contribution_id}") (User "{user_id}" "{description}" ({skills_str})))
!(Contribution "{contribution_id}")
"""
        
        stdout, stderr, return_code = self.execute_script(metta_code)
        success = return_code == 0
        
        if success:
            self.workspace[f"contribution_{contribution_id}"] = {
                "user_id": user_id,
                "description": description,
                "skills": skills
            }
            logger.info(f"Contribution {contribution_id} added successfully")
        else:
            logger.error(f"Failed to add contribution {contribution_id}: {stderr}")
        
        return success
    
    def verify_contribution(self, contribution_id: str, verifier_id: str = "system") -> Dict[str, Any]:
        """
        Verify a contribution using MeTTa reasoning
        
        Args:
            contribution_id: Contribution to verify
            verifier_id: Who is verifying (default: system)
            
        Returns:
            Dictionary with verification results
        """
        metta_code = f"""
; Verify contribution {contribution_id}
(= (Verify "{contribution_id}") 
   (if (Contribution "{contribution_id}") 
       (Verified "{contribution_id}" "{verifier_id}" True)
       (Verified "{contribution_id}" "{verifier_id}" False)))

!(Verify "{contribution_id}")
"""
        
        results = self.execute_query(f"!(Verify \"{contribution_id}\")")
        
        if results:
            # Parse verification result
            for result in results:
                if "True" in result.get("result", ""):
                    return {
                        "verified": True,
                        "verifier": verifier_id,
                        "confidence": 1.0,
                        "explanation": f"Contribution {contribution_id} successfully verified"
                    }
            
            return {
                "verified": False,
                "verifier": verifier_id,
                "confidence": 0.0,
                "explanation": f"Contribution {contribution_id} could not be verified"
            }
        
        return {
            "verified": False,
            "verifier": verifier_id,
            "confidence": 0.0,
            "explanation": "Verification query failed"
        }
    
    def calculate_tokens(self, user_id: str, contribution_id: str) -> int:
        """
        Calculate token reward for a contribution using MeTTa reasoning
        
        Args:
            user_id: User who made the contribution
            contribution_id: Contribution identifier
            
        Returns:
            Number of tokens to award
        """
        metta_code = f"""
; Calculate tokens for contribution
(= (TokenReward "{contribution_id}") 
   (if (and (Contribution "{contribution_id}") (User "{user_id}"))
       100  ; Base reward
       0))

!(TokenReward "{contribution_id}")
"""
        
        results = self.execute_query(f"!(TokenReward \"{contribution_id}\")")
        
        # Parse the token amount from results
        for result in results:
            result_str = result.get("result", "")
            try:
                # Extract numeric value
                if result_str.isdigit():
                    return int(result_str)
                # Try to extract from parentheses
                import re
                numbers = re.findall(r'\d+', result_str)
                if numbers:
                    return int(numbers[0])
            except:
                pass
        
        return 0
    
    def load_core_rules(self, rules_file: str) -> bool:
        """
        Load core MeTTa rules from file
        
        Args:
            rules_file: Path to the rules file
            
        Returns:
            True if successful
        """
        if not os.path.exists(rules_file):
            logger.error(f"Rules file not found: {rules_file}")
            return False
        
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules_content = f.read()
            
            stdout, stderr, return_code = self.execute_script(rules_content)
            success = return_code == 0
            
            if success:
                logger.info(f"Core rules loaded from {rules_file}")
            else:
                logger.error(f"Failed to load core rules: {stderr}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error loading rules file: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test if the MeTTa runner is working
        
        Returns:
            True if MeTTa is responsive
        """
        test_code = """
; Test MeTTa connection
(= (test) (Hello MeTTa))
!(test)
"""
        
        stdout, stderr, return_code = self.execute_script(test_code)
        
        success = return_code == 0 and "Hello" in stdout
        if success:
            logger.info("MeTTa connection test successful")
        else:
            logger.error(f"MeTTa connection test failed: {stderr}")
        
        return success

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize the runner
        runner = RealMeTTaRunner()
        
        # Test connection
        if runner.test_connection():
            print("MeTTa runner is working!")
            
            # Test user definition
            runner.define_user("alice", ["python", "blockchain"])
            
            # Test contribution
            runner.add_contribution("alice", "smart-contract-1", "Implemented ERC20 token", ["blockchain", "solidity"])
            
            # Test verification
            verification = runner.verify_contribution("smart-contract-1")
            print(f"Verification result: {verification}")
            
            # Test token calculation
            tokens = runner.calculate_tokens("alice", "smart-contract-1")
            print(f"Tokens to award: {tokens}")
            
        else:
            print("MeTTa runner test failed")
            
    except Exception as e:
        print(f"Error: {e}")