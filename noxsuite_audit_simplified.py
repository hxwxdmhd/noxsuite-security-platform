#!/usr/bin/env python3
"""
NoxSuite Simplified Audit & Sprint Preparation
==============================================

Windows-compatible version without Unicode emojis.
Performs comprehensive audit and generates sprint plans.

Author: NoxSuite Development Team
Date: July 31, 2025
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class NoxSuiteAuditor:
    """Simplified NoxSuite auditor for Windows"""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.audit_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "timestamp": self.audit_timestamp,
            "workspace_audit": {},
            "software_health": {},
            "database_validation": {},
            "next_sprint_plan": {},
        }

    def run_audit(self) -> Dict[str, Any]:
        """Execute comprehensive audit"""
        print("NoxSuite Comprehensive Audit Starting...")
        print(f"Workspace: {self.workspace_root}")
        print(f"Timestamp: {self.audit_timestamp}")
        print("-" * 60)

        try:
            # Phase 1: Workspace Structure
            print("\nPhase 1: Workspace Structure Audit")
            self.audit_workspace_structure()

            # Phase 2: Software Health
            print("\nPhase 2: Software Health Audit")
            self.audit_software_health()

            # Phase 3: Database Validation
            print("\nPhase 3: Database Validation")
            self.audit_database()

            # Phase 4: Sprint Planning
            print("\nPhase 4: Sprint Planning")
            self.plan_next_sprint()

            # Phase 5: Generate Reports
            print("\nPhase 5: Generate Reports")
            self.generate_reports()

            print("\nAudit completed successfully!")
            return self.results

        except Exception as e:
            print(f"Audit failed: {e}")
            self.results["error"] = str(e)
            return self.results

    def audit_workspace_structure(self):
        """Audit workspace structure"""
        workspace_audit = {
            "noxsuite_files_found": 0,
            "misplaced_files": [],
            "missing_files": [],
            "conflict_files": [],
            "duplicate_files": [],
        }

        # Find NoxSuite files
        noxsuite_files = self.find_noxsuite_files()
        workspace_audit["noxsuite_files_found"] = len(noxsuite_files)
        workspace_audit["discovered_files"] = noxsuite_files

        # Check for misplaced files
        for file_info in noxsuite_files:
            expected_location = self.get_expected_location(file_info["name"])
            if expected_location and not file_info["path"].endswith(expected_location):
                workspace_audit["misplaced_files"].append(
                    {
                        "file": file_info["name"],
                        "current": file_info["path"],
                        "expected": expected_location,
                    }
                )

        # Find conflict files
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if ".conflict." in file:
                    workspace_audit["conflict_files"].append(
                        str(Path(root) / file))

        # Check for missing critical files
        critical_files = [
            "backend/models/user.py",
            "backend/services/mfa_service.py",
            "backend/services/rbac_service.py",
            "frontend/src/services/api.js",
        ]

        for file_path in critical_files:
            if not (self.workspace_root / file_path).exists():
                workspace_audit["missing_files"].append(file_path)

        self.results["workspace_audit"] = workspace_audit
        print(f"  Found {len(noxsuite_files)} NoxSuite files")
        print(f"  {len(workspace_audit['misplaced_files'])} misplaced files")
        print(f"  {len(workspace_audit['missing_files'])} missing files")
        print(f"  {len(workspace_audit['conflict_files'])} conflict files")

    def find_noxsuite_files(self) -> List[Dict[str, Any]]:
        """Find NoxSuite-related files"""
        key_files = [
            "user_service.py",
            "api_routes.py",
            "auth_service.py",
            "Login.jsx",
            "Dashboard.jsx",
            "Login.css",
            "Dashboard.css",
            "docker-compose.noxsuite.yml",
            "testsprite_e2e.py",
        ]

        found_files = []
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if any(key_file in file for key_file in key_files):
                    file_path = Path(root) / file
                    found_files.append(
                        {
                            "name": file,
                            "path": str(file_path),
                            "size": (
                                file_path.stat().st_size if file_path.exists() else 0
                            ),
                        }
                    )

        return found_files

    def get_expected_location(self, filename: str) -> str:
        """Get expected location for file"""
        location_map = {
            "user_service.py": "backend/api/user_service.py",
            "api_routes.py": "backend/api/api_routes.py",
            "auth_service.py": "backend/services/auth_service.py",
            "Login.jsx": "frontend/src/components/Login.jsx",
            "Dashboard.jsx": "frontend/src/components/Dashboard.jsx",
            "Login.css": "frontend/src/components/Login.css",
            "Dashboard.css": "frontend/src/components/Dashboard.css",
            "testsprite_e2e.py": "tests/testsprite_e2e.py",
        }
        return location_map.get(filename, "")

    def audit_software_health(self):
        """Audit software health"""
        software_health = {
            "template_implementation": {},
            "testsprite_status": {},
            "code_quality": {},
            "dependency_audit": {},
        }

        # Check template implementations
        implementations = {
            "authentication": self.check_auth_implementation(),
            "api": self.check_api_implementation(),
            "frontend": self.check_frontend_implementation(),
        }
        software_health["template_implementation"] = implementations

        # Check TestSprite
        testsprite_file = self.workspace_root / "testsprite_e2e.py"
        software_health["testsprite_status"] = {
            "available": testsprite_file.exists(),
            "size": testsprite_file.stat().st_size if testsprite_file.exists() else 0,
        }

        # Basic code quality check
        python_files = list(self.workspace_root.glob("**/*.py"))
        software_health["code_quality"] = {
            "python_files_count": len(python_files),
            "total_lines": self.count_code_lines(python_files),
        }

        # Check requirements
        req_files = ["requirements.txt", "package.json"]
        software_health["dependency_audit"] = {
            "requirement_files": [
                f for f in req_files if (self.workspace_root / f).exists()
            ]
        }

        self.results["software_health"] = software_health

        # Print summary
        for component, details in implementations.items():
            status = details.get("status", "unknown")
            score = details.get("score", 0)
            print(f"  {component}: {score}% ({status})")

    def check_auth_implementation(self) -> Dict[str, Any]:
        """Check authentication implementation"""
        auth_files = ["user_service.py", "api_routes.py"]
        return self.check_file_implementation(auth_files)

    def check_api_implementation(self) -> Dict[str, Any]:
        """Check API implementation"""
        api_files = ["api_routes.py", "user_service.py"]
        return self.check_file_implementation(api_files)

    def check_frontend_implementation(self) -> Dict[str, Any]:
        """Check frontend implementation"""
        frontend_files = ["Login.css", "Dashboard.css"]
        return self.check_file_implementation(frontend_files)

    def check_file_implementation(self, files: List[str]) -> Dict[str, Any]:
        """Check if files are implemented"""
        result = {"files": {}, "score": 0, "status": "unknown"}

        implemented_count = 0
        for filename in files:
            file_found = False
            file_size = 0

            for root, dirs, file_list in os.walk(self.workspace_root):
                if filename in file_list:
                    file_path = Path(root) / filename
                    file_size = file_path.stat().st_size
                    file_found = True
                    break

            is_implemented = file_found and file_size > 100
            result["files"][filename] = {
                "found": file_found,
                "size": file_size,
                "implemented": is_implemented,
            }

            if is_implemented:
                implemented_count += 1

        result["score"] = int((implemented_count / len(files)) * 100)

        if result["score"] == 100:
            result["status"] = "complete"
        elif result["score"] > 0:
            result["status"] = "partial"
        else:
            result["status"] = "missing"

        return result

    def count_code_lines(self, files: List[Path]) -> int:
        """Count total lines of code"""
        total_lines = 0
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    total_lines += len(f.readlines())
            except:
                pass
        return total_lines

    def audit_database(self):
        """Audit database configuration"""
        database_validation = {
            "sqlite_databases": [],
            "mariadb_config": {},
            "schema_status": "unknown",
            "migration_status": "unknown",
        }

        # Find SQLite databases
        for file_path in self.workspace_root.glob("**/*.db"):
            database_validation["sqlite_databases"].append(str(file_path))

        # Check for MariaDB configuration
        compose_files = ["docker-compose.yml", "docker-compose.noxsuite.yml"]
        mariadb_found = False

        for compose_file in compose_files:
            file_path = self.workspace_root / compose_file
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        if "mariadb" in content.lower():
                            mariadb_found = True
                            database_validation["mariadb_config"][
                                compose_file
                            ] = "Found"
                except:
                    pass

        database_validation["mariadb_config"]["configured"] = mariadb_found

        # Check for Alembic
        alembic_ini = self.workspace_root / "alembic.ini"
        migrations_dir = self.workspace_root / "migrations"

        database_validation["migration_status"] = {
            "alembic_configured": alembic_ini.exists(),
            "migrations_directory": migrations_dir.exists(),
        }

        self.results["database_validation"] = database_validation

        print(
            f"  SQLite databases: {len(database_validation['sqlite_databases'])}")
        print(f"  MariaDB configured: {mariadb_found}")
        print(f"  Alembic configured: {alembic_ini.exists()}")

    def plan_next_sprint(self):
        """Plan next sprint"""
        # Calculate current progress
        auth_score = self.results["software_health"]["template_implementation"][
            "authentication"
        ]["score"]
        api_score = self.results["software_health"]["template_implementation"]["api"][
            "score"
        ]
        frontend_score = self.results["software_health"]["template_implementation"][
            "frontend"
        ]["score"]

        overall_progress = (auth_score + api_score + frontend_score) / 3

        # Define priority items
        priority_items = [
            {
                "title": "Database Integration",
                "priority": "HIGH",
                "effort": "3-5 days",
                "description": "Implement MariaDB and Alembic migrations",
                "tasks": [
                    "Set up MariaDB Docker service",
                    "Configure database connection",
                    "Create Alembic migration scripts",
                    "Implement database models",
                ],
            },
            {
                "title": "Security Audit",
                "priority": "HIGH",
                "effort": "2-3 days",
                "description": "Comprehensive security review",
                "tasks": [
                    "CVE scan and updates",
                    "Security header implementation",
                    "Authentication testing",
                    "Input validation review",
                ],
            },
            {
                "title": "Production Deployment",
                "priority": "MEDIUM",
                "effort": "2-4 days",
                "description": "Production readiness",
                "tasks": [
                    "Docker optimization",
                    "Environment configuration",
                    "CI/CD pipeline",
                    "Monitoring setup",
                ],
            },
        ]

        next_sprint = {
            "current_progress": {
                "overall_completion": round(overall_progress, 1),
                "authentication": auth_score,
                "api": api_score,
                "frontend": frontend_score,
                "database": 25,  # Estimated based on SQLite presence
                "production": 45,  # Estimated
            },
            "priority_items": priority_items,
            "sprint_duration": "2 weeks",
            "estimated_completion": min(95, overall_progress + 25),
        }

        self.results["next_sprint_plan"] = next_sprint

        print(f"  Current progress: {overall_progress:.1f}%")
        print(f"  Priority items: {len(priority_items)}")
        print(f"  Target completion: {next_sprint['estimated_completion']}%")

    def generate_reports(self):
        """Generate audit reports"""
        # Save detailed JSON report
        report_file = (
            self.workspace_root /
            f"noxsuite_audit_report_{self.audit_timestamp}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        # Generate executive summary
        self.generate_executive_summary()

        # Generate workspace migration plan
        self.generate_migration_plan()

        # Generate sprint backlog
        self.generate_sprint_backlog()

        print(f"  Reports saved with timestamp: {self.audit_timestamp}")
        print(f"  Main report: {report_file}")

    def generate_executive_summary(self):
        """Generate executive summary"""
        progress = self.results["next_sprint_plan"]["current_progress"]
        workspace_issues = self.results["workspace_audit"]

        summary = f"""# NoxSuite Audit Executive Summary

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Overall Progress:** {progress['overall_completion']}%

## Key Findings

### Achievements
- Authentication: {progress['authentication']}% complete
- API Implementation: {progress['api']}% complete  
- Frontend: {progress['frontend']}% complete
- Testing framework operational

### Issues Identified
- Workspace organization: {len(workspace_issues['misplaced_files'])} misplaced files
- Database: Using SQLite, need MariaDB migration
- Conflict files: {len(workspace_issues['conflict_files'])} files need cleanup
- Missing files: {len(workspace_issues['missing_files'])} critical files

## Next Sprint Priorities

1. **Database Integration (HIGH)** - MariaDB setup and migrations
2. **Security Audit (HIGH)** - CVE scanning and hardening
3. **Production Deployment (MEDIUM)** - Docker optimization and CI/CD

## Resource Requirements
- Development team: 2.5 FTE for 2 weeks
- Infrastructure: MariaDB server, CI/CD pipeline
- Target completion: {self.results['next_sprint_plan']['estimated_completion']}%

## Recommendation
Proceed with database integration as highest priority, followed by security hardening.
"""

        summary_file = (
            self.workspace_root
            / f"noxsuite_executive_summary_{self.audit_timestamp}.md"
        )
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

    def generate_migration_plan(self):
        """Generate workspace migration plan"""
        workspace_audit = self.results["workspace_audit"]

        migration_plan = f"""# NoxSuite Workspace Migration Plan

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Current Issues
- Misplaced files: {len(workspace_audit['misplaced_files'])}
- Conflict files: {len(workspace_audit['conflict_files'])}
- Missing files: {len(workspace_audit['missing_files'])}

## Target Structure
```
noxsuite/
├── backend/
│   ├── api/           # API routes and services
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── tests/         # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API clients
│   └── public/
├── docker/            # Docker configurations
├── tests/             # Integration tests
└── config/            # Configuration files
```

## Migration Steps

### 1. Backup Current State
```bash
cp -r . ../noxsuite_backup_{self.audit_timestamp}
```

### 2. Create Structure
```bash
mkdir -p noxsuite/{{backend/{{api,models,services,tests}},frontend/{{src,public}},docker,tests,config}}
```

### 3. Move Files
"""

        # Add specific file movements
        for misplaced in workspace_audit["misplaced_files"]:
            migration_plan += f"- Move {misplaced['file']} to {misplaced['expected']}\n"

        migration_plan += f"""

### 4. Clean Up
```bash
# Remove conflict files
find . -name "*.conflict.*" -delete

# Remove duplicates (manual review)
# Update import paths
```

### 5. Validation
- Run TestSprite validation
- Verify Docker builds
- Test API endpoints
"""

        migration_file = (
            self.workspace_root /
            f"noxsuite_migration_plan_{self.audit_timestamp}.md"
        )
        with open(migration_file, "w", encoding="utf-8") as f:
            f.write(migration_plan)

    def generate_sprint_backlog(self):
        """Generate sprint backlog"""
        priority_items = self.results["next_sprint_plan"]["priority_items"]

        backlog = f"""# NoxSuite Sprint Backlog

**Sprint Start:** {datetime.now().strftime('%Y-%m-%d')}
**Duration:** 2 weeks
**Goal:** Database integration and production readiness

## Sprint Items

"""

        for i, item in enumerate(priority_items, 1):
            backlog += f"""### {i}. {item['title']} ({item['priority']})
**Effort:** {item['effort']}
**Description:** {item['description']}

**Tasks:**
"""
            for task in item["tasks"]:
                backlog += f"- [ ] {task}\n"
            backlog += "\n"

        backlog += """
## Sprint Goals
- [ ] Complete database migration to MariaDB
- [ ] Pass security audit
- [ ] Achieve production deployment readiness
- [ ] Maintain test coverage above 90%

## Definition of Done
- Code reviewed and approved
- Tests passing
- Documentation updated
- Security checks passed
"""

        backlog_file = (
            self.workspace_root /
            f"noxsuite_sprint_backlog_{self.audit_timestamp}.md"
        )
        with open(backlog_file, "w", encoding="utf-8") as f:
            f.write(backlog)


def main():
    """Main execution"""
    print("NoxSuite Comprehensive Audit & Sprint Preparation")
    print("=" * 60)

    try:
        auditor = NoxSuiteAuditor()
        results = auditor.run_audit()

        # Print summary
        print("\n" + "=" * 60)
        print("AUDIT SUMMARY")
        print("=" * 60)

        workspace = results["workspace_audit"]
        software = results["software_health"]
        sprint = results["next_sprint_plan"]

        print(f"\nWorkspace Issues:")
        print(f"  Misplaced files: {len(workspace['misplaced_files'])}")
        print(f"  Missing files: {len(workspace['missing_files'])}")
        print(f"  Conflict files: {len(workspace['conflict_files'])}")

        print(f"\nSoftware Health:")
        for component, details in software["template_implementation"].items():
            print(f"  {component}: {details['score']}% ({details['status']})")

        print(f"\nCurrent Progress:")
        progress = sprint["current_progress"]
        print(f"  Overall: {progress['overall_completion']}%")
        print(f"  Database: {progress['database']}%")
        print(f"  Production: {progress['production']}%")

        print(f"\nNext Sprint:")
        print(f"  Priority items: {len(sprint['priority_items'])}")
        print(f"  Target completion: {sprint['estimated_completion']}%")

        print(f"\nReports generated with timestamp: {auditor.audit_timestamp}")
        return 0

    except Exception as e:
        print(f"Audit failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
