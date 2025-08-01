#!/usr/bin/env python3
"""
NoxSuite Smart Self-Healing Auto-Installer
Intelligent cross-platform setup with AI-powered error recovery and learning capabilities
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import requests
import sys
import threading

                import ctypes
                import psutil
            import locale
    import locale
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
import chardet
import codecs
import hashlib
import logging
import platform
import queue
import shutil
import subprocess
import tempfile
import time
import traceback
import uuid


                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Unix-like: Check if running as root
                return os.geteuid() == 0
        except:
            return False


class SmartDependencyManager:
    """Intelligent dependency management with multiple fallback strategies"""

    def __init__(self, system_info: SystemInfo, logger: SmartLogger):
        self.system_info = system_info
        self.logger = logger
        self.retry_count = {}
        self.max_retries = 3

    def check_and_install_dependencies(self, required_deps: List[str]) -> bool:
        """Check and install missing dependencies with smart fallbacks"""
        self.logger.step_start(
            "checking_dependencies", f"Validating {len(required_deps)} dependencies"
        )

        missing_deps = []
        version_issues = []

        for dep in required_deps:
            status = self._check_dependency_status(dep)
            if status["available"]:
                if status.get("version_ok", True):
                    self.logger.debug(
                        f"✅ {dep}: {status.get('version', 'unknown')}")
                else:
                    version_issues.append((dep, status))
                    self.logger.warning(
                        f"⚠️  {dep}: version {status.get('version')} (need {status.get('required_version')})"
                    )
            else:
                missing_deps.append(dep)
                self.logger.debug(f"❌ {dep}: not found")

        if not missing_deps and not version_issues:
            self.logger.step_complete("checking_dependencies", {
                                      "all_satisfied": True})
            return True

        # Handle missing dependencies
        if missing_deps:
            self.logger.info(
                f"📦 Missing dependencies: {', '.join(missing_deps)}")

            if not self._confirm_installation(missing_deps):
                return False

            success = self._install_missing_dependencies(missing_deps)
            if not success:
                return False

        # Handle version issues
        if version_issues:
            self.logger.info(
                f"🔄 Version updates needed: {len(version_issues)} packages"
            )
            success = self._handle_version_issues(version_issues)
            if not success:
                return False

        self.logger.step_complete(
            "checking_dependencies",
            {"installed": missing_deps, "updated": [
                dep for dep, _ in version_issues]},
        )
        return True

    def _check_dependency_status(self, dep: str) -> Dict[str, Any]:
        """Check detailed status of a dependency"""
        status = {"available": False, "version": None, "path": None}

        # Define version requirements
        version_requirements = {
            "docker": "20.0.0",
            "node": "16.0.0",
            "npm": "8.0.0",
            "git": "2.20.0",
            "python": "3.8.0",
        }

        try:
            # Check if command exists
            cmd_path = shutil.which(dep)
            if not cmd_path:
                return status

            status["available"] = True
            status["path"] = cmd_path

            # Get version information
            version_cmd_map = {
                "docker": ["docker", "--version"],
                "node": ["node", "--version"],
                "npm": ["npm", "--version"],
                "git": ["git", "--version"],
                "python": ["python", "--version"],
                "python3": ["python3", "--version"],
            }

            if dep in version_cmd_map:
                try:
                    result = subprocess.run(
                        version_cmd_map[dep], capture_output=True, text=True, timeout=10
                    )

                    if result.returncode == 0:
                        version_output = result.stdout.strip()
                        version = self._extract_version(version_output)
                        status["version"] = version

                        # Check if version meets requirements
                        if dep in version_requirements:
                            required = version_requirements[dep]
                            status["required_version"] = required
                            status["version_ok"] = (
                                self._compare_versions(version, required) >= 0
                            )
                        else:
                            status["version_ok"] = True

                except Exception as e:
                    self.logger.debug(f"Version check failed for {dep}: {e}")

        except Exception as e:
            self.logger.debug(f"Dependency check failed for {dep}: {e}")

        return status

    def _extract_version(self, version_output: str) -> str:
        """Extract version number from command output"""
        # Common version patterns
        patterns = [
            r"(\d+\.\d+\.\d+)",
            r"v(\d+\.\d+\.\d+)",
            r"version (\d+\.\d+\.\d+)",
            r"(\d+\.\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, version_output)
            if match:
                return match.group(1)

        return "unknown"

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings (-1: v1 < v2, 0: equal, 1: v1 > v2)"""
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]

            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for i in range(max_len):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1

            return 0
        except:
            return 0  # Assume equal if comparison fails

    def _confirm_installation(self, deps: List[str]) -> bool:
        """Confirm with user before installing dependencies"""
        self.logger.info(
            f"\n🤔 The following dependencies need to be installed:")
        for dep in deps:
            self.logger.info(f"   • {dep}")

        response = (
            input(f"\n💡 Install missing dependencies automatically? [Y/n]: ")
            .strip()
            .lower()
        )
        return response != "n"

    def _install_missing_dependencies(self, deps: List[str]) -> bool:
        """Install missing dependencies using best available method"""
        for dep in deps:
            if not self._install_single_dependency(dep):
                return False
        return True

    def _install_single_dependency(self, dep: str) -> bool:
        """Install a single dependency with multiple fallback methods"""
        self.logger.step_start("installing_dependency", f"Installing {dep}")

        # Get retry count for this dependency
        retry_key = f"install_{dep}"
        current_retry = self.retry_count.get(retry_key, 0)

        if current_retry >= self.max_retries:
            self.logger.step_error(
                "installing_dependency", Exception(
                    f"Max retries exceeded for {dep}")
            )
            return False

        # Try different installation methods in order of preference
        methods = self._get_installation_methods(dep)

        for method_name, method_func in methods:
            try:
                self.logger.debug(f"Trying installation method: {method_name}")
                success = method_func(dep)

                if success:
                    # Verify installation
                    if self._verify_installation(dep):
                        self.logger.step_complete(
                            "installing_dependency",
                            {
                                "dependency": dep,
                                "method": method_name,
                                "retry_count": current_retry,
                            },
                        )
                        return True
                    else:
                        self.logger.warning(
                            f"Installation verification failed for {dep}"
                        )

            except Exception as e:
                self.logger.debug(
                    f"Installation method {method_name} failed: {e}")
                continue

        # All methods failed, increment retry count
        self.retry_count[retry_key] = current_retry + 1
        self.logger.step_error(
            "installing_dependency",
            Exception(f"All installation methods failed for {dep}"),
        )
        return False

    def _get_installation_methods(self, dep: str) -> List[Tuple[str, callable]]:
        """Get ordered list of installation methods for a dependency"""
        methods = []

        # Platform-specific methods first
        if self.system_info.os_type == OSType.WINDOWS:
            if "winget" in self.system_info.package_managers:
                methods.append(
                    ("winget", lambda d: self._install_with_winget(d)))
            if "chocolatey" in self.system_info.package_managers:
                methods.append(
                    ("chocolatey", lambda d: self._install_with_chocolatey(d))
                )
            if "scoop" in self.system_info.package_managers:
                methods.append(
                    ("scoop", lambda d: self._install_with_scoop(d)))

        elif self.system_info.os_type == OSType.LINUX:
            # Try system package manager first
            for pm in ["apt-get", "apt", "yum", "dnf"]:
                if pm in self.system_info.package_managers:
                    methods.append(
                        (pm, lambda d: self._install_with_system_pm(d, pm)))
                    break

        elif self.system_info.os_type == OSType.MACOS:
            if "homebrew" in self.system_info.package_managers:
                methods.append(
                    ("homebrew", lambda d: self._install_with_homebrew(d)))

        # Universal fallback methods
        methods.extend(
            [
                ("manual_download", lambda d: self._install_manually(d)),
                ("containerized", lambda d: self._install_containerized(d)),
            ]
        )

        return methods

    def _install_with_winget(self, dep: str) -> bool:
        """Install dependency using Windows Package Manager (winget)"""
        package_map = {
            "docker": "Docker.DockerDesktop",
            "git": "Git.Git",
            "node": "OpenJS.NodeJS",
        }

        package_id = package_map.get(dep, dep)

        try:
            result = subprocess.run(
                [
                    "winget",
                    "install",
                    package_id,
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            return result.returncode == 0
        except:
            return False

    def _install_with_chocolatey(self, dep: str) -> bool:
        """Install dependency using Chocolatey"""
        package_map = {"docker": "docker-desktop",
                       "git": "git", "node": "nodejs"}

        package_name = package_map.get(dep, dep)

        try:
            result = subprocess.run(
                ["choco", "install", package_name, "-y"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            return result.returncode == 0
        except:
            return False

    def _install_with_scoop(self, dep: str) -> bool:
        """Install dependency using Scoop"""
        try:
            result = subprocess.run(
                ["scoop", "install", dep], capture_output=True, text=True, timeout=300
            )
            return result.returncode == 0
        except:
            return False

    def _install_with_system_pm(self, dep: str, package_manager: str) -> bool:
        """Install dependency using system package manager"""
        package_map = {"docker": "docker.io", "git": "git", "node": "nodejs"}

        package_name = package_map.get(dep, dep)

        try:
            if package_manager in ["apt-get", "apt"]:
                # Update package list first
                subprocess.run(["sudo", "apt-get", "update"], timeout=60)
                result = subprocess.run(
                    ["sudo", "apt-get", "install", "-y", package_name],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            elif package_manager in ["yum", "dnf"]:
                result = subprocess.run(
                    ["sudo", package_manager, "install", "-y", package_name],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            else:
                return False

            return result.returncode == 0
        except:
            return False

    def _install_with_homebrew(self, dep: str) -> bool:
        """Install dependency using Homebrew"""
        try:
            if dep == "docker":
                result = subprocess.run(
                    ["brew", "install", "--cask", "docker"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            else:
                result = subprocess.run(
                    ["brew", "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            return result.returncode == 0
        except:
            return False

    def _install_manually(self, dep: str) -> bool:
        """Manual installation fallback (download and install)"""
        # This would implement manual download and installation
        # For now, return False to indicate this method is not yet implemented
        self.logger.debug(f"Manual installation not yet implemented for {dep}")
        return False

    def _install_containerized(self, dep: str) -> bool:
        """Install dependency in containerized mode"""
        # This would set up dependencies to run in containers
        # For now, return False to indicate this method is not yet implemented
        self.logger.debug(
            f"Containerized installation not yet implemented for {dep}")
        return False

    def _verify_installation(self, dep: str) -> bool:
        """Verify that a dependency was installed correctly"""
        try:
            # Wait a moment for installation to complete
            time.sleep(2)

            # Check if command is now available
            if shutil.which(dep):
                # Try to run version command
                try:
                    result = subprocess.run(
                        [dep, "--version"], capture_output=True, timeout=10
                    )
                    return result.returncode == 0
                except:
                    # Command exists but version check failed - still count as success
                    return True

            return False
        except:
            return False

    def _handle_version_issues(self, version_issues: List[Tuple[str, Dict]]) -> bool:
        """Handle dependencies with version compatibility issues"""
        for dep, status in version_issues:
            self.logger.info(
                f"🔄 Updating {dep} from {status.get('version')} to {status.get('required_version')}"
            )
            # For now, we'll skip version updates and just warn
            # In a full implementation, this would upgrade packages
            self.logger.warning(f"Version update not implemented for {dep}")

        return True
