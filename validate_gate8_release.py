#!/usr/bin/env python3
"""
Gate 8: Release Readiness Validation
============================
Comprehensive validation script for Gate 8 readiness, checking all aspects
of release preparation for the NoxSuite system.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Gate8Validation")


class Gate8Validator:
    """Gate 8 validation for release readiness"""

    def __init__(self, workspace_path=None):
        """Initialize the validator"""
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "score": 0,
            "max_score": 0,
            "blockers": [],
            "recommendations": [],
        }

    def run_all_checks(self, environments=None):
        """Run all validation checks for Gate 8"""
        environments = environments or ["production"]

        logger.info(
            f"🔍 Running Gate 8 validation for environments: {', '.join(environments)}"
        )

        # Run each check, collecting results
        self.check_git_status()
        self.check_version_consistency()

        for env in environments:
            self.check_deployment_config(env)

        self.check_documentation()
        self.check_tests()
        self.check_security()
        self.check_dependencies()

        # Calculate final score
        if self.results["max_score"] > 0:
            self.results["score"] = int(
                (self.results["score"] / self.results["max_score"]) * 100
            )

        # Determine critical blockers
        critical_blockers = [
            b for b in self.results["blockers"] if b.startswith("[CRITICAL]")
        ]

        # Print summary
        print("\n" + "=" * 60)
        print(f"Gate 8 Validation Summary: {self.results['score']}%")
        print("=" * 60)
        print(
            f"Checks passed: {sum(1 for c in self.results['checks'] if c[1])} of {len(self.results['checks'])}"
        )
        print(f"Blockers: {len(self.results['blockers'])}")
        print(f"Recommendations: {len(self.results['recommendations'])}")
        print("=" * 60)

        # Print blockers if any
        if self.results["blockers"]:
            print("\nBlockers:")
            for blocker in self.results["blockers"]:
                print(f"  • {blocker}")

        if critical_blockers:
            print(
                f"\n❌ {len(critical_blockers)} critical blockers must be resolved before release!"
            )

        return self.results, len(critical_blockers) == 0

    def add_check_result(self, name, passed, message, weight=10, critical=False):
        """Add a check result"""
        self.results["checks"].append((name, passed, message))
        self.results["max_score"] += weight
        if passed:
            self.results["score"] += weight
        else:
            prefix = "[CRITICAL] " if critical else ""
            self.results["blockers"].append(f"{prefix}{name}: {message}")

    def add_recommendation(self, recommendation):
        """Add a recommendation"""
        self.results["recommendations"].append(recommendation)

    def check_git_status(self):
        """Check if branch name is valid for release (i.e., main/master or release*)"""
        print("🔍 Checking Git branch status...")

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
            )
            branch = result.stdout.strip()

            # Check if branch is valid for release
            is_valid_branch = branch in ["main", "master"] or branch.startswith(
                "release"
            )

            # Get clean/dirty status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            is_clean = not status_result.stdout.strip()

            if is_valid_branch and is_clean:
                message = f"On release branch '{branch}' with clean working tree"
                self.add_check_result("Git Status", True, message, weight=10)
            elif not is_valid_branch:
                message = f"Not on a release branch (current: '{branch}')"
                self.add_check_result("Git Status", False, message, weight=10)
                self.add_recommendation(
                    f"Checkout a release branch (main, master, or release*) instead of '{branch}'"
                )
            elif not is_clean:
                message = f"Working tree has uncommitted changes"
                self.add_check_result("Git Status", False, message, weight=10)
                self.add_recommendation(
                    "Commit or stash all changes before release")

        except Exception as e:
            logger.error(f"Failed to check Git status: {e}")
            self.add_check_result(
                "Git Status", False, f"Error checking Git status: {e}", weight=10
            )
            self.add_recommendation(
                "Ensure Git is installed and repository is initialized"
            )

    def check_deployment_config(self, environment):
        """Check if deployment configuration exists for the specified environment"""
        print(
            f"🔍 Checking deployment configuration files for environment '{environment}'..."
        )

        # Look for environment-specific configuration files
        config_patterns = [
            f"config/{environment}.json",
            f"config/{environment}.js",
            f"config/{environment}.yaml",
            f"config/{environment}.yml",
            f".env.{environment}",
            f"deployment/{environment}.json",
            f"deployment/{environment}.yaml",
            f"deployment/{environment}.yml",
            f"docker-compose.{environment}.yml",
            f"k8s/{environment}",
        ]

        found_configs = []
        for pattern in config_patterns:
            config_file = self.workspace_path / pattern
            if config_file.exists():
                found_configs.append(
                    str(config_file.relative_to(self.workspace_path)))

        if found_configs:
            message = f"Found {len(found_configs)} deployment configuration files for '{environment}'"
            for config_file in found_configs:
                logger.info(
                    f"✅ Found deployment configuration for '{environment}' environment: {config_file}"
                )
            self.add_check_result(
                f"Deployment Config ({environment})", True, message, weight=15
            )
        else:
            message = (
                f"No deployment configuration found for '{environment}' environment"
            )
            self.add_check_result(
                f"Deployment Config ({environment})",
                False,
                message,
                weight=15,
                critical=True,
            )
            self.add_recommendation(
                f"Create deployment configuration for '{environment}' environment"
            )

    def check_documentation(self):
        """Check documentation completeness including README, API docs, and required files"""
        print("🔍 Checking documentation completeness...")
        root_path = self.workspace_path

        # Check README
        try:
            readme_file = find_file(
                root_path, ["README.md", "Readme.md", "readme.md"])

            if readme_file:
                with open(readme_file, "r") as f:
                    content = f.read()

                    # Check for basic sections (simple heuristic)
                    has_installation = (
                        re.search(
                            r"#.*install|\binstall\b|installation",
                            content,
                            re.IGNORECASE,
                        )
                        is not None
                    )
                    has_usage = (
                        re.search(
                            r"#.*usage|\busage\b|#.*example|\bexample\b",
                            content,
                            re.IGNORECASE,
                        )
                        is not None
                    )
                    has_api = (
                        re.search(r"#.*api|\bapi\b|endpoint",
                                  content, re.IGNORECASE)
                        is not None
                    )

                    sections_found = [
                        s
                        for s, found in [
                            ("Installation", has_installation),
                            ("Usage", has_usage),
                            ("API", has_api),
                        ]
                        if found
                    ]

                    if len(sections_found) >= 2:  # At least 2 key sections
                        self.add_check_result(
                            "README",
                            True,
                            f"README found with sections: {', '.join(sections_found)}",
                            weight=10,
                        )
                    else:
                        self.add_check_result(
                            "README", False, "README is missing key sections", weight=10
                        )
                        self.add_recommendation(
                            "Add Installation, Usage, and API sections to README"
                        )
            else:
                self.add_check_result(
                    "README", False, "README not found", weight=10)
                self.add_recommendation(
                    "Create a README.md file with project documentation"
                )

        except Exception as e:
            logger.error(f"Error checking README: {e}")
            self.add_check_result(
                "README", False, f"Error checking README: {e}", weight=10
            )

        # Check API documentation
        try:
            api_docs = find_file(
                root_path, ["api.md", "API.md", "docs/api.md", "docs/API.md"]
            )

            if api_docs:
                self.add_check_result(
                    "API Documentation",
                    True,
                    f"API documentation found: {os.path.basename(api_docs)}",
                    weight=10,
                )
            else:
                self.add_check_result(
                    "API Documentation", False, "API documentation not found", weight=10
                )
                self.add_recommendation(
                    "Create API documentation with endpoint specifications"
                )

        except Exception as e:
            logger.error(f"Error checking API docs: {e}")
            self.add_check_result(
                "API Documentation", False, f"Error checking API docs: {e}", weight=10
            )

        # Check CHANGELOG
        try:
            changelog = find_file(
                root_path, ["CHANGELOG.md", "CHANGELOG", "CHANGES.md"]
            )

            if changelog:
                self.add_check_result(
                    "Changelog",
                    True,
                    f"Changelog found: {os.path.basename(changelog)}",
                    weight=5,
                )
            else:
                self.add_check_result(
                    "Changelog", False, "Changelog not found", weight=5
                )
                self.add_recommendation(
                    "Create a CHANGELOG.md file to track version changes"
                )

        except Exception as e:
            logger.error(f"Error checking Changelog: {e}")
            self.add_check_result(
                "Changelog", False, f"Error checking Changelog: {e}", weight=5
            )

        # Check security and compliance docs
        print("🔍 Checking for required security and compliance documentation...")
        try:
            # Check for security policy
            security_file = find_file(
                root_path, ["SECURITY.md", "security.md", "docs/security.md"]
            )

            if security_file:
                self.add_check_result(
                    "Security Policy",
                    True,
                    f"Security policy found: {os.path.basename(security_file)}",
                    weight=10,
                )
            else:
                self.add_check_result(
                    "Security Policy", False, "Security policy not found", weight=10
                )
                self.add_recommendation(
                    "Create a SECURITY.md file with security reporting guidelines"
                )

            # Check for license
            license_file = find_file(
                root_path, ["LICENSE", "LICENSE.md", "license.md"])

            if license_file:
                self.add_check_result(
                    "License",
                    True,
                    f"License found: {os.path.basename(license_file)}",
                    weight=5,
                )
            else:
                self.add_check_result(
                    "License", False, "License not found", weight=5)
                self.add_recommendation("Add a LICENSE file to the project")

        except Exception as e:
            logger.error(f"Error checking security docs: {e}")
            self.add_check_result(
                "Security Documentation",
                False,
                f"Error checking security docs: {e}",
                weight=10,
            )

    def check_tests(self):
        """Check if tests are passing and coverage is acceptable"""
        print("🔍 Checking for test coverage and completion status of test suite...")
        root_path = self.workspace_path

        # Check test files
        try:
            test_dirs = ["tests", "test", "__tests__"]
            test_files = []

            for test_dir in test_dirs:
                test_path = root_path / test_dir
                if test_path.exists() and test_path.is_dir():
                    test_files.extend(
                        [str(f)
                         for f in test_path.glob("**/*.py") if f.is_file()]
                    )
                    test_files.extend(
                        [str(f)
                         for f in test_path.glob("**/*.js") if f.is_file()]
                    )
                    test_files.extend(
                        [str(f)
                         for f in test_path.glob("**/*.ts") if f.is_file()]
                    )

            # This is a simplified example - in a real implementation, would parse coverage files
            coverage_files = [
                f
                for f in os.listdir(root_path)
                if f.endswith(".coverage") or f.endswith("coverage.xml")
            ]

            if test_files:
                self.add_check_result(
                    "Test Suite", True, f"Found {len(test_files)} test files", weight=10
                )

                if coverage_files:
                    self.add_check_result(
                        "Test Coverage", True, "Coverage reports found", weight=10
                    )
                else:
                    self.add_check_result(
                        "Test Coverage", False, "No coverage reports found", weight=10
                    )
                    self.add_recommendation(
                        "Generate test coverage reports before release"
                    )
            else:
                self.add_check_result(
                    "Test Suite", False, "No test files found", weight=10, critical=True
                )
                self.add_check_result(
                    "Test Coverage",
                    False,
                    "No tests to measure coverage",
                    weight=10,
                    critical=True,
                )
                self.add_recommendation(
                    "Create comprehensive test suite before release"
                )

        except Exception as e:
            logger.error(f"Error checking tests: {e}")
            self.add_check_result(
                "Test Suite", False, f"Error checking tests: {e}", weight=10
            )

    def check_version_consistency(self):
        """Check if version is consistent across different files"""
        print("🔍 Checking version consistency...")
        root_path = self.workspace_path

        try:
            version_files = {
                "setup.py": r"version=['\"]([^'\"]+)['\"]",
                "package.json": None,  # Special handling for JSON
                "__version__.py": r"__version__\s*=\s*['\"]([^'\"]+)['\"]",
                "VERSION": None,  # Read raw content
                "version.py": r"VERSION\s*=\s*['\"]([^'\"]+)['\"]",
            }

            versions = {}

            for filename, pattern in version_files.items():
                filepath = root_path / filename
                if filepath.exists():
                    if filename == "package.json":
                        try:
                            with open(filepath, "r") as f:
                                data = json.load(f)
                                if "version" in data:
                                    versions[filename] = data["version"]
                        except json.JSONDecodeError:
                            logger.error(f"Error parsing {filename}")
                    elif pattern:
                        with open(filepath, "r") as f:
                            content = f.read()
                            match = re.search(pattern, content)
                            if match:
                                versions[filename] = match.group(1)
                    else:
                        with open(filepath, "r") as f:
                            content = f.read().strip()
                            versions[filename] = content

            if versions:
                unique_versions = set(versions.values())
                if len(unique_versions) == 1:
                    version = list(unique_versions)[0]
                    self.add_check_result(
                        "Version Consistency",
                        True,
                        f"Consistent version ({version}) across {len(versions)} files",
                        weight=10,
                    )
                else:
                    msg = "Inconsistent versions: " + ", ".join(
                        f"{f}={v}" for f, v in versions.items()
                    )
                    self.add_check_result(
                        "Version Consistency", False, msg, weight=10, critical=True
                    )
                    self.add_recommendation(
                        "Ensure version is consistent across all files"
                    )
            else:
                self.add_check_result(
                    "Version Consistency",
                    False,
                    "No version information found",
                    weight=10,
                )
                self.add_recommendation(
                    "Add version information to setup.py or package.json"
                )

        except Exception as e:
            logger.error(f"Error checking version consistency: {e}")
            self.add_check_result(
                "Version Consistency",
                False,
                f"Error checking version consistency: {e}",
                weight=10,
            )

    def check_security(self):
        """Check security issues and vulnerabilities"""
        print("🔍 Checking for security issues...")

        # Check if there are open security issues that would block a release
        try:
            security_blockers = []

            # In a real implementation, this would query a security tracker or vulnerability database
            security_scan_files = find_files(
                self.workspace_path, [
                    "security_scan.json", "security_audit.json"]
            )

            if security_scan_files and os.path.exists(security_scan_files[0]):
                with open(security_scan_files[0], "r") as f:
                    try:
                        scan_data = json.load(f)

                        # Example structure: {"vulnerabilities": [{"severity": "high", "description": "..."}]}
                        if "vulnerabilities" in scan_data:
                            high_vulns = [
                                v
                                for v in scan_data["vulnerabilities"]
                                if v.get("severity", "").lower() in ["critical", "high"]
                            ]

                            if high_vulns:
                                security_blockers = [
                                    v.get("description",
                                          "Unnamed vulnerability")
                                    for v in high_vulns[:3]
                                ]
                                if len(high_vulns) > 3:
                                    security_blockers.append(
                                        f"...and {len(high_vulns) - 3} more"
                                    )
                    except json.JSONDecodeError:
                        security_blockers = [
                            "Error parsing security scan results"]

            if security_blockers:
                self.add_check_result(
                    "Security Issues",
                    False,
                    f"Found {len(security_blockers)} critical security issues",
                    weight=15,
                    critical=True,
                )
                for issue in security_blockers:
                    self.add_recommendation(f"Fix security issue: {issue}")
            else:
                self.add_check_result(
                    "Security Issues",
                    True,
                    "No critical security issues found",
                    weight=15,
                )
        except Exception as e:
            logger.error(f"Error checking security issues: {e}")
            self.add_check_result(
                "Security Issues",
                False,
                f"Error checking security issues: {e}",
                weight=15,
            )

    def check_dependencies(self):
        """Check if all dependencies are properly pinned and there are no known vulnerabilities"""
        print("🔍 Checking dependencies...")

        try:
            # Check for requirements.txt and pyproject.toml with version pinning
            requirements_file = find_file(
                self.workspace_path, ["requirements.txt", "pyproject.toml"]
            )
            package_json = self.workspace_path / "package.json"

            deps_pinned = False
            deps_message = "No dependency files found"

            if requirements_file:
                # Check if versions are pinned
                with open(requirements_file, "r") as f:
                    content = f.read()

                    # Check for pinned versions (==, >=, etc.)
                    if re.search(r"[a-zA-Z0-9_-]+(==|>=|<=|~=|!=)[0-9]", content):
                        deps_pinned = True
                        deps_message = f"Dependencies pinned in {os.path.basename(requirements_file)}"

            elif package_json.exists():
                # Check if versions are pinned in package.json
                with open(package_json, "r") as f:
                    try:
                        data = json.load(f)
                        has_deps = (
                            "dependencies" in data and len(
                                data["dependencies"]) > 0
                        )
                        has_dev_deps = (
                            "devDependencies" in data
                            and len(data["devDependencies"]) > 0
                        )

                        if has_deps or has_dev_deps:
                            # Check if versions are pinned (not *)
                            all_deps = {}
                            if has_deps:
                                all_deps.update(data["dependencies"])
                            if has_dev_deps:
                                all_deps.update(data["devDependencies"])

                            # If no deps have wildcard (*) or caret (^), consider them pinned
                            if not any(
                                v == "*" or v.startswith("^") for v in all_deps.values()
                            ):
                                deps_pinned = True
                                deps_message = "Dependencies pinned in package.json"
                            else:
                                deps_message = (
                                    "Some dependencies not pinned in package.json"
                                )
                    except json.JSONDecodeError:
                        deps_message = "Error parsing package.json"

            self.add_check_result(
                "Pinned Dependencies", deps_pinned, deps_message, weight=10
            )

            if not deps_pinned:
                self.add_recommendation(
                    "Pin all dependencies to specific versions before release"
                )

        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            self.add_check_result(
                "Pinned Dependencies",
                False,
                f"Error checking dependencies: {e}",
                weight=10,
            )

    def get_version(self):
        """Try to get the current version of the project"""
        try:
            version_files = {
                "setup.py": r"version=['\"]([^'\"]+)['\"]",
                "package.json": None,  # Special handling for JSON
                "__version__.py": r"__version__\s*=\s*['\"]([^'\"]+)['\"]",
                "VERSION": None,  # Read raw content
                "version.py": r"VERSION\s*=\s*['\"]([^'\"]+)['\"]",
            }

            for filename, pattern in version_files.items():
                filepath = self.workspace_path / filename
                if filepath.exists():
                    if filename == "package.json":
                        try:
                            with open(filepath, "r") as f:
                                data = json.load(f)
                                if "version" in data:
                                    return data["version"]
                        except:
                            pass
                    elif pattern:
                        with open(filepath, "r") as f:
                            content = f.read()
                            match = re.search(pattern, content)
                            if match:
                                return match.group(1)
                    else:
                        with open(filepath, "r") as f:
                            content = f.read().strip()
                            if re.match(r"^\d+\.\d+\.\d+", content):
                                return content
        except:
            pass

        return None

    def generate_report(self, output_file=None):
        """Generate a comprehensive release readiness report based on all checks"""
        version = self.get_version() or "Unknown"
        score = self.results["score"]
        max_score = self.results["max_score"]
        score_percent = (score / max_score * 100) if max_score > 0 else 0
        passed = score_percent >= 80 and not any(
            b.startswith("[CRITICAL]") for b in self.results["blockers"]
        )

        # Build summary
        if passed:
            summary = "✅ **The system has passed all critical release readiness checks** and is ready for deployment.\n\n"
        else:
            summary = "❌ **The system has NOT passed the release readiness requirements.** Critical issues must be addressed before deployment.\n\n"

        if self.results["blockers"]:
            critical_count = sum(
                1 for b in self.results["blockers"] if b.startswith("[CRITICAL]")
            )
            if critical_count > 0:
                summary += f"There are **{critical_count} critical blockers** that must be resolved before release. "

            summary += f"Additionally, there are {len(self.results['blockers']) - critical_count} non-critical issues that should be addressed."

        # Try to read the report template
        report_template_path = self.workspace_path / "gate8_release_readiness_report.md"
        try:
            with open(report_template_path, "r") as f:
                report_template = f.read()

            # Replace placeholders
            report_content = report_template.replace(
                "<!-- DATE -->", datetime.now().strftime("%Y-%m-%d")
            )
            report_content = report_content.replace(
                "<!-- VERSION -->", version)
            report_content = report_content.replace(
                "<!-- AUDITOR -->", os.environ.get("USER", "automated")
            )

            # Add scores and status
            if max_score > 0:
                report_content = report_content.replace(
                    "<!-- SCORE -->", f"{score}/{max_score} ({score_percent:.1f}%)"
                )
                report_content = report_content.replace(
                    "<!-- STATUS -->", "PASSED" if passed else "FAILED"
                )
                report_content = report_content.replace(
                    "<!-- SUMMARY -->", summary)

            # Add check results
            checks = self.results["checks"]
            checks_content = "\n".join(
                [
                    f"- {'✅' if check[1] else '❌'} **{check[0]}**: {check[2]}"
                    for check in checks
                ]
            )
            report_content = report_content.replace(
                "<!-- CHECKS -->", checks_content)

            # Add blockers
            blockers = self.results["blockers"]
            if blockers:
                blockers_content = "\n".join(
                    [f"- ❌ {blocker}" for blocker in blockers]
                )
                report_content = report_content.replace(
                    "<!-- BLOCKERS -->", blockers_content
                )
            else:
                report_content = report_content.replace(
                    "<!-- BLOCKERS -->", "None! ✅")

            # Add recommendations
            recommendations = self.results["recommendations"]
            if recommendations:
                recommendations_content = "\n".join(
                    [f"- 📝 {rec}" for rec in recommendations]
                )
                report_content = report_content.replace(
                    "<!-- RECOMMENDATIONS -->", recommendations_content
                )
            else:
                report_content = report_content.replace(
                    "<!-- RECOMMENDATIONS -->", "None! ✅"
                )

            # Add test-specific details
            test_statuses = {}
            test_details = {}

            for check_name, check_passed, check_message in checks:
                if "Version" in check_name:
                    test_statuses["VERSION"] = "PASSED" if check_passed else "FAILED"
                    test_details["VERSION"] = check_message
                elif "Deployment" in check_name:
                    test_statuses["DEPLOYMENT"] = "PASSED" if check_passed else "FAILED"
                    test_details["DEPLOYMENT"] = check_message
                elif (
                    "Documentation" in check_name
                    or "README" in check_name
                    or "API Doc" in check_name
                ):
                    test_statuses["DOCUMENTATION"] = (
                        "PASSED" if check_passed else "FAILED"
                    )
                    test_details["DOCUMENTATION"] = (
                        test_details.get("DOCUMENTATION", "") +
                        f"- {check_message}\n"
                    )
                elif "Security" in check_name:
                    test_statuses["SECURITY"] = "PASSED" if check_passed else "FAILED"
                    test_details["SECURITY"] = check_message
                elif "Test" in check_name or "Coverage" in check_name:
                    test_statuses["PERFORMANCE"] = (
                        "PASSED" if check_passed else "FAILED"
                    )
                    test_details["PERFORMANCE"] = (
                        test_details.get("PERFORMANCE", "") +
                        f"- {check_message}\n"
                    )

            # Replace test section placeholders
            for section in [
                "VERSION",
                "DEPLOYMENT",
                "DOCUMENTATION",
                "SECURITY",
                "PERFORMANCE",
            ]:
                status = test_statuses.get(section, "UNKNOWN")
                details = test_details.get(section, "No data available")

                report_content = report_content.replace(
                    f"<!-- {section}_STATUS -->", status
                )
                report_content = report_content.replace(
                    f"<!-- {section}_DETAILS -->", details
                )

            # Add conclusion
            if passed:
                conclusion = "Based on the comprehensive evaluation, the system meets the release readiness criteria and is approved for production deployment. All critical checks have passed, and the documentation, security, and testing requirements have been satisfied."
            else:
                conclusion = "Based on the evaluation, the system does not currently meet the release readiness criteria. The issues documented in this report must be addressed before proceeding with production deployment."

            report_content = report_content.replace(
                "<!-- CONCLUSION -->", conclusion)

            # Write the report
            if output_file:
                with open(output_file, "w") as f:
                    f.write(report_content)
                logger.info(f"✅ Report generated: {output_file}")

            return report_content

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None


def find_file(root_path, file_names):
    """Find the first file that matches any of the given names"""
    for name in file_names:
        file_path = os.path.join(root_path, name)
        if os.path.exists(file_path):
            return file_path
    return None


def find_files(root_path, file_names):
    """Find all files that match any of the given names"""
    found_files = []
    for name in file_names:
        file_path = os.path.join(root_path, name)
        if os.path.exists(file_path):
            found_files.append(file_path)
    return found_files


def main():
    """Main function"""
    # Parse command line arguments to determine environments to validate
    parser = argparse.ArgumentParser(
        description="Gate 8: Release Readiness Validation")
    parser.add_argument(
        "--env",
        nargs="+",
        default=["production"],
        help="Environments to validate (e.g., production staging)",
    )
    parser.add_argument("--workspace", default=None,
                        help="Path to workspace directory")
    parser.add_argument(
        "--report", action="store_true", help="Generate a comprehensive report"
    )
    parser.add_argument("--output", default=None,
                        help="Output file for report")
    parser.add_argument(
        "--detailed", action="store_true", help="Include detailed output"
    )
    parser.add_argument("--skip-git", action="store_true",
                        help="Skip Git checks")
    parser.add_argument(
        "--threshold", type=int, default=80, help="Passing threshold percentage"
    )
    parser.add_argument(
        "--publish", action="store_true", help="Trigger publish if validation passes"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = Gate8Validator(args.workspace)

    # Run checks based on command line args
    environments = args.env
    logger.info(
        f"🚀 Running Gate 8 validation for environments: {', '.join(environments)}"
    )

    try:
        if args.skip_git:
            logger.info("Skipping Git checks...")
        else:
            validator.check_git_status()

        # Always check version consistency
        validator.check_version_consistency()

        # Check deployment configs for each environment
        for env in environments:
            validator.check_deployment_config(env)

        # Run other checks
        validator.check_documentation()
        validator.check_tests()
        validator.check_security()
        validator.check_dependencies()

        # Calculate final results
        results, passed_critical = validator.run_all_checks(environments)
        passing_threshold = args.threshold
        score_percent = results["score"]
        critical_blockers = [
            b for b in results["blockers"] if b.startswith("[CRITICAL]")
        ]

        # Generate report if requested
        if args.report:
            report_output = (
                args.output
                or f"gate8_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
            report = validator.generate_report(report_output)
            if report and args.detailed:
                print("\nReport Preview:\n")
                print(report[:500] + "...\n")

        # Handle publish request if validation passes
        if (
            args.publish
            and score_percent >= passing_threshold
            and not critical_blockers
        ):
            logger.info("✅ Validation passed! Triggering publish...")
            # In a real implementation, would trigger publish workflow
            # For demo purposes, just print success
            print("🚀 Publishing triggered!")

        elif args.publish:  # Publishing was requested but checks failed
            logger.error("❌ Validation failed! Publishing skipped.")
            print(
                f"❌ Publishing skipped due to failing checks ({score_percent:.1f}% < {passing_threshold}%)"
            )
            if critical_blockers:
                print("   Critical blockers must be resolved:")
                for blocker in critical_blockers[:3]:
                    print(f"   - {blocker}")

        return 0 if score_percent >= passing_threshold and not critical_blockers else 1

    except Exception as e:
        logger.error(f"Error during validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
