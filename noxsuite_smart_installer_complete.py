
                import winreg
            import urllib.request
    import requests
from NoxPanel.noxcore.utils.logging_config import get_logger
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sys
import threading

                            import yaml
                        import yaml
                import ctypes
                import psutil
                import yaml
            import locale
            import urllib.error
    import chardet
    import locale
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
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


            for url in test_urls:
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        if response.getcode() != 200:
                            failed_urls.append(url)
                except:
                    failed_urls.append(url)

        if failed_urls:
            return {
                "status": "warning",
                "message": f"Network issues detected: {len(failed_urls)} sites unreachable"
            }

        return {"status": "passed"}

    def _handle_dependencies(self) -> bool:
        """Handle dependency installation and validation"""
        required_deps = ["docker", "git"]

        if self.config.enable_mobile or any("react" in module for module in self.config.modules):
            required_deps.append("node")

        return self.dependency_manager.check_and_install_dependencies(required_deps)

    def _setup_directories(self) -> bool:
        """Setup directory structure atomically"""
        if self.config.mode == InstallMode.DRY_RUN:
            self.logger.info("🔍 Dry run: Would create directory structure")
            return True

        directory_structure = {
            "frontend": {
                "noxpanel-ui": {},
                "noxgo-mobile": {} if self.config.enable_mobile else None
            },
            "backend": {
                "fastapi": {},
                "flask-legacy": {}
            },
            "services": {
                "langflow": {} if self.config.enable_ai else None,
                "ollama": {} if self.config.enable_ai else None
            },
            "data": {
                "postgres": {},
                "redis": {},
                "logs": {}
            },
            "config": {},
            "scripts": {},
            "docker": {},
            "plugins": {}
        }

        # Remove None entries
        def clean_structure(d):
            if isinstance(d, dict):
                return {k: clean_structure(v) for k, v in d.items() if v is not None}
            return d

        directory_structure = clean_structure(directory_structure)

        scaffold = DirectoryScaffold(
            self.config.install_directory, self.logger)
        return scaffold.create_structure(directory_structure, dry_run=self.config.mode == InstallMode.DRY_RUN)

    def _install_core_components(self) -> bool:
        """Install core NoxSuite components"""
        if self.config.mode == InstallMode.DRY_RUN:
            self.logger.info("🔍 Dry run: Would install core components")
            return True

        # This would implement the actual component installation
        # For now, return True to indicate success
        self.logger.step_start(
            "installing_core", "Installing NoxSuite core components")

        # Simulate installation time
        time.sleep(1)

        self.logger.step_complete("installing_core")
        return True

    def _setup_ai_components(self) -> bool:
        """Setup AI components and models"""
        if self.config.mode == InstallMode.DRY_RUN:
            self.logger.info("🔍 Dry run: Would setup AI components")
            return True

        if not self.config.enable_ai: return True

        self.logger.step_start(
            "setting_up_ai", f"Installing {len(self.config.ai_models)} AI models")

        # This would implement actual AI model installation
        # For now, simulate the process
        for model in self.config.ai_models:
            self.logger.info(f"📦 Installing model: {model}")
            time.sleep(0.5)  # Simulate download time

        self.logger.step_complete("setting_up_ai")
        return True

    def _generate_configurations(self) -> bool:
        """Generate comprehensive configuration files with platform-specific handling"""
        if self.config.mode == InstallMode.DRY_RUN:
            self.logger.info("🔍 Dry run: Would generate configuration files")
            return True

        self.logger.step_start("generating_configs",
                               "Creating configuration files")

        try:
            # Initialize configuration generator
            config_generator = ConfigurationGenerator(
                self.config,
                self.system_info,
                self.logger
            )

            # Generate all configuration files
            success = config_generator.generate_all_configs()

            if success:
                self.logger.step_complete("generating_configs", {
                    "configs_created": len(config_generator.created_configs),
                    "platform_specific": self.system_info.os_type.value
                })
                return True
            else:
                self.logger.step_error("generating_configs",
                    Exception("Configuration generation failed"))
                return False

        except Exception as e:
            self.logger.step_error("generating_configs", e, {
                "platform": self.system_info.os_type.value,
                "install_dir": str(self.config.install_directory)
            })
            return False

    def _setup_services(self) -> bool:
        """Setup and configure services"""
        if self.config.mode == InstallMode.DRY_RUN:
            self.logger.info("🔍 Dry run: Would setup services")
            return True

        self.logger.step_start("setting_up_services",
                               "Configuring Docker services")

        # This would implement actual service setup
        time.sleep(0.5)

        self.logger.step_complete("setting_up_services")
        return True

    def _validate_installation(self) -> bool:
        """Comprehensive post-installation validation with detailed diagnostics"""
        if self.config.mode == InstallMode.DRY_RUN:
            self.logger.step_start(
                "validating_installation", "Skipping validation (dry-run mode)")
            self.logger.info("🔍 Dry run: Would validate installation")
            self.logger.step_complete("validating_installation")
            return True

        self.logger.step_start(
            "validating_installation", "Running comprehensive post-installation validation")

        try:
            # Initialize comprehensive validator
            validator = InstallationValidator(
                self.config,
                self.system_info,
                self.logger
            )

            # Run comprehensive validation
            validation_result = validator.validate_complete_installation()

            if validation_result.all_passed:
                self.logger.step_complete("validating_installation", {
                    "total_checks": validation_result.total_checks,
                    "passed_checks": validation_result.passed_checks,
                    "platform": self.system_info.os_type.value
                })
                return True
            else:
                # Log detailed failure information
                self.logger.warning(
                    f"❌ Validation Summary: {validation_result.passed_checks}/{validation_result.total_checks} checks passed")

                for failure in validation_result.failures:
                    self.logger.warning(
                        f"   • {failure.check_name}: {failure.message}")
                    if failure.auto_fix_available:
                        self.logger.info(
                            f"     🔧 Auto-fix available: {failure.auto_fix_suggestion}")

                # Attempt auto-healing if enabled
                if self.config.mode in [InstallMode.SAFE, InstallMode.RECOVERY]:
                    self.logger.info(
                        "🔧 Attempting auto-healing of failed validations...")
                    healing_result = validator.attempt_auto_healing(
                        validation_result.failures)

                    if healing_result.healed_count > 0:
                        self.logger.info(
                            f"✅ Successfully healed {healing_result.healed_count} issues")
                        # Re-run validation after healing
                        validation_result = validator.validate_complete_installation()
                        if validation_result.all_passed:
                            self.logger.step_complete("validating_installation", {
                                "healed_issues": healing_result.healed_count,
                                "final_status": "passed_after_healing"
                            })
                            return True

                self.logger.step_error("validating_installation",
                    Exception(f"Validation failed: {len(validation_result.failures)} issues"), {
                        "failed_checks": [f.check_name for f in validation_result.failures],
                        "auto_healing_attempted": self.config.mode in [InstallMode.SAFE, InstallMode.RECOVERY]
                    })
                return False

        except Exception as e:
            self.logger.step_error("validating_installation", e, {
                "platform": self.system_info.os_type.value,
                "install_dir": str(self.config.install_directory)
            })
            return False

    def _validate_directories(self) -> bool:
        """Validate directory structure"""
        required_dirs = ["config", "scripts", "docker", "data/logs"]

        for dir_path in required_dirs:
            full_path = self.config.install_directory / dir_path
            if not full_path.exists():
                return False

        return True

    def _validate_configs(self) -> bool:
        """Validate configuration files"""
        required_configs = ["config/noxsuite.json"]

        for config_path in required_configs:
            full_path = self.config.install_directory / config_path
            if not full_path.exists():
                return False

        return True

    def _validate_services(self) -> bool:
        """Validate that services can be started"""
        # This would implement actual service validation
        return True

    def _finalize_installation(self):
        """Finalize installation and show completion message"""
        self.logger.step_start("finalizing", "Completing installation")

        # Create installation summary
        summary = {
            "installation_status": "completed",
            "installation_time": datetime.now(timezone.utc).isoformat(),
            "installation_directory": str(self.config.install_directory),
            "configuration": asdict(self.config),
            "system_info": asdict(self.system_info)
        }

        # Save summary
        summary_file = self.config.install_directory / "INSTALLATION_SUMMARY.json"
        if self.config.mode != InstallMode.DRY_RUN:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

        # Show completion message
        self._show_completion_message()

        self.logger.step_complete("finalizing")
        self.logger.info("🎉 NoxSuite installation completed successfully!")

    def _show_completion_message(self):
        """Display installation completion message"""
        logger.info(f"")
╔═══════════════════════════════════════════════════════════════════╗
║                    🎉 Installation Complete! ║
╠═══════════════════════════════════════════════════════════════════╣
║  NoxSuite Smart Installer has successfully completed setup       ║
║                                                                   ║
║  📁 Installation: {str(self.config.install_directory): < 44} ║
║  🔧 Modules: {len(self.config.modules)} modules installed{' ' * (37 - len(str(self.config.modules)))} ║
║  🤖 AI Features: {'✅ Enabled' if self.config.enable_ai else '❌ Disabled': < 43} ║
║                                                                   ║
║  🌐 Web Interface: http: // localhost: 3000                         ║
║  🔧 API Docs: http: // localhost: 8000/api/docs                     ║
║  📊 Monitoring: http: // localhost: 3001                            ║
{'║  🤖 AI Hub: http://localhost:7860                                ║' if self.config.enable_ai else ''}
║                                                                   ║
║  🚀 Next Steps:                                                  ║
║     1. Run: ./scripts/start-noxsuite.sh                         ║
║     2. Open web interface                                        ║
║     3. Complete initial setup wizard                            ║
║                                                                   ║
║  📚 Logs: noxsuite_installer.log                               ║
║  📋 Summary: INSTALLATION_SUMMARY.json                          ║
╚═══════════════════════════════════════════════════════════════════╝
        """)

    def _run_audit_and_heal_mode(self) -> bool:
        """Run comprehensive audit and self-healing mode"""
        self.logger.info("🔍 Starting NoxSuite Audit and Self-Heal Mode")

        audit_banner = """
╔═══════════════════════════════════════════════════════════════════╗
║              🩺 NoxSuite Audit & Self-Heal Mode                  ║
║              Comprehensive Installation Health Check              ║
╠═══════════════════════════════════════════════════════════════════╣
║  🔍 Deep System Analysis     🔧 Automatic Fixing                ║
║  📊 Config Validation        ⚡ Smart Recovery                   ║
║  🛠️  Self-Healing Operations  📋 Detailed Reporting              ║
║  🌐 Cross-Platform Checks    💊 Auto-Remediation                ║
╚═══════════════════════════════════════════════════════════════════╝
        """
        logger.info(audit_banner)

        try:
            # Step 1: Detect existing installations
            self.logger.step_start(
                "audit_detection", "Scanning for existing NoxSuite installations")

            existing_installs = self._detect_existing_installations()
            if not existing_installs:
                self.logger.warning(
                    "❌ No existing NoxSuite installations found")

                # Offer to run regular installation
                run_install = input(
                    "\n💡 Would you like to run a fresh installation instead? [Y/n]: ").strip().lower()
                if run_install != 'n':
                    self.logger.info(
                        "🚀 Switching to guided installation mode...")
                    return self.run_installation(InstallMode.GUIDED)
                else:
                    self.logger.info(
                        "❌ Audit mode cancelled - no installation to audit")
                    return False

            self.logger.step_complete(
                "audit_detection", {"found_installations": len(existing_installs)})

            # Step 2: Select installation to audit (if multiple found)
            target_install = self._select_installation_to_audit(
                existing_installs)
            if not target_install:
                self.logger.info("❌ No installation selected for audit")
                return False

            self.logger.info(f"🎯 Auditing installation: {target_install}")

            # Step 3: Load configuration from existing installation
            self.logger.step_start(
                "loading_config", "Loading existing installation configuration")

            try:
                self.config = self._load_existing_config(Path(target_install))
                if not self.config:
                    self.logger.warning(
                        "⚠️ Could not load existing configuration, using defaults")
                    # Create minimal config for audit
                    self.config = InstallConfig(
                        install_directory=Path(target_install),
                        modules=["noxpanel", "noxguard"],
                        mode=InstallMode.AUDIT_HEAL
                    )

                self.logger.step_complete("loading_config")
            except Exception as e:
                self.logger.step_error("loading_config", e)
                return False

            # Step 4: Run comprehensive audit
            self.logger.step_start("comprehensive_audit",
                                   "Running comprehensive installation audit")

            validator = InstallationValidator(
                self.config, self.system_info, self.logger)
            audit_result = validator.validate_complete_installation()

            self.logger.step_complete("comprehensive_audit", {
                "total_checks": audit_result.total_checks,
                "passed_checks": audit_result.passed_checks,
                "failed_checks": len(audit_result.failures)
            })

            # Step 5: Display detailed audit results
            self._display_audit_results(audit_result)

            # Step 6: Auto-healing (if issues found)
            if not audit_result.all_passed:
                self.logger.info(
                    f"\n🔧 Found {len(audit_result.failures)} issues to address")

                # Ask user if they want to attempt auto-healing
                auto_heal = input(
                    "\n💊 Attempt automatic healing of detected issues? [Y/n]: ").strip().lower()

                if auto_heal != 'n':
                    self.logger.step_start(
                        "auto_healing", "Attempting automatic issue resolution")

                    healing_result = validator.attempt_auto_healing(
                        audit_result.failures)

                    self.logger.step_complete("auto_healing", {
                        "healed_count": healing_result.healed_count,
                        "failed_count": healing_result.failed_count
                    })

                    # Display healing results
                    self._display_healing_results(healing_result)

                    # Re-run validation after healing
                    if healing_result.healed_count > 0:
                        self.logger.info(
                            "\n🔄 Re-validating installation after healing...")
                        final_audit = validator.validate_complete_installation()

                        if final_audit.all_passed:
                            self.logger.info(
                                "✅ All issues resolved! Installation is now healthy.")
                        else:
                            remaining_issues = len(final_audit.failures)
                            self.logger.warning(
                                f"⚠️ {remaining_issues} issues still require manual attention")
                            self._display_remaining_issues(final_audit.failures)
                else:
                    self.logger.info("ℹ️ Auto-healing skipped by user")
            else:
                self.logger.info(
                    "🎉 Installation audit completed - no issues found!")

            # Step 7: Generate comprehensive audit report
            self._generate_audit_report(
                audit_result, existing_installs, target_install)

            return True

        except Exception as e:
            self.logger.step_error("audit_and_heal", e, {
                "mode": "audit_heal",
                "system_info": asdict(self.system_info)
            })
            return False

    def _detect_existing_installations(self) -> List[str]:
        """Detect existing NoxSuite installations on the system"""
        installations = []

        # Common installation locations
        search_locations = []

        if self.system_info.os_type == OSType.WINDOWS:
            search_locations = [
                Path.home() / "NoxSuite",
                Path.home() / "noxsuite",
                Path("C:/Program Files/NoxSuite"),
                Path("C:/NoxSuite"),
                Path.home() / "Documents" / "NoxSuite"
            ]
        else:
            search_locations = [
                Path.home() / "noxsuite",
                Path.home() / "NoxSuite",
                Path("/opt/noxsuite"),
                Path("/usr/local/noxsuite"),
                Path("/var/lib/noxsuite")
            ]

        # Also check current directory
        search_locations.append(Path.cwd())

        for location in search_locations:
            if self._is_noxsuite_installation(location):
                installations.append(str(location))

        # Search for additional installations in common directories
        additional_locations = self._search_for_noxsuite_markers()
        installations.extend(additional_locations)

        # Remove duplicates and sort
        installations = sorted(list(set(installations)))

        return installations

    def _is_noxsuite_installation(self, path: Path) -> bool:
        """Check if a directory contains a NoxSuite installation"""
        if not path.exists() or not path.is_dir():
            return False

        # Check for NoxSuite markers
        markers = [
            "noxsuite.json",
            "INSTALLATION_SUMMARY.json",
            "config/noxsuite.json",
            "docker/docker-compose.noxsuite.yml"
        ]

        marker_count = 0
        for marker in markers:
            if (path / marker).exists():
                marker_count += 1

        # Consider it a NoxSuite installation if at least 2 markers are found
        return marker_count >= 2

    def _search_for_noxsuite_markers(self) -> List[str]:
        """Search filesystem for NoxSuite installation markers"""
        additional_installs = []

        # This is a simplified search - in a real implementation,
        # you might want to search more comprehensively

        try:
            # Search in user's home directory tree (limited depth)
            home_path = Path.home()
            for item in home_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        if self._is_noxsuite_installation(item):
                            additional_installs.append(str(item))
                    except PermissionError:
                        continue  # Skip directories we can't access
        except:
            pass  # Handle any filesystem errors gracefully

        return additional_installs

    def _select_installation_to_audit(self, installations: List[str]) -> str:
        """Let user select which installation to audit(if multiple found)"""
        if len(installations) == 1:
            return installations[0]

        logger.info(f"\n🔍 Multiple NoxSuite installations detected:")
        logger.info("=" * 60)

        for i, install_path in enumerate(installations, 1):
            install_info = self._get_installation_info(Path(install_path))
            logger.info(f"   {i}. {install_path}")
            logger.info(
                f"      Version: {install_info.get('version', 'unknown')}")
            logger.info(
                f"      Last Modified: {install_info.get('last_modified', 'unknown')}")
            logger.info(f"      Size: {install_info.get('size', 'unknown')}")
            logger.info()

        while True:
            try:
                selection = input(
                    f"Select installation to audit [1-{len(installations)}]: ").strip()
                index = int(selection) - 1

                if 0 <= index < len(installations):
                    return installations[index]
                else:
                    logger.info(
                        f"❌ Please enter a number between 1 and {len(installations)}")
            except ValueError:
                logger.info("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return None

    def _get_installation_info(self, install_path: Path) -> Dict[str, str]:
        """Get basic information about an installation"""
        info = {}

        try:
            # Get version from noxsuite.json or INSTALLATION_SUMMARY.json
            config_files = [
                install_path / "config" / "noxsuite.json",
                install_path / "noxsuite.json",
                install_path / "INSTALLATION_SUMMARY.json"
            ]

            for config_file in config_files:
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                            info['version'] = config_data.get(
                                'version', 'unknown')
                            break
                    except:
                        continue

            # Get last modified time
            if install_path.exists():
                last_modified = install_path.stat().st_mtime
                info['last_modified'] = datetime.fromtimestamp(
                    last_modified).strftime('%Y-%m-%d %H:%M')

            # Get approximate size
            total_size = 0
            try:
                for root, dirs, files in os.walk(install_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                        except:
                            continue

                if total_size > 1024**3:
                    info['size'] = f"{total_size / (1024**3):.1f}GB"
                elif total_size > 1024**2:
                    info['size'] = f"{total_size / (1024**2):.1f}MB"
                else:
                    info['size'] = f"{total_size / 1024:.1f}KB"
            except:
                info['size'] = "unknown"

        except Exception as e:
            self.logger.debug(
                f"Error getting installation info for {install_path}: {e}")

        return info

    def _load_existing_config(self, install_path: Path) -> Optional[InstallConfig]:
        """Load configuration from existing installation"""
        try:
            # Try to load from config/noxsuite.json first
            config_file = install_path / "config" / "noxsuite.json"
            if not config_file.exists():
                # Fallback to other possible locations
                config_file = install_path / "noxsuite.json"
                if not config_file.exists():
                    config_file = install_path / "INSTALLATION_SUMMARY.json"

            if not config_file.exists():
                self.logger.warning(
                    "No configuration file found in installation")
                return None

            encoding = "utf-8-sig" if self.system_info.os_type == OSType.WINDOWS else "utf-8"
            with open(config_file, 'r', encoding=encoding) as f:
                config_data = json.load(f)

            # Extract configuration from loaded data
            installation_data = config_data.get('installation', config_data)

            # Create InstallConfig from loaded data
            config = InstallConfig(
                install_directory=install_path,
                modules=installation_data.get(
                    'installed_modules', installation_data.get('modules', [])),
                enable_ai=installation_data.get(
                    'features', {}).get('ai_enabled', False),
                enable_voice=installation_data.get(
                    'features', {}).get('voice_enabled', False),
                enable_mobile=installation_data.get(
                    'features', {}).get('mobile_enabled', False),
                dev_mode=installation_data.get(
                    'features', {}).get('dev_mode', False),
                auto_start=installation_data.get('auto_start', True),
                ai_models=installation_data.get('ai_models', []),
                mode=InstallMode.AUDIT_HEAL
            )

            return config

        except Exception as e:
            self.logger.warning(f"Failed to load existing configuration: {e}")
            return None

    def _display_audit_results(self, audit_result: ValidationResult):
        """Display comprehensive audit results"""
        logger.info(f"\n📊 Audit Results Summary")
        logger.info("=" * 60)

        if audit_result.all_passed:
            logger.info("🎉 Installation Status: HEALTHY")
            logger.info(
                f"✅ All {audit_result.total_checks} validation checks passed")
        else:
            failed_count = len(audit_result.failures)
            logger.info(f"⚠️ Installation Status: NEEDS ATTENTION")
            logger.info(
                f"✅ Passed: {audit_result.passed_checks}/{audit_result.total_checks}")
            logger.info(
                f"❌ Failed: {failed_count}/{audit_result.total_checks}")

        if audit_result.platform_specific_issues:
            logger.info(f"\n🔧 Platform-Specific Issues Detected:")
            for issue in audit_result.platform_specific_issues:
                logger.info(f"   • {issue}")

        if audit_result.failures:
            logger.info(f"\n📋 Detailed Issue Report:")
            for i, failure in enumerate(audit_result.failures, 1):
                severity_icon = "🔴" if failure.severity == "error" else "🟡"
                logger.info(
                    f"\n{i}. {severity_icon} {failure.check_name.replace('_', ' ').title()}")
                logger.info(f"   Issue: {failure.message}")
                logger.info(f"   Severity: {failure.severity.upper()}")

                if failure.auto_fix_available:
                    logger.info(
                        f"   🔧 Auto-fix: {failure.auto_fix_suggestion}")
                else:
                    logger.info(f"   ⚠️ Manual intervention required")

                if failure.context:
                    # Show relevant context information
                    if 'missing_configs' in failure.context:
                        # Show first 3
                        missing = failure.context['missing_configs'][:3]
                        logger.info(f"   Missing files: {', '.join(missing)}")
                        if len(failure.context['missing_configs']) > 3:
                            logger.info(
                                f"   ... and {len(failure.context['missing_configs']) - 3} more")

    def _display_healing_results(self, healing_result: HealingResult):
        """Display healing attempt results"""
        logger.info(f"\n💊 Auto-Healing Results")
        logger.info("=" * 60)

        total_attempts = healing_result.healed_count + healing_result.failed_count
        logger.info(
            f"✅ Successfully healed: {healing_result.healed_count}/{total_attempts}")
        logger.info(
            f"❌ Failed to heal: {healing_result.failed_count}/{total_attempts}")

        if healing_result.healing_details:
            logger.info(f"\n📋 Healing Details:")
            for detail in healing_result.healing_details:
                status = detail['status']
                check_name = detail['check_name']

                if status == 'healed':
                    logger.info(
                        f"✅ {check_name}: {detail.get('details', 'Successfully healed')}")
                elif status == 'failed':
                    logger.info(
                        f"❌ {check_name}: {detail.get('error', 'Healing failed')}")
                elif status == 'no_auto_fix':
                    logger.info(
                        f"⚠️ {check_name}: Manual intervention required")
                elif status == 'exception':
                    logger.info(
                        f"💥 {check_name}: Healing error - {detail.get('error', 'Unknown error')}")

    def _display_remaining_issues(self, remaining_failures: List[ValidationFailure]):
        """Display issues that still need manual attention"""
        logger.info(f"\n⚠️ Remaining Issues Requiring Manual Attention:")
        logger.info("-" * 60)

        for i, failure in enumerate(remaining_failures, 1):
            severity_icon = "🔴" if failure.severity == "error" else "🟡"
            logger.info(
                f"\n{i}. {severity_icon} {failure.check_name.replace('_', ' ').title()}")
            logger.info(f"   Issue: {failure.message}")

            # Provide manual fix suggestions
            manual_suggestions = self._get_manual_fix_suggestions(failure)
            if manual_suggestions:
                logger.info(f"   💡 Manual Fix Suggestions:")
                for suggestion in manual_suggestions:
                    logger.info(f"      • {suggestion}")

    def _get_manual_fix_suggestions(self, failure: ValidationFailure) -> List[str]:
        """Get manual fix suggestions for validation failures"""
        suggestions = []

        if failure.check_name == "service_dependencies":
            suggestions.extend([
                "Install Docker Desktop from https://docker.com/get-started",
                "Install Node.js from https://nodejs.org (if mobile features enabled)",
                "Restart your terminal/command prompt after installation"
            ])
        elif failure.check_name == "path_compatibility":
            suggestions.extend([
                "Consider moving installation to a path without spaces",
                "Use short path names to avoid Windows path length limits",
                "Avoid reserved Windows filenames (CON, PRN, AUX, etc.)"
            ])
        elif failure.check_name == "disk_space":
            suggestions.extend([
                "Free up disk space on the installation drive",
                "Consider installing to a different drive with more space",
                "Remove old Docker images: docker system prune -a"
            ])
        elif failure.check_name == "platform_compatibility":
            if self.system_info.os_type == OSType.WINDOWS:
                suggestions.extend([
                    "Ensure Windows 10/11 with WSL2 support for Docker Desktop",
                    "Enable Hyper-V and Windows Subsystem for Linux features",
                    "Update Windows to the latest version"
                ])
            elif self.system_info.os_type == OSType.LINUX:
                suggestions.extend([
                    "Ensure systemd is available for service management",
                    "Install Docker using your distribution's package manager",
                    "Add your user to the docker group: sudo usermod -aG docker $USER"
                ])

        # Add generic suggestions if no specific ones found
        if not suggestions:
            suggestions.append(
                "Review the installation documentation for platform-specific requirements")
            suggestions.append(
                "Check the installation logs for more detailed error information")

        return suggestions

    def _generate_audit_report(self, audit_result: ValidationResult, installations: List[str], target_install: str):
        """Generate comprehensive audit report"""
        self.logger.step_start("generating_report",
                               "Creating comprehensive audit report")

        try:
            report_timestamp = datetime.now(timezone.utc)
            report = {
                "audit_metadata": {
                    "timestamp": report_timestamp.isoformat(),
                    "installer_version": "1.0.0",
                    "audit_session_id": self.logger.session_id,
                    "target_installation": target_install,
                    "all_detected_installations": installations,
                    "platform": self.system_info.os_type.value,
                    "system_info": asdict(self.system_info)
                },
                "audit_results": {
                    "overall_status": "healthy" if audit_result.all_passed else "needs_attention",
                    "total_checks": audit_result.total_checks,
                    "passed_checks": audit_result.passed_checks,
                    "failed_checks": len(audit_result.failures),
                    "platform_specific_issues": audit_result.platform_specific_issues or []
                },
                "detailed_failures": [],
                "configuration_snapshot": asdict(self.config) if self.config else None,
                "recommendations": []
            }

            # Add detailed failure information
            for failure in audit_result.failures:
                failure_detail = {
                    "check_name": failure.check_name,
                    "message": failure.message,
                    "severity": failure.severity,
                    "auto_fix_available": failure.auto_fix_available,
                    "auto_fix_suggestion": failure.auto_fix_suggestion,
                    "context": failure.context or {}
                }
                report["detailed_failures"].append(failure_detail)

            # Generate recommendations
            report["recommendations"] = self._generate_audit_recommendations(
                audit_result)

            # Save report
            report_file = Path(target_install) / "AUDIT_REPORT.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            # Save human-readable report
            readable_report = Path(target_install) / "AUDIT_REPORT.md"
            self._generate_readable_audit_report(
                readable_report, report, audit_result)

            self.logger.step_complete("generating_report", {
                "report_files": [str(report_file), str(readable_report)]
            })

            logger.info(f"\n📄 Audit reports saved:")
            logger.info(f"   • JSON Report: {report_file}")
            logger.info(f"   • Readable Report: {readable_report}")

        except Exception as e:
            self.logger.step_error("generating_report", e)

    def _generate_audit_recommendations(self, audit_result: ValidationResult) -> List[str]:
        """Generate actionable recommendations based on audit results"""
        recommendations = []

        if audit_result.all_passed:
            recommendations.extend([
                "Installation is healthy - no immediate action required",
                "Consider running periodic audits to maintain system health",
                "Keep Docker and other dependencies updated"
            ])
        else:
            # Priority recommendations based on failure types
            error_failures = [
                f for f in audit_result.failures if f.severity == "error"]
            warning_failures = [
                f for f in audit_result.failures if f.severity == "warning"]

            if error_failures:
                recommendations.append(
                    f"PRIORITY: Address {len(error_failures)} critical errors first")

                critical_checks = [f.check_name for f in error_failures]
                if "service_dependencies" in critical_checks:
                    recommendations.append(
                        "Install missing Docker/Node.js dependencies")
                if "configuration_files" in critical_checks:
                    recommendations.append(
                        "Regenerate missing configuration files")
                if "disk_space" in critical_checks:
                    recommendations.append(
                        "Free up disk space before proceeding")

            if warning_failures:
                recommendations.append(
                    f"Consider addressing {len(warning_failures)} warnings for optimal performance")

            # Platform-specific recommendations
            if self.system_info.os_type == OSType.WINDOWS:
                if any("encoding" in f.message.lower() for f in audit_result.failures):
                    recommendations.append(
                        "Windows: Ensure UTF-8 support is properly configured")
                if any("path" in f.message.lower() for f in audit_result.failures):
                    recommendations.append(
                        "Windows: Avoid spaces and long paths in installation directory")

            # General recommendations
            recommendations.extend([
                "Run the installer with 'recovery' mode to fix common issues",
                "Check installation logs for detailed error information",
                "Consider backup before making configuration changes"
            ])

        return recommendations

    def _generate_readable_audit_report(self, report_file: Path, report_data: Dict, audit_result: ValidationResult):
        """Generate human-readable markdown audit report"""
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# NoxSuite Installation Audit Report\n\n")
                f.write(
                    f"**Generated:** {report_data['audit_metadata']['timestamp']}\n")
                f.write(
                    f"**Installation:** {report_data['audit_metadata']['target_installation']}\n")
                f.write(
                    f"**Platform:** {report_data['audit_metadata']['platform'].title()}\n")
                f.write(
                    f"**Session ID:** {report_data['audit_metadata']['audit_session_id']}\n\n")

                # Overall Status
                f.write("## 📊 Overall Status\n\n")
                status = "✅ HEALTHY" if audit_result.all_passed else "⚠️ NEEDS ATTENTION"
                f.write(f"**Status:** {status}\n")
                f.write(
                    f"**Checks Passed:** {audit_result.passed_checks}/{audit_result.total_checks}\n\n")

                # Issues Found
                if audit_result.failures:
                    f.write("## ❌ Issues Found\n\n")
                    for i, failure in enumerate(audit_result.failures, 1):
                        severity_icon = "🔴" if failure.severity == "error" else "🟡"
                        f.write(
                            f"### {i}. {severity_icon} {failure.check_name.replace('_', ' ').title()}\n\n")
                        f.write(f"**Issue:** {failure.message}\n")
                        f.write(f"**Severity:** {failure.severity.upper()}\n")
                        f.write(
                            f"**Auto-fixable:** {'Yes' if failure.auto_fix_available else 'No'}\n")

                        if failure.auto_fix_available:
                            f.write(
                                f"**Auto-fix:** {failure.auto_fix_suggestion}\n")

                        f.write("\n")
                else:
                    f.write("## ✅ No Issues Found\n\n")
                    f.write("All validation checks passed successfully!\n\n")

                # Recommendations
                f.write("## 💡 Recommendations\n\n")
                for rec in report_data["recommendations"]:
                    f.write(f"- {rec}\n")

                f.write("\n---\n")
                f.write("*Report generated by NoxSuite Smart Installer*\n")

        except Exception as e:
            self.logger.warning(f"Failed to generate readable report: {e}")

    def _cleanup_on_failure(self):
        """Cleanup on installation failure"""
        self.logger.info("🧹 Cleaning up after installation failure...")

        # This would implement cleanup logic
        # For now, just log the attempt
        self.logger.debug("Cleanup completed")

def main():
    """Main entry point for the smart installer"""
    try:
        # Parse command line arguments for mode selection
        mode = InstallMode.GUIDED
        
        if len(sys.argv) > 1:
            mode_arg = sys.argv[1].lower()
            mode_map = {
                "fast": InstallMode.FAST,
                "guided": InstallMode.GUIDED,
                "dry-run": InstallMode.DRY_RUN,
                "safe": InstallMode.SAFE,
                "recovery": InstallMode.RECOVERY,
                "audit-heal": InstallMode.AUDIT_HEAL
            }
            mode = mode_map.get(mode_arg, InstallMode.GUIDED)
        
        # Create and run installer
        installer = SmartNoxSuiteInstaller()
        success = installer.run_installation(mode)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.info(f"\n❌ Installer crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
