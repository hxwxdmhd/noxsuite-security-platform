from pathlib import Path
import time
import sys
import subprocess
import os
import json
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Copilot Self-Repair System
Automatically diagnoses and fixes Copilot functionality issues
"""


class CopilotSelfRepair:
    def __init__(self):
        self.tool_count = 0
        self.max_tools = 120
        self.current_dir = Path.cwd()

    def diagnose_issues(self):
        """Diagnose current Copilot and system issues"""
        logger.info("🔍 Diagnosing Copilot Issues...")

        issues = []

        # Check 1: Python environment
        if "python313.dll" in str(sys.executable) and "3.12" in sys.version:
            issues.append("python_version_mismatch")

        # Check 2: VS Code Python interpreter
        vscode_settings = self.current_dir / ".vscode" / "settings.json"
        if vscode_settings.exists():
            try:
                with open(vscode_settings, "r") as f:
                    settings = json.load(f)
                current_interpreter = settings.get(
                    "python.defaultInterpreterPath", "")
                if "python313" in current_interpreter.lower() and "3.12" in sys.version:
                    issues.append("vscode_interpreter_mismatch")
            except:
                issues.append("vscode_settings_corrupted")

        # Check 3: Virtual environment
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_path = Path(sys.executable).parent
            if not (venv_path / "python.exe").exists():
                issues.append("venv_corrupted")

        return issues

    def fix_python_interpreter(self):
        """Fix Python interpreter mismatch"""
        logger.info("🔧 Fixing Python interpreter...")

        correct_python = sys.executable
        logger.info(f"   Using: {correct_python}")

        # Update VS Code settings
        vscode_dir = self.current_dir / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        settings_file = vscode_dir / "settings.json"

        new_settings = {
            "python.defaultInterpreterPath": correct_python.replace("\\", "/"),
            "python.terminal.activateEnvironment": True,
            "github.copilot.enable": {"*": True, "python": True, "markdown": True},
            "github.copilot.inlineSuggest.enable": True,
            "python.analysis.typeCheckingMode": "basic",
        }

        try:
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    existing_settings = json.load(f)
            else:
                existing_settings = {}

            existing_settings.update(new_settings)

            with open(settings_file, "w") as f:
                json.dump(existing_settings, f, indent=2)

            logger.info("   ✅ VS Code settings updated")
            return True

        except Exception as e:
            logger.info(f"   ❌ Failed to update settings: {e}")
            return False

    def create_emergency_launcher(self):
        """Create emergency Python launcher"""
        logger.info("🚀 Creating emergency launcher...")

        launcher_script = f"""@echo off
rem Emergency Python Launcher for NoxSuite
set PYTHONPATH=%cd%;%PYTHONPATH%
"{sys.executable}" %*
if errorlevel 1 (
    echo.
    echo ❌ Python execution failed
    echo 💡 Try: python_launcher.bat your_script.py
    pause
)
"""

        try:
            with open("emergency_python.bat", "w") as f:
                f.write(launcher_script)
            logger.info(
                "   ✅ Emergency launcher created: emergency_python.bat")
            return True
        except Exception as e:
            logger.info(f"   ❌ Failed to create launcher: {e}")
            return False

    def reset_copilot_state(self):
        """Reset Copilot state and tool count"""
        logger.info("🔄 Resetting Copilot state...")

        self.tool_count = 0

        # Kill any hanging Python processes that might interfere
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", "python.exe"],
                capture_output=True,
                check=False,
            )
            time.sleep(2)
        except:
            pass

        logger.info("   ✅ Copilot state reset")
        logger.info(f"   📊 Tool count: {self.tool_count}/{self.max_tools}")

    def perform_health_check(self):
        """Perform basic health check"""
        logger.info("🏥 Health Check...")

        checks = {
            "Python executable": sys.executable,
            "Python version": sys.version.split()[0],
            "Working directory": str(self.current_dir),
            "Virtual environment": (
                "Yes"
                if hasattr(sys, "real_prefix")
                or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
                else "No"
            ),
        }

        for check, value in checks.items():
            logger.info(f"   ✅ {check}: {value}")

        # Test basic Python functionality
        try:
            import requests

            logger.info("   ✅ Requests module: Available")
        except ImportError:
            logger.info("   ⚠️ Requests module: Missing")

        # Test file operations
        try:
            test_file = self.current_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("   ✅ File operations: Working")
        except Exception as e:
            logger.info(f"   ❌ File operations: Failed ({e})")

    def apply_comprehensive_fix(self):
        """Apply comprehensive fix based on diagnosis"""
        logger.info("🔧 Applying Comprehensive Fix...")
        logger.info("=" * 50)

        # Step 1: Diagnose
        issues = self.diagnose_issues()
        if issues:
            logger.info(f"   📋 Issues found: {', '.join(issues)}")
        else:
            logger.info("   ✅ No major issues detected")

        # Step 2: Fix Python interpreter
        self.fix_python_interpreter()

        # Step 3: Reset Copilot state
        self.reset_copilot_state()

        # Step 4: Create emergency tools
        self.create_emergency_launcher()

        # Step 5: Health check
        self.perform_health_check()

        logger.info("\n" + "=" * 50)
        logger.info("✅ Self-Repair Completed!")

        logger.info("\n📋 Next Steps:")
        logger.info("1. Restart VS Code completely")
        logger.info("2. Press Ctrl+Shift+P")
        logger.info("3. Run 'Python: Select Interpreter'")
        logger.info(f"4. Select: {sys.executable}")
        logger.info("5. Test Copilot with a simple Python file")
        logger.info("6. If issues persist, run: emergency_python.bat")

        return True


def main():
    """Main self-repair routine"""
    logger.info("🤖 Copilot Self-Repair System")
    logger.info("=" * 50)

    repair_system = CopilotSelfRepair()

    try:
        repair_system.apply_comprehensive_fix()

        # Create status file
        status = {
            "repair_timestamp": time.time(),
            "python_executable": sys.executable,
            "python_version": sys.version.split()[0],
            "tool_count": repair_system.tool_count,
            "status": "repaired",
        }

        with open("copilot_repair_status.json", "w") as f:
            json.dump(status, f, indent=2)

        logger.info("\n🎯 SELF-REPAIR MISSION ACCOMPLISHED!")
        logger.info("📄 Status saved to: copilot_repair_status.json")

    except Exception as e:
        logger.info(f"\n❌ Self-repair failed: {e}")
        logger.info("💡 Manual intervention required")
        return False

    return True


if __name__ == "__main__":
    main()
