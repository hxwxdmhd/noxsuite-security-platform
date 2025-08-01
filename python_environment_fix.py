from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Python Environment Emergency Fix
Resolves DLL issues and restores Copilot functionality
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_installation():
    """Check current Python installation status"""
    logger.info("🔍 Checking Python installation...")
    
    try:
        # Check Python version
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        logger.info(f"   Current Python: {result.stdout.strip()}")
        
        # Check Python path
        logger.info(f"   Python executable: {sys.executable}")
        
        # Check if DLL exists
        python_dir = Path(sys.executable).parent
        dll_path = python_dir / "python313.dll"
        
        if dll_path.exists():
            logger.info(f"   ✅ python313.dll found at: {dll_path}")
            return True
        else:
            logger.info(f"   ❌ python313.dll missing from: {python_dir}")
            return False
            
    except Exception as e:
        logger.info(f"   ❌ Error checking Python: {e}")
        return False

def fix_python_environment():
    """Fix Python environment issues"""
    logger.info("\n🔧 Fixing Python environment...")
    
    try:
        # Option 1: Repair Python installation
        logger.info("   Attempting to repair Python installation...")
        
        # For Windows, try to repair the installation
        if os.name == 'nt':
            # Try to find Python installer
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            # Common repair commands
            repair_commands = [
                ["py", "-m", "pip", "install", "--upgrade", "--force-reinstall", "pip"],
                ["py", "-m", "ensurepip", "--upgrade"],
            ]
            
            for cmd in repair_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.info(f"   ✅ Successfully ran: {' '.join(cmd)}")
                except subprocess.CalledProcessError:
                    logger.info(f"   ⚠️ Failed: {' '.join(cmd)}")
        
        return True
        
    except Exception as e:
        logger.info(f"   ❌ Repair failed: {e}")
        return False

def setup_vscode_python():
    """Configure VS Code Python settings"""
    logger.info("\n⚙️ Configuring VS Code Python settings...")
    
    vscode_settings = {
        "python.defaultInterpreterPath": sys.executable,
        "python.terminal.activateEnvironment": True,
        "github.copilot.enable": {
            "*": True,
            "yaml": True,
            "plaintext": False,
            "markdown": True,
            "python": True
        },
        "github.copilot.inlineSuggest.enable": True,
        "files.associations": {
            "*.py": "python"
        }
    }
    
    # Create .vscode directory if it doesn't exist
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # Update settings.json
    settings_file = vscode_dir / "settings.json"
    
    try:
        import json
        
        # Load existing settings or create new
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                existing_settings = json.load(f)
        else:
            existing_settings = {}
        
        # Merge settings
        existing_settings.update(vscode_settings)
        
        # Write back
        with open(settings_file, 'w') as f:
            json.dump(existing_settings, f, indent=2)
        
        logger.info(f"   ✅ VS Code settings updated: {settings_file}")
        return True
        
    except Exception as e:
        logger.info(f"   ❌ Failed to update VS Code settings: {e}")
        return False

def create_python_launcher():
    """Create a reliable Python launcher script"""
    logger.info("\n🚀 Creating Python launcher...")
    
    launcher_content = f'''@echo off
REM Python Launcher for NoxSuite
REM Ensures consistent Python environment

set PYTHON_PATH={sys.executable}
set PYTHONPATH=%cd%;%PYTHONPATH%

REM Check if Python is available
"%PYTHON_PATH%" --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found at %PYTHON_PATH%
    echo Please reinstall Python or update the path
    pause
    exit /b 1
)

REM Launch Python with provided arguments
"%PYTHON_PATH%" %*
'''
    
    try:
        with open("python_launcher.bat", 'w') as f:
            f.write(launcher_content)
        
        logger.info("   ✅ Python launcher created: python_launcher.bat")
        logger.info("   💡 Use this launcher if direct Python calls fail")
        return True
        
    except Exception as e:
        logger.info(f"   ❌ Failed to create launcher: {e}")
        return False

def restart_vscode_services():
    """Restart VS Code related services"""
    logger.info("\n🔄 Restarting VS Code services...")
    
    logger.info("   📝 Manual steps required:")
    logger.info("   1. Close VS Code completely")
    logger.info("   2. Press Ctrl+Shift+P in VS Code")
    logger.info("   3. Run 'Python: Select Interpreter'")
    logger.info(f"   4. Select: {sys.executable}")
    logger.info("   5. Restart VS Code")
    logger.info("   6. Test Copilot with Ctrl+I")

def main():
    """Main fix routine"""
    logger.info("🚨 Python Environment Emergency Fix")
    logger.info("=" * 50)
    
    # Step 1: Check current state
    python_ok = check_python_installation()
    
    # Step 2: Attempt fixes
    if not python_ok:
        logger.info("\n⚠️ Python DLL issues detected - attempting repair...")
        fix_python_environment()
    
    # Step 3: Configure VS Code
    setup_vscode_python()
    
    # Step 4: Create backup launcher
    create_python_launcher()
    
    # Step 5: Provide restart instructions
    restart_vscode_services()
    
    logger.info("\n" + "=" * 50)
    logger.info("🎯 Emergency fix completed!")
    logger.info("\n📋 Next steps:")
    logger.info("1. Restart VS Code completely")
    logger.info("2. Open Command Palette (Ctrl+Shift+P)")
    logger.info("3. Select 'Python: Select Interpreter'")
    logger.info("4. Choose the Python path shown above")
    logger.info("5. Test a .py file to verify Copilot works")
    
    logger.info(f"\n💻 If issues persist, reinstall Python from:")
    logger.info("   https://www.python.org/downloads/")

if __name__ == "__main__":
    main()