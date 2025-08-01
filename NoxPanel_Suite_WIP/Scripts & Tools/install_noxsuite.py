from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)

#!/usr/bin/env python3
"""
NoxSuite Smart Installer Launcher
Simple launcher script that provides multiple installation modes
"""

import sys
import os
from pathlib import Path

# Add current directory to path to import our modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def show_help():
    """
    REASONING CHAIN:
    1. Problem: Function show_help needs clear operational definition
    2. Analysis: Implementation requires specific logic for show_help operation
    3. Solution: Implement show_help with enterprise-grade patterns and error handling
    4. Validation: Test show_help with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Show help message with available modes"""
    help_text = """
🧠 NoxSuite Smart Self-Healing Installer

USAGE:
    python install_noxsuite.py [mode] [options]

INSTALLATION MODES:
    guided     Interactive guided installation (default)
    fast       Quick installation with recommended defaults
    dry-run    Preview installation without making changes
    safe       Minimal installation for maximum stability
    recovery   Recover from previous failed installation

EXAMPLES:
    python install_noxsuite.py                 # Guided mode
    python install_noxsuite.py fast            # Fast mode
    python install_noxsuite.py dry-run         # Preview only
    python install_noxsuite.py recovery        # Recovery mode

OPTIONS:
    --help, -h     Show this help message
    --version      Show installer version
    --check-deps   Check dependencies only
    --update       Check for installer updates

FEATURES:
    ✅ Smart dependency detection and installation
    ✅ Cross-platform support (Windows, Linux, macOS)
    ✅ Self-healing error recovery
    ✅ UTF-8 encoding support with fallbacks
    ✅ Atomic operations with rollback capability
    ✅ Comprehensive logging and auditing
    ✅ AI-powered issue analysis and suggestions
    ✅ Multiple package manager support
    ✅ Docker health checks and optimization
    ✅ Real-time progress tracking with ETA
    ✅ Network connectivity validation
    ✅ System resource monitoring
    ✅ Configuration validation
    ✅ Backup and restore functionality

For more information, visit: https://github.com/noxsuite/noxsuite
    """
    logger.info(help_text)

def check_dependencies():
    """
    REASONING CHAIN:
    1. Problem: Function check_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_dependencies operation
    3. Solution: Implement check_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test check_dependencies with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Quick dependency check"""
    logger.info("🔍 Checking dependencies...")
    
    dependencies = {
        "Python": sys.version_info >= (3, 8),
        "Git": os.system("git --version > /dev/null 2>&1") == 0,
        "Docker": os.system("docker --version > /dev/null 2>&1") == 0,
        "Node.js": os.system("node --version > /dev/null 2>&1") == 0
    }
    
    logger.info("\n📋 Dependency Status:")
    all_good = True
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        logger.info(f"   {status} {dep}")
        if not available:
            all_good = False
    
    if all_good:
        logger.info("\n🎉 All dependencies are available!")
    else:
        logger.info("\n⚠️  Some dependencies are missing. The installer can help install them.")
    
    return all_good

def check_updates():
    """
    REASONING CHAIN:
    1. Problem: Function check_updates needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_updates operation
    3. Solution: Implement check_updates with enterprise-grade patterns and error handling
    4. Validation: Test check_updates with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Check for installer updates"""
    logger.info("🔄 Checking for updates...")
    
    try:
        from noxsuite_installer_utils import UpdateChecker
        from noxsuite_smart_installer_complete import SmartLogger
        
        logger = SmartLogger()
        checker = UpdateChecker(logger)
        updates = checker.check_for_updates()
        
        if updates.get("available", False):
            logger.info("🆕 Updates available:")
            for component, info in updates["components"].items():
                if info.get("update_available", False):
                    current = info.get("current_version", "unknown")
                    latest = info.get("latest_version", "unknown")
                    logger.info(f"   • {component}: {current} → {latest}")
        else:
            logger.info("✅ You have the latest version!")
            
    except Exception as e:
        logger.info(f"❌ Could not check for updates: {e}")

def try_bootstrap():
    """
    REASONING CHAIN:
    1. Problem: Function try_bootstrap needs clear operational definition
    2. Analysis: Implementation requires specific logic for try_bootstrap operation
    3. Solution: Implement try_bootstrap with enterprise-grade patterns and error handling
    4. Validation: Test try_bootstrap with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Try to run bootstrap installer if main installer fails"""
    logger.info("\n🔄 Attempting to bootstrap dependencies...")
    try:
        bootstrap_file = Path("noxsuite_bootstrap_installer.py")
        if bootstrap_file.exists():
            import subprocess
            result = subprocess.run([
                sys.executable, 
                str(bootstrap_file)
            ] + sys.argv[1:], capture_output=False)
            sys.exit(result.returncode)
        else:
            logger.info("❌ Bootstrap installer not found")
            return False
    except Exception as e:
        logger.info(f"❌ Bootstrap failed: {e}")
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
    """Main launcher function"""
    # Parse command line arguments
    args = sys.argv[1:]
    
    if not args or args[0] in ["--help", "-h", "help"]:
        show_help()
        return
    
    if args[0] == "--version":
        logger.info("NoxSuite Smart Installer v1.0.0")
        return
    
    if args[0] == "--check-deps":
        check_dependencies()
        return
    
    if args[0] == "--update":
        check_updates()
        return
    
    # Import the main installer
    try:
        from noxsuite_smart_installer_complete import SmartNoxSuiteInstaller, InstallMode
    except ImportError as e:
        logger.info(f"❌ Could not import installer modules: {e}")
        logger.info("This usually means required dependencies are missing.")
        
        # Try to run bootstrap installer
        logger.info("\n🔧 The installer will now attempt to install missing dependencies...")
        try_bootstrap()
        
        logger.info("\nIf the problem persists, try manually installing dependencies:")
        logger.info("  pip install requests chardet")
        logger.info("  python install_noxsuite.py")
        sys.exit(1)
    
    # Determine installation mode
    mode_map = {
        "guided": InstallMode.GUIDED,
        "fast": InstallMode.FAST,
        "dry-run": InstallMode.DRY_RUN,
        "safe": InstallMode.SAFE,
        "recovery": InstallMode.RECOVERY
    }
    
    mode_arg = args[0].lower() if args else "guided"
    install_mode = mode_map.get(mode_arg, InstallMode.GUIDED)
    
    if mode_arg not in mode_map:
        logger.info(f"❌ Unknown mode: {mode_arg}")
        logger.info("Use --help to see available modes")
        sys.exit(1)
    
    # Welcome message
    logger.info(f"")
╔═══════════════════════════════════════════════════════════════════╗
║                🧠 NoxSuite Smart Self-Healing Installer           ║
║                      Starting {install_mode.value.title()} Mode Installation                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Run the installer
    try:
        installer = SmartNoxSuiteInstaller()
        success = installer.run_installation(install_mode)
        
        if success:
            logger.info("\n🎉 Installation completed successfully!")
            sys.exit(0)
        else:
            logger.info("\n❌ Installation failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.info(f"\n❌ Installer crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
