from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)

#!/usr/bin/env python3
"""
NoxSuite Installer Status Checker
Quick diagnostic tool to check installer health and environment
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
import traceback

class InstallerStatusChecker:
    """
    REASONING CHAIN:
    1. Problem: System component InstallerStatusChecker needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for InstallerStatusChecker functionality
    3. Solution: Implement InstallerStatusChecker with SOLID principles and enterprise patterns
    4. Validation: Test InstallerStatusChecker with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Check installer status and provide diagnostics"""
    
    def __init__(self):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.current_dir = Path.cwd()
        self.issues = []
        self.recommendations = []
    
    def check_installer_files(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function check_installer_files needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_installer_files operation
    3. Solution: Implement check_installer_files with enterprise-grade patterns and error handling
    4. Validation: Test check_installer_files with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if all installer files are present"""
        required_files = [
            "install_noxsuite.py",
            "noxsuite_smart_installer_complete.py",
            "noxsuite_bootstrap_installer.py"
        ]
        
        optional_files = [
            "noxsuite_installer_utils.py",
            "requirements.txt"
        ]
        
        status = {
            "required": {},
            "optional": {},
            "missing_required": [],
            "missing_optional": []
        }
        
        for file in required_files:
            file_path = self.current_dir / file
            exists = file_path.exists()
            status["required"][file] = {
                "exists": exists,
                "path": str(file_path),
                "size": file_path.stat().st_size if exists else 0
            }
            if not exists:
                status["missing_required"].append(file)
                self.issues.append(f"Missing required file: {file}")
        
        for file in optional_files:
            file_path = self.current_dir / file
            exists = file_path.exists()
            status["optional"][file] = {
                "exists": exists,
                "path": str(file_path),
                "size": file_path.stat().st_size if exists else 0
            }
            if not exists:
                status["missing_optional"].append(file)
        
        return status
    
    def check_python_dependencies(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function check_python_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_python_dependencies operation
    3. Solution: Implement check_python_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test check_python_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check Python dependencies"""
        dependencies = {
            "requests": {"required": False, "fallback": "urllib"},
            "chardet": {"required": False, "fallback": "basic encoding detection"}
        }
        
        status = {}
        
        for dep, info in dependencies.items():
            try:
                __import__(dep)
                status[dep] = {
                    "available": True,
                    "version": "unknown",
                    "required": info["required"]
                }
            except ImportError:
                status[dep] = {
                    "available": False,
                    "required": info["required"],
                    "fallback": info["fallback"]
                }
                
                if info["required"]:
                    self.issues.append(f"Missing required dependency: {dep}")
                else:
                    self.recommendations.append(f"Install {dep} for enhanced functionality")
        
        return status
    
    def check_system_compatibility(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function check_system_compatibility needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_system_compatibility operation
    3. Solution: Implement check_system_compatibility with enterprise-grade patterns and error handling
    4. Validation: Test check_system_compatibility with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check system compatibility"""
        import platform
        
        python_version = sys.version_info
        min_python = (3, 8)
        
        status = {
            "python_version": {
                "current": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                "required": f"{min_python[0]}.{min_python[1]}+",
                "compatible": python_version >= min_python
            },
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "architecture": platform.architecture()[0]
            },
            "encoding_support": {
                "stdout": getattr(sys.stdout, 'encoding', 'unknown'),
                "filesystem": sys.getfilesystemencoding(),
                "utf8_mode": sys.flags.utf8_mode if hasattr(sys.flags, 'utf8_mode') else False
            }
        }
        
        if not status["python_version"]["compatible"]:
            self.issues.append(f"Python {min_python[0]}.{min_python[1]}+ required")
        
        return status
    
    def check_logs(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function check_logs needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_logs operation
    3. Solution: Implement check_logs with enterprise-grade patterns and error handling
    4. Validation: Test check_logs with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check for existing logs and their status"""
        log_files = [
            "noxsuite_installer.log",
            "noxsuite_bootstrap.log"
        ]
        
        status = {}
        
        for log_file in log_files:
            log_path = self.current_dir / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    status[log_file] = {
                        "exists": True,
                        "size": log_path.stat().st_size,
                        "lines": len(lines),
                        "last_session": self._extract_last_session(lines)
                    }
                except Exception as e:
                    status[log_file] = {
                        "exists": True,
                        "error": str(e),
                        "readable": False
                    }
            else:
                status[log_file] = {"exists": False}
        
        return status
    
    def _extract_last_session(self, lines: List[str]) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _extract_last_session with enterprise-grade patterns and error handling
    4. Validation: Test _extract_last_session with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Extract information about the last session from log lines"""
        if not lines:
            return {"status": "empty_log"}
        
        # Look for session start and errors
        session_starts = [line for line in lines if "session_start" in line]
        errors = [line for line in lines if "[ERROR]" in line]
        completions = [line for line in lines if "Installation completed" in line]
        
        return {
            "sessions": len(session_starts),
            "errors": len(errors),
            "last_completion": len(completions) > 0,
            "last_error": errors[-1].strip() if errors else None
        }
    
    def generate_diagnostic_report(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Function generate_diagnostic_report needs clear operational definition
    2. Analysis: Implementation requires specific logic for generate_diagnostic_report operation
    3. Solution: Implement generate_diagnostic_report with enterprise-grade patterns and error handling
    4. Validation: Test generate_diagnostic_report with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Generate comprehensive diagnostic report"""
        logger.info("🔍 Running NoxSuite Installer Diagnostics...")
        
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "working_directory": str(self.current_dir),
            "files": self.check_installer_files(),
            "dependencies": self.check_python_dependencies(),
            "system": self.check_system_compatibility(),
            "logs": self.check_logs(),
            "issues": self.issues,
            "recommendations": self.recommendations
        }
        
        return report
    
    def print_status_summary(self, report: Dict[str, Any]):
    """
    REASONING CHAIN:
    1. Problem: Function print_status_summary needs clear operational definition
    2. Analysis: Implementation requires specific logic for print_status_summary operation
    3. Solution: Implement print_status_summary with enterprise-grade patterns and error handling
    4. Validation: Test print_status_summary with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Print human-readable status summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 NoxSuite Installer Status Summary")
        logger.info("=" * 60)
        
        # Files status
        logger.info("\n📁 Installer Files:")
        missing_req = report["files"]["missing_required"]
        if missing_req:
            logger.info(f"❌ Missing required files: {', '.join(missing_req)}")
        else:
            logger.info("✅ All required files present")
        
        missing_opt = report["files"]["missing_optional"]
        if missing_opt:
            logger.info(f"⚠️  Missing optional files: {', '.join(missing_opt)}")
        
        # Dependencies status
        logger.info("\n📦 Dependencies:")
        for dep, info in report["dependencies"].items():
            if info["available"]:
                logger.info(f"✅ {dep} available")
            else:
                fallback = info.get("fallback", "none")
                logger.info(f"⚠️  {dep} missing (fallback: {fallback})")
        
        # System status
        logger.info(f"\n💻 System:")
        sys_info = report["system"]
        python_compat = "✅" if sys_info["python_version"]["compatible"] else "❌"
        logger.info(f"{python_compat} Python {sys_info['python_version']['current']}")
        logger.info(f"📊 Platform: {sys_info['platform']['system']} {sys_info['platform']['architecture']}")
        
        # Logs status
        logger.info(f"\n📝 Logs:")
        for log_file, info in report["logs"].items():
            if info["exists"]:
                if "last_session" in info:
                    session_info = info["last_session"]
                    status = "✅" if session_info.get("last_completion") else "⚠️"
                    logger.info(f"{status} {log_file} ({info['lines']} lines, {session_info['sessions']} sessions)")
                else:
                    logger.info(f"❌ {log_file} (unreadable)")
            else:
                logger.info(f"📝 {log_file} (not found)")
        
        # Issues and recommendations
        if self.issues:
            logger.info(f"\n❌ Issues Found ({len(self.issues)}):")
            for issue in self.issues:
                logger.info(f"   • {issue}")
        
        if self.recommendations:
            logger.info(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for rec in self.recommendations:
                logger.info(f"   • {rec}")
        
        if not self.issues:
            logger.info(f"\n🎉 Installer Status: HEALTHY")
        else:
            logger.info(f"\n⚠️  Installer Status: NEEDS ATTENTION")

def main():
    """
    REASONING CHAIN:
    1. Problem: Function main needs clear operational definition
    2. Analysis: Implementation requires specific logic for main operation
    3. Solution: Implement main with enterprise-grade patterns and error handling
    4. Validation: Test main with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Main status checker"""
    try:
        checker = InstallerStatusChecker()
        report = checker.generate_diagnostic_report()
        
        # Print summary
        checker.print_status_summary(report)
        
        # Save detailed report
        report_file = Path("installer_diagnostic_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📊 Detailed report saved to: {report_file}")
        
        # Return exit code based on issues
        return 0 if not checker.issues else 1
        
    except Exception as e:
        logger.info(f"💥 Diagnostic check failed: {e}")
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())
