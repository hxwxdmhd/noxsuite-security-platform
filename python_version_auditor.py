#!/usr/bin/env python3
"""
Python Version Compatibility Auditor
====================================
Comprehensive cross-version Python compatibility checker and standardizer
"""

from datetime import datetime
from pathlib import Path
import json
import os
import re
import sys

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PythonVersionAuditor:
    """Cross-version Python compatibility auditor"""

    def __init__(self):
        self.baseline_version = "3.12.10"
        self.supported_versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
        self.future_target = "3.13"

        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "runtime_version": sys.version,
            "baseline_version": self.baseline_version,
            "files_scanned": 0,
            "version_references": [],
            "deprecated_imports": [],
            "compatibility_issues": [],
            "fixes_applied": [],
        }

    def scan_version_references(self):
        """Scan all files for Python version references"""
        version_patterns = [
            r"python.*?(\d+\.\d+(?:\.\d+)?)",
            r'version.*?["\'](\d+\.\d+(?:\.\d+)?)["\']',
            r'python_requires.*?["\']>=?(\d+\.\d+(?:\.\d+)?)["\']',
            r"FROM python:(\d+\.\d+(?:\.\d+)?)",
            r"py(\d)(\d+)",
            r"Programming Language :: Python :: (\d+\.\d+)",
        ]

        exclude_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            ".venv",
            "archived",
        }
        include_extensions = {
            ".py",
            ".txt",
            ".md",
            ".yml",
            ".yaml",
            ".json",
            ".cfg",
            ".ini",
            ".dockerfile",
        }

        for root, dirs, files in os.walk("."):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = Path(root) / file

                # Skip if not relevant extension
                if (
                    file_path.suffix.lower() not in include_extensions
                    and not file_path.name.lower().startswith("dockerfile")
                ):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    self.audit_results["files_scanned"] += 1

                    for pattern in version_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            version = (
                                match.group(1)
                                if len(match.groups()) == 1
                                else f"{match.group(1)}.{match.group(2)}"
                            )

                            self.audit_results["version_references"].append(
                                {
                                    "file": str(file_path),
                                    "line_context": content.split("\n")[
                                        content[: match.start()].count("\n")
                                    ],
                                    "version_found": version,
                                    "needs_update": version != self.baseline_version
                                    and not version.startswith("3.12"),
                                }
                            )

                except Exception as e:
                    logger.warning(f"Could not scan {file_path}: {e}")

    def check_deprecated_imports(self):
        """Check for deprecated imports that may break in future Python versions"""
        deprecated_patterns = {
            "collections": r"from collections import (?!abc)",
            "imp": r"import imp\b",
            "asyncio.coroutine": r"@asyncio\.coroutine",
            "deprecated_ssl": r"ssl\.PROTOCOL_TLS\b",
            "deprecated_distutils": r"from distutils",
        }

        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in {
                ".git", "__pycache__", "archived"}]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = Path(root) / file

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for issue_type, pattern in deprecated_patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1

                            self.audit_results["deprecated_imports"].append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "issue_type": issue_type,
                                    "context": content.split("\n")[line_num - 1],
                                    "recommendation": self.get_fix_recommendation(
                                        issue_type
                                    ),
                                }
                            )

                except Exception as e:
                    logger.warning(f"Could not check {file_path}: {e}")

    def get_fix_recommendation(self, issue_type):
        """Get fix recommendations for deprecated imports"""
        recommendations = {
            "collections": "Use 'from collections.abc import' for abstract base classes",
            "imp": "Replace with importlib",
            "asyncio.coroutine": "Use async/await syntax instead",
            "deprecated_ssl": "Use ssl.PROTOCOL_TLS_CLIENT or ssl.PROTOCOL_TLS_SERVER",
            "deprecated_distutils": "Replace with setuptools or packaging",
        }
        return recommendations.get(issue_type, "Check Python migration guide")

    def fix_docker_versions(self):
        """Fix Docker files to use Python 3.12.10"""
        docker_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if "dockerfile" in file.lower() or file.lower().startswith(
                    "dockerfile"
                ):
                    docker_files.append(Path(root) / file)

        for docker_file in docker_files:
            try:
                with open(docker_file, "r") as f:
                    content = f.read()

                # Update Python base image versions
                updated_content = re.sub(
                    r"FROM python:(\d+\.\d+(?:\.\d+)?)-slim",
                    "FROM python:3.12-slim",
                    content,
                )

                if updated_content != content:
                    with open(docker_file, "w") as f:
                        f.write(updated_content)

                    self.audit_results["fixes_applied"].append(
                        {
                            "file": str(docker_file),
                            "action": "Updated Python base image to 3.12-slim",
                        }
                    )
                    logger.info(f"✅ Updated Docker file: {docker_file}")

            except Exception as e:
                logger.error(f"Failed to update {docker_file}: {e}")

    def fix_compose_versions(self):
        """Fix docker-compose version declarations"""
        compose_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if "compose" in file.lower() and file.endswith((".yml", ".yaml")):
                    compose_files.append(Path(root) / file)

        for compose_file in compose_files:
            try:
                with open(compose_file, "r") as f:
                    content = f.read()

                # Update compose version to 3.8 (stable)
                updated_content = re.sub(
                    r'version:\s*["\'](\d+\.\d+)["\']', 'version: "3.8"', content
                )

                if updated_content != content:
                    with open(compose_file, "w") as f:
                        f.write(updated_content)

                    self.audit_results["fixes_applied"].append(
                        {
                            "file": str(compose_file),
                            "action": "Updated docker-compose version to 3.8",
                        }
                    )
                    logger.info(f"✅ Updated compose file: {compose_file}")

            except Exception as e:
                logger.error(f"Failed to update {compose_file}: {e}")

    def run_comprehensive_audit(self):
        """Run complete Python version compatibility audit"""
        logger.info("🐍 Starting Python version compatibility audit...")

        # Current runtime check
        logger.info(f"Current Python runtime: {sys.version}")

        # Scan for version references
        self.scan_version_references()

        # Check deprecated imports
        self.check_deprecated_imports()

        # Apply fixes
        self.fix_docker_versions()
        self.fix_compose_versions()

        # Save audit report
        with open("python_version_audit_report.json", "w") as f:
            json.dump(self.audit_results, f, indent=2)

        # Generate summary
        total_issues = len(self.audit_results["version_references"]) + len(
            self.audit_results["deprecated_imports"]
        )
        needs_update = sum(
            1 for ref in self.audit_results["version_references"] if ref["needs_update"]
        )

        logger.info("✅ Python version audit completed")

        print("\n🐍 PYTHON VERSION COMPATIBILITY AUDIT")
        print(f"✅ Runtime version: {sys.version.split()[0]}")
        print(f"✅ Baseline target: {self.baseline_version}")
        print(f"✅ Files scanned: {self.audit_results['files_scanned']}")
        print(
            f"✅ Version references found: {len(self.audit_results['version_references'])}"
        )
        print(f"⚠️  Outdated references: {needs_update}")
        print(
            f"⚠️  Deprecated imports: {len(self.audit_results['deprecated_imports'])}")
        print(f"✅ Fixes applied: {len(self.audit_results['fixes_applied'])}")

        return self.audit_results


if __name__ == "__main__":
    auditor = PythonVersionAuditor()
    results = auditor.run_comprehensive_audit()

    # Calculate compatibility score
    total_refs = len(results["version_references"])
    outdated_refs = sum(
        1 for ref in results["version_references"] if ref["needs_update"]
    )

    if total_refs > 0:
        compatibility_score = ((total_refs - outdated_refs) / total_refs) * 100
        print(f"\n🎯 COMPATIBILITY SCORE: {compatibility_score:.1f}%")
    else:
        print(f"\n🎯 COMPATIBILITY SCORE: 100% (no version references found)")
