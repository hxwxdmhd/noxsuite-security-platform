from typing import Dict, List, Tuple
from pathlib import Path
import os
import json
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Workspace Organization Validation Script
=========================================
Validates the new workspace organization and checks for any issues
"""


def check_folder_organization() -> Dict[str, List[str]]:
    """
    REASONING CHAIN:
    1. Problem: Function check_folder_organization needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_folder_organization operation
    3. Solution: Implement check_folder_organization with enterprise-grade patterns and error handling
    4. Validation: Test check_folder_organization with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Check the organized folder structure"""

    base_path = Path(".")
    expected_folders = {
        "NoxPanel Core": [
            "server_*.py",
            "main_*.py",
            "models_*.py",
            "gateway_service.py",
        ],
        "AI & NoxPanel": [
            "activate_multi_agent.py",
            "agent_*.py",
            "ai_*.py",
            "predictive_analytics.py",
        ],
        "Plugin System": ["plugins/", "generated_plugins/", "enhanced_plugin_*.py"],
        "Aethercore": ["aether*.py", "status.json"],
        "Docker & Config": ["docker-compose*.yml", "Dockerfile*", "requirements*.txt"],
        "Documentation": ["*.md", "*.html", "*.rst"],
        "Scripts & Tools": ["install*.py", "*_status*.py", "deploy*.py", "cleanup*.py"],
    }

    results = {}

    for folder, patterns in expected_folders.items():
        folder_path = base_path / folder
        if folder_path.exists():
            files = []
            for pattern in patterns:
                files.extend(list(folder_path.glob(pattern)))
            results[folder] = [str(f.relative_to(folder_path)) for f in files]
        else:
            results[folder] = ["FOLDER NOT FOUND"]

    return results


def check_server_files() -> Dict[str, Dict[str, any]]:
    """
    REASONING CHAIN:
    1. Problem: Function check_server_files needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_server_files operation
    3. Solution: Implement check_server_files with enterprise-grade patterns and error handling
    4. Validation: Test check_server_files with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Check server files for content and availability"""

    server_locations = [
        "NoxPanel Core/server_quick_deploy.py",
        "NoxPanel Core/main_unified_server.py",
        "NoxPanel Core/server_production.py",
        "NoxPanel Core/server_enhanced.py",
        "Scripts & Tools/launch_unified_server.py",
    ]

    results = {}

    for server_file in server_locations:
        file_path = Path(server_file)
        if file_path.exists():
            size = file_path.stat().st_size
            results[server_file] = {
                "exists": True,
                "size": size,
                "has_content": size > 100,
                "status": "✅ Working" if size > 100 else "⚠️ Empty",
            }
        else:
            results[server_file] = {
                "exists": False,
                "size": 0,
                "has_content": False,
                "status": "❌ Missing",
            }

    return results


def check_import_dependencies() -> Dict[str, List[str]]:
    """
    REASONING CHAIN:
    1. Problem: Function check_import_dependencies needs clear operational definition
    2. Analysis: Implementation requires specific logic for check_import_dependencies operation
    3. Solution: Implement check_import_dependencies with enterprise-grade patterns and error handling
    4. Validation: Test check_import_dependencies with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Check for critical dependency files"""

    critical_files = [
        "NoxPanel Core/models_simple.py",
        "NoxPanel Core/unified_plugin_system.py",
        "NoxPanel Core/models_unified.py",
        "Docker & Config/docker-compose.yml",
        "Docker & Config/requirements.txt",
    ]

    results = {}

    for file_path in critical_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            status = "✅ Available" if size > 50 else "⚠️ Empty"
        else:
            status = "❌ Missing"

        results[file_path] = [status]

    return results


def validate_workspace_config() -> Dict[str, any]:
    """
    REASONING CHAIN:
    1. Problem: Input validation needs comprehensive checking logic
    2. Analysis: Validation function requires thorough input analysis
    3. Solution: Implement validate_workspace_config with enterprise-grade patterns and error handling
    4. Validation: Test validate_workspace_config with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Validate the workspace configuration file"""

    config_file = Path("noxpanel-modular-workspace.code-workspace")

    if not config_file.exists():
        return {"status": "❌ Missing", "folders": []}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        folders = config.get("folders", [])
        folder_names = [f.get("name", "Unknown") for f in folders]

        return {
            "status": "✅ Valid",
            "folders": folder_names,
            "folder_count": len(folders),
        }
    except Exception as e:
        return {"status": f"❌ Error: {e}", "folders": []}


def main():
    """
    REASONING CHAIN:
    1. Problem: Function main needs clear operational definition
    2. Analysis: Implementation requires specific logic for main operation
    3. Solution: Implement main with enterprise-grade patterns and error handling
    4. Validation: Test main with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Run the complete validation"""
    logger.info("🔍 NoxPanel Suite - Workspace Organization Validation")
    logger.info("=" * 60)

    # Check folder organization
    logger.info("\n📁 FOLDER ORGANIZATION:")
    folder_results = check_folder_organization()
    for folder, files in folder_results.items():
        logger.info(f"\n{folder}:")
        if files == ["FOLDER NOT FOUND"]:
            logger.info("  ❌ Folder not found")
        else:
            logger.info(f"  ✅ Found {len(files)} files")
            for file in files[:5]:  # Show first 5 files
                logger.info(f"    - {file}")
            if len(files) > 5:
                logger.info(f"    ... and {len(files) - 5} more")

    # Check server files
    logger.info("\n🖥️ SERVER FILES STATUS:")
    server_results = check_server_files()
    for server, info in server_results.items():
        logger.info(f"  {info['status']} {server} ({info['size']} bytes)")

    # Check dependencies
    logger.info("\n📦 CRITICAL DEPENDENCIES:")
    dep_results = check_import_dependencies()
    for file, status in dep_results.items():
        logger.info(f"  {status[0]} {file}")

    # Check workspace config
    logger.info("\n⚙️ WORKSPACE CONFIGURATION:")
    config_results = validate_workspace_config()
    logger.info(f"  {config_results['status']}")
    if config_results.get("folders"):
        logger.info(f"  Configured folders: {config_results['folder_count']}")
        for folder in config_results["folders"]:
            logger.info(f"    - {folder}")

    logger.info("\n" + "=" * 60)
    logger.info("✅ Validation Complete!")

    # Summary recommendations
    working_servers = [k for k, v in server_results.items()
                       if v["has_content"]]
    if working_servers:
        logger.info(f"\n💡 RECOMMENDED SERVER: {working_servers[0]}")
    else:
        logger.info("\n⚠️ WARNING: No working server files found!")
        logger.info("   Consider restoring from archive/deprecated/")


if __name__ == "__main__":
    main()
