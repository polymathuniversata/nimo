"""
MeTTa Integration Service for Nimo Platform

This service provides integration with MeTTa language for representing
decentralized identities and contributions in the Nimo platform.

Based on research findings: docs/metta_research_findings.md

This version uses the metta_runner.py module which runs MeTTa through the Rust REPL
instead of using the Python bindings which are more difficult to install.
"""

import os
import json
import re
from .metta_runner import run_metta_script, run_metta_query

class MeTTaIntegration:
    def __init__(self, rules_dir=None, db_path=None):
        """
        Initialize MeTTa integration
        
        Args:
            rules_dir (str, optional): Directory containing MeTTa rule files
            db_path (str, optional): Path to save/load MeTTa space serialization
        """
        self.rules_dir = rules_dir or os.path.join(os.path.dirname(__file__), '../rules')
        self.db_path = db_path
        self.added_atoms = []
        
        # Create a new MeTTa space via our temp file approach
        self._load_core_rules()
        
        # Load serialized space if path provided
        if self.db_path and os.path.exists(self.db_path):
            try:
                self._load_serialized_space(self.db_path)
            except Exception as e:
                print(f"Error loading MeTTa store: {e}")
    
    def _load_core_rules(self):
        """Load core reasoning rules into the MeTTa space"""
        # Core identity and verification rules
        rules = '''
        ; Identity patterns
        (= (HasIdentity $user-id)
           (User $user-id $_))
           
        ; Verification patterns
        (= (IsVerified $user-id)
           (HasVerification $user-id $_ $_))
           
        ; Skill matching rule
        (= (HasRelevantSkill $user-id $skill-name)
           (HasSkill $user-id $skill-name $_))
           
        ; Contribution verification rule base
        (= (CanVerify $contribution-id)
           (and (Contribution $contribution-id $user-id $_)
                (HasIdentity $user-id)
                (HasEvidence $contribution-id $_)))
        '''
        
        run_metta_query(rules)
        self._track_atom(rules)
        
        # Load token award rules
        self._load_token_rules()
        
        # Load rules from files if available
        core_rules_path = os.path.join(self.rules_dir, 'core_rules.metta')
        if os.path.exists(core_rules_path):
            with open(core_rules_path, 'r') as f:
                rules = f.read()
                run_metta_query(rules)
                self._track_atom(rules)
    
    def _load_token_rules(self):
        """Load rules for token awards"""
        rules = '''
        ; Auto-award rule with confidence scoring
        (= (AutoAward $user-id $contribution-id)
           (let* (($verified (VerifyContribution $contribution-id))
                  ($confidence (CalculateConfidence $contribution-id))
                  ($base-amount 50)
                  ($bonus (* $confidence 50))
                  ($total (+ $base-amount $bonus)))
             (if $verified
                 (IncreaseToken $user-id $total)
                 (TokenBalance $user-id (GetTokenBalance $user-id)))))
        
        ; Default confidence calculation
        (= (CalculateConfidence $contribution-id)
           (let* (($evidence-count (CountEvidence $contribution-id))
                  ($verification-count (CountVerifications $contribution-id))
                  ($base-confidence 0.5)
                  ($evidence-factor (* $evidence-count 0.1))
                  ($verification-factor (* $verification-count 0.2)))
             (min 1.0 (+ $base-confidence $evidence-factor $verification-factor))))
        '''
        
        run_metta_query(rules)
        self._track_atom(rules)
    
    def _load_serialized_space(self, path):
        """
        Load serialized MeTTa space from JSON
        
        This is a custom implementation since PyMeTTa doesn't directly
        support serialization/deserialization yet.
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Process each atom in the serialized data
            for atom_str in data.get('atoms', []):
                run_metta_query(atom_str)
                self._track_atom(atom_str)
                
        except Exception as e:
            print(f"Error deserializing MeTTa space: {e}")
    
    def _serialize_space(self):
        """
        Serialize current MeTTa space to a JSON structure
        
        Returns:
            dict: Serialized representation of the space
        """
        return {
            "atoms": self.added_atoms,
            "version": "1.0"
        }
    
    def save_to_file(self, path=None):
        """
        Save MeTTa space to a file
        
        Args:
            path (str, optional): Path to save the file, defaults to self.db_path
        """
        save_path = path or self.db_path
        if save_path:
            serialized = self._serialize_space()
            
            # Make directory if there's a directory part in the path
            dir_path = os.path.dirname(save_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                
            with open(save_path, 'w') as f:
                json.dump(serialized, f, indent=2)
    
    def define_user(self, user_id, username=None):
        """
        Define a user in MeTTa
        
        Args:
            user_id (str): User ID
            username (str, optional): Username
        
        Returns:
            str: The atom expression
        """
        username_str = f'"{username}"' if username else '"anonymous"'
        atom = f'(User "{user_id}" {username_str})'
        run_metta_query(atom)
        self._track_atom(atom)
        return atom
    
    def add_skill(self, user_id, skill, level=1):
        """
        Add a skill to a user's profile
        
        Args:
            user_id (str): User ID
            skill (str): Skill name
            level (int, optional): Skill level (1-5)
        
        Returns:
            str: The atom expression
        """
        atom = f'(HasSkill "{user_id}" "{skill}" {level})'
        run_metta_query(atom)
        self._track_atom(atom)
        return atom
    
    def add_contribution(self, contribution_id, user_id, category, title=None):
        """
        Record a contribution
        
        Args:
            contribution_id (str): Contribution ID
            user_id (str): User ID
            category (str): Contribution category
            title (str, optional): Contribution title
        
        Returns:
            str: The atom expression
        """
        atom = f'(Contribution "{contribution_id}" "{user_id}" "{category}")'
        run_metta_query(atom)
        self._track_atom(atom)
        
        if title:
            title_atom = f'(ContributionTitle "{contribution_id}" "{title}")'
            run_metta_query(title_atom)
            self._track_atom(title_atom)
            
        return atom
    
    def _add_contribution_from_data(self, contribution_id, data):
        """
        Add contribution data to MeTTa space from dictionary
        
        Args:
            contribution_id (str): Contribution ID
            data (dict): Contribution data
        """
        try:
            user_id = data.get('user_id', '')
            category = data.get('category', 'other')
            title = data.get('title')
            
            # Add the contribution to MeTTa space
            self.add_contribution(contribution_id, user_id, category, title)
            
            # Add evidence if provided
            evidence_list = data.get('evidence', [])
            if isinstance(evidence_list, list):
                for i, evidence in enumerate(evidence_list):
                    if isinstance(evidence, dict):
                        evidence_type = evidence.get('type', 'url')
                        evidence_url = evidence.get('url', '')
                        evidence_id = evidence.get('id', f"evidence-{contribution_id}-{i}")
                        
                        if evidence_url:
                            self.add_evidence(contribution_id, evidence_type, evidence_url, evidence_id)
        except Exception as e:
            print(f"Error adding contribution from data: {e}")
    
    def add_evidence(self, contribution_id, evidence_type, evidence_url, evidence_id=None):
        """
        Add evidence for a contribution
        
        Args:
            contribution_id (str): Contribution ID
            evidence_type (str): Type of evidence (e.g., "github", "certificate")
            evidence_url (str): URL to the evidence
            evidence_id (str, optional): Unique ID for the evidence
        
        Returns:
            str: The atom expression
        """
        evidence_id = evidence_id or f"evidence-{contribution_id}-{evidence_type}"
        atom = f'(Evidence "{evidence_id}" "{contribution_id}" "{evidence_type}" "{evidence_url}")'
        run_metta_query(atom)
        self._track_atom(atom)
        return atom
    
    def verify_contribution(self, contribution_id, organization, verifier_id=None):
        """
        Record a contribution verification by an organization
        
        Args:
            contribution_id (str): Contribution ID
            organization (str): Verifying organization
            verifier_id (str, optional): ID of the verifier
            
        Returns:
            str: The atom expression
        """
        verifier_part = f'"{verifier_id}"' if verifier_id else 'None'
        atom = f'(HasVerification "{contribution_id}" "{organization}" {verifier_part})'
        run_metta_query(atom)
        self._track_atom(atom)
        return atom
    
    def set_token_balance(self, user_id, balance):
        """
        Set token balance for a user
        
        Args:
            user_id (str): User ID
            balance (int): Token balance
            
        Returns:
            str: The atom expression
        """
        atom = f'(TokenBalance "{user_id}" {balance})'
        run_metta_query(atom)
        self._track_atom(atom)
        return atom
    
    def auto_award(self, user_id, contribution_id):
        """
        Apply the autonomous agent logic for automatic token awards
        
        Args:
            user_id (str): User ID
            contribution_id (str): Contribution ID
            
        Returns:
            object: MeTTa result object
        """
        # Make sure the contribution exists and is linked to the user
        contribution_check = run_metta_query(
            f'!(match (Contribution "{contribution_id}" "{user_id}" $_) "exists")'
        )
        
        if not contribution_check or "exists" not in contribution_check:
            return None
            
        # Execute the auto-award rule
        result = run_metta_query(
            f'!(AutoAward "{user_id}" "{contribution_id}")'
        )
        
        return result
    
    def calculate_contribution_confidence(self, contribution_id):
        """
        Calculate confidence score for a contribution
        
        Args:
            contribution_id (str): Contribution ID
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        result = run_metta_query(
            f'!(CalculateConfidence "{contribution_id}")'
        )
        
        if result:
            try:
                # Extract numeric value from result
                match = re.search(r'(0\.\d+|1\.0)', result)
                if match:
                    return float(match.group(0))
                return 0.5
            except (ValueError, TypeError):
                return 0.5
        
        return 0.5
    
    def validate_contribution(self, contribution_id, contribution_data=None):
        """
        Validate a contribution using MeTTa reasoning
        
        Args:
            contribution_id (str): Contribution ID
            contribution_data (dict, optional): Contribution data to add first
            
        Returns:
            dict: Validation result with confidence and explanation
        """
        # If contribution data is provided, add it to MeTTa space first
        if contribution_data:
            self._add_contribution_from_data(contribution_id, contribution_data)
        
        # Check if contribution exists - use simpler syntax
        contribution_check = run_metta_query(
            f'!(match (Contribution "{contribution_id}" $_ $_) "exists")'
        )
        
        if not contribution_check or "exists" not in contribution_check:
            return {
                "valid": False,
                "confidence": 0.0,
                "explanation": "Contribution not found"
            }
        
        # Check if contribution can be verified
        can_verify = run_metta_query(
            f'!(CanVerify "{contribution_id}")'
        )
        
        if not can_verify or "True" not in can_verify:
            return {
                "valid": False,
                "confidence": 0.0,
                "explanation": "Cannot verify contribution - missing required elements"
            }
            
        # Execute verification query
        result = run_metta_query(
            f'!(VerifyContribution "{contribution_id}")'
        )
        
        # Calculate confidence
        confidence = self.calculate_contribution_confidence(contribution_id)
        
        # Generate explanation (if we had an explanation generator rule)
        explanation = "Contribution validation complete"
        if result and "True" in result:
            explanation = "Contribution validated successfully with sufficient evidence"
        else:
            explanation = "Contribution failed validation checks"
            
        return {
            "valid": bool(result and "True" in result),
            "confidence": confidence,
            "explanation": explanation
        }
    
    def query_user_contributions(self, user_id):
        """
        Query all contributions for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of contribution IDs
        """
        # Use simpler MeTTa query syntax without &self
        results = run_metta_query(
            f'!(match (Contribution $id "{user_id}" $_) $id)'
        )
        
        # Parse results into a list of contribution IDs
        contribution_ids = []
        if results:
            # Simple parsing of the output from MeTTa REPL
            # Looking for patterns like "contribution-1", "contribution-2"
            matches = re.findall(r'"([^"]+)"', results)
            contribution_ids.extend(matches)
        
        return contribution_ids
    
    def query_token_balance(self, user_id):
        """
        Query token balance for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: Token balance or 0 if not found
        """
        # Use simpler MeTTa query syntax without &self
        result = run_metta_query(
            f'!(match (TokenBalance "{user_id}" $balance) $balance)'
        )
        
        if result:
            # Extract the balance using regex
            match = re.search(r'\d+', result)
            if match:
                try:
                    return int(match.group(0))
                except (ValueError, TypeError):
                    return 0
        
        return 0
    
    def sync_user_to_metta(self, user):
        """
        Sync a user from the SQL database to MeTTa representation
        
        Args:
            user: User model instance
        """
        self.define_user(user.id, user.username)
        
        if hasattr(user, 'skills') and user.skills:
            for skill in user.skills:
                self.add_skill(user.id, skill.name, skill.level)
        
        if hasattr(user, 'tokens') and user.tokens:
            self.set_token_balance(user.id, user.tokens.balance)
        
        if hasattr(user, 'contributions') and user.contributions:
            for contribution in user.contributions:
                self.add_contribution(
                    contribution.id, 
                    user.id,
                    contribution.category,
                    contribution.title
                )
                
                if hasattr(contribution, 'evidence') and contribution.evidence:
                    for evidence in contribution.evidence:
                        self.add_evidence(
                            contribution.id,
                            evidence.type,
                            evidence.url,
                            evidence.id
                        )
                
                if hasattr(contribution, 'verifications') and contribution.verifications:
                    for verification in contribution.verifications:
                        self.verify_contribution(
                            contribution.id,
                            verification.organization,
                            verification.verifier_id
                        )
    
    def sync_all_users(self, users):
        """
        Sync all users from SQL database to MeTTa representation
        
        Args:
            users: List of User model instances
        """
        for user in users:
            self.sync_user_to_metta(user)
            
        # Save updated state
        if self.db_path:
            self.save_to_file()
    
    def _track_atom(self, atom):
        """Track atoms added to the space for serialization"""
        if atom not in self.added_atoms:
            self.added_atoms.append(atom)