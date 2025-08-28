"""
Mock MeTTa service for Nimo Platform.
Provides realistic fallback functionality when MeTTa is not available.
"""

import json
import os
import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class MockContribution:
    """Mock contribution data structure"""
    id: str
    user_id: str
    category: str
    title: Optional[str] = None
    confidence: float = 0.5
    verified: bool = False
    evidence_count: int = 0
    verification_count: int = 0

@dataclass 
class MockUser:
    """Mock user data structure"""
    id: str
    username: Optional[str] = None
    skills: List[Dict[str, Any]] = None
    token_balance: int = 0
    contributions: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.contributions is None:
            self.contributions = []

class MockMeTTaService:
    """
    Mock MeTTa service that simulates the behavior of the real MeTTa integration
    without requiring actual MeTTa installation.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize mock MeTTa service.
        
        Args:
            db_path: Optional path to persistent storage
        """
        self.db_path = db_path or "mock_metta_state.json"
        self.users: Dict[str, MockUser] = {}
        self.contributions: Dict[str, MockContribution] = {}
        self.rules_loaded = True
        self.connected = True
        
        # Load persistent state if available
        self._load_state()
        
        # Set up default response patterns
        self._setup_response_patterns()
    
    def _setup_response_patterns(self):
        """Set up patterns for generating realistic responses"""
        self.confidence_factors = {
            'evidence_bonus': 0.1,
            'verification_bonus': 0.2,
            'base_confidence': 0.5,
            'max_confidence': 1.0
        }
        
        self.verification_reasons = [
            "Contribution has sufficient evidence and meets quality standards",
            "External verification confirms authenticity of work",
            "Code repository analysis shows significant contribution",
            "Academic credentials verified through institutional channels",
            "Professional endorsement validates claimed expertise",
            "Multiple evidence sources corroborate the contribution"
        ]
        
        self.failure_reasons = [
            "Insufficient evidence provided for verification",
            "Unable to access referenced external resources",
            "Contribution does not meet minimum quality threshold",
            "Missing required documentation or proof",
            "External verification sources are unreachable",
            "Evidence provided does not support claimed contribution"
        ]
    
    def _load_state(self):
        """Load persistent state from file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                
                # Restore users
                for user_id, user_data in data.get('users', {}).items():
                    self.users[user_id] = MockUser(**user_data)
                
                # Restore contributions
                for contrib_id, contrib_data in data.get('contributions', {}).items():
                    self.contributions[contrib_id] = MockContribution(**contrib_data)
                    
        except Exception as e:
            print(f"Warning: Could not load mock MeTTa state: {e}")
    
    def _save_state(self):
        """Save current state to file"""
        try:
            data = {
                'users': {uid: user.__dict__ for uid, user in self.users.items()},
                'contributions': {cid: contrib.__dict__ for cid, contrib in self.contributions.items()},
                'timestamp': time.time()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save mock MeTTa state: {e}")
    
    def is_connected(self) -> bool:
        """Check if MeTTa service is connected (always True for mock)"""
        return self.connected
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status of mock service"""
        return {
            "status": "operational",
            "mode": "mock",
            "users": len(self.users),
            "contributions": len(self.contributions),
            "rules_loaded": self.rules_loaded,
            "timestamp": time.time()
        }
    
    def define_user(self, user_id: str, username: Optional[str] = None) -> str:
        """Define a user in the mock system"""
        if user_id not in self.users:
            self.users[user_id] = MockUser(id=user_id, username=username)
        else:
            # Update username if provided
            if username:
                self.users[user_id].username = username
        
        self._save_state()
        return f'(User "{user_id}" "{username or "anonymous"}")'
    
    def add_skill(self, user_id: str, skill: str, level: int = 1) -> str:
        """Add a skill to a user"""
        if user_id not in self.users:
            self.define_user(user_id)
        
        # Remove existing skill if present
        self.users[user_id].skills = [
            s for s in self.users[user_id].skills 
            if s.get('name') != skill
        ]
        
        # Add new skill
        self.users[user_id].skills.append({
            'name': skill,
            'level': max(1, min(5, level))  # Clamp between 1-5
        })
        
        self._save_state()
        return f'(HasSkill "{user_id}" "{skill}" {level})'
    
    def add_contribution(
        self, 
        contribution_id: str, 
        user_id: str, 
        category: str, 
        title: Optional[str] = None
    ) -> str:
        """Add a contribution to the system"""
        if user_id not in self.users:
            self.define_user(user_id)
        
        contribution = MockContribution(
            id=contribution_id,
            user_id=user_id,
            category=category,
            title=title
        )
        
        self.contributions[contribution_id] = contribution
        
        # Add to user's contributions list
        if contribution_id not in self.users[user_id].contributions:
            self.users[user_id].contributions.append(contribution_id)
        
        self._save_state()
        return f'(Contribution "{contribution_id}" "{user_id}" "{category}")'
    
    def add_evidence(
        self, 
        contribution_id: str, 
        evidence_type: str, 
        evidence_url: str, 
        evidence_id: Optional[str] = None
    ) -> str:
        """Add evidence for a contribution"""
        if contribution_id in self.contributions:
            self.contributions[contribution_id].evidence_count += 1
            self._recalculate_confidence(contribution_id)
        
        evidence_id = evidence_id or f"evidence-{contribution_id}-{evidence_type}"
        self._save_state()
        return f'(Evidence "{evidence_id}" "{contribution_id}" "{evidence_type}" "{evidence_url}")'
    
    def verify_contribution(
        self, 
        contribution_id: str, 
        organization: str, 
        verifier_id: Optional[str] = None
    ) -> str:
        """Record a contribution verification"""
        if contribution_id in self.contributions:
            self.contributions[contribution_id].verification_count += 1
            self.contributions[contribution_id].verified = True
            self._recalculate_confidence(contribution_id)
        
        verifier_part = f'"{verifier_id}"' if verifier_id else 'None'
        self._save_state()
        return f'(HasVerification "{contribution_id}" "{organization}" {verifier_part})'
    
    def set_token_balance(self, user_id: str, balance: int) -> str:
        """Set token balance for a user"""
        if user_id not in self.users:
            self.define_user(user_id)
        
        self.users[user_id].token_balance = max(0, balance)
        self._save_state()
        return f'(TokenBalance "{user_id}" {balance})'
    
    def _recalculate_confidence(self, contribution_id: str):
        """Recalculate confidence score for a contribution"""
        if contribution_id not in self.contributions:
            return
        
        contrib = self.contributions[contribution_id]
        base = self.confidence_factors['base_confidence']
        evidence_bonus = contrib.evidence_count * self.confidence_factors['evidence_bonus']
        verification_bonus = contrib.verification_count * self.confidence_factors['verification_bonus']
        
        # Add some realistic randomness
        random_factor = random.uniform(-0.05, 0.05)
        
        confidence = min(
            self.confidence_factors['max_confidence'],
            base + evidence_bonus + verification_bonus + random_factor
        )
        
        contrib.confidence = max(0.0, confidence)
    
    def calculate_contribution_confidence(self, contribution_id: str) -> float:
        """Calculate confidence score for a contribution"""
        if contribution_id not in self.contributions:
            return 0.0
        
        return self.contributions[contribution_id].confidence
    
    def validate_contribution(self, contribution_id: str, contribution_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a contribution using mock reasoning.
        Returns realistic validation results.
        """
        # If contribution data is provided, add it to the system first
        if contribution_data:
            user_id = str(contribution_data.get('user_id', ''))
            category = contribution_data.get('category', 'general')
            title = contribution_data.get('title')
            
            if user_id:
                self.add_contribution(contribution_id, user_id, category, title)
                
                # Add evidence if provided
                evidence_list = contribution_data.get('evidence', [])
                for evidence in evidence_list:
                    if isinstance(evidence, dict):
                        self.add_evidence(
                            contribution_id,
                            evidence.get('type', 'link'),
                            evidence.get('url', ''),
                            evidence.get('id')
                        )
        
        if contribution_id not in self.contributions:
            return {
                "valid": False,
                "confidence": 0.0,
                "explanation": "Contribution not found in system"
            }
        
        contrib = self.contributions[contribution_id]
        
        # Determine validity based on evidence and verification
        is_valid = (
            contrib.evidence_count > 0 and 
            contrib.confidence >= 0.6
        ) or contrib.verified
        
        # Add some realistic variability
        if not is_valid and random.random() < 0.1:  # 10% chance of false positive
            is_valid = True
        elif is_valid and random.random() < 0.05:  # 5% chance of false negative
            is_valid = False
        
        # Select appropriate explanation
        if is_valid:
            explanation = random.choice(self.verification_reasons)
        else:
            explanation = random.choice(self.failure_reasons)
        
        return {
            "valid": is_valid,
            "confidence": contrib.confidence,
            "explanation": explanation,
            "evidence_count": contrib.evidence_count,
            "verification_count": contrib.verification_count
        }
    
    def auto_award(self, user_id: str, contribution_id: str) -> Dict[str, Any]:
        """
        Simulate automatic token award calculation.
        """
        if contribution_id not in self.contributions:
            return {"error": "Contribution not found"}
        
        contrib = self.contributions[contribution_id]
        if contrib.user_id != user_id:
            return {"error": "Contribution does not belong to user"}
        
        # Calculate award amount
        base_amount = 50
        confidence_bonus = int(contrib.confidence * 50)
        evidence_bonus = contrib.evidence_count * 5
        verification_bonus = contrib.verification_count * 10
        
        total_award = base_amount + confidence_bonus + evidence_bonus + verification_bonus
        
        # Update user's balance
        if user_id not in self.users:
            self.define_user(user_id)
        
        old_balance = self.users[user_id].token_balance
        self.users[user_id].token_balance += total_award
        
        self._save_state()
        
        return {
            "awarded": total_award,
            "breakdown": {
                "base": base_amount,
                "confidence_bonus": confidence_bonus,
                "evidence_bonus": evidence_bonus,
                "verification_bonus": verification_bonus
            },
            "old_balance": old_balance,
            "new_balance": self.users[user_id].token_balance,
            "contribution_confidence": contrib.confidence
        }
    
    def query_user_contributions(self, user_id: str) -> List[str]:
        """Query all contributions for a user"""
        if user_id not in self.users:
            return []
        
        return self.users[user_id].contributions.copy()
    
    def query_token_balance(self, user_id: str) -> int:
        """Query token balance for a user"""
        if user_id not in self.users:
            return 0
        
        return self.users[user_id].token_balance
    
    def sync_user_to_metta(self, user_dict: Dict[str, Any]):
        """
        Sync a user from database representation.
        Expects a dictionary with user data.
        """
        user_id = str(user_dict.get('id'))
        username = user_dict.get('name') or user_dict.get('username')
        
        self.define_user(user_id, username)
        
        # Sync skills if provided
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
        
        # Sync token balance if provided
        if 'token_balance' in user_dict:
            self.set_token_balance(user_id, user_dict['token_balance'])
        
        # Sync contributions if provided
        contributions = user_dict.get('contributions', [])
        for contrib in contributions:
            if isinstance(contrib, dict):
                contrib_id = str(contrib.get('id'))
                category = contrib.get('category', 'general')
                title = contrib.get('title')
                
                self.add_contribution(contrib_id, user_id, category, title)
                
                # Add evidence if provided
                evidence_list = contrib.get('evidence', [])
                for evidence in evidence_list:
                    if isinstance(evidence, dict):
                        self.add_evidence(
                            contrib_id,
                            evidence.get('type', 'link'),
                            evidence.get('url', ''),
                            evidence.get('id')
                        )
                
                # Add verifications if provided
                verifications = contrib.get('verifications', [])
                for verification in verifications:
                    if isinstance(verification, dict):
                        self.verify_contribution(
                            contrib_id,
                            verification.get('organization', 'Unknown'),
                            verification.get('verifier_id')
                        )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total_contributions = len(self.contributions)
        verified_contributions = sum(1 for c in self.contributions.values() if c.verified)
        total_evidence = sum(c.evidence_count for c in self.contributions.values())
        total_tokens = sum(u.token_balance for u in self.users.values())
        
        avg_confidence = (
            sum(c.confidence for c in self.contributions.values()) / total_contributions
            if total_contributions > 0 else 0.0
        )
        
        return {
            "total_users": len(self.users),
            "total_contributions": total_contributions,
            "verified_contributions": verified_contributions,
            "total_evidence": total_evidence,
            "total_tokens": total_tokens,
            "average_confidence": round(avg_confidence, 3),
            "verification_rate": round(verified_contributions / total_contributions * 100, 1) if total_contributions > 0 else 0.0
        }

# Singleton instance for global use
mock_metta_service = MockMeTTaService()

def get_metta_service() -> MockMeTTaService:
    """Get the mock MeTTa service instance"""
    return mock_metta_service