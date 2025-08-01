#!/usr/bin/env python3
"""
NoxSuite Security Audit Script
==============================

Performs comprehensive security audit and hardening for NoxSuite.
This addresses the HIGH priority security audit item from sprint planning.

Author: NoxSuite Development Team
Date: July 31, 2025
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class SecurityAuditor:
    """Comprehensive security auditor for NoxSuite"""

    def __init__(self):
        self.workspace_root = Path.cwd()
        self.audit_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.findings = {
            "timestamp": self.audit_timestamp,
            "cve_scan": {},
            "dependency_audit": {},
            "code_security": {},
            "configuration_security": {},
            "recommendations": [],
        }

    def log_finding(
        self, category: str, severity: str, description: str, details: Dict = None
    ):
        """Log security finding"""
        finding = {
            "category": category,
            "severity": severity,
            "description": description,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }

        if category not in self.findings:
            self.findings[category] = []

        self.findings[category].append(finding)

        print(f"[{severity}] {category}: {description}")

    def run_security_audit(self):
        """Run comprehensive security audit"""
        print("NoxSuite Security Audit Starting...")
        print("=" * 50)

        try:
            # Phase 1: CVE and Dependency Scan
            print("\nPhase 1: CVE and Dependency Scan")
            self.scan_dependencies()

            # Phase 2: Code Security Analysis
            print("\nPhase 2: Code Security Analysis")
            self.analyze_code_security()

            # Phase 3: Configuration Security
            print("\nPhase 3: Configuration Security")
            self.audit_configurations()

            # Phase 4: Authentication Security
            print("\nPhase 4: Authentication Security")
            self.audit_authentication()

            # Phase 5: Generate Report
            print("\nPhase 5: Generating Security Report")
            self.generate_security_report()

            print("\nSecurity audit completed!")
            return self.findings

        except Exception as e:
            print(f"Security audit failed: {e}")
            return None

    def scan_dependencies(self):
        """Scan for vulnerable dependencies"""
        # Python dependency scan
        self.scan_python_dependencies()

        # Node.js dependency scan
        self.scan_node_dependencies()

        # Docker image scan
        self.scan_docker_images()

    def scan_python_dependencies(self):
        """Scan Python dependencies for vulnerabilities"""
        print("  Scanning Python dependencies...")

        # Check if pip-audit is available
        try:
            subprocess.run(["pip-audit", "--version"],
                           check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("    Installing pip-audit...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pip-audit"], check=True
                )
            except subprocess.CalledProcessError:
                self.log_finding(
                    "dependency_scan",
                    "WARNING",
                    "Could not install pip-audit for Python vulnerability scanning",
                )
                return

        # Run pip-audit
        try:
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                if audit_data.get("vulnerabilities"):
                    for vuln in audit_data["vulnerabilities"]:
                        self.log_finding(
                            "cve_scan",
                            "HIGH",
                            f"Vulnerable package: {vuln.get('package', 'unknown')}",
                            vuln,
                        )
                else:
                    print("    No Python vulnerabilities found")
            else:
                self.log_finding(
                    "dependency_scan",
                    "WARNING",
                    "pip-audit scan failed",
                    {"error": result.stderr},
                )

        except Exception as e:
            self.log_finding(
                "dependency_scan", "ERROR", f"Python dependency scan failed: {e}"
            )

    def scan_node_dependencies(self):
        """Scan Node.js dependencies"""
        print("  Scanning Node.js dependencies...")

        # Check for package.json files
        package_files = list(self.workspace_root.glob("**/package.json"))

        for package_file in package_files:
            if "node_modules" in str(package_file):
                continue

            print(f"    Checking {package_file}")

            try:
                # Run npm audit if npm is available
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    cwd=package_file.parent,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})

                    if vulnerabilities:
                        for pkg, vuln_data in vulnerabilities.items():
                            severity = vuln_data.get("severity", "unknown")
                            self.log_finding(
                                "cve_scan",
                                severity.upper(),
                                f"Node vulnerability in {pkg}",
                                vuln_data,
                            )
                    else:
                        print("      No Node.js vulnerabilities found")

            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                json.JSONDecodeError,
            ):
                self.log_finding(
                    "dependency_scan",
                    "INFO",
                    f"Could not scan {package_file} (npm not available or invalid)",
                )

    def scan_docker_images(self):
        """Scan Docker images for vulnerabilities"""
        print("  Scanning Docker configurations...")

        # Find Dockerfile and docker-compose files
        docker_files = list(self.workspace_root.glob("**/Dockerfile*")) + list(
            self.workspace_root.glob("**/docker-compose*.yml")
        )

        for docker_file in docker_files:
            self.analyze_docker_file(docker_file)

    def analyze_docker_file(self, docker_file: Path):
        """Analyze individual Docker file for security issues"""
        print(f"    Analyzing {docker_file.name}")

        try:
            with open(docker_file, "r") as f:
                content = f.read()

            # Check for security issues
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                line = line.strip()

                # Check for latest tag usage
                if re.search(r"FROM.*:latest", line):
                    self.log_finding(
                        "docker_security",
                        "MEDIUM",
                        f"Using 'latest' tag in {docker_file.name}:{i}",
                        {"line": line, "file": str(docker_file)},
                    )

                # Check for root user
                if re.search(r"USER\s+root", line):
                    self.log_finding(
                        "docker_security",
                        "HIGH",
                        f"Running as root user in {docker_file.name}:{i}",
                        {"line": line, "file": str(docker_file)},
                    )

                # Check for hardcoded secrets
                if re.search(r"(password|secret|key|token)=\w+", line, re.IGNORECASE):
                    self.log_finding(
                        "docker_security",
                        "CRITICAL",
                        f"Possible hardcoded secret in {docker_file.name}:{i}",
                        {"line": line, "file": str(docker_file)},
                    )

        except Exception as e:
            self.log_finding(
                "docker_security", "WARNING", f"Could not analyze {docker_file}: {e}"
            )

    def analyze_code_security(self):
        """Analyze code for security vulnerabilities"""
        # Python code analysis
        self.analyze_python_security()

        # JavaScript code analysis
        self.analyze_javascript_security()

        # Configuration file analysis
        self.analyze_config_files()

    def analyze_python_security(self):
        """Analyze Python code for security issues"""
        print("  Analyzing Python code security...")

        python_files = list(self.workspace_root.glob("**/*.py"))

        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            self.scan_python_file(py_file)

    def scan_python_file(self, py_file: Path):
        """Scan individual Python file for security issues"""
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for eval() usage
                if "eval(" in line_stripped:
                    self.log_finding(
                        "code_security",
                        "CRITICAL",
                        f"Use of eval() in {py_file.name}:{i}",
                        {"file": str(py_file), "line": line_stripped},
                    )

                # Check for exec() usage
                if "exec(" in line_stripped:
                    self.log_finding(
                        "code_security",
                        "CRITICAL",
                        f"Use of exec() in {py_file.name}:{i}",
                        {"file": str(py_file), "line": line_stripped},
                    )

                # Check for hardcoded secrets
                if re.search(
                    r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                    line_stripped,
                    re.IGNORECASE,
                ):
                    self.log_finding(
                        "code_security",
                        "HIGH",
                        f"Possible hardcoded secret in {py_file.name}:{i}",
                        {"file": str(py_file), "line": line_stripped},
                    )

                # Check for SQL injection risks
                if re.search(r'execute\s*\(\s*["\'].*%.*["\']', line_stripped):
                    self.log_finding(
                        "code_security",
                        "HIGH",
                        f"Possible SQL injection risk in {py_file.name}:{i}",
                        {"file": str(py_file), "line": line_stripped},
                    )

                # Check for unsafe deserialization
                if "pickle.loads(" in line_stripped:
                    self.log_finding(
                        "code_security",
                        "HIGH",
                        f"Unsafe pickle deserialization in {py_file.name}:{i}",
                        {"file": str(py_file), "line": line_stripped},
                    )

        except Exception as e:
            self.log_finding(
                "code_security", "WARNING", f"Could not analyze {py_file}: {e}"
            )

    def analyze_javascript_security(self):
        """Analyze JavaScript code for security issues"""
        print("  Analyzing JavaScript code security...")

        js_files = list(self.workspace_root.glob("**/*.js")) + list(
            self.workspace_root.glob("**/*.jsx")
        )

        for js_file in js_files:
            if "node_modules" in str(js_file):
                continue

            self.scan_javascript_file(js_file)

    def scan_javascript_file(self, js_file: Path):
        """Scan individual JavaScript file"""
        try:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for eval() usage
                if "eval(" in line_stripped:
                    self.log_finding(
                        "code_security",
                        "CRITICAL",
                        f"Use of eval() in {js_file.name}:{i}",
                        {"file": str(js_file), "line": line_stripped},
                    )

                # Check for innerHTML with user input
                if re.search(r"innerHTML\s*=.*\+", line_stripped):
                    self.log_finding(
                        "code_security",
                        "MEDIUM",
                        f"Possible XSS risk with innerHTML in {js_file.name}:{i}",
                        {"file": str(js_file), "line": line_stripped},
                    )

                # Check for document.write
                if "document.write(" in line_stripped:
                    self.log_finding(
                        "code_security",
                        "MEDIUM",
                        f"Use of document.write in {js_file.name}:{i}",
                        {"file": str(js_file), "line": line_stripped},
                    )

        except Exception as e:
            self.log_finding(
                "code_security", "WARNING", f"Could not analyze {js_file}: {e}"
            )

    def analyze_config_files(self):
        """Analyze configuration files for security issues"""
        print("  Analyzing configuration files...")

        config_patterns = ["**/.env*", "**/*.conf",
                           "**/*.ini", "**/*.yaml", "**/*.yml"]

        for pattern in config_patterns:
            config_files = list(self.workspace_root.glob(pattern))

            for config_file in config_files:
                self.scan_config_file(config_file)

    def scan_config_file(self, config_file: Path):
        """Scan configuration file for secrets"""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for potential secrets
            secret_patterns = [
                r"password\s*[=:]\s*\w+",
                r"secret\s*[=:]\s*\w+",
                r"key\s*[=:]\s*\w+",
                r"token\s*[=:]\s*\w+",
            ]

            for pattern in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    self.log_finding(
                        "config_security",
                        "MEDIUM",
                        f"Possible secret in {config_file.name}:{line_num}",
                        {"file": str(config_file), "pattern": pattern},
                    )

        except Exception as e:
            self.log_finding(
                "config_security", "WARNING", f"Could not analyze {config_file}: {e}"
            )

    def audit_configurations(self):
        """Audit security configurations"""
        print("  Auditing security configurations...")

        # Check for security headers in web configs
        self.check_security_headers()

        # Check HTTPS configuration
        self.check_https_config()

        # Check CORS configuration
        self.check_cors_config()

    def check_security_headers(self):
        """Check for security headers configuration"""
        # Look for security header configurations
        nginx_configs = list(self.workspace_root.glob("**/*.conf"))

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
        ]

        for config_file in nginx_configs:
            try:
                with open(config_file, "r") as f:
                    content = f.read()

                missing_headers = []
                for header in required_headers:
                    if header not in content:
                        missing_headers.append(header)

                if missing_headers:
                    self.log_finding(
                        "configuration_security",
                        "MEDIUM",
                        f"Missing security headers in {config_file.name}",
                        {"missing_headers": missing_headers},
                    )

            except Exception:
                pass

    def check_https_config(self):
        """Check HTTPS configuration"""
        # Check for HTTPS redirection
        config_files = list(self.workspace_root.glob("**/*.conf"))

        for config_file in config_files:
            try:
                with open(config_file, "r") as f:
                    content = f.read()

                if "listen 80" in content and "return 301 https" not in content:
                    self.log_finding(
                        "configuration_security",
                        "HIGH",
                        f"HTTP without HTTPS redirect in {config_file.name}",
                        {"file": str(config_file)},
                    )

            except Exception:
                pass

    def check_cors_config(self):
        """Check CORS configuration"""
        # Look for CORS configurations
        python_files = list(self.workspace_root.glob("**/*.py"))

        for py_file in python_files:
            try:
                with open(py_file, "r") as f:
                    content = f.read()

                # Check for overly permissive CORS
                if re.search(r"cors.*origins.*\*", content, re.IGNORECASE):
                    self.log_finding(
                        "configuration_security",
                        "MEDIUM",
                        f"Overly permissive CORS in {py_file.name}",
                        {"file": str(py_file)},
                    )

            except Exception:
                pass

    def audit_authentication(self):
        """Audit authentication security"""
        print("  Auditing authentication security...")

        # Check JWT configuration
        self.check_jwt_security()

        # Check password handling
        self.check_password_security()

        # Check session security
        self.check_session_security()

    def check_jwt_security(self):
        """Check JWT security configuration"""
        python_files = list(self.workspace_root.glob("**/*.py"))

        for py_file in python_files:
            try:
                with open(py_file, "r") as f:
                    content = f.read()

                # Check for weak JWT secrets
                if re.search(r'jwt.*secret.*["\']secret["\']', content, re.IGNORECASE):
                    self.log_finding(
                        "authentication_security",
                        "CRITICAL",
                        f"Weak JWT secret in {py_file.name}",
                        {"file": str(py_file)},
                    )

                # Check for missing token expiration
                if "jwt.encode" in content and "exp" not in content:
                    self.log_finding(
                        "authentication_security",
                        "MEDIUM",
                        f"JWT without expiration in {py_file.name}",
                        {"file": str(py_file)},
                    )

            except Exception:
                pass

    def check_password_security(self):
        """Check password handling security"""
        python_files = list(self.workspace_root.glob("**/*.py"))

        for py_file in python_files:
            try:
                with open(py_file, "r") as f:
                    content = f.read()

                # Check for password hashing
                if "password" in content.lower():
                    if not any(
                        hash_func in content
                        for hash_func in ["bcrypt", "scrypt", "argon2", "pbkdf2"]
                    ):
                        self.log_finding(
                            "authentication_security",
                            "HIGH",
                            f"Password handling without strong hashing in {py_file.name}",
                            {"file": str(py_file)},
                        )

            except Exception:
                pass

    def check_session_security(self):
        """Check session security"""
        # Check for secure session configuration
        config_patterns = ["**/*.py", "**/*.js"]

        for pattern in config_patterns:
            files = list(self.workspace_root.glob(pattern))

            for file_path in files:
                try:
                    with open(file_path, "r") as f:
                        content = f.read()

                    # Check for secure cookies
                    if "set-cookie" in content.lower():
                        if (
                            "secure" not in content.lower()
                            or "httponly" not in content.lower()
                        ):
                            self.log_finding(
                                "authentication_security",
                                "MEDIUM",
                                f"Insecure cookie configuration in {file_path.name}",
                                {"file": str(file_path)},
                            )

                except Exception:
                    pass

    def generate_security_report(self):
        """Generate comprehensive security report"""
        # Count findings by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for category, findings in self.findings.items():
            if isinstance(findings, list):
                for finding in findings:
                    severity = finding.get("severity", "LOW")
                    severity_counts[severity] += 1

        # Generate recommendations
        recommendations = self.generate_recommendations(severity_counts)
        self.findings["recommendations"] = recommendations

        # Save detailed report
        report_file = (
            self.workspace_root /
            f"security_audit_report_{self.audit_timestamp}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.findings, f, indent=2, default=str)

        # Generate summary report
        self.generate_security_summary(severity_counts, report_file)

        print(f"  Security report saved: {report_file}")

    def generate_recommendations(self, severity_counts: Dict[str, int]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        if severity_counts["CRITICAL"] > 0:
            recommendations.append(
                "URGENT: Address critical vulnerabilities immediately"
            )
            recommendations.append(
                "Review and remove any eval() or exec() usage")
            recommendations.append(
                "Remove hardcoded secrets and use environment variables"
            )

        if severity_counts["HIGH"] > 0:
            recommendations.append(
                "HIGH: Fix high-severity issues within 24 hours")
            recommendations.append(
                "Implement proper password hashing (bcrypt/scrypt)")
            recommendations.append(
                "Add HTTPS redirects for all HTTP endpoints")

        recommendations.extend(
            [
                "Install and configure security headers (CSP, HSTS, etc.)",
                "Implement proper input validation and sanitization",
                "Set up automated dependency vulnerability scanning",
                "Configure secure session management with HttpOnly and Secure flags",
                "Implement rate limiting for authentication endpoints",
                "Set up security monitoring and alerting",
                "Conduct regular penetration testing",
                "Create incident response procedures",
            ]
        )

        return recommendations

    def generate_security_summary(
        self, severity_counts: Dict[str, int], report_file: Path
    ):
        """Generate security summary report"""
        total_findings = sum(severity_counts.values())

        summary = f"""# NoxSuite Security Audit Summary

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Findings:** {total_findings}

## Severity Breakdown
- **Critical:** {severity_counts['CRITICAL']} issues
- **High:** {severity_counts['HIGH']} issues  
- **Medium:** {severity_counts['MEDIUM']} issues
- **Low:** {severity_counts['LOW']} issues

## Risk Assessment
"""

        if severity_counts["CRITICAL"] > 0:
            summary += "🔴 **HIGH RISK** - Critical vulnerabilities require immediate attention\n"
        elif severity_counts["HIGH"] > 0:
            summary += (
                "🟡 **MEDIUM RISK** - High-severity issues need prompt resolution\n"
            )
        elif total_findings > 0:
            summary += "🟢 **LOW RISK** - Minor security improvements recommended\n"
        else:
            summary += "✅ **SECURE** - No significant security issues found\n"

        summary += f"""
## Immediate Actions Required
"""

        for rec in self.findings["recommendations"][:5]:
            summary += f"- {rec}\n"

        summary += f"""
## Next Steps
1. Review detailed findings in {report_file.name}
2. Prioritize critical and high-severity issues
3. Implement security hardening measures
4. Set up automated security scanning
5. Schedule regular security audits

## Security Checklist
- [ ] Fix all critical vulnerabilities
- [ ] Address high-severity issues
- [ ] Implement security headers
- [ ] Configure HTTPS properly
- [ ] Set up dependency scanning
- [ ] Review authentication security
- [ ] Test input validation
- [ ] Configure secure sessions
"""

        summary_file = (
            self.workspace_root /
            f"security_audit_summary_{self.audit_timestamp}.md"
        )
        with open(summary_file, "w") as f:
            f.write(summary)

        print(f"  Security summary: {summary_file}")


def main():
    """Main execution"""
    print("NoxSuite Security Audit")
    print("=" * 30)

    try:
        auditor = SecurityAuditor()
        results = auditor.run_security_audit()

        if results:
            # Print summary
            total_findings = 0
            severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

            for category, findings in results.items():
                if isinstance(findings, list):
                    for finding in findings:
                        severity = finding.get("severity", "LOW")
                        severity_counts[severity] += 1
                        total_findings += 1

            print(f"\nSECURITY AUDIT SUMMARY:")
            print(f"Total findings: {total_findings}")
            print(f"Critical: {severity_counts['CRITICAL']}")
            print(f"High: {severity_counts['HIGH']}")
            print(f"Medium: {severity_counts['MEDIUM']}")
            print(f"Low: {severity_counts['LOW']}")

            if severity_counts["CRITICAL"] > 0:
                print("\n🔴 CRITICAL issues found - immediate action required!")
                return 1
            elif severity_counts["HIGH"] > 0:
                print("\n🟡 HIGH severity issues found - prompt action needed")
                return 1
            else:
                print("\n✅ No critical security issues found")
                return 0
        else:
            print("Security audit failed")
            return 1

    except Exception as e:
        print(f"Security audit error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
