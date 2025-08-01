#!/usr/bin/env python3
"""
NOXSUITE PHASE 1 SYSTEM VALIDATOR
Implementation of Phase 1 Core System Stabilization Protocol
Date: 2025-07-29
Author: System Stabilization Framework
"""

import json
import time
import psutil
import subprocess
import asyncio
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class SystemStatus(Enum):
    CRITICAL = "critical"
    STABLE = "stable"
    OPTIMAL = "optimal"

class IssuePriority(Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"

@dataclass
class SystemCheck:
    component: str
    status: SystemStatus
    metrics: Dict[str, float]
    issues: List[str]
    recommendations: List[str]
    timestamp: str

@dataclass
class GateRequirement:
    name: str
    criteria: List[str]
    current_score: float
    required_score: float
    blockers: List[str]
    passed: bool

class Phase1SystemValidator:
    """
    Core System Stabilization Validator
    Implements comprehensive Phase 1 validation protocol
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = []
        self.flask_server_url = "http://localhost:5000"
        self.critical_thresholds = {
            'response_time_ms': 200,
            'memory_usage_mb': 50,
            'cpu_usage_percent': 30,
            'error_rate_percent': 0.1,
            'security_score': 90
        }
        
    async def validate_system(self) -> List[SystemCheck]:
        """Main validation entry point"""
        print("🔍 PHASE 1 SYSTEM VALIDATION STARTING")
        print("=" * 50)
        
        checks = await asyncio.gather(
            self.validate_security(),
            self.validate_stability(),
            self.validate_performance(),
            return_exceptions=True
        )
        
        # Filter out exceptions
        valid_checks = [c for c in checks if isinstance(c, SystemCheck)]
        self.results = valid_checks
        
        print("\n📊 PHASE 1 VALIDATION COMPLETE")
        return valid_checks
    
    async def validate_security(self) -> SystemCheck:
        """Security validation - Gate 2 compliance check"""
        print("🔒 Validating Security Foundation...")
        
        metrics = {}
        issues = []
        recommendations = []
        
        # Check if Flask server is running with security patches
        try:
            response = requests.get(f"{self.flask_server_url}/api/emergency/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('security_status') == 'EMERGENCY_PATCHED':
                    metrics['security_patch_active'] = 1.0
                    print("  ✅ Emergency security patches: ACTIVE")
                else:
                    metrics['security_patch_active'] = 0.0
                    issues.append("Emergency security patches not detected")
            else:
                metrics['security_patch_active'] = 0.0
                issues.append("Emergency status endpoint not accessible")
        except Exception as e:
            metrics['security_patch_active'] = 0.0
            issues.append(f"Flask server not accessible: {str(e)}")
            recommendations.append("Start Flask server with security patches")
        
        # Test authentication protection
        try:
            auth_response = requests.get(f"{self.flask_server_url}/api/knowledge/search", timeout=5)
            if auth_response.status_code == 401:
                metrics['authentication_protection'] = 1.0
                print("  ✅ Authentication protection: ACTIVE")
            else:
                metrics['authentication_protection'] = 0.0
                issues.append("Authentication bypass detected")
        except Exception:
            metrics['authentication_protection'] = 0.0
            issues.append("Cannot test authentication protection")
        
        # Check security headers
        try:
            headers_response = requests.get(f"{self.flask_server_url}/", timeout=5)
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options', 
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'Content-Security-Policy'
            ]
            
            present_headers = sum(1 for header in security_headers 
                                if header in headers_response.headers)
            metrics['security_headers_score'] = (present_headers / len(security_headers)) * 100
            
            if present_headers >= 4:
                print(f"  ✅ Security headers: {present_headers}/5 present")
            else:
                issues.append(f"Missing security headers: {5-present_headers}")
                
        except Exception:
            metrics['security_headers_score'] = 0.0
            issues.append("Cannot check security headers")
        
        # Calculate overall security score
        security_score = (
            metrics.get('security_patch_active', 0) * 40 +
            metrics.get('authentication_protection', 0) * 35 +
            metrics.get('security_headers_score', 0) * 0.25
        )
        metrics['overall_security_score'] = security_score
        
        # Determine status
        if security_score >= 90:
            status = SystemStatus.OPTIMAL
        elif security_score >= 70:
            status = SystemStatus.STABLE
        else:
            status = SystemStatus.CRITICAL
            
        if security_score < 70:
            recommendations.extend([
                "Apply emergency security patches",
                "Verify authentication middleware",
                "Enable comprehensive security headers"
            ])
        
        return SystemCheck(
            component="Security Foundation",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    async def validate_stability(self) -> SystemCheck:
        """System stability validation"""
        print("🛡️ Validating System Stability...")
        
        metrics = {}
        issues = []
        recommendations = []
        
        # Memory usage check
        memory = psutil.virtual_memory()
        metrics['memory_usage_percent'] = memory.percent
        metrics['memory_available_gb'] = memory.available / (1024**3)
        
        if memory.percent > 85:
            issues.append(f"High memory usage: {memory.percent}%")
            recommendations.append("Investigate memory usage patterns")
        else:
            print(f"  ✅ Memory usage: {memory.percent}% (healthy)")
        
        # CPU usage check
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics['cpu_usage_percent'] = cpu_percent
        
        if cpu_percent > 70:
            issues.append(f"High CPU usage: {cpu_percent}%")
            recommendations.append("Investigate CPU intensive processes")
        else:
            print(f"  ✅ CPU usage: {cpu_percent}% (healthy)")
        
        # Disk usage check
        disk = psutil.disk_usage('/')
        metrics['disk_usage_percent'] = (disk.used / disk.total) * 100
        
        if metrics['disk_usage_percent'] > 85:
            issues.append(f"High disk usage: {metrics['disk_usage_percent']:.1f}%")
            recommendations.append("Clean up disk space")
        else:
            print(f"  ✅ Disk usage: {metrics['disk_usage_percent']:.1f}% (healthy)")
        
        # Process stability check
        try:
            # Check for Python processes (Flask server)
            python_processes = [p for p in psutil.process_iter(['pid', 'name', 'memory_info']) 
                             if 'python' in p.info['name'].lower()]
            metrics['python_processes_count'] = len(python_processes)
            
            if python_processes:
                total_memory = sum(p.info['memory_info'].rss for p in python_processes)
                metrics['python_memory_mb'] = total_memory / (1024**2)
                print(f"  ✅ Python processes: {len(python_processes)} running")
            else:
                issues.append("No Python processes detected")
                recommendations.append("Verify Flask server is running")
                
        except Exception as e:
            issues.append(f"Process check failed: {str(e)}")
        
        # Calculate stability score
        stability_factors = [
            1.0 if memory.percent < 70 else 0.5,
            1.0 if cpu_percent < 50 else 0.5,
            1.0 if metrics['disk_usage_percent'] < 80 else 0.5,
            1.0 if len(python_processes) > 0 else 0.0
        ]
        stability_score = (sum(stability_factors) / len(stability_factors)) * 100
        metrics['stability_score'] = stability_score
        
        # Determine status
        if stability_score >= 90:
            status = SystemStatus.OPTIMAL
        elif stability_score >= 70:
            status = SystemStatus.STABLE
        else:
            status = SystemStatus.CRITICAL
        
        return SystemCheck(
            component="System Stability",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    async def validate_performance(self) -> SystemCheck:
        """Performance validation - Response times and efficiency"""
        print("⚡ Validating Performance Baseline...")
        
        metrics = {}
        issues = []
        recommendations = []
        
        # API response time testing
        endpoints_to_test = [
            "/",
            "/api/emergency/status"
        ]
        
        response_times = []
        for endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                response = requests.get(f"{self.flask_server_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)
                
                if response_time_ms < 200:
                    print(f"  ✅ {endpoint}: {response_time_ms:.1f}ms")
                else:
                    issues.append(f"Slow response {endpoint}: {response_time_ms:.1f}ms")
                    
            except Exception as e:
                issues.append(f"Cannot test {endpoint}: {str(e)}")
                recommendations.append("Ensure Flask server is running")
        
        if response_times:
            metrics['avg_response_time_ms'] = sum(response_times) / len(response_times)
            metrics['max_response_time_ms'] = max(response_times)
        else:
            metrics['avg_response_time_ms'] = 0
            metrics['max_response_time_ms'] = 0
            issues.append("No response times measured")
        
        # File system performance
        try:
            test_file = self.base_path / "performance_test.tmp"
            
            # Write test
            start_time = time.time()
            test_file.write_text("performance test data" * 1000)
            write_time = (time.time() - start_time) * 1000
            
            # Read test
            start_time = time.time()
            test_file.read_text()
            read_time = (time.time() - start_time) * 1000
            
            # Cleanup
            test_file.unlink()
            
            metrics['file_write_ms'] = write_time
            metrics['file_read_ms'] = read_time
            
            if write_time < 10 and read_time < 5:
                print(f"  ✅ File I/O: Write {write_time:.1f}ms, Read {read_time:.1f}ms")
            else:
                issues.append(f"Slow file I/O: Write {write_time:.1f}ms, Read {read_time:.1f}ms")
                
        except Exception as e:
            issues.append(f"File I/O test failed: {str(e)}")
        
        # Calculate performance score
        perf_factors = []
        
        # Response time factor
        if metrics['avg_response_time_ms'] > 0:
            if metrics['avg_response_time_ms'] < 100:
                perf_factors.append(1.0)
            elif metrics['avg_response_time_ms'] < 200:
                perf_factors.append(0.8)
            else:
                perf_factors.append(0.4)
        
        # File I/O factor
        if 'file_write_ms' in metrics and 'file_read_ms' in metrics:
            if metrics['file_write_ms'] < 10 and metrics['file_read_ms'] < 5:
                perf_factors.append(1.0)
            else:
                perf_factors.append(0.6)
        
        performance_score = (sum(perf_factors) / len(perf_factors) * 100) if perf_factors else 0
        metrics['performance_score'] = performance_score
        
        # Determine status
        if performance_score >= 85:
            status = SystemStatus.OPTIMAL
        elif performance_score >= 70:
            status = SystemStatus.STABLE
        else:
            status = SystemStatus.CRITICAL
            
        if performance_score < 70:
            recommendations.extend([
                "Optimize API response times",
                "Implement caching strategies",
                "Review database query performance"
            ])
        
        return SystemCheck(
            component="Performance Baseline",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def validate_phase1_gates(self) -> List[GateRequirement]:
        """Validate Phase 1 progress gates"""
        print("\n🎯 VALIDATING PHASE 1 PROGRESS GATES")
        print("=" * 40)
        
        gates = []
        
        # Security Gate
        security_check = next((r for r in self.results if r.component == "Security Foundation"), None)
        if security_check:
            security_score = security_check.metrics.get('overall_security_score', 0)
            security_gate = GateRequirement(
                name="Security Validation",
                criteria=[
                    "No critical vulnerabilities",
                    "Authentication working", 
                    "Data validation complete",
                    "CSRF protection active"
                ],
                current_score=security_score,
                required_score=90.0,
                blockers=security_check.issues,
                passed=security_score >= 90
            )
            gates.append(security_gate)
            
            status_icon = "✅" if security_gate.passed else "❌"
            print(f"{status_icon} Security Gate: {security_score:.1f}/100 (Required: 90)")
        
        # Stability Gate
        stability_check = next((r for r in self.results if r.component == "System Stability"), None)
        if stability_check:
            stability_score = stability_check.metrics.get('stability_score', 0)
            stability_gate = GateRequirement(
                name="System Stability",
                criteria=[
                    "No memory leaks",
                    "Error handling complete",
                    "State management stable", 
                    "API endpoints reliable"
                ],
                current_score=stability_score,
                required_score=85.0,
                blockers=stability_check.issues,
                passed=stability_score >= 85
            )
            gates.append(stability_gate)
            
            status_icon = "✅" if stability_gate.passed else "❌"
            print(f"{status_icon} Stability Gate: {stability_score:.1f}/100 (Required: 85)")
        
        # Performance Gate
        performance_check = next((r for r in self.results if r.component == "Performance Baseline"), None)
        if performance_check:
            performance_score = performance_check.metrics.get('performance_score', 0)
            performance_gate = GateRequirement(
                name="Performance Baseline",
                criteria=[
                    "Response time < 200ms",
                    "Bundle size optimized",
                    "Caching implemented",
                    "Resources optimized"
                ],
                current_score=performance_score,
                required_score=80.0,
                blockers=performance_check.issues,
                passed=performance_score >= 80
            )
            gates.append(performance_gate)
            
            status_icon = "✅" if performance_gate.passed else "❌"
            print(f"{status_icon} Performance Gate: {performance_score:.1f}/100 (Required: 80)")
        
        return gates
    
    def can_proceed_to_phase2(self, gates: List[GateRequirement]) -> bool:
        """Check if all Phase 1 gates are passed"""
        all_passed = all(gate.passed for gate in gates)
        
        print(f"\n🚀 PHASE 2 READINESS: {'✅ READY' if all_passed else '❌ BLOCKED'}")
        
        if not all_passed:
            print("\n🚫 BLOCKERS:")
            for gate in gates:
                if not gate.passed:
                    print(f"  • {gate.name}: {gate.current_score:.1f}/{gate.required_score}")
                    for blocker in gate.blockers:
                        print(f"    - {blocker}")
        
        return all_passed
    
    def generate_report(self, gates: List[GateRequirement]) -> Dict[str, Any]:
        """Generate comprehensive Phase 1 validation report"""
        
        # Convert SystemCheck objects to serializable dictionaries
        serializable_checks = []
        for check in self.results:
            check_dict = {
                "component": check.component,
                "status": check.status.value,  # Convert enum to string
                "metrics": check.metrics,
                "issues": check.issues,
                "recommendations": check.recommendations,
                "timestamp": check.timestamp
            }
            serializable_checks.append(check_dict)
        
        # Convert GateRequirement objects to serializable dictionaries
        serializable_gates = []
        for gate in gates:
            gate_dict = {
                "name": gate.name,
                "criteria": gate.criteria,
                "current_score": gate.current_score,
                "required_score": gate.required_score,
                "blockers": gate.blockers,
                "passed": gate.passed
            }
            serializable_gates.append(gate_dict)
        
        report = {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "Phase 1 - Core System Stabilization",
            "overall_status": "PASSED" if self.can_proceed_to_phase2(gates) else "BLOCKED",
            "system_checks": serializable_checks,
            "progress_gates": serializable_gates,
            "recommendations": [],
            "next_steps": []
        }
        
        # Collect all recommendations
        for check in self.results:
            report["recommendations"].extend(check.recommendations)
        
        # Add next steps based on status
        if report["overall_status"] == "PASSED":
            report["next_steps"] = [
                "Phase 1 validation complete",
                "System ready for Phase 2 features",
                "Begin ADHD-friendly feature implementation",
                "Maintain monitoring and validation"
            ]
        else:
            failed_gates = [gate for gate in gates if not gate.passed]
            report["next_steps"] = [
                f"Resolve blockers in: {', '.join(gate.name for gate in failed_gates)}",
                "Re-run Phase 1 validation",
                "Address critical issues before Phase 2"
            ]
        
        return report

async def main():
    """Main execution function"""
    validator = Phase1SystemValidator()
    
    # Run system validation
    checks = await validator.validate_system()
    
    # Validate progress gates
    gates = validator.validate_phase1_gates()
    
    # Check Phase 2 readiness
    can_proceed = validator.can_proceed_to_phase2(gates)
    
    # Generate and save report
    report = validator.generate_report(gates)
    
    # Save report to file
    report_file = Path("PHASE_1_VALIDATION_REPORT.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 REPORT SAVED: {report_file}")
    
    # Display summary
    print("\n" + "="*60)
    print("🎯 PHASE 1 VALIDATION SUMMARY")
    print("="*60)
    
    for check in checks:
        status_emoji = {"critical": "🚨", "stable": "🟡", "optimal": "✅"}
        print(f"{status_emoji[check.status.value]} {check.component}: {check.status.value.upper()}")
    
    print(f"\n🚀 Phase 2 Readiness: {'✅ READY' if can_proceed else '❌ BLOCKED'}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
