#!/usr/bin/env python3
"""
Nimo Backend Security Validation Script

This script validates that critical security settings are properly configured
before deployment. It checks for common security misconfigurations and
provides recommendations for remediation.

Usage:
    python validate_security.py [--production] [--verbose]

Options:
    --production    Run production-specific checks
    --verbose       Show detailed output
"""

import os
import sys
import re
import json
from typing import Dict, List, Tuple
from pathlib import Path

class SecurityValidator:
    """Security configuration validator for Nimo Backend."""

    def __init__(self, production_mode: bool = False, verbose: bool = False):
        self.production_mode = production_mode
        self.verbose = verbose
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []
        self.passed: List[str] = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")

    def validate_secret_key(self) -> bool:
        """Validate Flask SECRET_KEY security."""
        secret_key = os.environ.get('SECRET_KEY', '')

        if not secret_key:
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'SECRET_KEY',
                'issue': 'SECRET_KEY environment variable not set',
                'recommendation': 'Set SECRET_KEY to a strong random value using: python -c "import secrets; print(secrets.token_hex(32))"'
            })
            return False

        if secret_key in ['your-super-secret-key-change-this-in-production',
                         'dev-key-please-change-in-production',
                         'CHANGE_THIS_IN_PRODUCTION_WITH_A_STRONG_RANDOM_KEY']:
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'SECRET_KEY',
                'issue': 'SECRET_KEY is using default/placeholder value',
                'recommendation': 'Generate a new SECRET_KEY with: python -c "import secrets; print(secrets.token_hex(32))"'
            })
            return False

        if len(secret_key) < 32:
            self.issues.append({
                'category': 'HIGH',
                'check': 'SECRET_KEY',
                'issue': f'SECRET_KEY is too short ({len(secret_key)} characters)',
                'recommendation': 'Use at least 32 characters for SECRET_KEY'
            })
            return False

        self.passed.append('SECRET_KEY is properly configured')
        return True

    def validate_jwt_secret(self) -> bool:
        """Validate JWT_SECRET_KEY security."""
        jwt_secret = os.environ.get('JWT_SECRET_KEY', '')

        if not jwt_secret:
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'JWT_SECRET_KEY',
                'issue': 'JWT_SECRET_KEY environment variable not set',
                'recommendation': 'Set JWT_SECRET_KEY to a strong random value using: python -c "import secrets; print(secrets.token_hex(32))"'
            })
            return False

        if jwt_secret in ['your-jwt-secret-key-change-this-in-production',
                         'jwt-dev-key-change-in-production',
                         'CHANGE_THIS_IN_PRODUCTION_WITH_A_STRONG_RANDOM_KEY']:
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'JWT_SECRET_KEY',
                'issue': 'JWT_SECRET_KEY is using default/placeholder value',
                'recommendation': 'Generate a new JWT_SECRET_KEY with: python -c "import secrets; print(secrets.token_hex(32))"'
            })
            return False

        if len(jwt_secret) < 32:
            self.issues.append({
                'category': 'HIGH',
                'check': 'JWT_SECRET_KEY',
                'issue': f'JWT_SECRET_KEY is too short ({len(jwt_secret)} characters)',
                'recommendation': 'Use at least 32 characters for JWT_SECRET_KEY'
            })
            return False

        self.passed.append('JWT_SECRET_KEY is properly configured')
        return True

    def validate_network_binding(self) -> bool:
        """Validate network binding security."""
        host = os.environ.get('FLASK_HOST', '127.0.0.1')

        if host == '0.0.0.0':
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'NETWORK_BINDING',
                'issue': 'Application is configured to bind to all interfaces (0.0.0.0)',
                'recommendation': 'Set FLASK_HOST=127.0.0.1 and use a reverse proxy for external access'
            })
            return False

        if host not in ['127.0.0.1', 'localhost']:
            self.warnings.append({
                'category': 'MEDIUM',
                'check': 'NETWORK_BINDING',
                'issue': f'Application binding to non-localhost interface: {host}',
                'recommendation': 'Consider using 127.0.0.1 unless you have proper firewall configuration'
            })

        self.passed.append('Network binding is secure')
        return True

    def validate_debug_mode(self) -> bool:
        """Validate debug mode is disabled in production."""
        debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

        if self.production_mode and debug_mode:
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'DEBUG_MODE',
                'issue': 'Debug mode is enabled in production',
                'recommendation': 'Set FLASK_DEBUG=false in production environment'
            })
            return False

        if debug_mode:
            self.warnings.append({
                'category': 'LOW',
                'check': 'DEBUG_MODE',
                'issue': 'Debug mode is enabled',
                'recommendation': 'Disable debug mode in production with FLASK_DEBUG=false'
            })

        self.passed.append('Debug mode is properly configured')
        return True

    def validate_database_security(self) -> bool:
        """Validate database configuration security."""
        db_url = os.environ.get('DATABASE_URL', '')

        if not db_url:
            self.issues.append({
                'category': 'HIGH',
                'check': 'DATABASE_URL',
                'issue': 'DATABASE_URL environment variable not set',
                'recommendation': 'Configure DATABASE_URL with production database credentials'
            })
            return False

        # Check for insecure database URLs
        if 'password' in db_url.lower() and 'changeme' in db_url.lower():
            self.issues.append({
                'category': 'CRITICAL',
                'check': 'DATABASE_PASSWORD',
                'issue': 'Database password appears to be default/placeholder',
                'recommendation': 'Set a strong, unique password for the database user'
            })
            return False

        # Check for localhost-only databases in production
        if self.production_mode and 'localhost' in db_url:
            self.warnings.append({
                'category': 'MEDIUM',
                'check': 'DATABASE_HOST',
                'issue': 'Database is configured to use localhost in production',
                'recommendation': 'Ensure database is properly secured and accessible'
            })

        self.passed.append('Database configuration is secure')
        return True

    def validate_blockchain_keys(self) -> bool:
        """Validate blockchain service keys."""
        issues = []

        # Check Cardano service key
        cardano_key = os.environ.get('CARDANO_SERVICE_PRIVATE_KEY', '')
        if not cardano_key or cardano_key == 'your_cardano_service_private_key_here':
            issues.append('CARDANO_SERVICE_PRIVATE_KEY not properly configured')

        # Check Ethereum service key
        eth_key = os.environ.get('BLOCKCHAIN_SERVICE_PRIVATE_KEY', '')
        if not eth_key or eth_key == 'your_ethereum_service_private_key_here':
            issues.append('BLOCKCHAIN_SERVICE_PRIVATE_KEY not properly configured')

        # Check Blockfrost API keys
        networks = ['PREVIEW', 'PREPROD', 'MAINNET']
        for network in networks:
            api_key = os.environ.get(f'BLOCKFROST_PROJECT_ID_{network}', '')
            if not api_key or api_key == f'your_blockfrost_{network.lower()}_api_key_here':
                issues.append(f'BLOCKFROST_PROJECT_ID_{network} not configured')

        if issues:
            self.issues.append({
                'category': 'HIGH',
                'check': 'BLOCKCHAIN_KEYS',
                'issue': f'Blockchain keys not properly configured: {", ".join(issues)}',
                'recommendation': 'Configure all blockchain service keys and API keys for production use'
            })
            return False

        self.passed.append('Blockchain keys are properly configured')
        return True

    def validate_rate_limiting(self) -> bool:
        """Validate rate limiting configuration."""
        rate_limit = os.environ.get('DEFAULT_RATE_LIMIT', '100')

        try:
            rate_limit_int = int(rate_limit)
            if rate_limit_int < 10:
                self.warnings.append({
                    'category': 'MEDIUM',
                    'check': 'RATE_LIMITING',
                    'issue': f'Rate limit is very low: {rate_limit_int} requests',
                    'recommendation': 'Consider increasing rate limit or implement proper DDoS protection'
                })
            elif rate_limit_int > 1000:
                self.warnings.append({
                    'category': 'LOW',
                    'check': 'RATE_LIMITING',
                    'issue': f'Rate limit is very high: {rate_limit_int} requests',
                    'recommendation': 'High rate limits may allow abuse; consider implementing additional protections'
                })
        except ValueError:
            self.issues.append({
                'category': 'MEDIUM',
                'check': 'RATE_LIMITING',
                'issue': f'Invalid rate limit value: {rate_limit}',
                'recommendation': 'Set DEFAULT_RATE_LIMIT to a valid integer'
            })
            return False

        self.passed.append('Rate limiting is properly configured')
        return True

    def validate_ssl_configuration(self) -> bool:
        """Validate SSL/TLS configuration."""
        if not self.production_mode:
            return True  # Skip SSL checks for development

        ssl_redirect = os.environ.get('SSL_REDIRECT', 'false').lower() == 'true'
        session_secure = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'

        if not ssl_redirect:
            self.issues.append({
                'category': 'HIGH',
                'check': 'SSL_REDIRECT',
                'issue': 'SSL redirect is disabled in production',
                'recommendation': 'Set SSL_REDIRECT=true to enforce HTTPS'
            })
            return False

        if not session_secure:
            self.issues.append({
                'category': 'HIGH',
                'check': 'SESSION_SECURITY',
                'issue': 'Session cookies are not marked as secure',
                'recommendation': 'Set SESSION_COOKIE_SECURE=true for HTTPS-only cookies'
            })
            return False

        self.passed.append('SSL configuration is secure')
        return True

    def validate_file_permissions(self) -> bool:
        """Validate file permissions for sensitive files."""
        sensitive_files = ['.env', '.env.local', 'config.py', 'key_manager.py']

        for filename in sensitive_files:
            filepath = Path(filename)
            if filepath.exists():
                # Check if file is readable by others
                if os.name != 'nt':  # Skip on Windows
                    try:
                        stat_info = filepath.stat()
                        # Check if file is readable by group or others
                        if stat_info.st_mode & 0o077:
                            self.issues.append({
                                'category': 'MEDIUM',
                                'check': 'FILE_PERMISSIONS',
                                'issue': f'File {filename} has overly permissive permissions',
                                'recommendation': f'Run: chmod 600 {filename}'
                            })
                    except OSError:
                        self.warnings.append({
                            'category': 'LOW',
                            'check': 'FILE_PERMISSIONS',
                            'issue': f'Could not check permissions for {filename}',
                            'recommendation': 'Manually verify file permissions'
                        })

        self.passed.append('File permissions are appropriate')
        return True

    def run_all_checks(self) -> bool:
        """Run all security validation checks."""
        self.log("Starting security validation...")

        checks = [
            self.validate_secret_key,
            self.validate_jwt_secret,
            self.validate_network_binding,
            self.validate_debug_mode,
            self.validate_database_security,
            self.validate_blockchain_keys,
            self.validate_rate_limiting,
            self.validate_ssl_configuration,
            self.validate_file_permissions,
        ]

        all_passed = True
        for check in checks:
            try:
                result = check()
                if not result:
                    all_passed = False
            except Exception as e:
                self.issues.append({
                    'category': 'MEDIUM',
                    'check': 'VALIDATION_ERROR',
                    'issue': f'Error running {check.__name__}: {str(e)}',
                    'recommendation': 'Fix the validation error and re-run checks'
                })
                all_passed = False

        return all_passed

    def generate_report(self) -> Dict:
        """Generate a comprehensive security validation report."""
        return {
            'summary': {
                'total_checks': len(self.passed) + len(self.issues) + len(self.warnings),
                'passed': len(self.passed),
                'issues': len(self.issues),
                'warnings': len(self.warnings),
                'overall_status': 'SECURE' if not self.issues else 'VULNERABLE'
            },
            'passed_checks': self.passed,
            'issues': self.issues,
            'warnings': self.warnings,
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Critical issues first
        critical_issues = [issue for issue in self.issues if issue['category'] == 'CRITICAL']
        if critical_issues:
            recommendations.append("🚨 CRITICAL: Address all critical security issues before deployment")

        # High priority issues
        high_issues = [issue for issue in self.issues if issue['category'] == 'HIGH']
        if high_issues:
            recommendations.append("⚠️ HIGH: Fix high-priority security issues")

        # General recommendations
        recommendations.extend([
            "🔐 Generate strong, random secrets for all cryptographic keys",
            "🌐 Use reverse proxy (nginx) for external access instead of binding to 0.0.0.0",
            "🔒 Enable SSL/TLS with valid certificates in production",
            "📊 Implement comprehensive logging and monitoring",
            "🔄 Regularly rotate secrets and API keys",
            "🛡️ Keep dependencies updated and scan for vulnerabilities"
        ])

        return recommendations

    def print_report(self):
        """Print a formatted security validation report."""
        report = self.generate_report()

        print("\n" + "="*80)
        print("🔒 NIMO BACKEND SECURITY VALIDATION REPORT")
        print("="*80)

        # Summary
        summary = report['summary']
        status_emoji = "✅" if summary['overall_status'] == 'SECURE' else "❌"
        print(f"\n{status_emoji} Overall Status: {summary['overall_status']}")
        print(f"📊 Checks Passed: {summary['passed']}/{summary['total_checks']}")
        print(f"🚨 Issues Found: {summary['issues']}")
        print(f"⚠️ Warnings: {summary['warnings']}")

        # Issues
        if summary['issues'] > 0:
            print(f"\n🚨 CRITICAL ISSUES ({len([i for i in self.issues if i['category'] == 'CRITICAL'])}):")
            for issue in self.issues:
                if issue['category'] == 'CRITICAL':
                    print(f"  ❌ {issue['check']}: {issue['issue']}")
                    print(f"     💡 {issue['recommendation']}")

            print(f"\n⚠️ HIGH PRIORITY ISSUES ({len([i for i in self.issues if i['category'] == 'HIGH'])}):")
            for issue in self.issues:
                if issue['category'] == 'HIGH':
                    print(f"  ❌ {issue['check']}: {issue['issue']}")
                    print(f"     💡 {issue['recommendation']}")

        # Warnings
        if summary['warnings'] > 0:
            print(f"\n⚠️ WARNINGS ({summary['warnings']}):")
            for warning in self.warnings:
                print(f"  ⚠️ {warning['check']}: {warning['issue']}")
                print(f"    💡 {warning['recommendation']}")

        # Passed checks
        if summary['passed'] > 0:
            print(f"\n✅ PASSED CHECKS ({summary['passed']}):")
            for check in self.passed:
                print(f"  ✅ {check}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")

        print("\n" + "="*80)


def main():
    """Main entry point for security validation."""
    import argparse

    parser = argparse.ArgumentParser(description='Nimo Backend Security Validator')
    parser.add_argument('--production', action='store_true',
                       help='Run production-specific security checks')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed validation output')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')

    args = parser.parse_args()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Run validation
    validator = SecurityValidator(
        production_mode=args.production,
        verbose=args.verbose
    )

    success = validator.run_all_checks()

    if args.json:
        report = validator.generate_report()
        print(json.dumps(report, indent=2))
    else:
        validator.print_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()