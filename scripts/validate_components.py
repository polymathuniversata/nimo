#!/usr/bin/env python3
"""
Nimo Platform - Component Validation Script

This script validates the implementation of all platform components without requiring
the full backend to be running. It tests:
- Service implementations
- Configuration files
- Documentation completeness
- Code quality and structure
"""

import os
import sys
import json
import ast
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class NimoValidator:
    """Validates Nimo platform components"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {}
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "INFO"):
        """Log validation messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def validate_service_implementations(self) -> Dict[str, Any]:
        """Validate service implementations"""
        self.log("🔍 Validating service implementations...")

        services_dir = self.project_root / 'backend' / 'services'
        services = [
            'blockchain_contribution_service.py',
            'redis_cache_service.py',
            'ipfs_service.py',
            'cardano_service.py',
            'metta_integration_enhanced.py'
        ]

        results = {}

        for service_file in services:
            service_path = services_dir / service_file
            if service_path.exists():
                try:
                    with open(service_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check for required components
                    checks = {
                        'class_definition': 'class' in content,
                        'methods_implemented': 'def ' in content,
                        'error_handling': 'try:' in content and 'except' in content,
                        'logging': 'logger' in content or 'print(' in content,
                        'docstrings': '"""' in content,
                        'type_hints': ': ' in content and '->' in content
                    }

                    results[service_file] = {
                        'exists': True,
                        'size': len(content),
                        'checks': checks,
                        'score': sum(checks.values()) / len(checks) * 100
                    }

                    self.log(f"✅ {service_file}: {results[service_file]['score']".1f"}% implementation score")

                except Exception as e:
                    results[service_file] = {'exists': True, 'error': str(e)}
                    self.log(f"❌ {service_file}: Error reading file - {e}", "ERROR")
            else:
                results[service_file] = {'exists': False}
                self.log(f"❌ {service_file}: File not found", "ERROR")

        return results

    def validate_api_routes(self) -> Dict[str, Any]:
        """Validate API route implementations"""
        self.log("🔍 Validating API routes...")

        routes_dir = self.project_root / 'backend' / 'routes'
        route_files = [
            'contribution.py', 'auth_routes.py', 'user_routes.py',
            'cardano_routes.py', 'health_routes.py', 'token_routes.py'
        ]

        results = {}

        for route_file in route_files:
            route_path = routes_dir / route_file
            if route_path.exists():
                try:
                    with open(route_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check for Flask Blueprint pattern
                    checks = {
                        'blueprint_created': 'Blueprint(' in content,
                        'routes_defined': '@' in content and 'route(' in content,
                        'error_handling': 'try:' in content and 'except' in content,
                        'json_responses': 'jsonify(' in content,
                        'authentication': 'jwt_required' in content or '@login_required' in content,
                        'validation': 'request.' in content
                    }

                    results[route_file] = {
                        'exists': True,
                        'size': len(content),
                        'checks': checks,
                        'score': sum(checks.values()) / len(checks) * 100
                    }

                    self.log(f"✅ {route_file}: {results[route_file]['score']".1f"}% implementation score")

                except Exception as e:
                    results[route_file] = {'exists': True, 'error': str(e)}
                    self.log(f"❌ {route_file}: Error reading file - {e}", "ERROR")
            else:
                results[route_file] = {'exists': False}
                self.log(f"❌ {route_file}: File not found", "ERROR")

        return results

    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness"""
        self.log("🔍 Validating documentation...")

        docs_dir = self.project_root / 'docs'
        required_docs = [
            'README.md',
            'backend/backend_implementation_status.md',
            'backend/redis_caching_setup.md',
            'backend/testing_deployment_suite.md'
        ]

        results = {}

        for doc_file in required_docs:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check documentation quality
                    checks = {
                        'has_title': content.startswith('#') and len(content.split('\n')[0]) > 5,
                        'has_content': len(content) > 1000,
                        'has_code_blocks': '```' in content,
                        'has_links': 'http' in content or 'https' in content,
                        'has_structure': len([line for line in content.split('\n') if line.startswith('##')]) >= 3,
                        'has_examples': 'Example' in content or 'example' in content.lower()
                    }

                    results[doc_file] = {
                        'exists': True,
                        'size': len(content),
                        'checks': checks,
                        'score': sum(checks.values()) / len(checks) * 100
                    }

                    self.log(f"✅ {doc_file}: {results[doc_file]['score']".1f"}% documentation score")

                except Exception as e:
                    results[doc_file] = {'exists': True, 'error': str(e)}
                    self.log(f"❌ {doc_file}: Error reading file - {e}", "ERROR")
            else:
                results[doc_file] = {'exists': False}
                self.log(f"❌ {doc_file}: File not found", "ERROR")

        return results

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration files"""
        self.log("🔍 Validating configuration files...")

        config_files = [
            ('backend/.env.example', 'Environment configuration'),
            ('contracts/cardano/.env', 'Cardano configuration'),
            ('frontend/.env', 'Frontend configuration')
        ]

        results = {}

        for config_file, description in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check for required configuration sections
                    checks = {
                        'has_api_keys': 'API_KEY' in content or 'PROJECT_ID' in content,
                        'has_network_config': 'NETWORK' in content or 'RPC' in content,
                        'has_database_config': 'DATABASE' in content or 'DB' in content,
                        'has_security_config': 'SECRET' in content or 'PASSWORD' in content,
                        'has_comments': '#' in content,
                        'has_structure': len([line for line in content.split('\n') if '=' in line]) >= 5
                    }

                    results[config_file] = {
                        'exists': True,
                        'size': len(content),
                        'description': description,
                        'checks': checks,
                        'score': sum(checks.values()) / len(checks) * 100
                    }

                    self.log(f"✅ {config_file}: {results[config_file]['score']".1f"}% configuration score")

                except Exception as e:
                    results[config_file] = {'exists': True, 'error': str(e)}
                    self.log(f"❌ {config_file}: Error reading file - {e}", "ERROR")
            else:
                results[config_file] = {'exists': False, 'description': description}
                self.log(f"❌ {config_file}: File not found", "ERROR")

        return results

    def validate_smart_contracts(self) -> Dict[str, Any]:
        """Validate smart contract implementation"""
        self.log("🔍 Validating smart contracts...")

        contracts_dir = self.project_root / 'contracts' / 'cardano'
        contract_files = [
            'contribution_validator.ak',
            'identity_registry.ak',
            'metta_bridge.ak',
            'nimo_token.ak'
        ]

        results = {}

        for contract_file in contract_files:
            contract_path = contracts_dir / contract_file
            if contract_path.exists():
                try:
                    with open(contract_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check Aiken contract structure
                    checks = {
                        'has_validator_function': 'validator' in content.lower(),
                        'has_parameters': '{' in content and '}' in content,
                        'has_imports': 'use' in content or 'import' in content,
                        'has_comments': '//' in content or '/*' in content,
                        'has_error_handling': 'error' in content.lower(),
                        'has_functions': 'fn' in content
                    }

                    results[contract_file] = {
                        'exists': True,
                        'size': len(content),
                        'checks': checks,
                        'score': sum(checks.values()) / len(checks) * 100
                    }

                    self.log(f"✅ {contract_file}: {results[contract_file]['score']".1f"}% contract score")

                except Exception as e:
                    results[contract_file] = {'exists': True, 'error': str(e)}
                    self.log(f"❌ {contract_file}: Error reading file - {e}", "ERROR")
            else:
                results[contract_file] = {'exists': False}
                self.log(f"❌ {contract_file}: File not found", "ERROR")

        return results

    def validate_scripts(self) -> Dict[str, Any]:
        """Validate script implementations"""
        self.log("🔍 Validating scripts...")

        scripts_dir = self.project_root / 'scripts'
        script_files = [
            'test_suite.py',
            'deploy_production.py',
            'monitor_dashboard.py'
        ]

        results = {}

        for script_file in script_files:
            script_path = scripts_dir / script_file
            if script_path.exists():
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check script quality
                    checks = {
                        'has_main_function': 'def main(' in content or 'if __name__' in content,
                        'has_error_handling': 'try:' in content and 'except' in content,
                        'has_logging': 'log(' in content or 'print(' in content,
                        'has_docstrings': '"""' in content,
                        'has_imports': 'import' in content,
                        'has_classes': 'class' in content
                    }

                    results[script_file] = {
                        'exists': True,
                        'size': len(content),
                        'checks': checks,
                        'score': sum(checks.values()) / len(checks) * 100
                    }

                    self.log(f"✅ {script_file}: {results[script_file]['score']".1f"}% script score")

                except Exception as e:
                    results[script_file] = {'exists': True, 'error': str(e)}
                    self.log(f"❌ {script_file}: Error reading file - {e}", "ERROR")
            else:
                results[script_file] = {'exists': False}
                self.log(f"❌ {script_file}: File not found", "ERROR")

        return results

    def run_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation"""
        self.log("🚀 Starting Nimo Platform Component Validation")
        self.log("=" * 60)

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }

        # Run all validations
        validations = [
            ('services', self.validate_service_implementations),
            ('api_routes', self.validate_api_routes),
            ('documentation', self.validate_documentation),
            ('configuration', self.validate_configuration),
            ('smart_contracts', self.validate_smart_contracts),
            ('scripts', self.validate_scripts)
        ]

        total_score = 0
        component_count = 0

        for component_name, validation_func in validations:
            self.log(f"\n{'='*40}")
            self.log(f"Validating {component_name.upper()}...")
            self.log('='*40)

            try:
                results = validation_func()
                validation_results['components'][component_name] = results

                # Calculate average score for this component
                scores = []
                for item in results.values():
                    if isinstance(item, dict) and 'score' in item:
                        scores.append(item['score'])

                if scores:
                    avg_score = sum(scores) / len(scores)
                    total_score += avg_score
                    component_count += 1
                    self.log(f"✅ {component_name}: {avg_score".1f"}% average score")

            except Exception as e:
                validation_results['components'][component_name] = {'error': str(e)}
                self.log(f"❌ {component_name}: Validation failed - {e}", "ERROR")

        # Overall summary
        overall_score = total_score / component_count if component_count > 0 else 0

        validation_results['summary'] = {
            'total_components': component_count,
            'overall_score': f"{overall_score".1f"}%",
            'validation_time': f"{(datetime.now() - self.start_time).total_seconds()".1f"}s",
            'timestamp': datetime.now().isoformat()
        }

        # Save validation report
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)

        self.log(f"\n{'='*60}")
        self.log("🎉 VALIDATION COMPLETED")
        self.log('='*60)
        self.log(f"Overall Score: {validation_results['summary']['overall_score']}")
        self.log(f"Components Validated: {component_count}")
        self.log(f"Report Saved: {report_file}")
        self.log('='*60)

        return validation_results

def main():
    """Main validation execution"""
    print("🔬 Nimo Platform - Component Validation Suite")
    print("=" * 50)

    validator = NimoValidator()
    results = validator.run_validation()

    # Exit with appropriate code
    overall_score = float(results['summary']['overall_score'].strip('%'))
    if overall_score >= 90:
        print("✅ All components validated successfully!")
        return 0
    elif overall_score >= 70:
        print("⚠️  Most components validated with some issues.")
        return 0
    else:
        print("❌ Validation found significant issues.")
        return 1

if __name__ == "__main__":
    exit(main())
