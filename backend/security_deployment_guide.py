#!/usr/bin/env python3
"""
Nimo Platform Security Deployment Guide and Validation Script

This script helps validate and document the secure deployment requirements
for the Nimo Platform, ensuring all security configurations are properly set.
"""

import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime
import argparse

def validate_environment_variables() -> Dict[str, Any]:
    """
    Validate all required environment variables for secure deployment.
    
    Returns:
        Dictionary with validation results and recommendations
    """
    
    required_vars = {
        # Critical Security Keys
        'CARDANO_SERVICE_PRIVATE_KEY': {
            'description': 'Cardano service wallet private key (hex format)',
            'required': True,
            'min_length': 64,
            'example': 'a1b2c3d4e5f6...64-character-hex-string',
            'security_level': 'CRITICAL'
        },
        'NIMO_MASTER_KEY': {
            'description': 'Master encryption key for sensitive data storage',
            'required': True,
            'min_length': 32,
            'example': 'Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"',
            'security_level': 'CRITICAL'
        },
        'SECRET_KEY': {
            'description': 'Flask application secret key',
            'required': True,
            'min_length': 32,
            'example': 'Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"',
            'security_level': 'HIGH'
        },
        'JWT_SECRET_KEY': {
            'description': 'JWT token signing secret',
            'required': True,
            'min_length': 32,
            'example': 'Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"',
            'security_level': 'HIGH'
        },
        
        # API Keys
        'BLOCKFROST_PROJECT_ID_PREVIEW': {
            'description': 'Blockfrost API key for Cardano Preview testnet',
            'required': False,
            'min_length': 20,
            'example': 'preview1234567890abcdef...',
            'security_level': 'MEDIUM'
        },
        'BLOCKFROST_PROJECT_ID_PREPROD': {
            'description': 'Blockfrost API key for Cardano PreProd testnet',
            'required': False,
            'min_length': 20,
            'example': 'preprod1234567890abcdef...',
            'security_level': 'MEDIUM'
        },
        'BLOCKFROST_PROJECT_ID_MAINNET': {
            'description': 'Blockfrost API key for Cardano Mainnet',
            'required': False,
            'min_length': 20,
            'example': 'mainnet1234567890abcdef...',
            'security_level': 'HIGH'
        },
        
        # Network Configuration
        'CARDANO_NETWORK': {
            'description': 'Cardano network to use',
            'required': True,
            'allowed_values': ['preview', 'preprod', 'mainnet'],
            'example': 'preview',
            'security_level': 'LOW'
        },
        
        # Database
        'DATABASE_URL': {
            'description': 'Database connection URL',
            'required': True,
            'min_length': 10,
            'example': 'postgresql://user:pass@host:5432/nimo_db',
            'security_level': 'MEDIUM'
        }
    }
    
    validation_result = {
        'timestamp': datetime.now().isoformat(),
        'validation_status': 'UNKNOWN',
        'security_score': 0,
        'total_checks': len(required_vars),
        'passed_checks': 0,
        'failed_checks': 0,
        'warnings': [],
        'errors': [],
        'recommendations': [],
        'environment_variables': {}
    }
    
    for var_name, config in required_vars.items():
        var_value = os.environ.get(var_name, '')
        var_status = {
            'name': var_name,
            'description': config['description'],
            'required': config['required'],
            'present': bool(var_value),
            'valid': False,
            'security_level': config['security_level'],
            'issues': []
        }
        
        # Check if variable is present
        if not var_value:
            if config['required']:
                var_status['issues'].append(f"Required variable {var_name} is not set")
                validation_result['errors'].append(f"Missing required variable: {var_name}")
            else:
                var_status['issues'].append(f"Optional variable {var_name} is not set")
                validation_result['warnings'].append(f"Optional variable not set: {var_name}")
        else:
            # Validate variable value
            if 'min_length' in config and len(var_value) < config['min_length']:
                var_status['issues'].append(f"Value too short (minimum {config['min_length']} characters)")
                validation_result['errors'].append(f"{var_name}: Value too short")
            
            if 'allowed_values' in config and var_value not in config['allowed_values']:
                var_status['issues'].append(f"Invalid value. Allowed: {', '.join(config['allowed_values'])}")
                validation_result['errors'].append(f"{var_name}: Invalid value")
            
            # Check for default/example values that shouldn't be used in production
            dangerous_values = [
                'your_', 'example_', 'test_', 'dev-', 'development',
                'change-this', 'placeholder', 'dummy'
            ]
            if any(dangerous in var_value.lower() for dangerous in dangerous_values):
                var_status['issues'].append("Using placeholder/development value in production")
                validation_result['warnings'].append(f"{var_name}: Using development placeholder")
            
            # Mark as valid if no issues
            if not var_status['issues']:
                var_status['valid'] = True
                validation_result['passed_checks'] += 1
                
                # Add security score based on level
                security_scores = {
                    'CRITICAL': 25,
                    'HIGH': 15,
                    'MEDIUM': 10,
                    'LOW': 5
                }
                validation_result['security_score'] += security_scores.get(config['security_level'], 0)
            else:
                validation_result['failed_checks'] += 1
        
        validation_result['environment_variables'][var_name] = var_status
    
    # Determine overall status
    if validation_result['failed_checks'] == 0:
        validation_result['validation_status'] = 'PASSED'
    elif validation_result['errors']:
        validation_result['validation_status'] = 'FAILED'
    else:
        validation_result['validation_status'] = 'WARNING'
    
    # Generate recommendations
    if validation_result['errors']:
        validation_result['recommendations'].append("Fix all critical errors before deployment")
    
    if validation_result['warnings']:
        validation_result['recommendations'].append("Address warnings for better security")
    
    validation_result['recommendations'].extend([
        "Store all sensitive keys in secure key management system (e.g., HashiCorp Vault, AWS Secrets Manager)",
        "Rotate all API keys and secrets regularly (every 90 days minimum)",
        "Use strong, randomly generated keys for all secrets",
        "Never commit actual keys to version control",
        "Monitor key usage and implement audit logging"
    ])
    
    return validation_result

def generate_security_report(output_file: str = None) -> None:
    """Generate a comprehensive security report."""
    
    print("🔒 Nimo Platform Security Validation Report")
    print("=" * 50)
    
    # Run validation
    validation_result = validate_environment_variables()
    
    # Display summary
    print(f"\n📊 Summary:")
    print(f"Validation Status: {validation_result['validation_status']}")
    print(f"Security Score: {validation_result['security_score']}/100")
    print(f"Passed Checks: {validation_result['passed_checks']}/{validation_result['total_checks']}")
    print(f"Failed Checks: {validation_result['failed_checks']}")
    print(f"Warnings: {len(validation_result['warnings'])}")
    print(f"Errors: {len(validation_result['errors'])}")
    
    # Display errors
    if validation_result['errors']:
        print(f"\n❌ Critical Errors:")
        for error in validation_result['errors']:
            print(f"  • {error}")
    
    # Display warnings
    if validation_result['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in validation_result['warnings']:
            print(f"  • {warning}")
    
    # Display environment variable status
    print(f"\n🔍 Environment Variables Status:")
    for var_name, var_status in validation_result['environment_variables'].items():
        status_emoji = "✅" if var_status['valid'] else "❌"
        security_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠', 
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(var_status['security_level'], '⚪')
        
        print(f"  {status_emoji} {security_emoji} {var_name}: {var_status['description']}")
        
        if var_status['issues']:
            for issue in var_status['issues']:
                print(f"    ⚠️  {issue}")
    
    # Display recommendations
    print(f"\n📋 Security Recommendations:")
    for i, recommendation in enumerate(validation_result['recommendations'], 1):
        print(f"  {i}. {recommendation}")
    
    # Generate required environment variables template
    print(f"\n📄 Required Environment Variables Template:")
    print("# Copy this template to your .env file and replace with actual values")
    print("# ============================================================")
    
    for var_name, config in {k: v for k, v in validation_result['environment_variables'].items() if v['required']}:
        var_status = validation_result['environment_variables'][var_name]
        print(f"\n# {var_status['description']}")
        print(f"# Security Level: {var_status['security_level']}")
        print(f"# Example: {var_status.get('example', 'N/A')}")
        print(f"{var_name}=your_value_here")
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(validation_result, f, indent=2)
        print(f"\n💾 Detailed report saved to: {output_file}")
    
    # Exit with appropriate code
    if validation_result['validation_status'] == 'FAILED':
        print(f"\n❌ Security validation failed. Please fix critical errors before deployment.")
        sys.exit(1)
    elif validation_result['validation_status'] == 'WARNING':
        print(f"\n⚠️  Security validation passed with warnings. Review recommendations.")
        sys.exit(0)
    else:
        print(f"\n✅ Security validation passed successfully!")
        sys.exit(0)

def generate_secure_keys() -> None:
    """Generate secure random keys for deployment."""
    import secrets
    
    print("🔑 Secure Key Generation")
    print("=" * 30)
    print("\nGenerated secure keys (save these securely):")
    
    keys_to_generate = {
        'NIMO_MASTER_KEY': ('Master encryption key', 32),
        'SECRET_KEY': ('Flask secret key', 32), 
        'JWT_SECRET_KEY': ('JWT signing key', 32)
    }
    
    for key_name, (description, length) in keys_to_generate.items():
        secure_key = secrets.token_urlsafe(length)
        print(f"\n{key_name}={secure_key}")
        print(f"# {description} ({length} bytes)")
    
    print("\n⚠️  IMPORTANT:")
    print("  • Store these keys securely (password manager, key vault)")
    print("  • Never share these keys or commit them to version control")
    print("  • Use different keys for each environment (dev, staging, prod)")
    print("  • Rotate keys regularly (every 90 days minimum)")

def main():
    """Main entry point for the security deployment script."""
    
    parser = argparse.ArgumentParser(description='Nimo Platform Security Deployment Validator')
    parser.add_argument('--validate', action='store_true', help='Validate current environment')
    parser.add_argument('--generate-keys', action='store_true', help='Generate secure keys')
    parser.add_argument('--output', help='Output file for detailed report (JSON format)')
    parser.add_argument('--all', action='store_true', help='Run all security checks')
    
    args = parser.parse_args()
    
    if args.all or (not args.validate and not args.generate_keys):
        # Default: run validation
        generate_security_report(args.output)
    
    if args.validate or args.all:
        generate_security_report(args.output)
    
    if args.generate_keys or args.all:
        generate_secure_keys()

if __name__ == "__main__":
    main()