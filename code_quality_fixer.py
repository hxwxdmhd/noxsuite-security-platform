#!/usr/bin/env python3
"""
NoxSuite Code Quality Fix Agent
Addresses critical code quality issues from audit findings
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeQualityFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.issues_found = 0

    def fix_bare_except_clauses(self, file_path: Path) -> int:
        """Fix bare except clauses with specific exception handling"""
        fixes = 0

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Common patterns to fix
            replacements = [
                # Basic bare except
                (
                    r"(\s+)except:\s*\n(\s+)(.+)",
                    r'\1except Exception as e:\n\2logger.warning(f"Unexpected error: {e}")\n\2\3',
                ),
                # Bare except with comment
                (
                    r"(\s+)except:\s*#\s*(.+)\n(\s+)(.+)",
                    r'\1except Exception as e:  # \2\n\3logger.warning(f"Error (\2): {e}")\n\3\4',
                ),
                # File operation bare except
                (
                    r"(\s+)except:\s*\n(\s+)return False",
                    r'\1except (IOError, OSError, ValueError) as e:\n\2logger.warning(f"File operation error: {e}")\n\2return False',
                ),
                # Token/JWT bare except
                (
                    r"(\s+)except:\s*\n(\s+)return None",
                    r'\1except (jwt.InvalidTokenError, ValueError) as e:\n\2logger.warning(f"Token validation error: {e}")\n\2return None',
                ),
            ]

            for pattern, replacement in replacements:
                new_content = re.sub(pattern, replacement,
                                     content, flags=re.MULTILINE)
                if new_content != content:
                    fixes += content.count("except:") - \
                        new_content.count("except:")
                    content = new_content

            # Manual specific fixes for known issues
            if "auth_critical.py" in str(file_path):
                # Fix specific patterns in auth_critical.py
                content = content.replace(
                    'except:\n                logger.error("Failed to create user directory")',
                    'except (OSError, PermissionError) as e:\n                logger.error(f"Failed to create user directory: {e}")',
                )
                content = content.replace(
                    "except:\n                    pass",
                    'except Exception as e:\n                    logger.warning(f"Cleanup error: {e}")',
                )

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                logger.info(
                    f"✅ Fixed {fixes} bare except clauses in {file_path.name}")

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")

        return fixes

    def remove_unused_imports(self, file_path: Path) -> int:
        """Remove unused imports based on static analysis results"""
        fixes = 0

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Known unused imports from flake8 analysis
            unused_imports = [
                "from typing import Optional",
                "import json",
                "import os",
                "from typing import List",
                "from fastapi import BackgroundTasks",
                "from fastapi.staticfiles import StaticFiles",
                "import hashlib",
                "from datetime import timezone",
                "from fastapi import Response",
                "from pydantic import EmailStr",
                "from pydantic import validator",
                "import redis",
                "import asyncio",
                "from dataclasses import asdict",
                "from pathlib import Path",
            ]

            cleaned_lines = []
            for line in lines:
                line_stripped = line.strip()
                if any(unused in line for unused in unused_imports) and line.startswith(
                    ("import ", "from ")
                ):
                    logger.info(f"Removing unused import: {line_stripped}")
                    fixes += 1
                    continue
                cleaned_lines.append(line)

            if fixes > 0:
                new_content = "\n".join(cleaned_lines)
                file_path.write_text(new_content, encoding="utf-8")
                logger.info(
                    f"✅ Removed {fixes} unused imports from {file_path.name}")

        except Exception as e:
            logger.error(f"Error cleaning imports in {file_path}: {e}")

        return fixes

    def fix_formatting_issues(self, file_path: Path) -> int:
        """Fix common formatting issues"""
        fixes = 0

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Fix trailing whitespace
            content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

            # Fix blank lines with whitespace
            content = re.sub(r"^[ \t]+$", "", content, flags=re.MULTILINE)

            # Fix multiple blank lines (max 2)
            content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)

            # Fix line length issues (simple cases)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if len(line) > 120 and "http" not in line:  # Don't break URLs
                    # Simple line breaking for long lines
                    if " and " in line and len(line) > 120:
                        lines[i] = line.replace(" and ", " and \\\n    ")
                        fixes += 1

            content = "\n".join(lines)

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                fixes = len(re.findall(
                    r"[ \t]+$", original_content, re.MULTILINE))
                logger.info(
                    f"✅ Fixed {fixes} formatting issues in {file_path.name}")

        except Exception as e:
            logger.error(f"Error fixing formatting in {file_path}: {e}")

        return fixes

    def add_missing_imports(self, file_path: Path) -> int:
        """Add missing imports for proper functionality"""
        fixes = 0

        try:
            content = file_path.read_text(encoding="utf-8")

            # Check if file needs logging and doesn't have it
            if "logger." in content and "import logging" not in content:
                lines = content.split("\n")
                import_section_end = 0

                for i, line in enumerate(lines):
                    if line.startswith(("import ", "from ")) or line.strip() == "":
                        import_section_end = i
                    else:
                        break

                lines.insert(import_section_end + 1, "import logging")
                lines.insert(import_section_end + 2, "")
                lines.insert(
                    import_section_end +
                    3, "logger = logging.getLogger(__name__)"
                )

                content = "\n".join(lines)
                file_path.write_text(content, encoding="utf-8")
                fixes += 1
                logger.info(
                    f"✅ Added missing logging import to {file_path.name}")

        except Exception as e:
            logger.error(f"Error adding imports to {file_path}: {e}")

        return fixes

    def process_file(self, file_path: Path) -> Dict[str, int]:
        """Process a single file for all quality fixes"""
        logger.info(f"🔧 Processing {file_path.name}...")

        results = {
            "bare_except_fixes": self.fix_bare_except_clauses(file_path),
            "unused_import_removals": self.remove_unused_imports(file_path),
            "formatting_fixes": self.fix_formatting_issues(file_path),
            "missing_import_additions": self.add_missing_imports(file_path),
        }

        total_fixes = sum(results.values())
        self.fixes_applied += total_fixes

        if total_fixes > 0:
            logger.info(
                f"✅ {file_path.name}: {total_fixes} total fixes applied")

        return results

    def run_comprehensive_fixes(self) -> Dict[str, Any]:
        """Run comprehensive code quality fixes"""
        logger.info("🚀 Starting comprehensive code quality fixes...")

        # Target files from static analysis
        target_files = [
            Path("backend/fastapi/main.py"),
            Path("backend/fastapi/routers/auth.py"),
            Path("backend/fastapi/routers/auth_enhanced.py"),
            Path("backend/fastapi/routers/auth_critical.py"),
            Path("backend/fastapi/core/access_control.py"),
            Path("langflow/components/noxsuite_system_monitor.py"),
            Path("langflow/components/noxsuite_multi_agent_coordinator.py"),
            Path("langflow/components/noxsuite_docker_manager.py"),
            Path("langflow/components/noxsuite_mcp_orchestrator.py"),
            Path("langflow/component_registry.py"),
        ]

        results = {"files_processed": 0, "total_fixes": 0, "files_results": {}}

        for file_path in target_files:
            if file_path.exists():
                file_results = self.process_file(file_path)
                results["files_results"][str(file_path)] = file_results
                results["files_processed"] += 1
                results["total_fixes"] += sum(file_results.values())

        logger.info("=" * 60)
        logger.info("🎉 CODE QUALITY FIXES COMPLETE")
        logger.info("=" * 60)
        logger.info(f"📁 Files Processed: {results['files_processed']}")
        logger.info(f"🔧 Total Fixes Applied: {results['total_fixes']}")
        logger.info("=" * 60)

        return results


def main():
    """Main execution function"""
    fixer = CodeQualityFixer()
    results = fixer.run_comprehensive_fixes()

    # Save results
    import json

    results_file = Path("logs/code_audit_installer/code_quality_fixes.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(
        f"✅ Code quality fixes complete: {results['total_fixes']} fixes applied")
    return results


if __name__ == "__main__":
    main()
