from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
NoxSuite Bootstrap Installer
Self-contained installer that bootstraps its own dependencies before launching the full installer
Uses only Python standard library modules to ensure maximum compatibility
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import traceback
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Force UTF-8 output on Windows
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

class BootstrapLogger:
    """
    REASONING CHAIN:
    1. Problem: System component BootstrapLogger needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for BootstrapLogger functionality
    3. Solution: Implement BootstrapLogger with SOLID principles and enterprise patterns
    4. Validation: Test BootstrapLogger with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Simple logger using only standard library"""
    
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
        self.log_file = Path("noxsuite_bootstrap.log")
        self.ensure_log_file()
    
    def ensure_log_file(self):
    """
    REASONING CHAIN:
    1. Problem: Function ensure_log_file needs clear operational definition
    2. Analysis: Implementation requires specific logic for ensure_log_file operation
    3. Solution: Implement ensure_log_file with enterprise-grade patterns and error handling
    4. Validation: Test ensure_log_file with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Ensure log file exists and is writable"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Bootstrap Session Started: {self._get_timestamp()} ===\n")
        except Exception as e:
            logger.info(f"Warning: Could not create log file: {e}")
            self.log_file = None
    
    def _get_timestamp(self):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _get_timestamp with enterprise-grade patterns and error handling
    4. Validation: Test _get_timestamp with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_to_file(self, level: str, message: str):
    """
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement _log_to_file with enterprise-grade patterns and error handling
    4. Validation: Test _log_to_file with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log message to file if possible"""
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{self._get_timestamp()}] [{level}] {message}\n")
            except:
                pass  # Silent fail for logging
    
    def info(self, message: str):
    """
    REASONING CHAIN:
    1. Problem: Function info needs clear operational definition
    2. Analysis: Implementation requires specific logic for info operation
    3. Solution: Implement info with enterprise-grade patterns and error handling
    4. Validation: Test info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log info message"""
        logger.info(f"ℹ️  {message}")
        self._log_to_file("INFO", message)
    
    def success(self, message: str):
    """
    REASONING CHAIN:
    1. Problem: Function success needs clear operational definition
    2. Analysis: Implementation requires specific logic for success operation
    3. Solution: Implement success with enterprise-grade patterns and error handling
    4. Validation: Test success with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log success message"""
        logger.info(f"✅ {message}")
        self._log_to_file("SUCCESS", message)
    
    def warning(self, message: str):
    """
    REASONING CHAIN:
    1. Problem: Function warning needs clear operational definition
    2. Analysis: Implementation requires specific logic for warning operation
    3. Solution: Implement warning with enterprise-grade patterns and error handling
    4. Validation: Test warning with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log warning message"""
        logger.info(f"⚠️  {message}")
        self._log_to_file("WARNING", message)
    
    def error(self, message: str):
    """
    REASONING CHAIN:
    1. Problem: Function error needs clear operational definition
    2. Analysis: Implementation requires specific logic for error operation
    3. Solution: Implement error with enterprise-grade patterns and error handling
    4. Validation: Test error with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log error message"""
        logger.info(f"❌ {message}")
        self._log_to_file("ERROR", message)
    
    def debug(self, message: str):
    """
    REASONING CHAIN:
    1. Problem: Function debug needs clear operational definition
    2. Analysis: Implementation requires specific logic for debug operation
    3. Solution: Implement debug with enterprise-grade patterns and error handling
    4. Validation: Test debug with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Log debug message"""
        self._log_to_file("DEBUG", message)

class DependencyInstaller:
    """
    REASONING CHAIN:
    1. Problem: System component DependencyInstaller needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for DependencyInstaller functionality
    3. Solution: Implement DependencyInstaller with SOLID principles and enterprise patterns
    4. Validation: Test DependencyInstaller with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Handles installation of required Python packages"""
    
    def __init__(self, logger: BootstrapLogger):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.logger = logger
        self.required_packages = [
            'requests>=2.25.0',
            'chardet>=4.0.0'
        ]
    
    def check_dependencies(self) -> Dict[str, bool]:
    """
    REASONING CHAIN:
    1. Problem: Function check_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_dependencies operation
    3. Solution: Implement check_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test check_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check which dependencies are available"""
        status = {}
        
        for package in self.required_packages:
            package_name = package.split('>=')[0].split('==')[0]
            try:
                __import__(package_name)
                status[package_name] = True
                self.logger.debug(f"Found package: {package_name}")
            except ImportError:
                status[package_name] = False
                self.logger.debug(f"Missing package: {package_name}")
        
        return status
    
    def install_package(self, package: str) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function install_package needs clear operational definition
    2. Analysis: Implementation requires specific logic for install_package operation
    3. Solution: Implement install_package with enterprise-grade patterns and error handling
    4. Validation: Test install_package with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Install a single package using various methods"""
        self.logger.info(f"Installing {package}...")
        
        try:
            # Try different installation methods in order of preference
            install_methods = [
                # Standard pip install
                [sys.executable, '-m', 'pip', 'install', package],
                ['pip3', 'install', package],
                ['pip', 'install', package],
                
                # User install (for managed environments)
                [sys.executable, '-m', 'pip', 'install', '--user', package],
                ['pip3', 'install', '--user', package],
                
                # Break system packages (last resort)
                [sys.executable, '-m', 'pip', 'install', '--break-system-packages', package],
                ['pip3', 'install', '--break-system-packages', package],
                
                # Try system package manager (Linux)
                ['apt-get', 'install', '-y', f'python3-{package.split(">=")[0]}'],
                ['yum', 'install', '-y', f'python3-{package.split(">=")[0]}'],
                ['dnf', 'install', '-y', f'python3-{package.split(">=")[0]}'],
                
                # Try package managers (macOS)
                ['brew', 'install', f'python3-{package.split(">=")[0]}'],
            ]
            
            for cmd in install_methods:
                try:
                    self.logger.debug(f"Trying: {' '.join(cmd)}")
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        self.logger.success(f"Successfully installed {package} using {cmd[0]}")
                        return True
                    else:
                        self.logger.debug(f"Command failed with return code {result.returncode}")
                        if result.stderr:
                            self.logger.debug(f"Error output: {result.stderr.strip()}")
                        
                        # Check for specific error patterns
                        if "externally-managed-environment" in result.stderr:
                            self.logger.debug("Detected externally managed environment, trying alternative methods...")
                            continue
                        
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    self.logger.debug(f"Command not available or timed out: {' '.join(cmd)}")
                    continue
                except Exception as e:
                    self.logger.debug(f"Exception with command {' '.join(cmd)}: {e}")
                    continue
            
            self.logger.error(f"Failed to install {package} with all available methods")
            return False
            
        except Exception as e:
            self.logger.error(f"Exception during installation of {package}: {e}")
            return False
    
    def install_dependencies(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function install_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for install_dependencies operation
    3. Solution: Implement install_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test install_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Install all required dependencies"""
        self.logger.info("Checking and installing dependencies...")
        
        status = self.check_dependencies()
        missing = [pkg for pkg, available in status.items() if not available]
        
        if not missing:
            self.logger.success("All dependencies are already available!")
            return True
        
        self.logger.info(f"Missing dependencies: {', '.join(missing)}")
        
        # Install missing packages
        success_count = 0
        for package in self.required_packages:
            package_name = package.split('>=')[0].split('==')[0]
            if package_name in missing:
                if self.install_package(package):
                    success_count += 1
        
        # Verify installations
        final_status = self.check_dependencies()
        still_missing = [pkg for pkg, available in final_status.items() if not available]
        
        if still_missing:
            self.logger.warning(f"Still missing: {', '.join(still_missing)}")
            self.logger.warning("The installer will attempt to run with reduced functionality")
            return False
        else:
            self.logger.success("All dependencies installed successfully!")
            return True

class SystemChecker:
    """
    REASONING CHAIN:
    1. Problem: System component SystemChecker needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for SystemChecker functionality
    3. Solution: Implement SystemChecker with SOLID principles and enterprise patterns
    4. Validation: Test SystemChecker with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Check system compatibility and requirements"""
    
    def __init__(self, logger: BootstrapLogger):
    """
    Enhanced __init__ with AI-driven reasoning patterns
    
    REASONING CHAIN:
    1. Problem: Internal operation needs clear implementation boundary
    2. Analysis: Private method requires controlled access and defined behavior
    3. Solution: Implement __init__ with enterprise-grade patterns and error handling
    4. Validation: Test __init__ with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        self.logger = logger
    
    def check_python_version(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function check_python_version needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_python_version operation
    3. Solution: Implement check_python_version with enterprise-grade patterns and error handling
    4. Validation: Test check_python_version with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if Python version is compatible"""
        version = sys.version_info
        required = (3, 8)
        
        self.logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version >= required:
            self.logger.success(f"Python version {version.major}.{version.minor} is compatible")
            return True
        else:
            self.logger.error(f"Python {required[0]}.{required[1]}+ is required")
            return False
    
    def check_network_connectivity(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function check_network_connectivity needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_network_connectivity operation
    3. Solution: Implement check_network_connectivity with enterprise-grade patterns and error handling
    4. Validation: Test check_network_connectivity with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if we can reach the internet"""
        test_urls = [
            'https://pypi.org',
            'https://github.com',
            'https://google.com'
        ]
        
        for url in test_urls:
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    if response.getcode() == 200:
                        self.logger.success("Network connectivity confirmed")
                        return True
            except:
                continue
        
        self.logger.warning("Network connectivity check failed")
        self.logger.warning("Some features may not work without internet access")
        return False
    
    def check_permissions(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function check_permissions needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_permissions operation
    3. Solution: Implement check_permissions with enterprise-grade patterns and error handling
    4. Validation: Test check_permissions with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Check if we have necessary permissions"""
        test_dir = Path.cwd() / "noxsuite_permission_test"
        
        try:
            test_dir.mkdir(exist_ok=True)
            test_file = test_dir / "test.txt"
            test_file.write_text("test", encoding='utf-8')
            test_file.unlink()
            test_dir.rmdir()
            
            self.logger.success("File system permissions confirmed")
            return True
            
        except Exception as e:
            self.logger.error(f"Insufficient permissions: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_system_info with enterprise-grade patterns and error handling
    4. Validation: Test get_system_info with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Get system information"""
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'working_directory': str(Path.cwd()),
            'user': os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        }

class NoxSuiteBootstrap:
    """
    REASONING CHAIN:
    1. Problem: System component NoxSuiteBootstrap needs clear responsibility definition
    2. Analysis: Class requires specific implementation patterns for NoxSuiteBootstrap functionality
    3. Solution: Implement NoxSuiteBootstrap with SOLID principles and enterprise patterns
    4. Validation: Test NoxSuiteBootstrap with comprehensive unit and integration tests
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Main bootstrap class"""
    
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
        self.logger = BootstrapLogger()
        self.system_checker = SystemChecker(self.logger)
        self.dependency_installer = DependencyInstaller(self.logger)
    
    def show_banner(self):
    """
    REASONING CHAIN:
    1. Problem: Function show_banner needs clear operational definition
    2. Analysis: Implementation requires specific logic for show_banner operation
    3. Solution: Implement show_banner with enterprise-grade patterns and error handling
    4. Validation: Test show_banner with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Show welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════╗
║              🧠 NoxSuite Bootstrap Installer v1.0                ║
║              Self-Contained Dependency Manager                    ║
╚═══════════════════════════════════════════════════════════════════╝
        """
        logger.info(banner)
        self.logger.info("NoxSuite Bootstrap Installer started")
    
    def run_system_checks(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function run_system_checks needs clear operational definition
    2. Analysis: Implementation requires specific logic for run_system_checks operation
    3. Solution: Implement run_system_checks with enterprise-grade patterns and error handling
    4. Validation: Test run_system_checks with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Run all system compatibility checks"""
        self.logger.info("Running system compatibility checks...")
        
        checks = [
            ("Python Version", self.system_checker.check_python_version),
            ("File Permissions", self.system_checker.check_permissions),
            ("Network Connectivity", self.system_checker.check_network_connectivity)
        ]
        
        results = []
        for check_name, check_func in checks:
            self.logger.info(f"Checking {check_name}...")
            try:
                result = check_func()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error during {check_name} check: {e}")
                results.append(False)
        
        # Log system info
        system_info = self.system_checker.get_system_info()
        self.logger.debug(f"System info: {json.dumps(system_info, indent=2)}")
        
        critical_checks = results[:2]  # Python version and permissions are critical
        if not all(critical_checks):
            self.logger.error("Critical system checks failed")
            return False
        
        self.logger.success("System compatibility checks completed")
        return True
    
    def bootstrap_dependencies(self) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function bootstrap_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for bootstrap_dependencies operation
    3. Solution: Implement bootstrap_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test bootstrap_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Bootstrap all required dependencies"""
        self.logger.info("Bootstrapping dependencies...")
        return self.dependency_installer.install_dependencies()
    
    def launch_main_installer(self, args: List[str]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function launch_main_installer needs clear operational definition
    2. Analysis: Implementation requires specific logic for launch_main_installer operation
    3. Solution: Implement launch_main_installer with enterprise-grade patterns and error handling
    4. Validation: Test launch_main_installer with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Launch the main NoxSuite installer"""
        self.logger.info("Launching main installer...")
        
        try:
            # Check if main installer exists
            main_installer = Path("noxsuite_smart_installer_complete.py")
            if not main_installer.exists():
                self.logger.error("Main installer file not found: noxsuite_smart_installer_complete.py")
                return False
            
            # Import and run the main installer
            sys.path.insert(0, str(Path.cwd()))
            
            try:
                from install_noxsuite import main as launcher_main
                from noxsuite_smart_installer_complete import (
                    InstallMode,
                    SmartNoxSuiteInstaller,
                )

                # Pass control to the launcher with original arguments
                launcher_main()
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to launch main installer: {e}")
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during installer launch: {e}")
            return False
    
    def run(self, args: List[str]) -> bool:
    """
    REASONING CHAIN:
    1. Problem: Function run needs clear operational definition
    2. Analysis: Implementation requires specific logic for run operation
    3. Solution: Implement run with enterprise-grade patterns and error handling
    4. Validation: Test run with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
        """Main bootstrap process"""
        try:
            self.show_banner()
            
            # Skip bootstrap for certain commands
            if args and args[0] in ['--help', '-h', '--version']:
                return self.launch_main_installer(args)
            
            # Run system checks
            if not self.run_system_checks():
                self.logger.error("System checks failed. Cannot continue.")
                return False
            
            # Bootstrap dependencies
            deps_ok = self.bootstrap_dependencies()
            if not deps_ok:
                self.logger.warning("Some dependencies could not be installed")
                self.logger.warning("Attempting to continue with reduced functionality...")
            
            # Launch main installer
            return self.launch_main_installer(args)
            
        except KeyboardInterrupt:
            self.logger.warning("Bootstrap cancelled by user")
            return False
        except Exception as e:
            self.logger.error(f"Bootstrap failed: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False

def main():
    """
    REASONING CHAIN:
    1. Problem: Function main needs clear operational definition
    2. Analysis: Implementation requires specific logic for main operation
    3. Solution: Implement main with enterprise-grade patterns and error handling
    4. Validation: Test main with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Entry point"""
    bootstrap = NoxSuiteBootstrap()
    success = bootstrap.run(sys.argv[1:])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
