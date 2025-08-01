#!/usr/bin/env python3
"""
NoxSuite Project Audit Engine v4.0
===================================

Comprehensive project state validation and gate assessment system.
This script provides real-time analysis of project health and progression status.

Usage:
    python audit_engine_v4.py [--gate N] [--report] [--fix] [--emergency]
    
Options:
    --gate N      Validate specific gate (1-8)
    --report      Generate comprehensive report
    --fix         Attempt automated fixes for critical issues
    --emergency   Emergency stabilization mode
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AuditResult:
    """Audit result data structure"""
    gate: str
    score: int
    max_score: int
    status: str
    details: List[str]
    blockers: List[str]
    recommendations: List[str]
    timestamp: str

class NoxSuiteAuditEngine:
    """Comprehensive audit engine for NoxSuite project"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results = {}
        self.critical_issues = []
        self.security_gaps = []
        
        # Load project state
        self.project_state = self._load_project_state()
        
        logger.info(f"🔍 NoxSuite Audit Engine v4.0 initialized")
        logger.info(f"📁 Project root: {self.project_root}")
    
    def _load_project_state(self) -> Dict[str, Any]:
        """Load current project state"""
        state_file = self.project_root / "project_state.json"
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning("⚠️ project_state.json not found, using defaults")
            return {"system_name": "Unknown", "version": "0.0", "current_phase": "unknown"}
    
    def audit_gate_1_foundation(self) -> AuditResult:
        """Audit Gate 1: Foundation systems"""
        logger.info("🏗️ Auditing Gate 1: Foundation Systems")
        
        score = 0
        max_score = 100
        details = []
        blockers = []
        
        # Check Docker infrastructure (20 points)
        docker_files = [
            "docker-compose.yml",
            "Dockerfile",
            "docker-compose.production.yml"
        ]
        
        docker_score = 0
        for file in docker_files:
            if (self.project_root / file).exists():
                docker_score += 7
                details.append(f"✅ {file} exists")
            else:
                details.append(f"❌ {file} missing")
        
        score += min(docker_score, 20)
        
        # Check database functionality (20 points)
        database_files = [
            "NoxPanel/noxcore/database.py",
            "NoxPanel/noxcore/migrations.py",
            "NoxPanel/noxcore/database_service.py"
        ]
        
        db_score = 0
        for file in database_files:
            if (self.project_root / file).exists():
                db_score += 7
                details.append(f"✅ Database: {file} exists")
            else:
                details.append(f"❌ Database: {file} missing")
        
        score += min(db_score, 20)
        
        # Check core server (20 points)
        server_files = [
            "NoxPanel/webpanel/app.py",
            "NoxPanel/webpanel/app_v5.py",
            "main.py"
        ]
        
        server_exists = any((self.project_root / file).exists() for file in server_files)
        if server_exists:
            score += 20
            details.append("✅ Core server files found")
        else:
            details.append("❌ No core server files found")
            blockers.append("Core server application missing")
        
        # Check monitoring (20 points)
        monitoring_files = [
            "docker-compose.yml",  # Should contain Prometheus/Grafana
        ]
        
        # Simple check for monitoring mentions in docker-compose
        try:
            with open(self.project_root / "docker-compose.yml", 'r') as f:
                compose_content = f.read()
                if "prometheus" in compose_content.lower() or "grafana" in compose_content.lower():
                    score += 20
                    details.append("✅ Monitoring stack configured")
                else:
                    details.append("⚠️ Monitoring stack not detected in compose")
        except FileNotFoundError:
            details.append("❌ docker-compose.yml not found")
        
        # Check installation system (20 points)
        installer_files = [
            "install_noxsuite.py",
            "SMART_INSTALLER_README.md",
            "AUDIT_AND_FIX_REPORT.md"
        ]
        
        installer_score = 0
        for file in installer_files:
            if (self.project_root / file).exists():
                installer_score += 7
                details.append(f"✅ Installer: {file} exists")
        
        score += min(installer_score, 20)
        
        # Determine status
        if score >= 80:
            status = "PASSED"
        elif score >= 60:
            status = "CONDITIONAL_PASS"
        else:
            status = "FAILED"
            
        # Add critical syntax error check
        syntax_error_found = self._check_critical_syntax_errors()
        if syntax_error_found:
            blockers.append("Critical syntax error found - must fix before progression")
            status = "BLOCKED"
        
        return AuditResult(
            gate="Gate 1: Foundation",
            score=score,
            max_score=max_score,
            status=status,
            details=details,
            blockers=blockers,
            recommendations=self._get_gate1_recommendations(score),
            timestamp=datetime.now().isoformat()
        )
    
    def audit_gate_2_security(self) -> AuditResult:
        """Audit Gate 2: Security foundation"""
        logger.info("🔒 Auditing Gate 2: Security Foundation")
        
        score = 0
        max_score = 100
        details = []
        blockers = []
        
        # Check authentication system (30 points)
        auth_files = [
            "NoxPanel/noxcore/auth.py",
            "NoxPanel/noxcore/security.py"
        ]
        
        auth_score = 0
        for file in auth_files:
            if (self.project_root / file).exists():
                auth_score += 15
                details.append(f"✅ Auth: {file} exists")
                
                # Check for authentication bypass vulnerability
                try:
                    with open(self.project_root / file, 'r') as f:
                        content = f.read()
                        if "/api/knowledge" in content and "@auth_required" not in content:
                            blockers.append("Critical: /api/knowledge/* endpoints lack authentication")
                            auth_score -= 10  # Penalty for security gap
                except Exception as e:
                    details.append(f"⚠️ Could not analyze {file}: {e}")
        
        score += auth_score
        
        # Check security headers (25 points)
        security_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        headers_implemented = self._check_security_headers()
        header_score = len(headers_implemented) * 5
        score += min(header_score, 25)
        
        for header in headers_implemented:
            details.append(f"✅ Security header: {header}")
        
        missing_headers = set(security_headers) - set(headers_implemented)
        for header in missing_headers:
            details.append(f"❌ Missing security header: {header}")
            
        if missing_headers:
            blockers.append(f"Missing critical security headers: {', '.join(missing_headers)}")
        
        # Check input validation (25 points)
        validation_score = self._check_input_validation()
        score += validation_score
        
        if validation_score < 20:
            blockers.append("Insufficient input validation - SQL injection risk")
            details.append("❌ Input validation insufficient")
        else:
            details.append("✅ Input validation implemented")
        
        # Check session security (20 points)
        session_score = self._check_session_security()
        score += session_score
        
        if session_score < 15:
            blockers.append("Insecure session management detected")
            details.append("❌ Session security insufficient")
        else:
            details.append("✅ Session security implemented")
        
        # Determine status
        if blockers:
            status = "BLOCKED"
        elif score >= 80:
            status = "PASSED"
        elif score >= 60:
            status = "CONDITIONAL_PASS"
        else:
            status = "FAILED"
        
        return AuditResult(
            gate="Gate 2: Security",
            score=score,
            max_score=max_score,
            status=status,
            details=details,
            blockers=blockers,
            recommendations=self._get_gate2_recommendations(score),
            timestamp=datetime.now().isoformat()
        )
    
    def audit_gate_3_code_quality(self) -> AuditResult:
        """Audit Gate 3: Code quality and stability"""
        logger.info("📊 Auditing Gate 3: Code Quality")
        
        score = 0
        max_score = 100
        details = []
        blockers = []
        
        # Load analysis results
        analysis_file = self.project_root / "current_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
                
            # Critical issues (30 points)
            critical_count = analysis.get("summary", {}).get("severities", {}).get("critical", 0)
            if critical_count == 0:
                score += 30
                details.append("✅ No critical issues")
            elif critical_count <= 10:
                score += 20
                details.append(f"⚠️ {critical_count} critical issues (target: 0)")
            else:
                details.append(f"❌ {critical_count} critical issues (target: 0)")
                blockers.append(f"{critical_count} critical issues must be resolved")
            
            # Type annotations (25 points)
            type_hint_count = analysis.get("summary", {}).get("issue_types", {}).get("type_hint", 0)
            if type_hint_count <= 100:
                score += 25
                details.append("✅ Type annotations adequate")
            elif type_hint_count <= 500:
                score += 15
                details.append(f"⚠️ {type_hint_count} missing type annotations")
            else:
                details.append(f"❌ {type_hint_count} missing type annotations")
            
            # Performance issues (25 points) 
            perf_count = analysis.get("summary", {}).get("issue_types", {}).get("performance", 0)
            if perf_count <= 500:
                score += 25
                details.append("✅ Performance issues minimal")
            elif perf_count <= 1000:
                score += 15
                details.append(f"⚠️ {perf_count} performance issues")
            else:
                details.append(f"❌ {perf_count} performance issues")
            
            # Deprecated code (20 points)
            deprecated_count = analysis.get("summary", {}).get("issue_types", {}).get("deprecated", 0)
            if deprecated_count == 0:
                score += 20
                details.append("✅ No deprecated code")
            elif deprecated_count <= 10:
                score += 10
                details.append(f"⚠️ {deprecated_count} deprecated code instances")
            else:
                details.append(f"❌ {deprecated_count} deprecated code instances")
        
        else:
            details.append("❌ Code analysis results not found")
            blockers.append("Code analysis must be completed")
        
        # Test coverage check (bonus points if available)
        # This would require actual test execution
        
        # Determine status
        if blockers:
            status = "BLOCKED"
        elif score >= 75:
            status = "PASSED"
        elif score >= 50:
            status = "CONDITIONAL_PASS"
        else:
            status = "FAILED"
        
        return AuditResult(
            gate="Gate 3: Code Quality",
            score=score,
            max_score=max_score,
            status=status,
            details=details,
            blockers=blockers,
            recommendations=self._get_gate3_recommendations(score),
            timestamp=datetime.now().isoformat()
        )
    
    def _check_critical_syntax_errors(self) -> bool:
        """Check for critical syntax errors"""
        try:
            # Check the known syntax error location
            problem_file = self.project_root / "AI/NoxPanel/simple_noxpanel_fixed.py"
            if problem_file.exists():
                # Try to compile the file to check for syntax errors
                with open(problem_file, 'r') as f:
                    content = f.read()
                try:
                    compile(content, str(problem_file), 'exec')
                    return False
                except SyntaxError:
                    logger.error(f"Syntax error found in {problem_file}")
                    return True
        except Exception as e:
            logger.warning(f"Could not check syntax: {e}")
        
        return False
    
    def _check_security_headers(self) -> List[str]:
        """Check for security headers implementation"""
        implemented = []
        
        # Check in common locations
        search_files = [
            "NoxPanel/noxcore/security.py",
            "NoxPanel/noxcore/security_headers.py",
            "NoxPanel/webpanel/app.py",
            "NoxPanel/webpanel/app_v5.py"
        ]
        
        headers_to_check = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection", 
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        for file_path in search_files:
            file_full_path = self.project_root / file_path
            if file_full_path.exists():
                try:
                    with open(file_full_path, 'r') as f:
                        content = f.read()
                        for header in headers_to_check:
                            if header in content and header not in implemented:
                                implemented.append(header)
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        return implemented
    
    def _check_input_validation(self) -> int:
        """Check input validation implementation"""
        score = 0
        
        # Look for validation patterns in route handlers
        search_files = [
            "NoxPanel/webpanel/app.py",
            "NoxPanel/webpanel/app_v5.py",
            "NoxPanel/noxcore/validation.py"
        ]
        
        validation_patterns = [
            "sanitize",
            "validate",
            "escape",
            "clean_input",
            "request.json",
            "wtforms"
        ]
        
        for file_path in search_files:
            file_full_path = self.project_root / file_path
            if file_full_path.exists():
                try:
                    with open(file_full_path, 'r') as f:
                        content = f.read().lower()
                        for pattern in validation_patterns:
                            if pattern in content:
                                score += 3
                except Exception as e:
                    logger.warning(f"Could not analyze {file_path}: {e}")
        
        return min(score, 25)
    
    def _check_session_security(self) -> int:
        """Check session security configuration"""
        score = 0
        
        search_files = [
            "NoxPanel/webpanel/app.py",
            "NoxPanel/webpanel/app_v5.py"
        ]
        
        security_configs = [
            "SESSION_COOKIE_SECURE",
            "SESSION_COOKIE_HTTPONLY",
            "SESSION_COOKIE_SAMESITE",
            "SECRET_KEY",
            "session.permanent"
        ]
        
        for file_path in search_files:
            file_full_path = self.project_root / file_path
            if file_full_path.exists():
                try:
                    with open(file_full_path, 'r') as f:
                        content = f.read()
                        for config in security_configs:
                            if config in content:
                                score += 4
                except Exception as e:
                    logger.warning(f"Could not analyze {file_path}: {e}")
        
        return min(score, 20)
    
    def _get_gate1_recommendations(self, score: int) -> List[str]:
        """Get recommendations for Gate 1"""
        recommendations = []
        
        if score < 80:
            recommendations.append("Ensure all Docker configuration files are present and valid")
            recommendations.append("Verify database system is properly configured and accessible")
            recommendations.append("Complete core server application setup")
            recommendations.append("Configure monitoring stack (Prometheus/Grafana)")
        
        recommendations.append("Fix critical syntax error in simple_noxpanel_fixed.py")
        recommendations.append("Run comprehensive system health check")
        
        return recommendations
    
    def _get_gate2_recommendations(self, score: int) -> List[str]:
        """Get recommendations for Gate 2"""
        recommendations = []
        
        if score < 80:
            recommendations.append("CRITICAL: Implement authentication on /api/knowledge/* endpoints")
            recommendations.append("Add comprehensive security headers middleware")
            recommendations.append("Implement input validation on all user-facing endpoints")
            recommendations.append("Configure secure session management")
            recommendations.append("Run security vulnerability scan")
        
        return recommendations
    
    def _get_gate3_recommendations(self, score: int) -> List[str]:
        """Get recommendations for Gate 3"""
        recommendations = []
        
        if score < 75:
            recommendations.append("Address all critical issues (target: 0)")
            recommendations.append("Add type annotations to improve code clarity")
            recommendations.append("Optimize performance bottlenecks")
            recommendations.append("Replace deprecated code with modern alternatives")
            recommendations.append("Implement comprehensive test suite")
        
        return recommendations
    
    def run_comprehensive_audit(self) -> Dict[str, AuditResult]:
        """Run comprehensive audit of all gates"""
        logger.info("🚀 Starting comprehensive audit...")
        
        results = {}
        
        # Audit available gates
        results["gate_1"] = self.audit_gate_1_foundation()
        results["gate_2"] = self.audit_gate_2_security()
        results["gate_3"] = self.audit_gate_3_code_quality()
        
        return results
    
    def generate_audit_report(self, results: Dict[str, AuditResult]) -> str:
        """Generate comprehensive audit report"""
        report_lines = []
        report_lines.append("# 🔍 NOXSUITE COMPREHENSIVE AUDIT REPORT")
        report_lines.append(f"**Generated**: {datetime.now().isoformat()}")
        report_lines.append(f"**Engine**: NoxSuite Audit Engine v4.0")
        report_lines.append("")
        
        # Executive summary
        total_score = sum(result.score for result in results.values())
        max_total = sum(result.max_score for result in results.values())
        overall_percentage = (total_score / max_total) * 100 if max_total > 0 else 0
        
        report_lines.append("## 📊 EXECUTIVE SUMMARY")
        report_lines.append(f"**Overall Score**: {total_score}/{max_total} ({overall_percentage:.1f}%)")
        report_lines.append("")
        
        # Individual gate results
        for gate_key, result in results.items():
            report_lines.append(f"## {result.gate}")
            report_lines.append(f"**Status**: {result.status}")
            report_lines.append(f"**Score**: {result.score}/{result.max_score} ({(result.score/result.max_score)*100:.1f}%)")
            report_lines.append("")
            
            if result.blockers:
                report_lines.append("### 🚨 CRITICAL BLOCKERS:")
                for blocker in result.blockers:
                    report_lines.append(f"- ❌ {blocker}")
                report_lines.append("")
            
            if result.details:
                report_lines.append("### 📋 DETAILED RESULTS:")
                for detail in result.details:
                    report_lines.append(f"- {detail}")
                report_lines.append("")
            
            if result.recommendations:
                report_lines.append("### 💡 RECOMMENDATIONS:")
                for rec in result.recommendations:
                    report_lines.append(f"- {rec}")
                report_lines.append("")
        
        # Action plan
        report_lines.append("## 🎯 IMMEDIATE ACTION PLAN")
        
        # Collect all blockers
        all_blockers = []
        for result in results.values():
            all_blockers.extend(result.blockers)
        
        if all_blockers:
            report_lines.append("### CRITICAL ISSUES (Fix Immediately):")
            for i, blocker in enumerate(all_blockers, 1):
                report_lines.append(f"{i}. {blocker}")
        else:
            report_lines.append("✅ No critical blockers identified")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*This report was generated by NoxSuite Audit Engine v4.0*")
        
        return "\\n".join(report_lines)
    
    def emergency_stabilization(self) -> Dict[str, str]:
        """Emergency stabilization mode - fix critical issues"""
        logger.info("🚨 EMERGENCY STABILIZATION MODE ACTIVATED")
        
        fixes_applied = {}
        
        # Fix 1: Critical syntax error
        syntax_file = self.project_root / "AI/NoxPanel/simple_noxpanel_fixed.py"
        if syntax_file.exists():
            try:
                with open(syntax_file, 'r') as f:
                    content = f.read()
                
                # Simple fix for common indentation errors
                lines = content.split('\\n')
                fixed_lines = []
                for line in lines:
                    # Remove excessive indentation
                    if line.strip() and len(line) - len(line.lstrip()) > 8:
                        fixed_line = line.lstrip() + "    # Fixed indentation"
                        fixed_lines.append(fixed_line)
                    else:
                        fixed_lines.append(line)
                
                # Write back fixed content
                with open(syntax_file, 'w') as f:
                    f.write('\\n'.join(fixed_lines))
                
                fixes_applied["syntax_error"] = "Attempted automatic indentation fix"
                logger.info("✅ Applied syntax error fix")
                
            except Exception as e:
                fixes_applied["syntax_error"] = f"Failed: {e}"
                logger.error(f"❌ Could not fix syntax error: {e}")
        
        # Fix 2: Create basic security headers middleware
        security_file = self.project_root / "NoxPanel/noxcore/security_headers.py"
        if not security_file.exists():
            try:
                security_file.parent.mkdir(parents=True, exist_ok=True)
                
                security_content = '''"""
Security headers middleware for NoxPanel
"""

from flask import Flask

def add_security_headers(app: Flask):
    """Add security headers to Flask app"""
    
    @app.after_request
    def security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    return app
'''
                
                with open(security_file, 'w') as f:
                    f.write(security_content)
                
                fixes_applied["security_headers"] = "Created security headers middleware"
                logger.info("✅ Created security headers middleware")
                
            except Exception as e:
                fixes_applied["security_headers"] = f"Failed: {e}"
                logger.error(f"❌ Could not create security headers: {e}")
        
        # Fix 3: Create authentication decorator
        auth_file = self.project_root / "NoxPanel/noxcore/auth_required.py"
        if not auth_file.exists():
            try:
                auth_file.parent.mkdir(parents=True, exist_ok=True)
                
                auth_content = '''"""
Authentication decorator for NoxPanel routes
"""

from functools import wraps
from flask import request, jsonify, session

def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for valid session or API key
        if 'user_id' not in session and not request.headers.get('Authorization'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function
'''
                
                with open(auth_file, 'w') as f:
                    f.write(auth_content)
                
                fixes_applied["auth_decorator"] = "Created authentication decorator"
                logger.info("✅ Created authentication decorator")
                
            except Exception as e:
                fixes_applied["auth_decorator"] = f"Failed: {e}"
                logger.error(f"❌ Could not create auth decorator: {e}")
        
        return fixes_applied

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="NoxSuite Audit Engine v4.0")
    parser.add_argument("--gate", type=int, help="Audit specific gate (1-8)")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--fix", action="store_true", help="Attempt automated fixes")
    parser.add_argument("--emergency", action="store_true", help="Emergency stabilization mode")
    
    args = parser.parse_args()
    
    # Initialize audit engine
    audit_engine = NoxSuiteAuditEngine()
    
    if args.emergency:
        logger.info("🚨 Emergency stabilization requested")
        fixes = audit_engine.emergency_stabilization()
        print("\\n🔧 EMERGENCY FIXES APPLIED:")
        for fix_type, result in fixes.items():
            print(f"  {fix_type}: {result}")
        return
    
    if args.gate:
        logger.info(f"🎯 Auditing specific gate: {args.gate}")
        if args.gate == 1:
            result = audit_engine.audit_gate_1_foundation()
        elif args.gate == 2:
            result = audit_engine.audit_gate_2_security()
        elif args.gate == 3:
            result = audit_engine.audit_gate_3_code_quality()
        else:
            logger.error(f"Gate {args.gate} not implemented yet")
            return
        
        print(f"\\n📊 {result.gate} Results:")
        print(f"Status: {result.status}")
        print(f"Score: {result.score}/{result.max_score}")
        
        if result.blockers:
            print("\\n🚨 Blockers:")
            for blocker in result.blockers:
                print(f"  - {blocker}")
        
        return
    
    # Run comprehensive audit
    results = audit_engine.run_comprehensive_audit()
    
    # Print summary
    print("\\n" + "="*60)
    print("🔍 NOXSUITE AUDIT RESULTS SUMMARY")
    print("="*60)
    
    for gate_key, result in results.items():
        status_emoji = "✅" if result.status == "PASSED" else "❌" if result.status == "FAILED" else "⚠️"
        print(f"{status_emoji} {result.gate}: {result.score}/{result.max_score} ({result.status})")
    
    # Show critical blockers
    all_blockers = []
    for result in results.values():
        all_blockers.extend(result.blockers)
    
    if all_blockers:
        print("\\n🚨 CRITICAL BLOCKERS:")
        for blocker in all_blockers:
            print(f"  - {blocker}")
    
    if args.report:
        report = audit_engine.generate_audit_report(results)
        report_file = Path("AUDIT_REPORT_v4.md")
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\\n📄 Comprehensive report saved to: {report_file}")
    
    if args.fix and all_blockers:
        print("\\n🔧 Automated fixes available. Run with --emergency to apply.")

if __name__ == "__main__":
    main()
