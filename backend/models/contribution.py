from app import db
from datetime import datetime
import json

class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    contribution_type = db.Column(db.String(50))  # e.g. coding, education, volunteer
    impact_level = db.Column(db.String(20), default='moderate')  # minimal, moderate, significant, transformative
    evidence = db.Column(db.Text)  # JSON string for evidence data
    status = db.Column(db.String(20), default='pending')  # pending, verified, flagged_for_review
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='contributions')
    verifications = db.relationship('Verification', back_populates='contribution', cascade='all, delete-orphan')
    
    def __init__(self, user_id, title, description=None, contribution_type=None, impact_level='moderate', evidence=None):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.contribution_type = contribution_type
        self.impact_level = impact_level
        # Store evidence as JSON string if it's a dict
        if isinstance(evidence, dict):
            self.evidence = json.dumps(evidence)
        else:
            self.evidence = evidence
    
    @property
    def evidence_dict(self):
        """Return evidence as a dictionary"""
        if self.evidence:
            try:
                return json.loads(self.evidence)
            except (json.JSONDecodeError, TypeError):
                return {"url": self.evidence} if self.evidence else None
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'contribution_type': self.contribution_type,
            'impact_level': self.impact_level,
            'evidence': self.evidence_dict,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'verified': len(self.verifications) > 0,
            'verifications': [v.to_dict() for v in self.verifications]
        }


class Verification(db.Model):
    __tablename__ = 'verifications'

    id = db.Column(db.Integer, primary_key=True)
    contribution_id = db.Column(db.Integer, db.ForeignKey('contributions.id'), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    verifier_name = db.Column(db.String(100))
    comments = db.Column(db.Text)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    contribution = db.relationship('Contribution', back_populates='verifications')
    
    def __init__(self, contribution_id, organization, verifier_name=None, comments=None):
        self.contribution_id = contribution_id
        self.organization = organization
        self.verifier_name = verifier_name
        self.comments = comments
    
    def to_dict(self):
        return {
            'id': self.id,
            'contribution_id': self.contribution_id,
            'organization': self.organization,
            'verifier_name': self.verifier_name,
            'comments': self.comments,
            'verified_at': self.verified_at.isoformat()
        }