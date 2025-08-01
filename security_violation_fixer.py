#!/usr/bin/env python3
"""
Security Violations Audit and Fix Tool
=====================================
Identifies and provides fixes for critical security violations.
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityViolationFixer:
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.violations_found = []
        self.fixes_applied = []
        
    def audit_sql_injection(self) -> List[Dict[str, Any]]:
        """Audit for SQL injection vulnerabilities"""
        violations = []
        
        # Search for string concatenation in SQL queries
        python_files = list(self.workspace_path.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        # Check for SQL injection patterns
                        if re.search(r'f".*SELECT.*{', line, re.IGNORECASE):
                            violations.append({
                                'type': 'SQL_INJECTION',
                                'file': str(file_path),
                                'line': i,
                                'pattern': 'f-string in SQL query',
                                'code': line.strip(),
                                'severity': 'CRITICAL'
                            })
                        
                        if re.search(r'".*(SELECT|INSERT|UPDATE|DELETE).*"\s*\+', line, re.IGNORECASE):
                            violations.append({
                                'type': 'SQL_INJECTION',
                                'file': str(file_path),
                                'line': i,
                                'pattern': 'String concatenation in SQL',
                                'code': line.strip(),
                                'severity': 'CRITICAL'
                            })
                            
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                
        return violations
    
    def audit_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Audit for hardcoded secrets and credentials"""
        violations = []
        
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'HARDCODED_PASSWORD'),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'HARDCODED_API_KEY'),
            (r'secret\s*=\s*["\'][^"\']{8,}["\']', 'HARDCODED_SECRET'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'HARDCODED_TOKEN'),
        ]
        
        python_files = list(self.workspace_path.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, violation_type in secret_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                violations.append({
                                    'type': violation_type,
                                    'file': str(file_path),
                                    'line': i,
                                    'pattern': pattern,
                                    'code': line.strip(),
                                    'severity': 'HIGH'
                                })
                                
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                
        return violations
    
    def audit_input_validation(self) -> List[Dict[str, Any]]:
        """Audit for missing input validation"""
        violations = []
        
        validation_patterns = [
            (r'request\.(form|args|json)\[', 'UNVALIDATED_INPUT'),
            (r'input\s*\(', 'UNVALIDATED_USER_INPUT'),
            (r'eval\s*\(', 'DANGEROUS_EVAL'),
            (r'exec\s*\(', 'DANGEROUS_EXEC'),
        ]
        
        python_files = list(self.workspace_path.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, violation_type in validation_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                violations.append({
                                    'type': violation_type,
                                    'file': str(file_path),
                                    'line': i,
                                    'pattern': pattern,
                                    'code': line.strip(),
                                    'severity': 'HIGH' if 'DANGEROUS' in violation_type else 'MEDIUM'
                                })
                                
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                
        return violations
    
    def audit_session_security(self) -> List[Dict[str, Any]]:
        """Audit for session security issues"""
        violations = []
        
        session_patterns = [
            (r'session\s*\[.*\]\s*=.*', 'INSECURE_SESSION'),
            (r'SECRET_KEY\s*=\s*["\'][^"\']{1,16}["\']', 'WEAK_SECRET_KEY'),
            (r'session\.permanent\s*=\s*False', 'SESSION_NO_EXPIRY'),
        ]
        
        python_files = list(self.workspace_path.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, violation_type in session_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                violations.append({
                                    'type': violation_type,
                                    'file': str(file_path),
                                    'line': i,
                                    'pattern': pattern,
                                    'code': line.strip(),
                                    'severity': 'HIGH'
                                })
                                
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                
        return violations
    
    def run_full_audit(self) -> Dict[str, List[Dict[str, Any]]]:
        """Run comprehensive security audit"""
        logger.info("🔍 Starting comprehensive security audit...")
        
        audit_results = {
            'sql_injection': self.audit_sql_injection(),
            'hardcoded_secrets': self.audit_hardcoded_secrets(),
            'input_validation': self.audit_input_validation(),
            'session_security': self.audit_session_security(),
        }
        
        # Count violations by severity
        total_violations = 0
        critical_count = 0
        high_count = 0
        medium_count = 0
        
        for category, violations in audit_results.items():
            total_violations += len(violations)
            for violation in violations:
                if violation['severity'] == 'CRITICAL':
                    critical_count += 1
                elif violation['severity'] == 'HIGH':
                    high_count += 1
                elif violation['severity'] == 'MEDIUM':
                    medium_count += 1
        
        logger.info(f"📊 Audit Results:")
        logger.info(f"   Total Violations: {total_violations}")
        logger.info(f"   🔴 Critical: {critical_count}")
        logger.info(f"   🟠 High: {high_count}")
        logger.info(f"   🟡 Medium: {medium_count}")
        
        return audit_results
    
    def generate_security_report(self, audit_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate detailed security report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_content = f"""# Security Audit Report
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Audit Tool**: SecurityViolationFixer v1.0

## Executive Summary
"""
        
        total_violations = sum(len(violations) for violations in audit_results.values())
        
        if total_violations == 0:
            report_content += "✅ **NO SECURITY VIOLATIONS FOUND** - System is secure!\n\n"
        else:
            report_content += f"⚠️ **{total_violations} SECURITY VIOLATIONS FOUND** - Immediate attention required!\n\n"
        
        # Detailed findings
        for category, violations in audit_results.items():
            if violations:
                report_content += f"## {category.replace('_', ' ').title()} ({len(violations)} violations)\n\n"
                
                for violation in violations:
                    severity_emoji = {
                        'CRITICAL': '🔴',
                        'HIGH': '🟠', 
                        'MEDIUM': '🟡',
                        'LOW': '🟢'
                    }.get(violation['severity'], '⚪')
                    
                    report_content += f"### {severity_emoji} {violation['type']}\n"
                    report_content += f"- **File**: `{violation['file']}`\n"
                    report_content += f"- **Line**: {violation['line']}\n"
                    report_content += f"- **Severity**: {violation['severity']}\n"
                    report_content += f"- **Code**: `{violation['code']}`\n\n"
        
        # Save report
        report_file = f"security_audit_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📋 Security report saved to: {report_file}")
        return report_file

def main():
    """Main execution function"""
    logger.info("🛡️ NoxSuite Security Violation Fixer - Starting Audit")
    
    fixer = SecurityViolationFixer()
    audit_results = fixer.run_full_audit()
    report_file = fixer.generate_security_report(audit_results)
    
    total_violations = sum(len(violations) for violations in audit_results.values())
    
    if total_violations > 0:
        logger.error(f"❌ {total_violations} security violations found! Review {report_file}")
        sys.exit(1)
    else:
        logger.info("✅ No security violations found - system is secure!")
        sys.exit(0)

if __name__ == "__main__":
    main()
