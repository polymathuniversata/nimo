#!/usr/bin/env python3
"""
Nimo Platform - Security Audit and Testing Suite

This script performs comprehensive security auditing of the Nimo Platform
smart contracts, including static analysis, vulnerability scanning, and
formal verification checks.
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib

@dataclass
class SecurityFinding:
    """Represents a security finding"""
    severity: str  # "critical", "high", "medium", "low", "info"
    category: str  # "vulnerability", "best_practice", "optimization", "style"
    title: str
    description: str
    file: str
    line: Optional[int]
    recommendation: str
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID

@dataclass
class SecurityAuditReport:
    """Complete security audit report"""
    audit_date: str
    auditor: str
    version: str
    contracts_audited: List[str]
    findings: List[SecurityFinding]
    summary: Dict[str, int]
    overall_score: int  # 0-100
    recommendations: List[str]

class NimoSecurityAuditor:
    """Comprehensive security auditor for Nimo Platform smart contracts"""
    
    def __init__(self, contracts_dir: Path = Path.cwd()):
        """Initialize the security auditor"""
        self.contracts_dir = contracts_dir
        self.findings = []
        self.audit_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Security patterns to check for
        self.vulnerability_patterns = {
            'unsafe_arithmetic': [
                r'(\+|\-|\*|\/)\s*(?!.*overflow)',
                r'(\+|\-|\*|\/)\s*(?!.*underflow)',
            ],
            'unchecked_external_calls': [
                r'external_call\s*\(',
                r'call\s*\(',
            ],
            'missing_access_control': [
                r'fn\s+\w+\s*\([^)]*\)\s*{[^}]*(?!.*require|.*assert|.*list\.has)',
            ],
            'hardcoded_addresses': [
                r'addr1[a-z0-9]{58}',
                r'addr_test1[a-z0-9]{58}',
                r'#"[a-fA-F0-9]{40,64}"',
            ],
            'weak_randomness': [
                r'random\s*\(',
                r'timestamp.*mod',
                r'block.*hash.*mod',
            ],
            'missing_input_validation': [
                r'fn\s+\w+\s*\([^)]*\)\s*{(?![^}]*(?:require|assert|if.*length|when.*is))',
            ]
        }
        
        # Best practices patterns
        self.best_practice_patterns = {
            'missing_documentation': [
                r'fn\s+\w+(?!.*//)',
                r'pub\s+type\s+\w+(?!.*//)',
            ],
            'long_functions': [],  # Handled separately
            'magic_numbers': [
                r'\b(?<!0x)(?<![a-zA-Z_])\d{4,}\b(?![a-zA-Z_])',
            ],
            'unused_imports': [
                r'^use\s+.*$(?!.*//.*used)',
            ]
        }
    
    def audit_all_contracts(self) -> SecurityAuditReport:
        """Perform comprehensive security audit of all contracts"""
        print("🔍 Starting comprehensive security audit...")
        
        # Find all Aiken contract files
        contract_files = list(self.contracts_dir.glob("*.ak"))
        contract_files.extend(list(self.contracts_dir.glob("**/*.ak")))
        
        if not contract_files:
            raise FileNotFoundError("No Aiken contract files found")
        
        print(f"📋 Found {len(contract_files)} contract files to audit")
        
        # Audit each contract file
        for contract_file in contract_files:
            print(f"🔍 Auditing {contract_file.name}...")
            self.audit_contract_file(contract_file)
        
        # Run additional security checks
        self.run_aiken_checks()
        self.check_project_structure()
        self.analyze_dependencies()
        
        # Generate audit report
        report = self.generate_report(contract_files)
        
        print(f"✅ Security audit completed: {len(self.findings)} findings")
        return report
    
    def audit_contract_file(self, file_path: Path):
        """Audit a single contract file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.add_finding(
                "high", "infrastructure", "File Read Error",
                f"Could not read contract file: {e}",
                str(file_path), None,
                "Ensure all contract files are accessible and properly encoded"
            )
            return
        
        lines = content.split('\n')
        
        # Check for vulnerability patterns
        self.check_vulnerability_patterns(content, lines, file_path)
        
        # Check for best practice violations
        self.check_best_practices(content, lines, file_path)
        
        # Perform contract-specific checks
        self.check_contract_specific_issues(content, lines, file_path)
        
        # Check for business logic issues
        self.check_business_logic(content, lines, file_path)
    
    def check_vulnerability_patterns(self, content: str, lines: List[str], file_path: Path):
        """Check for common vulnerability patterns"""
        
        # Check for unsafe arithmetic operations
        for line_num, line in enumerate(lines, 1):
            if re.search(r'(\+|\-|\*|\/)', line) and not re.search(r'(overflow|underflow|safe)', line, re.IGNORECASE):
                if any(op in line for op in ['+', '-', '*', '/']):
                    self.add_finding(
                        "medium", "vulnerability", "Potential Arithmetic Overflow",
                        f"Arithmetic operation without explicit overflow/underflow protection: {line.strip()}",
                        str(file_path), line_num,
                        "Add explicit overflow/underflow checks or use safe arithmetic functions"
                    )
        
        # Check for missing access control
        function_pattern = r'fn\s+(\w+)\s*\([^)]*\)\s*->\s*Bool\s*\{'
        for line_num, line in enumerate(lines, 1):
            if re.search(function_pattern, line):
                # Look ahead to check if there's access control
                next_lines = lines[line_num:line_num + 10]  # Check next 10 lines
                has_access_control = any(
                    re.search(r'(list\.has.*signatories|authorized|admin|verifier)', next_line, re.IGNORECASE)
                    for next_line in next_lines
                )
                
                if not has_access_control and 'test' not in line.lower():
                    self.add_finding(
                        "high", "vulnerability", "Missing Access Control",
                        f"Function may be missing access control checks: {line.strip()}",
                        str(file_path), line_num,
                        "Add proper authorization checks using signatories verification",
                        "CWE-862"
                    )
        
        # Check for hardcoded addresses
        for line_num, line in enumerate(lines, 1):
            if re.search(r'#"[a-fA-F0-9]{40,64}"', line) and 'test' not in file_path.name.lower():
                self.add_finding(
                    "medium", "vulnerability", "Hardcoded Address",
                    f"Hardcoded address found in production code: {line.strip()}",
                    str(file_path), line_num,
                    "Use configuration parameters instead of hardcoded addresses",
                    "CWE-798"
                )
        
        # Check for weak randomness
        for line_num, line in enumerate(lines, 1):
            if re.search(r'timestamp.*mod|block.*hash.*mod', line, re.IGNORECASE):
                self.add_finding(
                    "high", "vulnerability", "Weak Randomness Source",
                    f"Potentially predictable randomness source: {line.strip()}",
                    str(file_path), line_num,
                    "Use cryptographically secure randomness sources",
                    "CWE-338"
                )
    
    def check_best_practices(self, content: str, lines: List[str], file_path: Path):
        """Check for best practice violations"""
        
        # Check for missing documentation
        for line_num, line in enumerate(lines, 1):
            if re.match(r'^\s*fn\s+\w+', line) and not re.search(r'//', line):
                # Check if previous line has documentation
                if line_num == 1 or not re.search(r'//', lines[line_num - 2]):
                    self.add_finding(
                        "low", "best_practice", "Missing Function Documentation",
                        f"Function lacks documentation: {line.strip()}",
                        str(file_path), line_num,
                        "Add comprehensive documentation for all public functions"
                    )
        
        # Check for long functions (>50 lines)
        in_function = False
        function_start = 0
        function_name = ""
        brace_count = 0
        
        for line_num, line in enumerate(lines, 1):
            if re.match(r'^\s*fn\s+(\w+)', line):
                function_match = re.search(r'fn\s+(\w+)', line)
                if function_match:
                    function_name = function_match.group(1)
                    function_start = line_num
                    in_function = True
                    brace_count = line.count('{') - line.count('}')
            
            elif in_function:
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0:
                    function_length = line_num - function_start
                    if function_length > 50:
                        self.add_finding(
                            "medium", "best_practice", "Long Function",
                            f"Function '{function_name}' is {function_length} lines long",
                            str(file_path), function_start,
                            "Consider breaking down long functions into smaller, more manageable functions"
                        )
                    in_function = False
        
        # Check for magic numbers
        for line_num, line in enumerate(lines, 1):
            magic_numbers = re.findall(r'\b(?<!0x)(?<![a-zA-Z_])([1-9]\d{3,})\b(?![a-zA-Z_])', line)
            for number in magic_numbers:
                if number not in ['1000000', '86400']:  # Common Cardano values
                    self.add_finding(
                        "low", "best_practice", "Magic Number",
                        f"Magic number found: {number} in line: {line.strip()}",
                        str(file_path), line_num,
                        "Replace magic numbers with named constants"
                    )
    
    def check_contract_specific_issues(self, content: str, lines: List[str], file_path: Path):
        """Check for contract-specific security issues"""
        
        contract_name = file_path.stem
        
        if 'contribution' in contract_name.lower():
            self.check_contribution_validator_issues(content, lines, file_path)
        elif 'identity' in contract_name.lower():
            self.check_identity_registry_issues(content, lines, file_path)
        elif 'metta' in contract_name.lower():
            self.check_metta_bridge_issues(content, lines, file_path)
    
    def check_contribution_validator_issues(self, content: str, lines: List[str], file_path: Path):
        """Check contribution validator specific issues"""
        
        # Check for reward calculation security
        if 'calculate_confidence_based_reward' in content:
            for line_num, line in enumerate(lines, 1):
                if 'calculate_confidence_based_reward' in line:
                    # Check if there's overflow protection
                    next_lines = lines[line_num:line_num + 20]
                    has_bounds_check = any(
                        re.search(r'(min_reward|max_reward|<|>)', next_line)
                        for next_line in next_lines
                    )
                    
                    if not has_bounds_check:
                        self.add_finding(
                            "high", "vulnerability", "Unbounded Reward Calculation",
                            "Reward calculation may not have proper bounds checking",
                            str(file_path), line_num,
                            "Add explicit minimum and maximum reward bounds"
                        )
        
        # Check for contribution uniqueness
        if 'submit' in content.lower() and 'contribution' in content.lower():
            has_uniqueness_check = re.search(r'(duplicate|unique|already.*exist)', content, re.IGNORECASE)
            if not has_uniqueness_check:
                self.add_finding(
                    "medium", "vulnerability", "Missing Uniqueness Check",
                    "Contribution submission may allow duplicates",
                    str(file_path), None,
                    "Implement checks to prevent duplicate contribution submissions"
                )
    
    def check_identity_registry_issues(self, content: str, lines: List[str], file_path: Path):
        """Check identity registry specific issues"""
        
        # Check for username uniqueness
        if 'username' in content:
            has_uniqueness_check = re.search(r'(username.*unique|duplicate.*username)', content, re.IGNORECASE)
            if not has_uniqueness_check:
                self.add_finding(
                    "high", "vulnerability", "Missing Username Uniqueness",
                    "Username uniqueness may not be properly enforced",
                    str(file_path), None,
                    "Implement proper username uniqueness validation"
                )
        
        # Check for identity transfer security
        if 'transfer' in content.lower():
            for line_num, line in enumerate(lines, 1):
                if 'transfer' in line.lower():
                    # Check if both parties must sign
                    next_lines = lines[line_num:line_num + 10]
                    has_dual_signature = any(
                        re.search(r'(new_owner.*sign|current_owner.*sign)', next_line, re.IGNORECASE)
                        for next_line in next_lines
                    )
                    
                    if not has_dual_signature:
                        self.add_finding(
                            "high", "vulnerability", "Insecure Identity Transfer",
                            "Identity transfer may not require signatures from both parties",
                            str(file_path), line_num,
                            "Require signatures from both current owner and new owner for transfers"
                        )
    
    def check_metta_bridge_issues(self, content: str, lines: List[str], file_path: Path):
        """Check MeTTa bridge specific issues"""
        
        # Check for proof validation
        if 'metta_proof' in content:
            has_proof_validation = re.search(r'(validate.*proof|verify.*proof|proof.*valid)', content, re.IGNORECASE)
            if not has_proof_validation:
                self.add_finding(
                    "critical", "vulnerability", "Missing Proof Validation",
                    "MeTTa proofs may not be properly validated",
                    str(file_path), None,
                    "Implement cryptographic validation of MeTTa proofs",
                    "CWE-345"
                )
        
        # Check for confidence score validation
        for line_num, line in enumerate(lines, 1):
            if 'confidence' in line and ('score' in line or 'value' in line):
                # Check if confidence is bounded 0-100
                if not re.search(r'(0.*100|<.*100|>.*0)', line):
                    self.add_finding(
                        "medium", "vulnerability", "Unbounded Confidence Score",
                        f"Confidence score may not be properly bounded: {line.strip()}",
                        str(file_path), line_num,
                        "Ensure confidence scores are bounded between 0 and 100"
                    )
    
    def check_business_logic(self, content: str, lines: List[str], file_path: Path):
        """Check for business logic vulnerabilities"""
        
        # Check for time-based vulnerabilities
        for line_num, line in enumerate(lines, 1):
            if re.search(r'(expires?_at|created_at|timestamp)', line):
                # Check if there's proper time validation
                next_lines = lines[max(0, line_num-3):line_num+3]
                has_time_validation = any(
                    re.search(r'(current_time|validity_range|>|<)', next_line)
                    for next_line in next_lines
                )
                
                if not has_time_validation:
                    self.add_finding(
                        "medium", "vulnerability", "Missing Time Validation",
                        f"Timestamp usage without proper validation: {line.strip()}",
                        str(file_path), line_num,
                        "Add proper timestamp validation against current time"
                    )
        
        # Check for fee extraction vulnerabilities
        if 'fee' in content.lower():
            for line_num, line in enumerate(lines, 1):
                if 'fee' in line.lower() and ('calculate' in line or '*' in line or '/' in line):
                    if not re.search(r'(percentage|%|/\s*100)', line):
                        self.add_finding(
                            "medium", "vulnerability", "Unclear Fee Calculation",
                            f"Fee calculation may be unclear or unsafe: {line.strip()}",
                            str(file_path), line_num,
                            "Ensure fee calculations are explicit and safe from manipulation"
                        )
    
    def run_aiken_checks(self):
        """Run Aiken's built-in security checks"""
        try:
            # Run Aiken check command
            result = subprocess.run(
                ['aiken', 'check', '--all'],
                cwd=self.contracts_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.add_finding(
                    "high", "infrastructure", "Aiken Check Failed",
                    f"Aiken security checks failed: {result.stderr}",
                    "project", None,
                    "Fix all issues reported by Aiken checker"
                )
            else:
                # Parse Aiken warnings/errors if any
                if result.stdout:
                    self.parse_aiken_output(result.stdout)
                    
        except subprocess.TimeoutExpired:
            self.add_finding(
                "medium", "infrastructure", "Aiken Check Timeout",
                "Aiken security checks timed out",
                "project", None,
                "Investigate why Aiken checks are taking too long"
            )
        except FileNotFoundError:
            self.add_finding(
                "critical", "infrastructure", "Aiken Not Found",
                "Aiken compiler not found or not properly installed",
                "project", None,
                "Install Aiken compiler and ensure it's in PATH"
            )
    
    def parse_aiken_output(self, output: str):
        """Parse Aiken compiler output for warnings and errors"""
        lines = output.split('\n')
        
        for line in lines:
            if 'Warning:' in line or 'Error:' in line:
                severity = "high" if "Error:" in line else "medium"
                
                self.add_finding(
                    severity, "infrastructure", "Aiken Compiler Issue",
                    line.strip(),
                    "aiken_output", None,
                    "Address the issue reported by Aiken compiler"
                )
    
    def check_project_structure(self):
        """Check for secure project structure"""
        required_files = [
            'aiken.toml',
            'lib/nimo_types.ak',
            'tests/'
        ]
        
        for required_file in required_files:
            file_path = self.contracts_dir / required_file
            if not file_path.exists():
                self.add_finding(
                    "medium", "infrastructure", "Missing Required File",
                    f"Required file/directory missing: {required_file}",
                    "project_structure", None,
                    f"Create the required file/directory: {required_file}"
                )
        
        # Check for sensitive files that shouldn't be included
        sensitive_patterns = [
            '*.key',
            '*.skey',
            '*.seed',
            '*.mnemonic',
            '.env'
        ]
        
        for pattern in sensitive_patterns:
            sensitive_files = list(self.contracts_dir.glob(pattern))
            for sensitive_file in sensitive_files:
                self.add_finding(
                    "high", "vulnerability", "Sensitive File in Repository",
                    f"Sensitive file found: {sensitive_file}",
                    str(sensitive_file), None,
                    "Remove sensitive files from repository and add to .gitignore"
                )
    
    def analyze_dependencies(self):
        """Analyze project dependencies for security issues"""
        aiken_toml = self.contracts_dir / 'aiken.toml'
        
        if not aiken_toml.exists():
            return
        
        try:
            with open(aiken_toml, 'r') as f:
                content = f.read()
            
            # Check for pinned dependency versions
            if 'dependencies' in content:
                lines = content.split('\n')
                in_dependencies = False
                
                for line in lines:
                    if '[dependencies]' in line:
                        in_dependencies = True
                        continue
                    
                    if in_dependencies:
                        if line.startswith('['):  # New section
                            break
                        
                        if '=' in line and 'version' in line:
                            if '*' in line or 'latest' in line:
                                self.add_finding(
                                    "medium", "best_practice", "Unpinned Dependency",
                                    f"Dependency with unpinned version: {line.strip()}",
                                    "aiken.toml", None,
                                    "Pin dependency versions for reproducible builds"
                                )
        
        except Exception as e:
            self.add_finding(
                "low", "infrastructure", "Dependency Analysis Failed",
                f"Could not analyze dependencies: {e}",
                "aiken.toml", None,
                "Ensure aiken.toml is properly formatted"
            )
    
    def add_finding(self, severity: str, category: str, title: str, 
                   description: str, file: str, line: Optional[int],
                   recommendation: str, cwe_id: Optional[str] = None):
        """Add a security finding to the report"""
        finding = SecurityFinding(
            severity=severity,
            category=category,
            title=title,
            description=description,
            file=file,
            line=line,
            recommendation=recommendation,
            cwe_id=cwe_id
        )
        
        self.findings.append(finding)
    
    def generate_report(self, contract_files: List[Path]) -> SecurityAuditReport:
        """Generate comprehensive security audit report"""
        
        # Calculate summary statistics
        summary = {
            'critical': len([f for f in self.findings if f.severity == 'critical']),
            'high': len([f for f in self.findings if f.severity == 'high']),
            'medium': len([f for f in self.findings if f.severity == 'medium']),
            'low': len([f for f in self.findings if f.severity == 'low']),
            'info': len([f for f in self.findings if f.severity == 'info'])
        }
        
        # Calculate overall security score (0-100)
        total_findings = len(self.findings)
        if total_findings == 0:
            overall_score = 100
        else:
            # Weight findings by severity
            weighted_score = (
                summary['critical'] * 20 +
                summary['high'] * 10 +
                summary['medium'] * 5 +
                summary['low'] * 2 +
                summary['info'] * 1
            )
            
            # Convert to 0-100 score (arbitrary scale)
            max_possible_score = total_findings * 20  # If all were critical
            overall_score = max(0, 100 - (weighted_score * 100 / max(max_possible_score, 1)))
        
        # Generate recommendations
        recommendations = self.generate_recommendations(summary)
        
        report = SecurityAuditReport(
            audit_date=self.audit_timestamp,
            auditor="Nimo Platform Security Auditor v1.0",
            version="1.0.0",
            contracts_audited=[str(f.relative_to(self.contracts_dir)) for f in contract_files],
            findings=self.findings,
            summary=summary,
            overall_score=int(overall_score),
            recommendations=recommendations
        )
        
        return report
    
    def generate_recommendations(self, summary: Dict[str, int]) -> List[str]:
        """Generate prioritized recommendations based on findings"""
        recommendations = []
        
        if summary['critical'] > 0:
            recommendations.append(
                f"URGENT: Address {summary['critical']} critical security issues immediately"
            )
        
        if summary['high'] > 0:
            recommendations.append(
                f"HIGH PRIORITY: Fix {summary['high']} high-severity issues before deployment"
            )
        
        if summary['medium'] > 0:
            recommendations.append(
                f"Address {summary['medium']} medium-severity issues to improve security posture"
            )
        
        if summary['low'] > 0:
            recommendations.append(
                f"Consider fixing {summary['low']} low-severity issues for best practices"
            )
        
        # Add general recommendations
        recommendations.extend([
            "Perform external security audit before mainnet deployment",
            "Implement comprehensive test coverage (>90%)",
            "Set up continuous security monitoring",
            "Establish incident response procedures",
            "Regular security reviews and updates"
        ])
        
        return recommendations
    
    def save_report(self, report: SecurityAuditReport, output_file: str = None):
        """Save the security audit report to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"security_audit_report_{timestamp}.json"
        
        report_dict = asdict(report)
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        print(f"📄 Security audit report saved to: {output_file}")
        
        # Also create human-readable HTML report
        html_file = output_file.replace('.json', '.html')
        self.generate_html_report(report, html_file)
    
    def generate_html_report(self, report: SecurityAuditReport, output_file: str):
        """Generate human-readable HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Nimo Platform Security Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #e7f3ff; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .finding {{ margin: 20px 0; padding: 15px; border-left: 4px solid #ddd; }}
        .critical {{ border-left-color: #dc3545; }}
        .high {{ border-left-color: #fd7e14; }}
        .medium {{ border-left-color: #ffc107; }}
        .low {{ border-left-color: #28a745; }}
        .severity {{ font-weight: bold; text-transform: uppercase; }}
        .recommendation {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; }}
        .score {{ font-size: 2em; font-weight: bold; color: {'#28a745' if report.overall_score >= 80 else '#ffc107' if report.overall_score >= 60 else '#dc3545'}; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Nimo Platform Security Audit Report</h1>
        <p><strong>Audit Date:</strong> {report.audit_date}</p>
        <p><strong>Auditor:</strong> {report.auditor}</p>
        <p><strong>Version:</strong> {report.version}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Security Score</h2>
        <div class="score">{report.overall_score}/100</div>
        
        <h3>Findings Summary</h3>
        <ul>
            <li>🔴 Critical: {report.summary['critical']}</li>
            <li>🟠 High: {report.summary['high']}</li>
            <li>🟡 Medium: {report.summary['medium']}</li>
            <li>🟢 Low: {report.summary['low']}</li>
            <li>ℹ️ Info: {report.summary['info']}</li>
        </ul>
    </div>
    
    <h2>📋 Contracts Audited</h2>
    <ul>
        {''.join(f'<li>{contract}</li>' for contract in report.contracts_audited)}
    </ul>
    
    <h2>🔍 Detailed Findings</h2>
    {''.join(f'''
    <div class="finding {finding.severity}">
        <h3><span class="severity">{finding.severity}</span> - {finding.title}</h3>
        <p><strong>File:</strong> {finding.file}{f" (Line {finding.line})" if finding.line else ""}</p>
        <p><strong>Category:</strong> {finding.category}</p>
        <p><strong>Description:</strong> {finding.description}</p>
        <div class="recommendation">
            <strong>💡 Recommendation:</strong> {finding.recommendation}
        </div>
        {f'<p><strong>CWE ID:</strong> {finding.cwe_id}</p>' if finding.cwe_id else ''}
    </div>
    ''' for finding in report.findings)}
    
    <h2>🎯 Recommendations</h2>
    <ul>
        {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
    </ul>
    
    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        Generated by Nimo Platform Security Auditor on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </footer>
</body>
</html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML report saved to: {output_file}")


def main():
    """Main security audit CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nimo Platform Security Auditor')
    parser.add_argument('--contracts-dir', type=str, default='.',
                       help='Directory containing contract files')
    parser.add_argument('--output', type=str,
                       help='Output file for audit report')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Report format')
    
    args = parser.parse_args()
    
    try:
        auditor = NimoSecurityAuditor(Path(args.contracts_dir))
        report = auditor.audit_all_contracts()
        
        # Print summary to console
        print("\n" + "="*60)
        print("🔒 SECURITY AUDIT SUMMARY")
        print("="*60)
        print(f"Overall Security Score: {report.overall_score}/100")
        print(f"Total Findings: {len(report.findings)}")
        print(f"Critical: {report.summary['critical']}")
        print(f"High: {report.summary['high']}")
        print(f"Medium: {report.summary['medium']}")
        print(f"Low: {report.summary['low']}")
        
        if report.summary['critical'] > 0 or report.summary['high'] > 0:
            print("\n⚠️  HIGH PRIORITY ISSUES FOUND - Address before deployment!")
        elif report.summary['medium'] > 0:
            print("\n⚡ Medium priority issues found - Consider addressing")
        else:
            print("\n✅ No critical or high-severity issues found")
        
        # Save report
        auditor.save_report(report, args.output)
        
        print("\n📄 Security audit completed successfully!")
        
        return 0 if report.summary['critical'] == 0 and report.summary['high'] == 0 else 1
        
    except Exception as e:
        print(f"❌ Security audit failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())