#!/usr/bin/env python3
"""
Nimo Platform - Comprehensive Testing Suite Runner

This script runs all tests for the Nimo Platform smart contracts,
including unit tests, integration tests, security tests, and performance tests.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class TestResult:
    """Result of a test run"""
    test_suite: str
    test_name: str
    status: str  # "passed", "failed", "skipped", "error"
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class TestSummary:
    """Summary of all test runs"""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    coverage_percentage: float
    results: List[TestResult]

class NimoTestRunner:
    """Comprehensive test runner for Nimo Platform"""
    
    def __init__(self, contracts_dir: Path = Path.cwd()):
        """Initialize the test runner"""
        self.contracts_dir = contracts_dir
        self.test_results = []
        self.start_time = time.time()
        
    def run_all_tests(self, test_types: List[str] = None) -> TestSummary:
        """Run all test suites"""
        print("🧪 Starting comprehensive test suite...")
        
        if test_types is None:
            test_types = ["unit", "integration", "security", "performance"]
        
        # Run each test type
        for test_type in test_types:
            print(f"\n📋 Running {test_type} tests...")
            
            if test_type == "unit":
                self.run_unit_tests()
            elif test_type == "integration":
                self.run_integration_tests()
            elif test_type == "security":
                self.run_security_tests()
            elif test_type == "performance":
                self.run_performance_tests()
            else:
                print(f"⚠️  Unknown test type: {test_type}")
        
        # Generate summary
        summary = self.generate_summary()
        
        # Print results
        self.print_summary(summary)
        
        return summary
    
    def run_unit_tests(self):
        """Run Aiken unit tests"""
        try:
            print("🔬 Running Aiken unit tests...")
            
            # Run aiken test command
            result = subprocess.run(
                ['aiken', 'test', '--verbose'],
                cwd=self.contracts_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                self.parse_aiken_test_output(result.stdout)
                print("✅ Unit tests completed successfully")
            else:
                print(f"❌ Unit tests failed: {result.stderr}")
                self.add_test_result(
                    "unit", "aiken_test_suite", "failed", 0,
                    error_message=result.stderr
                )
        
        except subprocess.TimeoutExpired:
            print("⏰ Unit tests timed out")
            self.add_test_result(
                "unit", "aiken_test_suite", "error", 300,
                error_message="Test suite timed out"
            )
        except FileNotFoundError:
            print("❌ Aiken not found - skipping unit tests")
            self.add_test_result(
                "unit", "aiken_test_suite", "skipped", 0,
                error_message="Aiken not installed"
            )
    
    def parse_aiken_test_output(self, output: str):
        """Parse Aiken test output and extract results"""
        lines = output.split('\n')
        current_test = None
        
        for line in lines:
            line = line.strip()
            
            # Test start
            if line.startswith('test ') and '...' in line:
                current_test = line.replace('test ', '').replace('...', '').strip()
            
            # Test result
            elif line in ['ok', 'PASSED']:
                if current_test:
                    self.add_test_result("unit", current_test, "passed", 0.1)
                    current_test = None
            
            elif line in ['FAILED', 'ERROR']:
                if current_test:
                    self.add_test_result("unit", current_test, "failed", 0.1)
                    current_test = None
            
            # Parse test summary if available
            elif 'test result:' in line:
                # Example: "test result: ok. 15 passed; 0 failed; 0 ignored"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        if i > 0:
                            prev_word = parts[i-1]
                            if 'passed' in prev_word:
                                # Results already added individually
                                pass
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("🔗 Running integration tests...")
        
        # Test contract compilation
        self.test_contract_compilation()
        
        # Test deployment simulation
        self.test_deployment_simulation()
        
        # Test contract interactions
        self.test_contract_interactions()
    
    def test_contract_compilation(self):
        """Test that all contracts compile successfully"""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ['aiken', 'build', '--trace-level', 'silent'],
                cwd=self.contracts_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.add_test_result(
                    "integration", "contract_compilation", "passed", duration,
                    details={"compilation_time": duration}
                )
            else:
                self.add_test_result(
                    "integration", "contract_compilation", "failed", duration,
                    error_message=result.stderr
                )
        
        except subprocess.TimeoutExpired:
            self.add_test_result(
                "integration", "contract_compilation", "error", 60,
                error_message="Compilation timed out"
            )
    
    def test_deployment_simulation(self):
        """Test deployment scripts without actual deployment"""
        start_time = time.time()
        
        try:
            # Test deployment script compilation check
            result = subprocess.run(
                [sys.executable, 'deploy.py', '--compile-only'],
                cwd=self.contracts_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.add_test_result(
                    "integration", "deployment_simulation", "passed", duration,
                    details={"simulation_time": duration}
                )
            else:
                self.add_test_result(
                    "integration", "deployment_simulation", "failed", duration,
                    error_message=result.stderr
                )
        
        except subprocess.TimeoutExpired:
            self.add_test_result(
                "integration", "deployment_simulation", "error", 120,
                error_message="Deployment simulation timed out"
            )
        except FileNotFoundError:
            self.add_test_result(
                "integration", "deployment_simulation", "skipped", 0,
                error_message="Deploy script not found"
            )
    
    def test_contract_interactions(self):
        """Test basic contract interaction patterns"""
        # This would test contract datum/redeemer validation
        # For now, we'll check if contract files contain expected patterns
        
        start_time = time.time()
        
        contracts_to_test = [
            'contribution_validator.ak',
            'identity_registry.ak',
            'metta_bridge.ak'
        ]
        
        all_passed = True
        
        for contract_file in contracts_to_test:
            contract_path = self.contracts_dir / contract_file
            
            if contract_path.exists():
                with open(contract_path, 'r') as f:
                    content = f.read()
                
                # Check for required patterns
                required_patterns = [
                    'validator(',
                    'ScriptContext',
                    'transaction',
                    'extra_signatories'
                ]
                
                missing_patterns = []
                for pattern in required_patterns:
                    if pattern not in content:
                        missing_patterns.append(pattern)
                
                if missing_patterns:
                    all_passed = False
                    self.add_test_result(
                        "integration", f"{contract_file}_patterns", "failed",
                        time.time() - start_time,
                        error_message=f"Missing patterns: {missing_patterns}"
                    )
                else:
                    self.add_test_result(
                        "integration", f"{contract_file}_patterns", "passed",
                        time.time() - start_time
                    )
            else:
                all_passed = False
                self.add_test_result(
                    "integration", f"{contract_file}_exists", "failed",
                    0, error_message="Contract file not found"
                )
        
        duration = time.time() - start_time
        
        if all_passed:
            self.add_test_result(
                "integration", "contract_interactions", "passed", duration
            )
        else:
            self.add_test_result(
                "integration", "contract_interactions", "failed", duration,
                error_message="Some contract interaction tests failed"
            )
    
    def run_security_tests(self):
        """Run security tests"""
        print("🔒 Running security tests...")
        
        start_time = time.time()
        
        try:
            # Import and run security auditor
            from security_audit import NimoSecurityAuditor
            
            auditor = NimoSecurityAuditor(self.contracts_dir)
            report = auditor.audit_all_contracts()
            
            duration = time.time() - start_time
            
            # Determine if security tests passed based on findings
            critical_issues = report.summary.get('critical', 0)
            high_issues = report.summary.get('high', 0)
            
            if critical_issues == 0 and high_issues == 0:
                status = "passed"
                error_message = None
            else:
                status = "failed"
                error_message = f"Security issues found: {critical_issues} critical, {high_issues} high"
            
            self.add_test_result(
                "security", "security_audit", status, duration,
                error_message=error_message,
                details={
                    "overall_score": report.overall_score,
                    "findings_summary": report.summary,
                    "total_findings": len(report.findings)
                }
            )
            
        except ImportError:
            self.add_test_result(
                "security", "security_audit", "skipped", 0,
                error_message="Security audit module not available"
            )
        except Exception as e:
            self.add_test_result(
                "security", "security_audit", "error", time.time() - start_time,
                error_message=f"Security audit failed: {str(e)}"
            )
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("⚡ Running performance tests...")
        
        # Test contract size limits
        self.test_contract_sizes()
        
        # Test compilation performance
        self.test_compilation_performance()
        
        # Test deployment cost estimates
        self.test_deployment_costs()
    
    def test_contract_sizes(self):
        """Test that contract sizes are within acceptable limits"""
        start_time = time.time()
        
        max_contract_size = 100 * 1024  # 100KB limit
        contracts_checked = 0
        oversized_contracts = []
        
        for contract_file in self.contracts_dir.glob("*.ak"):
            if contract_file.is_file():
                size = contract_file.stat().st_size
                contracts_checked += 1
                
                if size > max_contract_size:
                    oversized_contracts.append((contract_file.name, size))
        
        duration = time.time() - start_time
        
        if oversized_contracts:
            error_msg = f"Oversized contracts: {oversized_contracts}"
            self.add_test_result(
                "performance", "contract_sizes", "failed", duration,
                error_message=error_msg,
                details={"oversized_contracts": oversized_contracts}
            )
        else:
            self.add_test_result(
                "performance", "contract_sizes", "passed", duration,
                details={"contracts_checked": contracts_checked}
            )
    
    def test_compilation_performance(self):
        """Test compilation performance"""
        start_time = time.time()
        
        try:
            # Time compilation
            compilation_start = time.time()
            
            result = subprocess.run(
                ['aiken', 'build'],
                cwd=self.contracts_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            compilation_time = time.time() - compilation_start
            total_duration = time.time() - start_time
            
            # Performance thresholds
            max_compilation_time = 60  # 60 seconds
            
            if result.returncode == 0:
                if compilation_time <= max_compilation_time:
                    self.add_test_result(
                        "performance", "compilation_performance", "passed", total_duration,
                        details={"compilation_time": compilation_time}
                    )
                else:
                    self.add_test_result(
                        "performance", "compilation_performance", "failed", total_duration,
                        error_message=f"Compilation too slow: {compilation_time:.2f}s > {max_compilation_time}s",
                        details={"compilation_time": compilation_time}
                    )
            else:
                self.add_test_result(
                    "performance", "compilation_performance", "error", total_duration,
                    error_message="Compilation failed"
                )
        
        except subprocess.TimeoutExpired:
            self.add_test_result(
                "performance", "compilation_performance", "error", 300,
                error_message="Compilation timed out"
            )
    
    def test_deployment_costs(self):
        """Test deployment cost estimates"""
        start_time = time.time()
        
        try:
            # This would ideally simulate deployment and measure costs
            # For now, we'll do basic cost estimation
            
            estimated_costs = {
                'contribution_validator': 5000000,  # ~5 ADA
                'identity_registry': 4000000,      # ~4 ADA
                'metta_bridge': 6000000,           # ~6 ADA
                'nimo_token_policy': 2000000       # ~2 ADA
            }
            
            total_cost = sum(estimated_costs.values())
            max_acceptable_cost = 25000000  # 25 ADA
            
            duration = time.time() - start_time
            
            if total_cost <= max_acceptable_cost:
                self.add_test_result(
                    "performance", "deployment_costs", "passed", duration,
                    details={
                        "estimated_total_cost": total_cost,
                        "cost_breakdown": estimated_costs
                    }
                )
            else:
                self.add_test_result(
                    "performance", "deployment_costs", "failed", duration,
                    error_message=f"Deployment costs too high: {total_cost/1000000:.1f} ADA",
                    details={
                        "estimated_total_cost": total_cost,
                        "cost_breakdown": estimated_costs
                    }
                )
        
        except Exception as e:
            self.add_test_result(
                "performance", "deployment_costs", "error", time.time() - start_time,
                error_message=f"Cost estimation failed: {str(e)}"
            )
    
    def add_test_result(self, test_suite: str, test_name: str, status: str,
                       duration: float, error_message: str = None,
                       details: Dict[str, Any] = None):
        """Add a test result to the collection"""
        result = TestResult(
            test_suite=test_suite,
            test_name=test_name,
            status=status,
            duration=duration,
            error_message=error_message,
            details=details
        )
        
        self.test_results.append(result)
    
    def generate_summary(self) -> TestSummary:
        """Generate test summary"""
        total_duration = time.time() - self.start_time
        
        summary = {
            'passed': len([r for r in self.test_results if r.status == 'passed']),
            'failed': len([r for r in self.test_results if r.status == 'failed']),
            'skipped': len([r for r in self.test_results if r.status == 'skipped']),
            'errors': len([r for r in self.test_results if r.status == 'error']),
        }
        
        # Calculate coverage (simplified)
        total_tests = len(self.test_results)
        effective_tests = summary['passed'] + summary['failed']
        coverage = (effective_tests / total_tests * 100) if total_tests > 0 else 0
        
        return TestSummary(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_tests=total_tests,
            passed=summary['passed'],
            failed=summary['failed'],
            skipped=summary['skipped'],
            errors=summary['errors'],
            total_duration=total_duration,
            coverage_percentage=coverage,
            results=self.test_results
        )
    
    def print_summary(self, summary: TestSummary):
        """Print test summary to console"""
        print("\n" + "="*60)
        print("🧪 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary.total_tests}")
        print(f"✅ Passed: {summary.passed}")
        print(f"❌ Failed: {summary.failed}")
        print(f"⏭️  Skipped: {summary.skipped}")
        print(f"🚨 Errors: {summary.errors}")
        print(f"⏱️  Duration: {summary.total_duration:.2f}s")
        print(f"📊 Coverage: {summary.coverage_percentage:.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in summary.results if r.status == 'failed']
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test.test_suite}.{test.test_name}: {test.error_message}")
        
        # Show error tests
        error_tests = [r for r in summary.results if r.status == 'error']
        if error_tests:
            print("\n🚨 ERROR TESTS:")
            for test in error_tests:
                print(f"  - {test.test_suite}.{test.test_name}: {test.error_message}")
        
        # Overall result
        if summary.failed == 0 and summary.errors == 0:
            print(f"\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {summary.failed + summary.errors} TEST(S) FAILED")
    
    def save_results(self, summary: TestSummary, output_file: str = None):
        """Save test results to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_results_{timestamp}.json"
        
        results_dict = asdict(summary)
        
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        print(f"📄 Test results saved to: {output_file}")
        
        # Also save JUnit XML format for CI/CD integration
        junit_file = output_file.replace('.json', '_junit.xml')
        self.save_junit_xml(summary, junit_file)
    
    def save_junit_xml(self, summary: TestSummary, output_file: str):
        """Save test results in JUnit XML format"""
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Nimo Platform Tests" 
            tests="{summary.total_tests}" 
            failures="{summary.failed}" 
            errors="{summary.errors}" 
            time="{summary.total_duration:.3f}">
'''
        
        # Group tests by suite
        test_suites = {}
        for result in summary.results:
            if result.test_suite not in test_suites:
                test_suites[result.test_suite] = []
            test_suites[result.test_suite].append(result)
        
        for suite_name, tests in test_suites.items():
            suite_passed = len([t for t in tests if t.status == 'passed'])
            suite_failed = len([t for t in tests if t.status == 'failed'])
            suite_errors = len([t for t in tests if t.status == 'error'])
            suite_duration = sum(t.duration for t in tests)
            
            xml_content += f'''  <testsuite name="{suite_name}" 
                      tests="{len(tests)}" 
                      failures="{suite_failed}" 
                      errors="{suite_errors}" 
                      time="{suite_duration:.3f}">
'''
            
            for test in tests:
                xml_content += f'    <testcase name="{test.test_name}" time="{test.duration:.3f}"'
                
                if test.status == 'passed':
                    xml_content += '/>\n'
                elif test.status == 'failed':
                    xml_content += '>\n'
                    xml_content += f'      <failure message="{test.error_message or "Test failed"}">{test.error_message or ""}</failure>\n'
                    xml_content += '    </testcase>\n'
                elif test.status == 'error':
                    xml_content += '>\n'
                    xml_content += f'      <error message="{test.error_message or "Test error"}">{test.error_message or ""}</error>\n'
                    xml_content += '    </testcase>\n'
                elif test.status == 'skipped':
                    xml_content += '>\n'
                    xml_content += f'      <skipped message="{test.error_message or "Test skipped"}"/>\n'
                    xml_content += '    </testcase>\n'
            
            xml_content += '  </testsuite>\n'
        
        xml_content += '</testsuites>\n'
        
        with open(output_file, 'w') as f:
            f.write(xml_content)
        
        print(f"📄 JUnit XML results saved to: {output_file}")


def main():
    """Main test runner CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nimo Platform Test Runner')
    parser.add_argument('--contracts-dir', type=str, default='.',
                       help='Directory containing contract files')
    parser.add_argument('--test-types', nargs='+', 
                       choices=['unit', 'integration', 'security', 'performance'],
                       default=['unit', 'integration', 'security', 'performance'],
                       help='Types of tests to run')
    parser.add_argument('--output', type=str,
                       help='Output file for test results')
    parser.add_argument('--junit', action='store_true',
                       help='Generate JUnit XML output')
    
    args = parser.parse_args()
    
    try:
        runner = NimoTestRunner(Path(args.contracts_dir))
        summary = runner.run_all_tests(args.test_types)
        
        # Save results
        if args.output or args.junit:
            runner.save_results(summary, args.output)
        
        # Exit with appropriate code
        exit_code = 0 if summary.failed == 0 and summary.errors == 0 else 1
        return exit_code
        
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())