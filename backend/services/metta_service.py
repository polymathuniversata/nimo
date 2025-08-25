"""
MeTTa Integration Service for Nimo Platform

This service provides integration with MeTTa language for representing
decentralized identities and contributions in the Nimo platform.
"""

import pymetta as metta

class MeTTaIntegration:
    def __init__(self, db_path=None):
        """Initialize MeTTa integration with optional database path"""
        self.space = metta.Metta()
        self.db_path = db_path
        
        # Load MeTTa definitions if path provided
        if self.db_path:
            try:
                self.load_from_file(self.db_path)
            except Exception as e:
                print(f"Error loading MeTTa store: {e}")
    
    def load_from_file(self, path):
        """Load MeTTa definitions from a file"""
        self.space.load_space(path)
    
    def save_to_file(self, path=None):
        """Save MeTTa definitions to a file"""
        save_path = path or self.db_path
        if save_path:
            self.space.save_space(save_path)
    
    def define_user(self, user_id):
        """Define a user in MeTTa"""
        atom = f'(user "{user_id}")'
        self.space.parse_and_eval(atom)
        return atom
    
    def add_skill(self, user_id, skill):
        """Add a skill to a user's profile"""
        atom = f'(skill "{user_id}" "{skill}")'
        self.space.parse_and_eval(atom)
        return atom
    
    def add_contribution(self, user_id, activity):
        """Record a contribution by a user"""
        atom = f'(contribution "{user_id}" "{activity}")'
        self.space.parse_and_eval(atom)
        return atom
    
    def verify_contribution(self, user_id, organization):
        """Record a contribution verification by an organization"""
        atom = f'(verified-by "{user_id}" "{organization}")'
        self.space.parse_and_eval(atom)
        return atom
    
    def set_token_balance(self, user_id, balance):
        """Set token balance for a user"""
        atom = f'(token-balance "{user_id}" {balance})'
        self.space.parse_and_eval(atom)
        return atom
    
    def auto_award(self, user_id, task):
        """Apply the autonomous agent logic for automatic token awards"""
        # Define the auto-award rule
        rule = '''
        (= (auto-award $user $task)
           (if (and (contribution $user $task)
                   (verified-by $user $_))
               (increase-token $user 50)
               (token-balance $user (get-token-balance $user))))
        '''
        self.space.parse_and_eval(rule)
        
        # Execute the auto-award with specific user and task
        result = self.space.parse_and_eval(f'(auto-award "{user_id}" "{task}")')
        return result
    
    def query_user_contributions(self, user_id):
        """Query all contributions for a user"""
        query = f'(get-contributions "{user_id}")'
        result = self.space.parse_and_eval(query)
        return result
    
    def query_token_balance(self, user_id):
        """Query token balance for a user"""
        query = f'(get-token-balance "{user_id}")'
        result = self.space.parse_and_eval(query)
        return result
    
    def sync_user_to_metta(self, user):
        """Sync a user from the SQL database to MeTTa representation"""
        self.define_user(user.id)
        
        for skill in user.skills:
            self.add_skill(user.id, skill.name)
        
        if hasattr(user, 'tokens') and user.tokens:
            self.set_token_balance(user.id, user.tokens.balance)
        
        for contribution in user.contributions:
            self.add_contribution(user.id, contribution.title)
            
            for verification in contribution.verifications:
                self.verify_contribution(user.id, verification.organization)
    
    def sync_all_users(self, users):
        """Sync all users from SQL database to MeTTa representation"""
        for user in users:
            self.sync_user_to_metta(user)