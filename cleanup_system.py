#!/usr/bin/env python3
"""
NoxPanel Suite Comprehensive Cleanup and Issue Resolution
Date: 2025-07-29
Author: @hxwxdmhd

This script performs:
1. Active code analysis and issue identification
2. Installer analysis and fixes
3. Archive strategy implementation
4. Code cleanup and fixes
5. Validation and testing
"""

        import re
from datetime import datetime
from pathlib import Path
import ast
import json
import os
import sys

            from app import init_database
    import argparse
from typing import Dict, List, Set, Tuple
import importlib.util
import logging
import shutil
import subprocess

    
    parser = argparse.ArgumentParser(description="NoxSuite Installer")
    parser.add_argument("--mode", choices=["development", "production"], 
                       default="development", help="Installation mode")
    parser.add_argument("--test", action="store_true", 
                       help="Run installation test without making changes")
    
    args = parser.parse_args()
    
    installer = NoxSuiteInstaller()
    
    if args.test:
        logger.info("Running installation test...")
        # Just check requirements
        success = installer.check_python_version()
        sys.exit(0 if success else 1)
    else:
        success = installer.install(args.mode)
        sys.exit(0 if success else 1)
'''

        installer_path = self.project_root / "install.py"
        try:
            with open(installer_path, "w", encoding="utf-8") as f:
                f.write(installer_content)

            # Make executable on Unix-like systems
            if os.name != "nt":
                os.chmod(installer_path, 0o755)

            logger.info(f"Created installer: {installer_path}")

        except Exception as e:
            logger.error(f"Failed to create installer: {e}")

    def clean_requirements(self):
        """Clean up requirements.txt to remove unused dependencies"""
        logger.info("🔧 Cleaning requirements.txt...")

        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            return

        # Read current requirements
        with open(requirements_file, "r") as f:
            lines = f.readlines()

        # Keep essential dependencies
        essential_deps = {
            "Flask",
            "Flask-CORS",
            "Flask-SocketIO",
            "Flask-JWT-Extended",
            "SQLAlchemy",
            "psycopg2-binary",
            "redis",
            "cryptography",
            "psutil",
            "requests",
            "python-dotenv",
            "PyYAML",
            "colorama",
        }

        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if (
                not line
                or line.startswith("#")
                or any(dep in line for dep in essential_deps)
            ):
                cleaned_lines.append(line)

        # Write cleaned requirements
        with open(requirements_file, "w") as f:
            f.write("\n".join(cleaned_lines))

        logger.info("Cleaned requirements.txt")

    def generate_report(self):
        """Generate comprehensive cleanup report"""
        logger.info("📊 Generating cleanup report...")

        report = {
            "cleanup_date": self.archive_date,
            "project_root": str(self.project_root),
            "issues_found": self.issues_found,
            "files_processed": {
                "empty_files_archived": len(self.issues_found["empty_files"]),
                "duplicate_files_archived": len(self.issues_found["duplicate_files"]),
                "syntax_errors_found": len(self.issues_found["syntax_errors"]),
                "import_errors_found": len(self.issues_found["import_errors"]),
                "security_issues_found": len(self.issues_found["security_issues"]),
            },
            "recommendations": [
                "Run 'python install.py' to set up the environment",
                "Test the installation with 'python install.py --test'",
                "Run 'python validate_system.py' to verify system health",
                "Check archived files before permanent deletion",
                "Update .env file with production credentials before deployment",
            ],
        }

        report_file = self.project_root / "cleanup_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Generate markdown report
        md_content = f"""# NoxSuite Cleanup Report - {self.archive_date}

## Summary
- **Empty files archived**: {len(self.issues_found['empty_files'])}
- **Duplicate files archived**: {len(self.issues_found['duplicate_files'])}
- **Syntax errors found**: {len(self.issues_found['syntax_errors'])}
- **Import errors found**: {len(self.issues_found['import_errors'])}
- **Security issues found**: {len(self.issues_found['security_issues'])}

## Actions Taken

### Files Archived
- Empty files moved to `archive/{self.archive_date}/empty-files/`
- Duplicate servers moved to `archive/{self.archive_date}/duplicate-servers/`
- Files with broken imports moved to `archive/{self.archive_date}/broken-imports/`

### Installer Improvements
- Created new `install.py` with comprehensive setup
- Cleaned `requirements.txt` to remove unused dependencies
- Added environment configuration template

### Core Files Preserved
- `app.py` (main application)
- `advanced_ai_engine.py` (AI functionality)
- `validate_system.py` (system validation)
- `requirements.txt` (dependencies)
- `docker-compose.yml` (containerization)

## Next Steps
1. Run `python install.py` to set up the environment
2. Test installation with `python install.py --test`
3. Run `python validate_system.py` to verify system health
4. Review archived files before permanent deletion
5. Update `.env` file with production credentials

## Files That Need Attention
"""

        if self.issues_found["syntax_errors"]:
            md_content += "\n### Syntax Errors\n"
            for file in self.issues_found["syntax_errors"]:
                md_content += f"- {file}\n"

        if self.issues_found["security_issues"]:
            md_content += "\n### Security Issues\n"
            for file in self.issues_found["security_issues"]:
                md_content += f"- {file}\n"

        md_report_file = self.project_root / "CLEANUP_REPORT.md"
        with open(md_report_file, "w") as f:
            f.write(md_content)

        logger.info(f"Reports generated: {report_file}, {md_report_file}")

    def run_cleanup(self):
        """Run the complete cleanup process"""
        logger.info("🚀 Starting NoxSuite comprehensive cleanup...")

        # Phase 1: Analysis
        logger.info("=" * 50)
        logger.info("PHASE 1: CODE ANALYSIS")
        logger.info("=" * 50)

        syntax_errors = self.analyze_syntax_errors()
        import_errors = self.analyze_import_errors()
        empty_files = self.identify_empty_files()
        duplicate_servers = self.identify_duplicate_servers()
        security_issues = self.check_security_issues()

        # Phase 2: Archive problematic files
        logger.info("=" * 50)
        logger.info("PHASE 2: ARCHIVING FILES")
        logger.info("=" * 50)

        self.archive_files(
            self.issues_found["empty_files"], "empty-files", "Empty or minimal content"
        )
        self.archive_files(
            self.issues_found["duplicate_files"],
            "duplicate-servers",
            "Duplicate server implementations",
        )
        self.archive_files(
            self.issues_found["import_errors"],
            "broken-imports",
            "Broken import statements",
        )

        # Phase 3: Fix installer and dependencies
        logger.info("=" * 50)
        logger.info("PHASE 3: INSTALLER FIXES")
        logger.info("=" * 50)

        self.fix_installer_issues()
        self.clean_requirements()

        # Phase 4: Generate report
        logger.info("=" * 50)
        logger.info("PHASE 4: REPORTING")
        logger.info("=" * 50)

        self.generate_report()

        logger.info("🎉 Cleanup completed successfully!")
        logger.info(f"Check CLEANUP_REPORT.md for details")
        logger.info(f"Archived files are in: {self.archive_root}")


if __name__ == "__main__":
    cleanup = NoxSuiteCleanup()
    cleanup.run_cleanup()
