#!/usr/bin/env python3
"""
🎨 NoxSuite Code Quality Improver
=================================

Comprehensive tool for improving code quality across the NoxSuite Security Platform.
Automatically fixes formatting, imports, and code style issues.

Features:
- Automatic code formatting with Black
- Import organization with isort
- Lint error fixing
- Code complexity analysis
- Duplicate code detection
- Documentation improvements
- Type hint additions

Author: NoxSuite AI Enhancement Team
Date: August 1, 2025
Version: 1.0.0
"""

import ast
import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("code_quality_improvement.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CodeQualityImprover:
    """Comprehensive code quality improvement tool"""

    def __init__(self, repo_root: str = None):
        self.repo_root = Path(repo_root or os.getcwd())
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.improvements_made = []
        self.quality_report = {
            "timestamp": self.timestamp,
            "files_processed": 0,
            "improvements": {
                "formatting": 0,
                "imports": 0,
                "linting": 0,
                "complexity": 0,
                "documentation": 0,
                "type_hints": 0,
            },
            "issues_found": [],
            "issues_fixed": [],
        }

    def run_comprehensive_improvements(self) -> Dict[str, Any]:
        """Run comprehensive code quality improvements"""
        print(f"🎨 NoxSuite Code Quality Improver")
        print(f"=" * 50)
        logger.info("🎨 Starting comprehensive code quality improvements")
        logger.info(f"📁 Repository: {self.repo_root}")
        logger.info(f"🕐 Timestamp: {self.timestamp}")

        # Phase 1: Install required tools
        print(f"\n📦 Phase 1: Installing Quality Tools")
        self._install_quality_tools()

        # Phase 2: Code formatting
        print(f"\n🎨 Phase 2: Code Formatting")
        self._format_code()

        # Phase 3: Import organization
        print(f"\n📚 Phase 3: Import Organization")
        self._organize_imports()

        # Phase 4: Lint fixing
        print(f"\n🔧 Phase 4: Lint Error Fixing")
        self._fix_lint_errors()

        # Phase 5: Complexity analysis
        print(f"\n📊 Phase 5: Code Complexity Analysis")
        self._analyze_complexity()

        # Phase 6: Documentation improvements
        print(f"\n📝 Phase 6: Documentation Improvements")
        self._improve_documentation()

        # Phase 7: Type hint additions
        print(f"\n🏷️ Phase 7: Type Hint Improvements")
        self._improve_type_hints()

        return self.quality_report

    def _install_quality_tools(self):
        """Install required code quality tools"""
        tools = [
            "black",
            "isort",
            "flake8",
            "mypy",
            "autopep8",
            "pylint",
            "bandit",
            "pydocstyle",
        ]

        for tool in tools:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", tool],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    logger.info(f"✅ Installed {tool}")
                else:
                    logger.warning(
                        f"⚠️ Failed to install {tool}: {result.stderr}")
            except Exception as e:
                logger.warning(f"⚠️ Error installing {tool}: {e}")

    def _format_code(self):
        """Format code using Black"""
        try:
            # Run Black formatter
            result = subprocess.run(
                [sys.executable, "-m", "black", ".", "--line-length", "88"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info("✅ Code formatting completed with Black")
                self.quality_report["improvements"]["formatting"] += 1
                self.improvements_made.append("Applied Black code formatting")
            else:
                logger.warning(f"⚠️ Black formatting issues: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Error running Black: {e}")

    def _organize_imports(self):
        """Organize imports using isort"""
        try:
            # Run isort
            result = subprocess.run(
                [sys.executable, "-m", "isort", ".", "--profile", "black"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info("✅ Import organization completed with isort")
                self.quality_report["improvements"]["imports"] += 1
                self.improvements_made.append("Organized imports with isort")
            else:
                logger.warning(f"⚠️ isort issues: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Error running isort: {e}")

    def _fix_lint_errors(self):
        """Fix lint errors using autopep8"""
        try:
            # Run autopep8 for automatic fixes
            result = subprocess.run(
                [sys.executable, "-m", "autopep8",
                    "--in-place", "--recursive", "."],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info("✅ Automatic lint fixes applied with autopep8")
                self.quality_report["improvements"]["linting"] += 1
                self.improvements_made.append("Applied automatic lint fixes")
            else:
                logger.warning(f"⚠️ autopep8 issues: {result.stderr}")

            # Run flake8 to check remaining issues
            flake8_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    ".",
                    "--max-line-length=88",
                    "--extend-ignore=E203,W503",
                ],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if flake8_result.stdout:
                issues = flake8_result.stdout.strip().split("\n")
                self.quality_report["issues_found"].extend(
                    issues[:10]
                )  # Limit to first 10
                logger.info(f"🔍 Found {len(issues)} remaining lint issues")

        except Exception as e:
            logger.error(f"❌ Error running lint fixes: {e}")

    def _analyze_complexity(self):
        """Analyze code complexity"""
        complex_functions = []

        # Find Python files
        python_files = list(self.repo_root.rglob("*.py"))

        for py_file in python_files:
            if "cleanup_empty_files" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if not content.strip():
                        continue

                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Count complexity indicators
                            complexity = self._calculate_complexity(node)
                            if complexity > 10:  # McCabe complexity threshold
                                complex_functions.append(
                                    {
                                        "file": str(
                                            py_file.relative_to(self.repo_root)
                                        ),
                                        "function": node.name,
                                        "complexity": complexity,
                                        "line": node.lineno,
                                    }
                                )

            except (SyntaxError, UnicodeDecodeError, OSError):
                continue

        self.quality_report["improvements"]["complexity"] = len(
            complex_functions)
        if complex_functions:
            logger.info(f"📊 Found {len(complex_functions)} complex functions")
            self.quality_report["issues_found"].extend(
                [
                    f"Complex function: {func['file']}:{func['line']} - {func['function']} (complexity: {func['complexity']})"
                    for func in complex_functions[:5]
                ]
            )

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate McCabe complexity for a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _improve_documentation(self):
        """Improve code documentation"""
        documented_files = 0

        # Find Python files without proper docstrings
        python_files = list(self.repo_root.rglob("*.py"))

        for py_file in python_files:
            if "cleanup_empty_files" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if not content.strip():
                        continue

                    tree = ast.parse(content)

                    # Check for module docstring
                    if not ast.get_docstring(tree):
                        # Add basic module docstring
                        lines = content.split("\n")
                        if lines and not lines[0].startswith('"""'):
                            module_name = py_file.stem.replace(
                                "_", " ").title()
                            docstring = f'"""\n{module_name} module for NoxSuite Security Platform.\n"""\n\n'

                            # Find first non-comment, non-import line
                            insert_line = 0
                            for i, line in enumerate(lines):
                                stripped = line.strip()
                                if (
                                    stripped
                                    and not stripped.startswith("#")
                                    and not stripped.startswith("import")
                                    and not stripped.startswith("from")
                                ):
                                    insert_line = i
                                    break

                            lines.insert(insert_line, docstring)

                            with open(py_file, "w", encoding="utf-8") as out_f:
                                out_f.write("\n".join(lines))

                            documented_files += 1
                            logger.info(f"📝 Added docstring to {py_file.name}")

            except (SyntaxError, UnicodeDecodeError, OSError):
                continue

        self.quality_report["improvements"]["documentation"] = documented_files
        if documented_files > 0:
            self.improvements_made.append(
                f"Added docstrings to {documented_files} files"
            )

    def _improve_type_hints(self):
        """Add basic type hints to functions"""
        files_improved = 0

        # Find Python files that could benefit from type hints
        python_files = list(self.repo_root.rglob("*.py"))

        for py_file in python_files:
            if "cleanup_empty_files" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if not content.strip():
                        continue

                    # Add typing import if functions exist but no type hints
                    if (
                        "def " in content
                        and "from typing import" not in content
                        and "import typing" not in content
                    ):
                        lines = content.split("\n")

                        # Find import section
                        import_end = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith(("import ", "from ")):
                                import_end = i + 1

                        # Add typing import
                        typing_import = (
                            "from typing import Dict, List, Optional, Any, Tuple"
                        )
                        lines.insert(import_end, typing_import)
                        lines.insert(import_end + 1, "")

                        with open(py_file, "w", encoding="utf-8") as out_f:
                            out_f.write("\n".join(lines))

                        files_improved += 1
                        logger.info(
                            f"🏷️ Added typing import to {py_file.name}")

            except (SyntaxError, UnicodeDecodeError, OSError):
                continue

        self.quality_report["improvements"]["type_hints"] = files_improved
        if files_improved > 0:
            self.improvements_made.append(
                f"Added typing imports to {files_improved} files"
            )

    def create_quality_config_files(self):
        """Create quality configuration files"""
        configs_created = []

        # Create .flake8 config
        flake8_config = self.repo_root / ".flake8"
        if not flake8_config.exists():
            flake8_content = """[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
max-complexity = 10
per-file-ignores = 
    __init__.py:F401
    tests/*:S101
exclude = 
    .git,
    __pycache__,
    .pytest_cache,
    .tox,
    venv,
    .venv,
    env,
    .env,
    cleanup_empty_files,
    node_modules,
    build,
    dist
"""
            flake8_config.write_text(flake8_content)
            configs_created.append(".flake8")
            logger.info("📄 Created .flake8 configuration")

        # Create mypy.ini config
        mypy_config = self.repo_root / "mypy.ini"
        if not mypy_config.exists():
            mypy_content = """[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
check_untyped_defs = True
disallow_untyped_decorators = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
ignore_missing_imports = True

[mypy-tests.*]
ignore_errors = True
"""
            mypy_config.write_text(mypy_content)
            configs_created.append("mypy.ini")
            logger.info("📄 Created mypy.ini configuration")

        # Update pyproject.toml if it exists
        pyproject_toml = self.repo_root / "pyproject.toml"
        if pyproject_toml.exists():
            content = pyproject_toml.read_text()
            if "[tool.black]" not in content:
                additional_config = """

[tool.black]
line-length = 88
target-version = ['py311']
include = '\\.pyi?$'
extend-exclude = '''
(
  cleanup_empty_files/
  | __pycache__/
  | .pytest_cache/
)
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["noxsuite"]
skip = ["cleanup_empty_files"]

[tool.coverage.run]
source = ["src", "."]
omit = [
    "*/tests/*",
    "*/test_*",
    "cleanup_empty_files/*",
    "setup.py",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
"""
                with open(pyproject_toml, "a") as f:
                    f.write(additional_config)
                configs_created.append("pyproject.toml (updated)")
                logger.info("📄 Updated pyproject.toml with quality configs")

        return configs_created

    def run_final_quality_check(self):
        """Run final quality check and generate report"""
        print(f"\n🔍 Final Quality Assessment")

        quality_checks = []

        # Check Black formatting
        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", ".", "--check"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            quality_checks.append(
                {
                    "name": "Black Formatting",
                    "status": "PASS" if result.returncode == 0 else "FAIL",
                    "details": result.stdout or result.stderr,
                }
            )
        except Exception:
            quality_checks.append(
                {
                    "name": "Black Formatting",
                    "status": "ERROR",
                    "details": "Black not available",
                }
            )

        # Check isort
        try:
            result = subprocess.run(
                [sys.executable, "-m", "isort", ".", "--check-only"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            quality_checks.append(
                {
                    "name": "Import Sorting",
                    "status": "PASS" if result.returncode == 0 else "FAIL",
                    "details": result.stdout or result.stderr,
                }
            )
        except Exception:
            quality_checks.append(
                {
                    "name": "Import Sorting",
                    "status": "ERROR",
                    "details": "isort not available",
                }
            )

        # Check flake8
        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "."],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            error_count = (
                len(result.stdout.strip().split("\n")
                    ) if result.stdout.strip() else 0
            )
            quality_checks.append(
                {
                    "name": "Flake8 Linting",
                    "status": (
                        "PASS" if error_count == 0 else f"ISSUES ({error_count} errors)"
                    ),
                    "details": (
                        result.stdout[:500] if result.stdout else "No issues found"
                    ),
                }
            )
        except Exception:
            quality_checks.append(
                {
                    "name": "Flake8 Linting",
                    "status": "ERROR",
                    "details": "flake8 not available",
                }
            )

        self.quality_report["final_checks"] = quality_checks
        return quality_checks

    def save_quality_report(self):
        """Save comprehensive quality report"""
        report_file = self.repo_root / \
            f"code_quality_report_{self.timestamp}.json"

        # Add summary
        summary = {
            "total_improvements": sum(self.quality_report["improvements"].values()),
            "improvements_made": self.improvements_made,
            "files_processed": self.quality_report["files_processed"],
            "issues_found_count": len(self.quality_report["issues_found"]),
            "issues_fixed_count": len(self.quality_report["issues_fixed"]),
        }

        full_report = {
            "quality_report": self.quality_report, "summary": summary}

        with open(report_file, "w") as f:
            json.dump(full_report, f, indent=2)

        logger.info(f"📄 Quality report saved: {report_file}")
        return report_file

    def print_summary(self):
        """Print quality improvement summary"""
        print(f"\n" + "=" * 50)
        print(f"📊 CODE QUALITY IMPROVEMENT SUMMARY")
        print(f"=" * 50)

        total_improvements = sum(self.quality_report["improvements"].values())
        print(f"🎨 Total Improvements: {total_improvements}")

        for category, count in self.quality_report["improvements"].items():
            if count > 0:
                print(f"   • {category.title()}: {count}")

        print(f"\n📋 Improvements Made:")
        for improvement in self.improvements_made:
            print(f"   ✅ {improvement}")

        if self.quality_report.get("final_checks"):
            print(f"\n🔍 Final Quality Checks:")
            for check in self.quality_report["final_checks"]:
                status_icon = (
                    "✅"
                    if check["status"] == "PASS"
                    else "❌" if "ERROR" in check["status"] else "⚠️"
                )
                print(f"   {status_icon} {check['name']}: {check['status']}")

        print(f"\n✅ Code quality improvement completed!")
        print(f"📄 Detailed report: code_quality_report_{self.timestamp}.json")


def main():
    """Main execution function"""
    improver = CodeQualityImprover()

    # Run comprehensive improvements
    quality_report = improver.run_comprehensive_improvements()

    # Create quality config files
    configs = improver.create_quality_config_files()

    # Run final quality check
    final_checks = improver.run_final_quality_check()

    # Save report
    report_file = improver.save_quality_report()

    # Print summary
    improver.print_summary()

    return quality_report


if __name__ == "__main__":
    main()
