"""
MeTTa Reasoning Service for Nimo Platform

This service implements enhanced reasoning capabilities for the Nimo platform
using MeTTa language for autonomous verification, reputation scoring, and
token award calculations.

Updated based on research findings: docs/metta_research_findings.md
"""

import json
import hashlib
import os
from typing import Dict, List, Any, Optional, Tuple, Union

# Try importing hyperon (official MeTTa implementation)
try:
    from hyperon import MeTTa, S, V, E, SymbolAtom, ExpressionAtom
    METTA_AVAILABLE = True
    METTA_TYPE = "hyperon"
except ImportError:
    # Fallback to pymetta if hyperon is not available
    try:
        import pymetta
        METTA_AVAILABLE = True
        METTA_TYPE = "pymetta"
    except ImportError:
        METTA_AVAILABLE = False
        METTA_TYPE = None
        print("Warning: No MeTTa implementation available. Using mock implementation.")

class MeTTaReasoning:
    def __init__(self, rules_dir=None, db_path=None):
        """
        Initialize MeTTa reasoning service
        
        Args:
            rules_dir (str, optional): Directory containing MeTTa rule files
            db_path (str, optional): Path to save/load MeTTa space serialization
        """
        self.rules_dir = rules_dir or os.path.join(os.path.dirname(__file__), '../rules')
        self.db_path = db_path
        self.cache = {}
        self.added_atoms = []
        
        # Initialize MeTTa space based on available implementation
        if METTA_AVAILABLE:
            if METTA_TYPE == "hyperon":
                self.space = MeTTa()
                self.metta_api = "hyperon"
            else:  # pymetta
                self.space = pymetta.MeTTa()
                self.metta_api = "pymetta"
        else:
            self.space = None
            self.metta_api = "mock"
            print("Using mock MeTTa implementation")
        
        # Load MeTTa definitions if path provided
        if self.db_path and os.path.exists(self.db_path):
            try:
                self._load_serialized_space(self.db_path)
            except Exception as e:
                print(f"Error loading MeTTa store: {e}")
        
        # Initialize core reasoning rules
        self._initialize_core_rules()
    
    def _execute_metta(self, metta_code: str) -> Any:
        """
        Universal method to execute MeTTa code regardless of implementation
        
        Args:
            metta_code (str): MeTTa code to execute
            
        Returns:
            Any: Result of execution
        """
        if self.metta_api == "hyperon":
            try:
                # Use hyperon API
                result = self.space.run(metta_code)
                return result
            except Exception as e:
                print(f"Hyperon execution error: {e}")
                return None
        elif self.metta_api == "pymetta":
            try:
                # Use pymetta API
                result = self.space.parse_and_eval(metta_code)
                return result
            except Exception as e:
                print(f"PyMeTTa execution error: {e}")
                return None
        else:
            # Mock implementation for testing
            print(f"Mock MeTTa execution: {metta_code}")
            return self._mock_metta_execution(metta_code)
    
    def _mock_metta_execution(self, metta_code: str) -> Any:
        """
        Mock implementation for testing when MeTTa is not available
        
        Args:
            metta_code (str): MeTTa code to mock
            
        Returns:
            Any: Mock result
        """
        # Simple pattern matching for common queries
        if "verify-with-confidence" in metta_code:
            return {
                'verified': True,
                'confidence': 0.8,
                'factors': {
                    'evidence_type': 'github',
                    'user_reputation': 75,
                    'past_contributions': 5,
                    'verification_rate': 0.8
                }
            }
        elif "verify-contribution" in metta_code:
            return True
        elif "calculate-token-award" in metta_code:
            return 50
        elif "calculate-confidence" in metta_code:
            return 0.8
        elif "detect-fraud" in metta_code:
            return False
        elif "generate-explanation" in metta_code:
            return "Contribution verified based on provided evidence and user reputation."
        elif "User" in metta_code and "$_" in metta_code:
            return True  # Mock user exists
        elif "Contribution" in metta_code and "$_" in metta_code:
            return True  # Mock contribution exists
        else:
            return None
    
    def _add_to_space(self, atom: str) -> None:
        """
        Add atom to MeTTa space using appropriate API
        
        Args:
            atom (str): Atom to add to space
        """
        if self.metta_api == "hyperon":
            try:
                # For hyperon, we need to parse and add the atom
                self.space.add_parse(atom)
            except Exception as e:
                print(f"Error adding atom to hyperon space: {e}")
        elif self.metta_api == "pymetta":
            try:
                # For pymetta, use parse_and_eval
                self.space.parse_and_eval(atom)
            except Exception as e:
                print(f"Error adding atom to pymetta space: {e}")
        # For mock, we just track the atom
        self._track_atom(atom)
    
    def _load_serialized_space(self, path: str) -> None:
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
                self._add_to_space(atom_str)
                
            # Restore added atoms tracking
            self.added_atoms = data.get('atoms', [])
                
        except Exception as e:
            print(f"Error deserializing MeTTa space: {e}")
    
    def save_to_file(self, path: str = None) -> None:
        """
        Save MeTTa space to a file
        
        Args:
            path (str, optional): Path to save the file, defaults to self.db_path
        """
        save_path = path or self.db_path
        if save_path:
            serialized = {
                "atoms": self.added_atoms,
                "version": "1.0"
            }
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(serialized, f, indent=2)
    
    def _initialize_core_rules(self) -> None:
        """Initialize core MeTTa reasoning rules"""
        # Load core rules from file if available
        core_rules_path = os.path.join(self.rules_dir, 'core_rules.metta')
        if os.path.exists(core_rules_path):
            with open(core_rules_path, 'r') as f:
                rules = f.read()
                self._execute_metta(rules)
                print(f"Loaded core rules from {core_rules_path}")
                return
                
        # If rules file not found, define rules directly
        print(f"Core rules file not found at {core_rules_path}, defining rules directly")
                
        # Initialize base verification rule
        self._implement_core_reasoning()
        
        # Initialize confidence scoring
        self._implement_confidence_scoring()
        
        # Initialize explanation generation
        self._implement_explanation_generator()
        
        # Initialize fraud detection
        self._implement_fraud_detection()
    
    def _implement_core_reasoning(self) -> None:
        """Implement core verification reasoning rules"""
        # Enhanced verification rule for contributions with fraud detection
        verification_rule = '''
        (= (verify-contribution $user $contrib $evidence)
           (and 
             (valid-evidence $evidence)
             (skill-match $user $contrib)
             (impact-assessment $contrib "moderate")
             (not (detect-fraud $contrib $user))))
        '''
        self._add_to_space(verification_rule)
        
        # Enhanced evidence validation rule with quality scoring
        evidence_rule = '''
        (= (valid-evidence $evidence)
           (and
             (or
               (github-repository $evidence)
               (website-with-proof $evidence)
               (document-with-signature $evidence)
               (video-evidence $evidence)
               (image-evidence $evidence))
             (evidence-quality-sufficient $evidence)))
        '''
        self._add_to_space(evidence_rule)
        
        # GitHub repository validation
        github_rule = '''
        (= (github-repository $evidence)
           (and 
             (contains? $evidence "url")
             (starts-with? (get-field $evidence "url") "https://github.com/")))
        '''
        self._add_to_space(github_rule)
        
        # Website with proof validation
        website_rule = '''
        (= (website-with-proof $evidence)
           (and 
             (contains? $evidence "url")
             (contains? $evidence "description")
             (not (empty? (get-field $evidence "description")))))
        '''
        self._add_to_space(website_rule)
        
        # Document with signature validation
        document_rule = '''
        (= (document-with-signature $evidence)
           (and 
             (contains? $evidence "document_url")
             (contains? $evidence "signature")
             (valid-signature? (get-field $evidence "signature"))))
        '''
        self._add_to_space(document_rule)
        
        # Video evidence validation
        video_rule = '''
        (= (video-evidence $evidence)
           (and 
             (contains? $evidence "url")
             (contains? $evidence "type")
             (== (get-field $evidence "type") "video")))
        '''
        self._add_to_space(video_rule)
        
        # Image evidence validation
        image_rule = '''
        (= (image-evidence $evidence)
           (and 
             (contains? $evidence "url")
             (contains? $evidence "type")
             (== (get-field $evidence "type") "image")))
        '''
        self._add_to_space(image_rule)
        
        # Evidence quality assessment
        quality_rule = '''
        (= (evidence-quality-sufficient $evidence)
           (let (($quality-score (calculate-evidence-quality $evidence)))
             (>= $quality-score 0.6)))
        '''
        self._add_to_space(quality_rule)
        
        # Skill match check
        skill_match_rule = '''
        (= (skill-match $user $contrib)
           (let (($contrib-skills (get-field $contrib "required_skills"))
                 ($user-skills (get-skills $user)))
             (has-any-skill? $user-skills $contrib-skills)))
        '''
        self._add_to_space(skill_match_rule)
        
        # Has any skill helper
        has_skill_rule = '''
        (= (has-any-skill? $user-skills $contrib-skills)
           (or
             (empty? $contrib-skills)
             (contains-any? $user-skills $contrib-skills)))
        '''
        self._add_to_space(has_skill_rule)
        
        # Impact assessment rule
        impact_rule = '''
        (= (impact-assessment $contrib $min-level)
           (let (($impact (get-field $contrib "impact")))
             (impact-level-sufficient? $impact $min-level)))
        '''
        self._add_to_space(impact_rule)
        
        # Impact level check
        impact_level_rule = '''
        (= (impact-level-sufficient? $actual $minimum)
           (let (($impact-levels '("minimal" "moderate" "significant" "transformative")))
             (>= (position $actual $impact-levels)
                 (position $minimum $impact-levels))))
        '''
        self._add_to_space(impact_level_rule)
        
        # Token award calculation
        token_rule = '''
        (= (calculate-token-award $contrib-type)
           (match $contrib-type
             ("coding" 75)
             ("education" 60)
             ("volunteer" 50)
             ("activism" 65)
             ("leadership" 70)
             ("entrepreneurship" 80)
             ("environmental" 70)
             ("community" 60)
             (_ 50)))
        '''
        self._add_to_space(token_rule)
    
    def _implement_confidence_scoring(self) -> None:
        """Implement confidence scoring for decisions"""
        # Base confidence calculation
        confidence_rule = '''
        (= (calculate-confidence $factors)
           (let* (($evidence-score (get-evidence-score $factors))
                  ($reputation-score (get-reputation-score $factors))
                  ($consistency-score (get-consistency-score $factors)))
             (/ (+ $evidence-score $reputation-score $consistency-score) 3.0)))
        '''
        self._add_to_space(confidence_rule)
        
        # Evidence score calculation
        evidence_score_rule = '''
        (= (get-evidence-score $factors)
           (let (($evidence-type (get-field $factors "evidence_type")))
             (match $evidence-type
               ("github" 0.9)
               ("website" 0.6)
               ("document" 0.7)
               ("image" 0.5)
               ("video" 0.8)
               (_ 0.4))))
        '''
        self._add_to_space(evidence_score_rule)
        
        # Reputation score calculation
        reputation_score_rule = '''
        (= (get-reputation-score $factors)
           (let (($user-reputation (get-field $factors "user_reputation")))
             (min 1.0 (/ $user-reputation 100.0))))
        '''
        self._add_to_space(reputation_score_rule)
        
        # Consistency score calculation
        consistency_score_rule = '''
        (= (get-consistency-score $factors)
           (let (($past-contributions (get-field $factors "past_contributions"))
                 ($verification-rate (get-field $factors "verification_rate")))
             (if (< $past-contributions 3)
                 0.5
                 (min 1.0 $verification-rate))))
        '''
        self._add_to_space(consistency_score_rule)
        
        # Use confidence in verification
        verification_with_confidence = '''
        (= (verify-with-confidence $user $contrib $evidence)
           (let* (($factors (collect-verification-factors $user $contrib $evidence))
                  ($verified (verify-contribution $user $contrib $evidence))
                  ($confidence (calculate-confidence $factors)))
             (object "verified" $verified "confidence" $confidence "factors" $factors)))
        '''
        self._add_to_space(verification_with_confidence)
        
        # Collect verification factors helper
        collect_factors_rule = '''
        (= (collect-verification-factors $user $contrib $evidence)
           (object
             "evidence_type" (get-evidence-type $evidence)
             "user_reputation" (get-user-reputation $user)
             "past_contributions" (count-user-contributions $user)
             "verification_rate" (get-user-verification-rate $user)
             "contribution_quality" (assess-contribution-quality $contrib)))
        '''
        self._add_to_space(collect_factors_rule)
    
    def _implement_explanation_generator(self) -> None:
        """Implement explanation generator for MeTTa decisions"""
        explanation_rule = '''
        (= (generate-explanation $decision)
           (let* (($verified (get-field $decision "verified"))
                  ($confidence (get-field $decision "confidence"))
                  ($factors (get-field $decision "factors")))
             (if $verified
                 (format-positive-explanation $confidence $factors)
                 (format-negative-explanation $confidence $factors))))
        '''
        self._add_to_space(explanation_rule)
        
        # Format positive explanation
        positive_template = '''
        (= (format-positive-explanation $confidence $factors)
           (let* (($primary-factor (get-primary-factor $factors))
                  ($formatted-confidence (format-percentage $confidence)))
             (string-append 
               "Contribution verified with " $formatted-confidence " confidence. "
               "Key factor: " $primary-factor)))
        '''
        self._add_to_space(positive_template)
        
        # Format negative explanation
        negative_template = '''
        (= (format-negative-explanation $confidence $factors)
           (let* (($reason (get-rejection-reason $factors))
                  ($formatted-confidence (format-percentage $confidence)))
             (string-append 
               "Contribution could not be verified with sufficient confidence (" $formatted-confidence "). "
               "Reason: " $reason)))
        '''
        self._add_to_space(negative_template)
        
        # Get primary factor helper
        primary_factor_rule = '''
        (= (get-primary-factor $factors)
           (let (($evidence-type (get-field $factors "evidence_type")))
             (match $evidence-type
               ("github" "Strong GitHub repository evidence")
               ("website" "Website evidence")
               ("document" "Documented proof")
               ("image" "Image evidence")
               ("video" "Video evidence")
               (_ "Provided evidence"))))
        '''
        self._add_to_space(primary_factor_rule)
        
        # Format percentage helper
        format_percentage_rule = '''
        (= (format-percentage $value)
           (string-append (number->string (round (* $value 100))) "%"))
        '''
        self._add_to_space(format_percentage_rule)
    
    def _implement_fraud_detection(self) -> None:
        """Implement fraud detection patterns in MeTTa"""
        # Base fraud detection
        fraud_patterns = '''
        (= (detect-fraud $contrib $user)
           (or
             (duplicate-submission $contrib $user)
             (suspicious-activity-pattern $user)
             (evidence-inconsistency $contrib)))
        '''
        self._add_to_space(fraud_patterns)
        
        # Duplicate submission detection
        duplicate_detection = '''
        (= (duplicate-submission $contrib $user)
           (let* (($user-contribs (get-user-contributions $user))
                  ($similar-contrib (find-similar-contribution $contrib $user-contribs 0.8)))
             (not (equal? $similar-contrib #f))))
        '''
        self._add_to_space(duplicate_detection)
        
        # Suspicious activity pattern
        suspicious_pattern = '''
        (= (suspicious-activity-pattern $user)
           (let* (($submission-times (get-submission-times $user))
                  ($avg-interval (calculate-average-interval $submission-times)))
             (< $avg-interval 3600)))  ;; Less than 1 hour between submissions
        '''
        self._add_to_space(suspicious_pattern)
        
        # Evidence inconsistency check
        evidence_inconsistency = '''
        (= (evidence-inconsistency $contrib)
           (let* (($evidence (get-field $contrib "evidence"))
                  ($metadata (get-field $contrib "metadata"))
                  ($dates-consistent (check-date-consistency $evidence $metadata))
                  ($author-consistent (check-author-consistency $evidence $contrib)))
             (not (and $dates-consistent $author-consistent))))
        '''
        self._add_to_space(evidence_inconsistency)
    
    def verify_contribution(self, user_id: str, contribution_id: str, 
                          evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify a contribution using MeTTa reasoning
        
        Args:
            user_id (str): User ID
            contribution_id (str): Contribution ID
            evidence (Dict[str, Any], optional): Evidence data
            
        Returns:
            Dict[str, Any]: Verification result with confidence and explanation
        """
        # Ensure entities exist in MeTTa space
        self._ensure_entities_in_space(user_id, contribution_id, evidence)
        
        # Try to use atom-based approach first (preferred)
        try:
            # Execute verification using atom-based rules (from core_rules.metta)
            result = self._execute_metta(f'(VerifyWithConfidence "{contribution_id}")')
            
            if result:
                verified = bool(result.get_args()[1])
                confidence = float(result.get_args()[2])
                explanation = str(result.get_args()[3])
                
                # Calculate token award
                tokens = self._calculate_token_award(contribution_id)
                
                return {
                    'verified': verified,
                    'confidence': confidence,
                    'explanation': explanation,
                    'tokens': tokens,
                    'metta_proof': self._generate_proof({
                        'verified': verified,
                        'confidence': confidence,
                        'contribution_id': contribution_id,
                        'user_id': user_id
                    })
                }
        except Exception as e:
            print(f"Atom-based verification failed: {e}, falling back to object-based approach")
        
        # Fallback to object-based approach if atom-based fails
        # Get user and contribution data
        user_data = self._get_user_data(user_id)
        contrib_data = self._get_contribution_data(contribution_id)
        evidence_data = self._process_evidence(evidence or {})
        
        # Convert to MeTTa format
        user_atom = self._to_metta_user(user_data)
        contrib_atom = self._to_metta_contribution(contrib_data)
        evidence_atom = self._to_metta_evidence(evidence_data)
        
        # Execute verification
        result = self._execute_metta(f'(verify-with-confidence {user_atom} {contrib_atom} {evidence_atom})')
        
        # Generate explanation
        explanation = self._execute_metta(f'(generate-explanation {result})')
        
        # Calculate token award
        tokens = self._execute_metta(f'(calculate-token-award "{contrib_data["type"]}")')
        
        return {
            'verified': result['verified'],
            'confidence': result['confidence'],
            'explanation': explanation,
            'tokens': tokens,
            'metta_proof': self._generate_proof(result)
        }
        
    def _ensure_entities_in_space(self, user_id: str, contribution_id: str, evidence: Dict[str, Any] = None) -> None:
        """
        Ensure user, contribution, and evidence are defined in MeTTa space
        
        Args:
            user_id (str): User ID
            contribution_id (str): Contribution ID
            evidence (Dict[str, Any], optional): Evidence data
        """
        # Check if user exists in space
        user_exists = self._execute_metta(f'(User "{user_id}" $_)')
        if not user_exists:
            # Add user to space
            user_data = self._get_user_data(user_id)
            self._add_user_to_space(user_id, user_data)
            
        # Check if contribution exists in space
        contrib_exists = self._execute_metta(f'(Contribution "{contribution_id}" $_ $_)')
        if not contrib_exists:
            # Add contribution to space
            contrib_data = self._get_contribution_data(contribution_id)
            self._add_contribution_to_space(contribution_id, user_id, contrib_data)
            
        # Add evidence if provided
        if evidence:
            evidence_data = self._process_evidence(evidence)
            self._add_evidence_to_space(contribution_id, evidence_data)
    
    def _add_user_to_space(self, user_id: str, user_data: Dict[str, Any]) -> None:
        """
        Add user to MeTTa space
        
        Args:
            user_id (str): User ID
            user_data (Dict[str, Any]): User data
        """
        username = user_data.get('username', 'anonymous')
        atom = f'(User "{user_id}" "{username}")'
        self._add_to_space(atom)
        
        # Add skills
        for skill in user_data.get('skills', []):
            skill_name = skill
            skill_level = 1
            
            if isinstance(skill, dict):
                skill_name = skill.get('name', '')
                skill_level = skill.get('level', 1)
                
            skill_atom = f'(HasSkill "{user_id}" "{skill_name}" {skill_level})'
            self._add_to_space(skill_atom)
    
    def _add_contribution_to_space(self, contribution_id: str, user_id: str, contrib_data: Dict[str, Any]) -> None:
        """
        Add contribution to MeTTa space
        
        Args:
            contribution_id (str): Contribution ID
            user_id (str): User ID
            contrib_data (Dict[str, Any]): Contribution data
        """
        category = contrib_data.get('type', contrib_data.get('category', 'other'))
        
        atom = f'(Contribution "{contribution_id}" "{user_id}" "{category}")'
        self._add_to_space(atom)
        
        # Add title if available
        title = contrib_data.get('title', '')
        if title:
            title_atom = f'(ContributionTitle "{contribution_id}" "{title}")'
            self._add_to_space(title_atom)
            
        # Add impact level if available
        impact = contrib_data.get('impact', 'moderate')
        impact_atom = f'(ContributionImpact "{contribution_id}" "{impact}")'
        self._add_to_space(impact_atom)
    
    def _add_evidence_to_space(self, contribution_id: str, evidence_data: Dict[str, Any]) -> None:
        """
        Add evidence to MeTTa space
        
        Args:
            contribution_id (str): Contribution ID
            evidence_data (Dict[str, Any]): Evidence data
        """
        evidence_type = self._determine_evidence_type(evidence_data)
        evidence_url = evidence_data.get('url', evidence_data.get('document_url', ''))
        evidence_id = evidence_data.get('id', f"evidence-{contribution_id}-{evidence_type}")
        
        if evidence_url:
            atom = f'(Evidence "{evidence_id}" "{contribution_id}" "{evidence_type}" "{evidence_url}")'
            self._add_to_space(atom)
    
    def _determine_evidence_type(self, evidence_data: Dict[str, Any]) -> str:
        """
        Determine the type of evidence based on its data
        
        Args:
            evidence_data (Dict[str, Any]): Evidence data
            
        Returns:
            str: Evidence type ('github', 'website', 'document', etc.)
        """
        if 'type' in evidence_data:
            return evidence_data['type']
            
        url = evidence_data.get('url', '')
        if url and 'github.com' in url:
            return 'github'
        elif 'document_url' in evidence_data or 'signature' in evidence_data:
            return 'document'
        elif url:
            return 'website'
            
        return 'other'
        
    def _calculate_token_award(self, contribution_id: str) -> int:
        """
        Calculate token award amount for a contribution
        
        Args:
            contribution_id (str): Contribution ID
            
        Returns:
            int: Token award amount
        """
        # Try to calculate using atom-based approach
        try:
            result = self._execute_metta(f'(CalculateTokenAward "{contribution_id}")')
            if result:
                return int(float(result))
        except Exception:
            pass
            
        # Fallback to category-based calculation
        try:
            category_result = self._execute_metta(f'(GetContributionCategory "{contribution_id}")')
            if category_result:
                category = str(category_result)
                base_result = self._execute_metta(f'(BaseTokenAmount "{category}")')
                if base_result:
                    return int(float(base_result))
        except Exception:
            pass
            
        # Default amount if all else fails
        return 50
    
    def detect_fraudulent_activity(self, user_id: str, contribution_id: str) -> Dict[str, Any]:
        """Detect potentially fraudulent activity"""
        # Get user and contribution data
        user_data = self._get_user_data(user_id)
        contrib_data = self._get_contribution_data(contribution_id)
        
        # Convert to MeTTa format
        user_atom = self._to_metta_user(user_data)
        contrib_atom = self._to_metta_contribution(contrib_data)
        
        # Execute fraud detection
        is_fraud = self._execute_metta(f'(detect-fraud {contrib_atom} {user_atom})')
        
        if is_fraud:
            return {
                'is_fraud': True,
                'reason': self._determine_fraud_reason(user_id, contribution_id),
                'confidence': self._calculate_fraud_confidence(user_id, contribution_id)
            }
        
        return {'is_fraud': False}
    
    def calculate_reputation(self, user_id: str) -> float:
        """Calculate user reputation score based on contributions and verifications"""
        user_data = self._get_user_data(user_id)
        
        # Enhanced reputation calculation with temporal decay and quality weighting
        rep_calc = '''
        (= (calculate-user-reputation $user)
           (let* (($verified-contribs (count-verified-contributions $user))
                  ($skill-diversity (count-unique-skills $user))
                  ($community-endorsements (count-endorsements $user))
                  ($impact-score (average-impact-score $user))
                  ($recent-activity-bonus (recent-activity-bonus $user))
                  ($quality-multiplier (quality-multiplier $user)))
             (* (+ (* $verified-contribs 10)
                   (* $skill-diversity 5)
                   (* $community-endorsements 3)
                   (* $impact-score 7)
                   $recent-activity-bonus)
                $quality-multiplier)))
        '''
        self._add_to_space(rep_calc)
        
        # Define recent activity bonus
        activity_bonus = '''
        (= (recent-activity-bonus $user)
           (let (($days-since-last-contrib (days-since-last-contribution $user)))
             (if (< $days-since-last-contrib 30)
                 15
                 (if (< $days-since-last-contrib 90)
                     5
                     0))))
        '''
        self._add_to_space(activity_bonus)
        
        # Define quality multiplier
        quality_mult = '''
        (= (quality-multiplier $user)
           (let (($avg-confidence (average-verification-confidence $user)))
             (if (>= $avg-confidence 0.8)
                 1.2
                 (if (>= $avg-confidence 0.6)
                     1.0
                     0.8))))
        '''
        self._add_to_space(quality_mult)
        
        # Convert user to MeTTa format
        user_atom = self._to_metta_user(user_data)
        
        # Calculate reputation
        reputation = self._execute_metta(f'(calculate-user-reputation {user_atom})')
        
        return float(reputation)
    
    def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from database or cache"""
        # Implementation would query database
        # For now, return mock data
        return {
            "id": user_id,
            "skills": ["python", "web_development", "community_building"],
            "reputation": 75,
            "past_contributions": 5,
            "verification_rate": 0.8
        }
    
    def _get_contribution_data(self, contribution_id: str) -> Dict[str, Any]:
        """Get contribution data from database or cache"""
        # Implementation would query database
        # For now, return mock data
        return {
            "id": contribution_id,
            "title": "Python Web Development Workshop",
            "type": "education",
            "required_skills": ["python", "web_development"],
            "impact": "significant",
            "metadata": {
                "date": "2025-07-15",
                "location": "Nairobi",
                "participants": 25
            }
        }
    
    def _process_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate evidence data"""
        # Implementation would do additional processing
        # For now, return the evidence as is
        return evidence
    
    def _to_metta_user(self, user_data: Dict[str, Any]) -> str:
        """Convert user data to MeTTa atom representation"""
        user_str = json.dumps(user_data).replace('"', '\\"')
        return f'(parse-json "{user_str}")'
    
    def _to_metta_contribution(self, contrib_data: Dict[str, Any]) -> str:
        """Convert contribution data to MeTTa atom representation"""
        contrib_str = json.dumps(contrib_data).replace('"', '\\"')
        return f'(parse-json "{contrib_str}")'
    
    def _to_metta_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Convert evidence data to MeTTa atom representation"""
        evidence_str = json.dumps(evidence_data).replace('"', '\\"')
        return f'(parse-json "{evidence_str}")'
    
    def _generate_proof(self, result: Dict[str, Any]) -> str:
        """Generate a cryptographic proof of the MeTTa decision"""
        # Convert result to canonical form
        canonical = json.dumps(result, sort_keys=True)
        
        # Generate hash
        proof_hash = hashlib.sha256(canonical.encode()).hexdigest()
        
        return f"0x{proof_hash}"
    
    def _determine_fraud_reason(self, user_id: str, contribution_id: str) -> str:
        """Determine the reason for fraud detection"""
        # Implementation would involve MeTTa reasoning
        # For now, return a generic message
        return "Potential duplicate submission or suspicious activity pattern detected"
    
    def _calculate_fraud_confidence(self, user_id: str, contribution_id: str) -> float:
        """Calculate confidence of fraud detection"""
        # Implementation would involve MeTTa reasoning
        # For now, return a generic value
        return 0.75
    
    def _track_atom(self, atom: str) -> None:
        """
        Track atoms added to the space for serialization
        
        Args:
            atom (str): Atom expression to track
        """
        if atom not in self.added_atoms:
            self.added_atoms.append(atom)
    
    def add_user(self, user_id: str, username: str, skills: List[Dict[str, Any]] = None) -> None:
        """
        Add a user to MeTTa space
        
        Args:
            user_id (str): User ID
            username (str): Username
            skills (List[Dict[str, Any]], optional): List of skills with name and level
        """
        # Add user atom
        atom = f'(User "{user_id}" "{username}")'
        self._add_to_space(atom)
        
        # Add skills if provided
        if skills:
            for skill in skills:
                if isinstance(skill, dict):
                    skill_name = skill.get('name', '')
                    skill_level = skill.get('level', 1)
                    
                    skill_atom = f'(HasSkill "{user_id}" "{skill_name}" {skill_level})'
                    self._add_to_space(skill_atom)
                else:
                    skill_atom = f'(HasSkill "{user_id}" "{skill}" 1)'
                    self._add_to_space(skill_atom)
    
    def add_contribution(self, contribution_id: str, user_id: str, 
                       category: str, title: str = None, impact: str = None) -> None:
        """
        Add a contribution to MeTTa space
        
        Args:
            contribution_id (str): Contribution ID
            user_id (str): User ID
            category (str): Contribution category
            title (str, optional): Contribution title
            impact (str, optional): Impact level (minimal, moderate, significant, transformative)
        """
        # Add contribution atom
        atom = f'(Contribution "{contribution_id}" "{user_id}" "{category}")'
        self._add_to_space(atom)
        
        # Add title if provided
        if title:
            title_atom = f'(ContributionTitle "{contribution_id}" "{title}")'
            self._add_to_space(title_atom)
            
        # Add impact level if provided
        if impact:
            impact_atom = f'(ContributionImpact "{contribution_id}" "{impact}")'
            self._add_to_space(impact_atom)
    
    def add_evidence(self, contribution_id: str, evidence_type: str, 
                   evidence_url: str, evidence_id: str = None) -> None:
        """
        Add evidence for a contribution
        
        Args:
            contribution_id (str): Contribution ID
            evidence_type (str): Evidence type (github, website, document, etc.)
            evidence_url (str): URL to evidence
            evidence_id (str, optional): Evidence ID
        """
        evidence_id = evidence_id or f"evidence-{contribution_id}-{evidence_type}"
        
        atom = f'(Evidence "{evidence_id}" "{contribution_id}" "{evidence_type}" "{evidence_url}")'
        self._add_to_space(atom)
    
    def verify_contribution_with_explanation(self, contribution_id: str) -> Dict[str, Any]:
        """
        Verify a contribution and generate an explanation
        
        Args:
            contribution_id (str): Contribution ID
            
        Returns:
            Dict[str, Any]: Verification result with explanation
        """
        try:
            # Try atom-based approach first
            result = self._execute_metta(f'(VerifyWithConfidence "{contribution_id}")')
            
            if result:
                verified = bool(result.get_args()[1])
                confidence = float(result.get_args()[2])
                explanation = str(result.get_args()[3])
                
                return {
                    'verified': verified,
                    'confidence': confidence,
                    'explanation': explanation
                }
        except Exception:
            # Fallback to checking if the contribution can be verified
            can_verify = self._execute_metta(f'(CanVerify "{contribution_id}")')
            if can_verify:
                return {
                    'verified': True,
                    'confidence': 0.7,
                    'explanation': "Contribution has sufficient evidence"
                }
            else:
                return {
                    'verified': False,
                    'confidence': 0.3,
                    'explanation': "Contribution lacks sufficient evidence"
                }
    
    def calculate_user_reputation(self, user_id: str) -> int:
        """
        Calculate reputation score for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: Reputation score
        """
        try:
            # Try atom-based approach first
            result = self._execute_metta(f'(CalculateUserReputation "{user_id}")')
            
            if result:
                return int(float(result))
        except Exception:
            pass
        
        # Fallback to the older approach
        return self.calculate_reputation(user_id)
    
    def cached_query(self, query_key: str, query_func, *args, **kwargs):
        """
        Cache results of expensive queries
        
        Args:
            query_key (str): Cache key
            query_func: Function to call if cache miss
            *args, **kwargs: Arguments to pass to query_func
            
        Returns:
            Any: Query result
        """
        if query_key in self.cache:
            return self.cache[query_key]
        
        result = query_func(*args, **kwargs)
        self.cache[query_key] = result
        return result
        
    def batch_verify_contributions(self, contribution_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch verify multiple contributions for improved performance
        
        Args:
            contribution_batch (List[Dict[str, Any]]): List of contributions to verify
            
        Returns:
            List[Dict[str, Any]]: List of verification results
        """
        results = []
        
        # Pre-load all users and contributions into MeTTa space
        for contrib_data in contribution_batch:
            user_id = contrib_data.get('user_id')
            contribution_id = contrib_data.get('contribution_id') 
            evidence = contrib_data.get('evidence', {})
            
            if user_id and contribution_id:
                self._ensure_entities_in_space(user_id, contribution_id, evidence)
        
        # Process verifications in batch
        for contrib_data in contribution_batch:
            user_id = contrib_data.get('user_id')
            contribution_id = contrib_data.get('contribution_id')
            evidence = contrib_data.get('evidence', {})
            
            if user_id and contribution_id:
                try:
                    result = self.verify_contribution(user_id, contribution_id, evidence)
                    result['contribution_id'] = contribution_id
                    result['user_id'] = user_id
                    results.append(result)
                except Exception as e:
                    results.append({
                        'contribution_id': contribution_id,
                        'user_id': user_id,
                        'verified': False,
                        'error': str(e),
                        'confidence': 0.0
                    })
        
        return results
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """
        Get statistics about verification performance and patterns
        
        Returns:
            Dict[str, Any]: Verification statistics
        """
        try:
            # Query MeTTa space for statistics
            total_verifications = self._execute_metta('(CountTotalVerifications)')
            successful_verifications = self._execute_metta('(CountSuccessfulVerifications)')
            average_confidence = self._execute_metta('(AverageConfidenceScore)')
            fraud_detections = self._execute_metta('(CountFraudDetections)')
            
            success_rate = successful_verifications / total_verifications if total_verifications > 0 else 0
            fraud_rate = fraud_detections / total_verifications if total_verifications > 0 else 0
            
            return {
                'total_verifications': int(total_verifications or 0),
                'successful_verifications': int(successful_verifications or 0),
                'success_rate': float(success_rate),
                'average_confidence': float(average_confidence or 0),
                'fraud_detections': int(fraud_detections or 0),
                'fraud_rate': float(fraud_rate)
            }
        except Exception:
            # Return default stats if MeTTa queries fail
            return {
                'total_verifications': 0,
                'successful_verifications': 0,
                'success_rate': 0.0,
                'average_confidence': 0.0,
                'fraud_detections': 0,
                'fraud_rate': 0.0
            }
    
    def export_reasoning_trace(self, contribution_id: str) -> Dict[str, Any]:
        """
        Export detailed reasoning trace for a contribution verification
        
        Args:
            contribution_id (str): Contribution ID
            
        Returns:
            Dict[str, Any]: Detailed reasoning trace
        """
        try:
            # Get verification result with full trace
            result = self.verify_contribution_with_explanation(contribution_id)
            
            # Get additional trace information
            evidence_analysis = self._execute_metta(f'(AnalyzeEvidence "{contribution_id}")')
            skill_analysis = self._execute_metta(f'(AnalyzeSkillMatch "{contribution_id}")')
            fraud_analysis = self._execute_metta(f'(AnalyzeFraudRisk "{contribution_id}")')
            
            return {
                'contribution_id': contribution_id,
                'verification_result': result,
                'evidence_analysis': str(evidence_analysis) if evidence_analysis else None,
                'skill_analysis': str(skill_analysis) if skill_analysis else None,
                'fraud_analysis': str(fraud_analysis) if fraud_analysis else None,
                'metta_atoms_used': self._get_relevant_atoms(contribution_id),
                'timestamp': self._get_current_timestamp()
            }
        except Exception as e:
            return {
                'contribution_id': contribution_id,
                'error': str(e),
                'timestamp': self._get_current_timestamp()
            }
    
    def _get_relevant_atoms(self, contribution_id: str) -> List[str]:
        """Get MeTTa atoms relevant to a specific contribution"""
        relevant_atoms = []
        
        for atom in self.added_atoms:
            if contribution_id in atom:
                relevant_atoms.append(atom)
        
        return relevant_atoms
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for tracing"""
        import datetime
        return datetime.datetime.now().isoformat()

    def clear_space(self) -> None:
        """Clear the MeTTa space and reinitialize rules"""
        if METTA_AVAILABLE:
            if METTA_TYPE == "hyperon":
                self.space = MeTTa()
            else:  # pymetta
                self.space = pymetta.MeTTa()
        else:
            self.space = None
        self.added_atoms = []
        self.cache = {}
        self._initialize_core_rules()
