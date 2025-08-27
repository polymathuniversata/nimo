"""
Test script for MeTTa integration in Nimo project.
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MeTTa integration
from services.metta_service import MeTTaIntegration

def main():
    # Initialize MeTTa integration
    metta = MeTTaIntegration()
    
    # Define users
    metta.define_user("user1", "Alice")
    metta.define_user("user2", "Bob")
    
    # Add skills
    metta.add_skill("user1", "coding", 4)
    metta.add_skill("user1", "music", 3)
    metta.add_skill("user2", "art", 5)
    metta.add_skill("user2", "writing", 4)
    
    # Add contributions
    metta.add_contribution("contrib1", "user1", "coding", "Calculator App")
    metta.add_contribution("contrib2", "user2", "education", "Programming Tutorial")
    
    # Add evidence
    metta.add_evidence("contrib1", "github", "https://github.com/alice/calculator")
    metta.add_evidence("contrib2", "website", "https://bob-tutorials.com/programming")
    
    # Verify contribution
    metta.verify_contribution("contrib1", "CodeSchool")
    
    # Set token balances
    metta.set_token_balance("user1", 100)
    metta.set_token_balance("user2", 75)
    
    # Query user contributions
    alice_contributions = metta.query_user_contributions("user1")
    print(f"Alice's contributions: {alice_contributions}")
    
    # Query token balances
    alice_tokens = metta.query_token_balance("user1")
    bob_tokens = metta.query_token_balance("user2")
    print(f"Alice's tokens: {alice_tokens}")
    print(f"Bob's tokens: {bob_tokens}")
    
    # Validate a contribution
    validation = metta.validate_contribution("contrib1")
    print(f"Validation result for contrib1: {validation}")
    
    # Save state to file
    metta.save_to_file("metta_state.json")
    
if __name__ == "__main__":
    main()