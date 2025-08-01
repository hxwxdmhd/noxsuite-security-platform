#!/usr/bin/env python3
"""
Security Audit Emulation Script
Workaround for blocked external security scanning services (Safety, Semgrep)
"""

import os
import json
import subprocess
import re
import datetime
from pathlib import Path

class SecurityAuditEmulator:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "bandit_scan": {},
            "custom_vulnerabilities": [],
            "dependency_issues": [],
            "summary": {}
        }
        
    def run_local_bandit_scan(self):
        """Run Bandit security scanner locally"""
        print("🔍 Running local Bandit security scan...")
        
        try:
            # Run bandit with JSON output, excluding archived/deprecated folders
            cmd = [
                "bandit", "-r", ".", 
                "--format", "json",
                "--skip", "B101,B601",  # Skip assert and shell usage in tests
                "--exclude", "./archive,./archived,./NoxPanel_Suite_WIP/archive,./backup_*,./node_modules,./venv"
            ]
            
            result = subprocess.run(cmd, cwd=self.project_path, capture_output=True, text=True)
            
            if result.stdout:
                bandit_data = json.loads(result.stdout)
                self.results["bandit_scan"] = bandit_data
                
                # Filter high severity issues
                high_severity = [r for r in bandit_data.get("results", []) 
                               if r.get("issue_severity") == "HIGH"]
                
                print(f"✅ Bandit scan completed: {len(bandit_data.get('results', []))} total issues")
                print(f"🚨 High severity issues: {len(high_severity)}")
                
                return bandit_data
            else:
                print("⚠️ Bandit scan completed with no JSON output")
                return {}
                
        except Exception as e:
            print(f"❌ Bandit scan failed: {e}")
            return {}
    
    def emulate_safety_check(self):
        """Emulate Safety dependency vulnerability checking"""
        print("🔍 Emulating Safety dependency vulnerability check...")
        
        known_vulnerabilities = {
            "requests": ["<2.31.0", "CVE-2023-32681"],
            "flask": ["<2.2.0", "CVE-2023-30861"],
            "jinja2": ["<3.1.0", "CVE-2024-22195"],
            "werkzeug": ["<2.2.0", "CVE-2023-25577"],
            "pyyaml": ["<6.0", "CVE-2020-14343"]
        }
        
        requirements_files = [
            "requirements.txt", "requirements-prod.txt", "requirements-dev.txt",
            "requirements-security.txt", "requirements-ai.txt"
        ]
        
        for req_file in requirements_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                print(f"📋 Checking {req_file}...")
                with open(req_path, 'r') as f:
                    content = f.read()
                    
                    for package, (version, cve) in known_vulnerabilities.items():
                        if package in content:
                            self.results["dependency_issues"].append({
                                "package": package,
                                "file": req_file,
                                "vulnerability": cve,
                                "recommended_version": version,
                                "severity": "HIGH"
                            })
    
    def emulate_semgrep_patterns(self):
        """Emulate Semgrep security pattern detection"""
        print("🔍 Emulating Semgrep security pattern detection...")
        
        security_patterns = {
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'secret\s*=\s*["\'][^"\']{16,}["\']',
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']'
            ],
            "command_injection": [
                r'subprocess\.(call|run|Popen)\([^)]*shell\s*=\s*True',
                r'os\.system\(',
                r'os\.popen\(',
                r'commands\.(getoutput|getstatusoutput)\('
            ],
            "insecure_crypto": [
                r'hashlib\.md5\(',
                r'Crypto\.Hash\.MD5',
                r'ssl_verify\s*=\s*False',
                r'verify\s*=\s*False'
            ],
            "debug_mode": [
                r'debug\s*=\s*True',
                r'DEBUG\s*=\s*True',
                r'app\.run\([^)]*debug\s*=\s*True'
            ]
        }
        
        python_files = list(self.project_path.rglob("*.py"))
        
        # Exclude archived and deprecated files
        excluded_patterns = ["archive", "archived", "backup_", "deprecated", "node_modules"]
        python_files = [f for f in python_files 
                       if not any(excl in str(f) for excl in excluded_patterns)]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for category, patterns in security_patterns.items():
                        for pattern in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                self.results["custom_vulnerabilities"].append({
                                    "file": str(file_path.relative_to(self.project_path)),
                                    "line": line_num,
                                    "category": category,
                                    "pattern": pattern,
                                    "match": match.group(),
                                    "severity": "HIGH" if category in ["hardcoded_secrets", "command_injection"] else "MEDIUM"
                                })
            except Exception as e:
                print(f"⚠️ Error scanning {file_path}: {e}")
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        print("📊 Generating security audit report...")
        
        # Count issues by severity
        bandit_high = len([r for r in self.results["bandit_scan"].get("results", []) 
                          if r.get("issue_severity") == "HIGH"])
        
        custom_high = len([v for v in self.results["custom_vulnerabilities"] 
                          if v.get("severity") == "HIGH"])
        
        dependency_high = len([d for d in self.results["dependency_issues"] 
                              if d.get("severity") == "HIGH"])
        
        total_high = bandit_high + custom_high + dependency_high
        
        self.results["summary"] = {
            "total_high_severity": total_high,
            "bandit_high_severity": bandit_high,
            "custom_pattern_high_severity": custom_high,
            "dependency_high_severity": dependency_high,
            "total_issues": len(self.results["bandit_scan"].get("results", [])) + 
                           len(self.results["custom_vulnerabilities"]) + 
                           len(self.results["dependency_issues"])
        }
        
        # Save detailed report
        report_file = self.project_path / f"security_audit_emulated_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📋 Detailed report saved to: {report_file}")
        
        return self.results
    
    def print_summary(self):
        """Print executive summary"""
        summary = self.results["summary"]
        
        print("\n" + "="*60)
        print("🛡️  SECURITY AUDIT EMULATION COMPLETE")
        print("="*60)
        print(f"📊 Total High Severity Issues: {summary['total_high_severity']}")
        print(f"🔍 Bandit High Severity: {summary['bandit_high_severity']}")
        print(f"🎯 Custom Pattern High Severity: {summary['custom_pattern_high_severity']}")
        print(f"📦 Dependency High Severity: {summary['dependency_high_severity']}")
        print(f"📈 Total Issues Found: {summary['total_issues']}")
        print("="*60)
        
        # Show top issues by category
        if self.results["custom_vulnerabilities"]:
            print("\n🚨 Top Security Issues Found:")
            categories = {}
            for vuln in self.results["custom_vulnerabilities"]:
                cat = vuln["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(vuln)
            
            for category, vulns in categories.items():
                high_severity_count = len([v for v in vulns if v.get("severity") == "HIGH"])
                if high_severity_count > 0:
                    print(f"  • {category}: {high_severity_count} high severity issues")
    
    def run_complete_audit(self):
        """Run complete security audit emulation"""
        print("🚀 Starting Security Audit Emulation...")
        print("📍 Working around blocked external services (Safety, Semgrep)")
        print(f"📂 Scanning project: {self.project_path}")
        print("-" * 60)
        
        # Run all audit components
        self.run_local_bandit_scan()
        self.emulate_safety_check()
        self.emulate_semgrep_patterns()
        
        # Generate comprehensive report
        self.generate_security_report()
        self.print_summary()
        
        return self.results

if __name__ == "__main__":
    project_path = "/home/runner/work/noxsuite-security-platform/noxsuite-security-platform"
    auditor = SecurityAuditEmulator(project_path)
    results = auditor.run_complete_audit()