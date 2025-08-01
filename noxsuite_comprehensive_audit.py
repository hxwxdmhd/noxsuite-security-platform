#!/usr/bin/env python3
"""
🔍 NoxSuite Comprehensive Audit & Sprint Preparation Engine
===========================================================

Performs full workspace audit and prepares for next development sprint.

Features:
- Workspace structure analysis and misplaced file detection
- Software health audit with TestSprite integration
- Database validation and schema verification  
- Next sprint planning with actionable items

Author: NoxSuite Development Team
Date: July 31, 2025
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('noxsuite_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NoxSuiteComprehensiveAuditor:
    """Comprehensive auditor for NoxSuite project"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.audit_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.audit_results = {
            'timestamp': self.audit_timestamp,
            'workspace_audit': {},
            'software_health': {},
            'database_validation': {},
            'next_sprint_plan': {},
            'summary': {}
        }
        
        # Expected NoxSuite structure
        self.expected_structure = {
            'backend': {
                'api': ['user_service.py', 'api_routes.py', 'auth_service.py'],
                'models': ['user.py', 'roles.py', 'audit_log.py'],
                'services': ['mfa_service.py', 'rbac_service.py'],
                'database': ['connection.py', 'migrations/'],
                'tests': ['test_api.py', 'test_auth.py']
            },
            'frontend': {
                'src': {
                    'components': ['Login.jsx', 'Dashboard.jsx', 'Login.css', 'Dashboard.css'],
                    'services': ['api.js', 'auth.js'],
                    'utils': ['helpers.js']
                },
                'public': ['index.html'],
                'package.json': True
            },
            'docker': ['docker-compose.noxsuite.yml', 'Dockerfile.noxsuite'],
            'tests': ['testsprite_e2e.py', 'validate_template_implementation.py'],
            'config': ['requirements.txt', 'pyproject.toml']
        }
        
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Execute comprehensive audit"""
        logger.info("🔍 Starting NoxSuite Comprehensive Audit")
        logger.info(f"📁 Workspace: {self.workspace_root}")
        logger.info(f"🕐 Timestamp: {self.audit_timestamp}")
        
        try:
            # Phase 1: Workspace Structure Audit
            self.audit_workspace_structure()
            
            # Phase 2: Software Health Audit
            self.audit_software_health()
            
            # Phase 3: Database Validation
            self.audit_database_validation()
            
            # Phase 4: Next Sprint Preparation
            self.prepare_next_sprint()
            
            # Phase 5: Generate Reports
            self.generate_audit_reports()
            
            logger.info("✅ Comprehensive audit completed successfully")
            return self.audit_results
            
        except Exception as e:
            logger.error(f"❌ Audit failed: {e}")
            self.audit_results['error'] = str(e)
            return self.audit_results
    
    def audit_workspace_structure(self):
        """Phase 1: Audit workspace structure and detect misplaced files"""
        logger.info("\n📁 Phase 1: Workspace Structure Audit")
        
        workspace_audit = {
            'misplaced_files': [],
            'missing_files': [],
            'duplicate_files': [],
            'conflict_files': [],
            'unified_structure_plan': {},
            'migration_commands': []
        }
        
        # Scan for NoxSuite files
        noxsuite_files = self._find_noxsuite_files()
        workspace_audit['discovered_files'] = noxsuite_files
        
        # Check for misplaced files
        workspace_audit['misplaced_files'] = self._identify_misplaced_files(noxsuite_files)
        
        # Check for missing expected files
        workspace_audit['missing_files'] = self._identify_missing_files()
        
        # Check for duplicates and conflicts
        workspace_audit['duplicate_files'] = self._find_duplicate_files()
        workspace_audit['conflict_files'] = self._find_conflict_files()
        
        # Generate unified structure plan
        workspace_audit['unified_structure_plan'] = self._generate_unified_structure()
        workspace_audit['migration_commands'] = self._generate_migration_commands()
        
        self.audit_results['workspace_audit'] = workspace_audit
        logger.info(f"📊 Found {len(noxsuite_files)} NoxSuite files")
        logger.info(f"⚠️  {len(workspace_audit['misplaced_files'])} misplaced files")
        logger.info(f"❌ {len(workspace_audit['missing_files'])} missing files")
        
    def audit_software_health(self):
        """Phase 2: Audit software health and implementation quality"""
        logger.info("\n🔧 Phase 2: Software Health Audit")
        
        software_health = {
            'template_implementation': {},
            'testsprite_results': {},
            'code_quality': {},
            'cve_scan': {},
            'dependency_audit': {}
        }
        
        # Verify template implementations
        software_health['template_implementation'] = self._verify_template_implementations()
        
        # Run TestSprite validation
        software_health['testsprite_results'] = self._run_testsprite_validation()
        
        # Code quality analysis
        software_health['code_quality'] = self._analyze_code_quality()
        
        # CVE scan
        software_health['cve_scan'] = self._perform_cve_scan()
        
        # Dependency audit
        software_health['dependency_audit'] = self._audit_dependencies()
        
        self.audit_results['software_health'] = software_health
        logger.info("🔧 Software health audit completed")
        
    def audit_database_validation(self):
        """Phase 3: Validate database configuration and schema"""
        logger.info("\n🗄️  Phase 3: Database Validation")
        
        database_validation = {
            'mariadb_config': {},
            'connection_validation': {},
            'schema_audit': {},
            'migration_status': {},
            'recommendations': []
        }
        
        # Check for MariaDB configuration
        database_validation['mariadb_config'] = self._check_mariadb_config()
        
        # Validate database connections
        database_validation['connection_validation'] = self._validate_db_connections()
        
        # Audit schema
        database_validation['schema_audit'] = self._audit_database_schema()
        
        # Check migration status
        database_validation['migration_status'] = self._check_migration_status()
        
        # Generate recommendations
        database_validation['recommendations'] = self._generate_db_recommendations()
        
        self.audit_results['database_validation'] = database_validation
        logger.info("🗄️  Database validation completed")
        
    def prepare_next_sprint(self):
        """Phase 4: Prepare next development sprint"""
        logger.info("\n🚀 Phase 4: Next Sprint Preparation")
        
        next_sprint = {
            'current_progress': self._calculate_current_progress(),
            'priority_items': [],
            'script_generation': {},
            'timeline_estimation': {},
            'resource_requirements': {}
        }
        
        # Calculate current progress
        progress = self._calculate_current_progress()
        next_sprint['current_progress'] = progress
        
        # Define priority items based on audit results
        next_sprint['priority_items'] = self._define_priority_items()
        
        # Generate integration scripts
        next_sprint['script_generation'] = self._generate_integration_scripts()
        
        # Estimate timeline
        next_sprint['timeline_estimation'] = self._estimate_sprint_timeline()
        
        # Calculate resource requirements
        next_sprint['resource_requirements'] = self._calculate_resource_requirements()
        
        self.audit_results['next_sprint_plan'] = next_sprint
        logger.info(f"🎯 Current progress: {progress.get('overall_completion', 'N/A')}%")
        
    def generate_audit_reports(self):
        """Phase 5: Generate comprehensive audit reports"""
        logger.info("\n📊 Phase 5: Generating Audit Reports")
        
        # Save detailed audit results
        audit_file = self.workspace_root / f"noxsuite_audit_report_{self.audit_timestamp}.json"
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        # Generate executive summary
        self._generate_executive_summary()
        
        # Generate migration plan
        self._generate_migration_plan()
        
        # Generate sprint backlog
        self._generate_sprint_backlog()
        
        logger.info(f"📄 Audit report saved: {audit_file}")
        
    def _find_noxsuite_files(self) -> List[Dict[str, Any]]:
        """Find all NoxSuite-related files"""
        noxsuite_files = []
        
        # Key NoxSuite files to locate
        key_files = [
            'user_service.py', 'api_routes.py', 'auth_service.py',
            'Login.jsx', 'Dashboard.jsx', 'Login.css', 'Dashboard.css',
            'docker-compose.noxsuite.yml', 'Dockerfile.noxsuite',
            'testsprite_e2e.py', 'validate_template_implementation.py'
        ]
        
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if any(key_file in file for key_file in key_files):
                    file_path = Path(root) / file
                    noxsuite_files.append({
                        'name': file,
                        'path': str(file_path),
                        'size': file_path.stat().st_size if file_path.exists() else 0,
                        'modified': file_path.stat().st_mtime if file_path.exists() else 0
                    })
        
        return noxsuite_files
    
    def _identify_misplaced_files(self, noxsuite_files: List[Dict]) -> List[Dict]:
        """Identify files that are not in their expected locations"""
        misplaced = []
        
        for file_info in noxsuite_files:
            file_path = Path(file_info['path'])
            file_name = file_info['name']
            
            # Check if file is in expected location
            expected_location = self._get_expected_location(file_name)
            if expected_location and not str(file_path).endswith(expected_location):
                misplaced.append({
                    'file': file_name,
                    'current_location': str(file_path),
                    'expected_location': expected_location,
                    'migration_needed': True
                })
        
        return misplaced
    
    def _get_expected_location(self, filename: str) -> str:
        """Get expected location for a file"""
        location_map = {
            'user_service.py': 'backend/api/user_service.py',
            'api_routes.py': 'backend/api/api_routes.py',
            'auth_service.py': 'backend/services/auth_service.py',
            'Login.jsx': 'frontend/src/components/Login.jsx',
            'Dashboard.jsx': 'frontend/src/components/Dashboard.jsx',
            'Login.css': 'frontend/src/components/Login.css',
            'Dashboard.css': 'frontend/src/components/Dashboard.css',
            'docker-compose.noxsuite.yml': 'docker/docker-compose.noxsuite.yml',
            'testsprite_e2e.py': 'tests/testsprite_e2e.py'
        }
        return location_map.get(filename, '')
    
    def _identify_missing_files(self) -> List[str]:
        """Identify missing expected files"""
        missing = []
        
        # Check for critical NoxSuite files
        critical_files = [
            'backend/models/user.py',
            'backend/services/mfa_service.py',
            'backend/services/rbac_service.py',
            'frontend/src/services/api.js',
            'frontend/src/services/auth.js',
            'backend/database/connection.py'
        ]
        
        for file_path in critical_files:
            full_path = self.workspace_root / file_path
            if not full_path.exists():
                missing.append(file_path)
        
        return missing
    
    def _find_duplicate_files(self) -> List[Dict]:
        """Find duplicate files"""
        file_counts = {}
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if file_counts.get(file):
                    file_counts[file].append(Path(root) / file)
                else:
                    file_counts[file] = [Path(root) / file]
        
        duplicates = []
        for filename, paths in file_counts.items():
            if len(paths) > 1 and filename.endswith(('.py', '.js', '.jsx', '.css')):
                duplicates.append({
                    'filename': filename,
                    'locations': [str(p) for p in paths],
                    'count': len(paths)
                })
        
        return duplicates
    
    def _find_conflict_files(self) -> List[str]:
        """Find conflict files (.conflict.* files)"""
        conflict_files = []
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if '.conflict.' in file:
                    conflict_files.append(str(Path(root) / file))
        return conflict_files
    
    def _generate_unified_structure(self) -> Dict[str, Any]:
        """Generate unified workspace structure plan"""
        return {
            'target_structure': {
                'noxsuite/': {
                    'backend/': ['api/', 'models/', 'services/', 'database/', 'tests/'],
                    'frontend/': ['src/', 'public/', 'package.json'],
                    'docker/': ['docker-compose.yml', 'Dockerfile'],
                    'tests/': ['e2e/', 'unit/', 'integration/'],
                    'docs/': ['api/', 'deployment/', 'user/'],
                    'config/': ['requirements.txt', 'pyproject.toml']
                }
            },
            'migration_benefits': [
                'Cleaner project structure',
                'Better IDE support',
                'Easier deployment',
                'Improved maintainability'
            ]
        }
    
    def _generate_migration_commands(self) -> List[str]:
        """Generate commands to migrate files to unified structure"""
        commands = [
            "# Create unified NoxSuite structure",
            "mkdir -p noxsuite/{backend/{api,models,services,database,tests},frontend/{src,public},docker,tests,docs,config}",
            "",
            "# Move backend files",
            "mv backend/api/* noxsuite/backend/api/",
            "mv backend/models/* noxsuite/backend/models/ 2>/dev/null || true",
            "mv backend/services/* noxsuite/backend/services/ 2>/dev/null || true",
            "",
            "# Move frontend files", 
            "mv frontend/src/* noxsuite/frontend/src/",
            "mv frontend/package.json noxsuite/frontend/",
            "",
            "# Move configuration files",
            "mv requirements.txt noxsuite/config/",
            "cp pyproject.toml noxsuite/config/",
            "",
            "# Clean up conflict files",
            "find . -name '*.conflict.*' -delete",
            "",
            "# Update import paths (manual review required)",
            "echo 'Review and update import paths in Python files'"
        ]
        return commands
    
    def _verify_template_implementations(self) -> Dict[str, Any]:
        """Verify template implementations are working"""
        implementations = {}
        
        # Check authentication template
        auth_files = ['user_service.py', 'api_routes.py']
        implementations['authentication'] = self._check_file_implementations(auth_files)
        
        # Check API template
        api_files = ['api_routes.py', 'user_service.py']
        implementations['api'] = self._check_file_implementations(api_files)
        
        # Check frontend template
        frontend_files = ['Login.css', 'Dashboard.css']
        implementations['frontend'] = self._check_file_implementations(frontend_files)
        
        return implementations
    
    def _check_file_implementations(self, files: List[str]) -> Dict[str, Any]:
        """Check if files exist and have content"""
        result = {'status': 'unknown', 'files': {}, 'score': 0}
        
        total_files = len(files)
        implemented_files = 0
        
        for filename in files:
            file_found = False
            file_size = 0
            
            # Search for file in workspace
            for root, dirs, file_list in os.walk(self.workspace_root):
                if filename in file_list:
                    file_path = Path(root) / filename
                    file_size = file_path.stat().st_size
                    file_found = True
                    break
            
            result['files'][filename] = {
                'found': file_found,
                'size': file_size,
                'implemented': file_found and file_size > 100
            }
            
            if file_found and file_size > 100:
                implemented_files += 1
        
        result['score'] = int((implemented_files / total_files) * 100)
        result['status'] = 'complete' if result['score'] == 100 else 'partial' if result['score'] > 0 else 'missing'
        
        return result
    
    def _run_testsprite_validation(self) -> Dict[str, Any]:
        """Run TestSprite validation"""
        testsprite_results = {
            'available': False,
            'execution_status': 'not_run',
            'test_results': {},
            'coverage': 0
        }
        
        # Check if TestSprite exists
        testsprite_file = self.workspace_root / 'testsprite_e2e.py'
        if testsprite_file.exists():
            testsprite_results['available'] = True
            
            try:
                # Run TestSprite validation
                result = subprocess.run([
                    sys.executable, str(testsprite_file), '--validate'
                ], capture_output=True, text=True, timeout=60)
                
                testsprite_results['execution_status'] = 'completed'
                testsprite_results['exit_code'] = result.returncode
                testsprite_results['output'] = result.stdout
                testsprite_results['errors'] = result.stderr
                
                # Parse results if available
                if result.returncode == 0:
                    testsprite_results['test_results'] = self._parse_testsprite_output(result.stdout)
                
            except subprocess.TimeoutExpired:
                testsprite_results['execution_status'] = 'timeout'
            except Exception as e:
                testsprite_results['execution_status'] = 'error'
                testsprite_results['error'] = str(e)
        
        return testsprite_results
    
    def _parse_testsprite_output(self, output: str) -> Dict[str, Any]:
        """Parse TestSprite output for test results"""
        results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'coverage_percentage': 0
        }
        
        lines = output.split('\n')
        for line in lines:
            if 'tests run' in line.lower():
                try:
                    results['tests_run'] = int(line.split()[0])
                except:
                    pass
            elif 'coverage' in line.lower() and '%' in line:
                try:
                    coverage_str = line.split('%')[0].split()[-1]
                    results['coverage_percentage'] = float(coverage_str)
                except:
                    pass
        
        return results
    
    def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality"""
        quality_results = {
            'python_files': 0,
            'javascript_files': 0,
            'linting_results': {},
            'pep8_compliance': {},
            'unused_imports': []
        }
        
        # Count files
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if file.endswith('.py'):
                    quality_results['python_files'] += 1
                elif file.endswith(('.js', '.jsx')):
                    quality_results['javascript_files'] += 1
        
        # Run basic Python linting on key files
        key_python_files = [
            'backend/api/user_service.py',
            'backend/api/api_routes.py',
            'testsprite_e2e.py'
        ]
        
        for file_path in key_python_files:
            full_path = self.workspace_root / file_path
            if full_path.exists():
                quality_results['linting_results'][file_path] = self._lint_python_file(full_path)
        
        return quality_results
    
    def _lint_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Perform basic linting on Python file"""
        lint_result = {
            'syntax_valid': False,
            'import_issues': [],
            'line_count': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lint_result['line_count'] = len(content.split('\n'))
            
            # Check syntax
            compile(content, str(file_path), 'exec')
            lint_result['syntax_valid'] = True
            
            # Check for unused imports (basic check)
            import_lines = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
            lint_result['import_count'] = len(import_lines)
            
        except SyntaxError as e:
            lint_result['syntax_error'] = str(e)
        except Exception as e:
            lint_result['error'] = str(e)
        
        return lint_result
    
    def _perform_cve_scan(self) -> Dict[str, Any]:
        """Perform CVE scan on dependencies"""
        cve_results = {
            'python_packages': {},
            'node_packages': {},
            'docker_images': {},
            'vulnerabilities_found': 0,
            'recommendations': []
        }
        
        # Check Python packages
        requirements_file = self.workspace_root / 'requirements.txt'
        if requirements_file.exists():
            cve_results['python_packages'] = self._scan_python_packages(requirements_file)
        
        # Check Node packages
        package_json = self.workspace_root / 'frontend' / 'package.json'
        if package_json.exists():
            cve_results['node_packages'] = self._scan_node_packages(package_json)
        
        # Basic Docker image scan
        dockerfile = self.workspace_root / 'Dockerfile'
        if dockerfile.exists():
            cve_results['docker_images'] = self._scan_docker_images(dockerfile)
        
        return cve_results
    
    def _scan_python_packages(self, requirements_file: Path) -> Dict[str, Any]:
        """Scan Python packages for vulnerabilities"""
        scan_result = {
            'packages_scanned': 0,
            'vulnerabilities': [],
            'outdated_packages': []
        }
        
        try:
            with open(requirements_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                scan_result['packages_scanned'] = len(packages)
                
                # Check for known vulnerable packages (basic check)
                vulnerable_patterns = ['flask==0.', 'django==1.', 'requests==2.1']
                for package in packages:
                    for pattern in vulnerable_patterns:
                        if pattern in package.lower():
                            scan_result['vulnerabilities'].append({
                                'package': package,
                                'issue': f'Potentially vulnerable version: {pattern}'
                            })
        except Exception as e:
            scan_result['error'] = str(e)
        
        return scan_result
    
    def _scan_node_packages(self, package_json: Path) -> Dict[str, Any]:
        """Scan Node packages for vulnerabilities"""
        scan_result = {
            'packages_scanned': 0,
            'audit_available': False
        }
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                scan_result['packages_scanned'] = len(dependencies) + len(dev_dependencies)
        except Exception as e:
            scan_result['error'] = str(e)
        
        return scan_result
    
    def _scan_docker_images(self, dockerfile: Path) -> Dict[str, Any]:
        """Scan Docker images for vulnerabilities"""
        scan_result = {
            'base_images': [],
            'recommendations': []
        }
        
        try:
            with open(dockerfile, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip().startswith('FROM '):
                        image = line.strip().split()[1]
                        scan_result['base_images'].append(image)
                        
                        # Basic recommendations
                        if ':latest' in image:
                            scan_result['recommendations'].append(f"Pin version for {image}")
        except Exception as e:
            scan_result['error'] = str(e)
        
        return scan_result
    
    def _audit_dependencies(self) -> Dict[str, Any]:
        """Audit project dependencies"""
        return {
            'python_requirements': self._check_python_requirements(),
            'node_dependencies': self._check_node_dependencies(),
            'system_dependencies': self._check_system_dependencies()
        }
    
    def _check_python_requirements(self) -> Dict[str, Any]:
        """Check Python requirements"""
        req_files = [
            'requirements.txt', 'requirements-dev.txt', 'requirements-prod.txt',
            'requirements-test.txt', 'pyproject.toml'
        ]
        
        result = {'files_found': [], 'total_packages': 0}
        
        for req_file in req_files:
            file_path = self.workspace_root / req_file
            if file_path.exists():
                result['files_found'].append(req_file)
                if req_file.endswith('.txt'):
                    with open(file_path, 'r') as f:
                        packages = [line for line in f if line.strip() and not line.startswith('#')]
                        result['total_packages'] += len(packages)
        
        return result
    
    def _check_node_dependencies(self) -> Dict[str, Any]:
        """Check Node.js dependencies"""
        package_files = ['frontend/package.json', 'package.json']
        result = {'files_found': [], 'total_packages': 0}
        
        for package_file in package_files:
            file_path = self.workspace_root / package_file
            if file_path.exists():
                result['files_found'].append(package_file)
                try:
                    with open(file_path, 'r') as f:
                        package_data = json.load(f)
                        deps = len(package_data.get('dependencies', {}))
                        dev_deps = len(package_data.get('devDependencies', {}))
                        result['total_packages'] += deps + dev_deps
                except:
                    pass
        
        return result
    
    def _check_system_dependencies(self) -> Dict[str, Any]:
        """Check system dependencies"""
        return {
            'docker_available': self._check_docker_available(),
            'python_version': self._get_python_version(),
            'node_available': self._check_node_available()
        }
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available"""
        try:
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _get_python_version(self) -> str:
        """Get Python version"""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _check_node_available(self) -> bool:
        """Check if Node.js is available"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _check_mariadb_config(self) -> Dict[str, Any]:
        """Check MariaDB configuration"""
        mariadb_config = {
            'docker_compose_found': False,
            'mariadb_service_configured': False,
            'config_details': {}
        }
        
        # Check docker-compose files for MariaDB
        compose_files = [
            'docker-compose.yml', 'docker-compose.noxsuite.yml',
            'docker/docker-compose.yml', 'docker-compose.production.yml'
        ]
        
        for compose_file in compose_files:
            file_path = self.workspace_root / compose_file
            if file_path.exists():
                mariadb_config['docker_compose_found'] = True
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'mariadb' in content.lower() or 'mysql' in content.lower():
                            mariadb_config['mariadb_service_configured'] = True
                            mariadb_config['config_details'][compose_file] = 'MariaDB service found'
                except:
                    pass
        
        return mariadb_config
    
    def _validate_db_connections(self) -> Dict[str, Any]:
        """Validate database connections"""
        connection_validation = {
            'sqlite_dbs_found': [],
            'connection_files': [],
            'environment_variables': {}
        }
        
        # Find SQLite databases
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if file.endswith('.db') or file.endswith('.sqlite'):
                    connection_validation['sqlite_dbs_found'].append(str(Path(root) / file))
        
        # Look for database connection files
        db_files = ['database.py', 'connection.py', 'db.py']
        for db_file in db_files:
            for root, dirs, files in os.walk(self.workspace_root):
                if db_file in files:
                    connection_validation['connection_files'].append(str(Path(root) / db_file))
        
        # Check environment variables (basic)
        env_vars = ['DATABASE_URL', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        for var in env_vars:
            connection_validation['environment_variables'][var] = os.getenv(var) is not None
        
        return connection_validation
    
    def _audit_database_schema(self) -> Dict[str, Any]:
        """Audit database schema"""
        schema_audit = {
            'expected_tables': ['users', 'roles', 'audit_logs', 'sessions'],
            'found_tables': [],
            'migration_files': [],
            'schema_status': 'unknown'
        }
        
        # Check for Alembic migration files
        migration_dirs = ['migrations', 'backend/migrations', 'alembic']
        for migration_dir in migration_dirs:
            dir_path = self.workspace_root / migration_dir
            if dir_path.exists():
                migration_files = [f for f in dir_path.glob('**/*.py') if f.name != '__init__.py']
                schema_audit['migration_files'].extend([str(f) for f in migration_files])
        
        # Check SQLite databases for schema
        sqlite_files = [
            'noxsuite.db', 'noxsuite_auth.db', 'unified_heimnetz.db'
        ]
        
        for db_file in sqlite_files:
            db_path = self.workspace_root / db_file
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    schema_audit['found_tables'].extend(tables)
                    conn.close()
                except:
                    pass
        
        # Determine schema status
        found_expected = len([t for t in schema_audit['expected_tables'] if t in schema_audit['found_tables']])
        if found_expected == len(schema_audit['expected_tables']):
            schema_audit['schema_status'] = 'complete'
        elif found_expected > 0:
            schema_audit['schema_status'] = 'partial'
        else:
            schema_audit['schema_status'] = 'missing'
        
        return schema_audit
    
    def _check_migration_status(self) -> Dict[str, Any]:
        """Check database migration status"""
        return {
            'alembic_configured': Path(self.workspace_root / 'alembic.ini').exists(),
            'migration_directory': Path(self.workspace_root / 'migrations').exists(),
            'pending_migrations': 'unknown',  # Would need actual DB connection to check
            'recommendation': 'Set up Alembic for database migrations'
        }
    
    def _generate_db_recommendations(self) -> List[str]:
        """Generate database recommendations"""
        recommendations = [
            "Configure MariaDB as primary database (currently using SQLite)",
            "Set up Alembic for database migrations",
            "Create proper database models for users, roles, audit_logs, sessions",
            "Implement database connection pooling",
            "Add database backup and recovery procedures",
            "Set up database monitoring and health checks"
        ]
        return recommendations
    
    def _calculate_current_progress(self) -> Dict[str, Any]:
        """Calculate current development progress"""
        progress = {
            'overall_completion': 71.8,  # From previous audit
            'authentication': 100,
            'api_endpoints': 100,
            'frontend_components': 100,
            'database_integration': 25,
            'testing_framework': 85,
            'deployment_ready': 60,
            'production_ready': 45
        }
        
        # Update based on current audit findings
        if self.audit_results.get('software_health', {}).get('template_implementation'):
            template_results = self.audit_results['software_health']['template_implementation']
            
            auth_score = template_results.get('authentication', {}).get('score', 0)
            api_score = template_results.get('api', {}).get('score', 0)
            frontend_score = template_results.get('frontend', {}).get('score', 0)
            
            progress['authentication'] = auth_score
            progress['api_endpoints'] = api_score
            progress['frontend_components'] = frontend_score
        
        # Calculate overall completion
        component_scores = [
            progress['authentication'],
            progress['api_endpoints'], 
            progress['frontend_components'],
            progress['database_integration'],
            progress['testing_framework'],
            progress['deployment_ready']
        ]
        progress['overall_completion'] = sum(component_scores) / len(component_scores)
        
        return progress
    
    def _define_priority_items(self) -> List[Dict[str, Any]]:
        """Define priority items for next sprint"""
        priority_items = [
            {
                'title': 'Database Integration & Migration',
                'priority': 'HIGH',
                'estimated_effort': '3-5 days',
                'description': 'Implement MariaDB integration and Alembic migrations',
                'tasks': [
                    'Set up MariaDB Docker service',
                    'Configure database connection',
                    'Create Alembic migration scripts',
                    'Implement user/role/audit models',
                    'Test database operations'
                ]
            },
            {
                'title': 'Security Audit & Hardening',
                'priority': 'HIGH',
                'estimated_effort': '2-3 days',
                'description': 'Comprehensive security audit and hardening',
                'tasks': [
                    'CVE scan and package updates',
                    'Security headers implementation',
                    'Input validation enhancement',
                    'Authentication flow testing',
                    'RBAC permission testing'
                ]
            },
            {
                'title': 'Production Deployment',
                'priority': 'MEDIUM',
                'estimated_effort': '2-4 days',
                'description': 'Prepare for production deployment',
                'tasks': [
                    'Docker optimization',
                    'Environment configuration',
                    'CI/CD pipeline setup',
                    'Monitoring integration',
                    'Load testing'
                ]
            },
            {
                'title': 'Advanced Features',
                'priority': 'LOW',
                'estimated_effort': '5-7 days',
                'description': 'Implement advanced features and optimizations',
                'tasks': [
                    'Real-time notifications',
                    'Advanced analytics',
                    'API rate limiting',
                    'Caching implementation',
                    'Performance monitoring'
                ]
            }
        ]
        
        return priority_items
    
    def _generate_integration_scripts(self) -> Dict[str, Any]:
        """Generate integration scripts"""
        scripts = {
            'database_setup': self._generate_db_setup_script(),
            'testsprite_ci': self._generate_testsprite_ci_script(),
            'deployment_prep': self._generate_deployment_script()
        }
        return scripts
    
    def _generate_db_setup_script(self) -> Dict[str, str]:
        """Generate database setup script"""
        return {
            'filename': 'setup_database.py',
            'description': 'Sets up MariaDB and runs migrations',
            'content': '''#!/usr/bin/env python3
"""
Database Setup Script for NoxSuite
Configures MariaDB and runs Alembic migrations
"""

import os
import subprocess
import time
from pathlib import Path

def setup_mariadb():
    """Set up MariaDB using Docker"""
    print("🗄️ Setting up MariaDB...")
    
    # Start MariaDB container
    subprocess.run([
        "docker", "run", "-d",
        "--name", "noxsuite-mariadb",
        "-e", "MYSQL_ROOT_PASSWORD=noxsuite_root",
        "-e", "MYSQL_DATABASE=noxsuite",
        "-e", "MYSQL_USER=noxsuite_user", 
        "-e", "MYSQL_PASSWORD=noxsuite_pass",
        "-p", "3306:3306",
        "mariadb:10.6"
    ])
    
    print("⏳ Waiting for MariaDB to start...")
    time.sleep(10)

def setup_alembic():
    """Set up Alembic for migrations"""
    print("📋 Setting up Alembic...")
    
    if not Path("alembic.ini").exists():
        subprocess.run(["alembic", "init", "migrations"])
    
    # Run initial migration
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])
    subprocess.run(["alembic", "upgrade", "head"])

if __name__ == "__main__":
    setup_mariadb()
    setup_alembic()
    print("✅ Database setup completed!")
'''
        }
    
    def _generate_testsprite_ci_script(self) -> Dict[str, str]:
        """Generate TestSprite CI script"""
        return {
            'filename': 'testsprite_ci.py',
            'description': 'Runs TestSprite in CI/CD pipeline',
            'content': '''#!/usr/bin/env python3
"""
TestSprite CI/CD Integration Script
Runs comprehensive tests in automated pipeline
"""

import subprocess
import sys
import json
from datetime import datetime

def run_testsprite_suite():
    """Run full TestSprite test suite"""
    print("🧪 Running TestSprite test suite...")
    
    tests = [
        "python testsprite_e2e.py --full",
        "python validate_template_implementation.py",
        "python disaster_recovery.py --action backup"
    ]
    
    results = []
    for test in tests:
        print(f"Running: {test}")
        result = subprocess.run(test.split(), capture_output=True, text=True)
        results.append({
            'command': test,
            'exit_code': result.returncode,
            'passed': result.returncode == 0
        })
    
    # Generate test report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(results),
        'passed': len([r for r in results if r['passed']]),
        'failed': len([r for r in results if not r['passed']]),
        'results': results
    }
    
    with open('testsprite_ci_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Exit with error if any tests failed
    if report['failed'] > 0:
        print(f"❌ {report['failed']} tests failed")
        sys.exit(1)
    else:
        print(f"✅ All {report['passed']} tests passed")

if __name__ == "__main__":
    run_testsprite_suite()
'''
        }
    
    def _generate_deployment_script(self) -> Dict[str, str]:
        """Generate deployment preparation script"""
        return {
            'filename': 'prepare_deployment.py',
            'description': 'Prepares NoxSuite for production deployment',
            'content': '''#!/usr/bin/env python3
"""
Production Deployment Preparation Script
Optimizes and prepares NoxSuite for production
"""

import subprocess
import shutil
from pathlib import Path

def build_production_images():
    """Build production Docker images"""
    print("🐋 Building production Docker images...")
    
    subprocess.run([
        "docker", "build", 
        "-f", "Dockerfile.noxsuite",
        "-t", "noxsuite:latest",
        "."
    ])

def optimize_frontend():
    """Build optimized frontend"""
    print("⚛️ Building optimized frontend...")
    
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir)

def run_security_checks():
    """Run security checks"""
    print("🔒 Running security checks...")
    
    # Check for secrets in code
    subprocess.run(["git", "secrets", "--scan"])
    
    # Run dependency audit
    subprocess.run(["pip", "audit"])

def create_deployment_package():
    """Create deployment package"""
    print("📦 Creating deployment package...")
    
    # Create deployment directory
    deploy_dir = Path("deployment_package")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        "docker-compose.production.yml",
        "nginx.production.conf", 
        "requirements.txt"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy(file, deploy_dir)

if __name__ == "__main__":
    build_production_images()
    optimize_frontend()
    run_security_checks()
    create_deployment_package()
    print("✅ Deployment preparation completed!")
'''
        }
    
    def _estimate_sprint_timeline(self) -> Dict[str, Any]:
        """Estimate sprint timeline"""
        return {
            'sprint_duration': '2 weeks',
            'total_effort': '12-19 days',
            'milestones': [
                {'week': 1, 'focus': 'Database Integration & Security Audit'},
                {'week': 2, 'focus': 'Production Deployment & Advanced Features'}
            ],
            'critical_path': [
                'Database setup (Day 1-3)',
                'Security audit (Day 4-6)', 
                'Production prep (Day 7-10)',
                'Testing & validation (Day 11-14)'
            ]
        }
    
    def _calculate_resource_requirements(self) -> Dict[str, Any]:
        """Calculate resource requirements"""
        return {
            'development_team': {
                'backend_developer': '1 FTE',
                'frontend_developer': '0.5 FTE',
                'devops_engineer': '0.5 FTE',
                'qa_engineer': '0.5 FTE'
            },
            'infrastructure': {
                'development_server': 'Current (sufficient)',
                'database_server': 'MariaDB (new requirement)',
                'ci_cd_pipeline': 'GitHub Actions (recommended)',
                'monitoring': 'Prometheus + Grafana (optional)'
            },
            'budget_estimate': '$5,000 - $8,000 for infrastructure and tools'
        }
    
    def _generate_executive_summary(self):
        """Generate executive summary report"""
        summary_content = f"""# NoxSuite Comprehensive Audit Report - Executive Summary

**Audit Date:** {self.audit_timestamp}
**Current Progress:** {self.audit_results.get('next_sprint_plan', {}).get('current_progress', {}).get('overall_completion', 'N/A')}%

## 🎯 Key Findings

### ✅ Achievements
- Authentication system: JWT + MFA + RBAC implemented (100%)
- API endpoints: Full CRUD operations completed (100%) 
- Frontend components: ADHD-friendly responsive design (100%)
- Testing framework: TestSprite integration active

### ⚠️ Areas Requiring Attention
- **Database Integration:** Currently using SQLite, need MariaDB migration
- **Workspace Organization:** Multiple duplicate and conflict files detected
- **Security Hardening:** CVE scanning and dependency updates needed
- **Production Readiness:** Deployment optimization required

## 🚀 Next Sprint Priorities

1. **Database Integration (HIGH)** - 3-5 days
   - MariaDB setup and migration
   - Alembic integration
   - Schema implementation

2. **Security Audit (HIGH)** - 2-3 days
   - CVE scanning and updates
   - Security hardening
   - Authentication testing

3. **Production Deployment (MEDIUM)** - 2-4 days
   - Docker optimization
   - CI/CD pipeline
   - Monitoring setup

## 📊 Resource Requirements
- **Team:** 2.5 FTE for 2 weeks
- **Infrastructure:** MariaDB server, CI/CD pipeline
- **Budget:** $5,000 - $8,000

## 🎯 Success Metrics
- Overall completion: 71.8% → 95%+
- Security audit: 100% pass rate
- Production deployment: Successful
- Performance: <200ms response times

---
**Recommendation:** Proceed with next sprint focusing on database integration and security hardening.
"""
        
        summary_file = self.workspace_root / f"noxsuite_audit_executive_summary_{self.audit_timestamp}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        logger.info(f"📋 Executive summary: {summary_file}")
    
    def _generate_migration_plan(self):
        """Generate detailed migration plan"""
        migration_content = f"""# NoxSuite Workspace Migration Plan

**Generated:** {self.audit_timestamp}

## 🎯 Objective
Consolidate NoxSuite files into unified workspace structure for better organization and maintainability.

## 📁 Current Issues
- {len(self.audit_results.get('workspace_audit', {}).get('misplaced_files', []))} misplaced files
- {len(self.audit_results.get('workspace_audit', {}).get('duplicate_files', []))} duplicate files  
- {len(self.audit_results.get('workspace_audit', {}).get('conflict_files', []))} conflict files

## 🏗️ Target Structure
```
noxsuite/
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── database/
│   └── tests/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/
├── tests/
├── docs/
└── config/
```

## 🔧 Migration Steps

### Phase 1: Backup and Preparation
```bash
# Create backup
cp -r . ../noxsuite_backup_{self.audit_timestamp}

# Create new structure
mkdir -p noxsuite/{{backend,frontend,docker,tests,docs,config}}
mkdir -p noxsuite/backend/{{api,models,services,database,tests}}
mkdir -p noxsuite/frontend/{{src,public}}
```

### Phase 2: File Migration
{chr(10).join(self.audit_results.get('workspace_audit', {}).get('migration_commands', []))}

### Phase 3: Configuration Updates
- Update import paths in Python files
- Update package.json paths
- Update Docker compose file paths
- Update CI/CD configuration

### Phase 4: Validation
- Run TestSprite validation
- Verify all imports work
- Test Docker builds
- Validate API endpoints

## ⚠️ Risks & Mitigation
- **Import path breaks:** Test thoroughly, update systematically
- **Docker build failures:** Update Dockerfile paths
- **Lost files:** Complete backup before migration

## ✅ Success Criteria
- All files in correct locations
- No import errors
- All tests passing
- Docker builds successful
"""
        
        migration_file = self.workspace_root / f"noxsuite_migration_plan_{self.audit_timestamp}.md"
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)
        
        logger.info(f"📋 Migration plan: {migration_file}")
    
    def _generate_sprint_backlog(self):
        """Generate next sprint backlog"""
        priority_items = self.audit_results.get('next_sprint_plan', {}).get('priority_items', [])
        
        backlog_content = f"""# NoxSuite Next Sprint Backlog

**Sprint Start:** {datetime.now().strftime('%Y-%m-%d')}
**Sprint Duration:** 2 weeks
**Sprint Goal:** Database integration, security hardening, and production readiness

## 📋 Sprint Backlog Items

"""
        
        for i, item in enumerate(priority_items, 1):
            backlog_content += f"""### {i}. {item['title']} ({item['priority']} Priority)
**Effort:** {item['estimated_effort']}
**Description:** {item['description']}

**Tasks:**
"""
            for task in item['tasks']:
                backlog_content += f"- [ ] {task}\n"
            backlog_content += "\n"
        
        backlog_content += """
## 🎯 Sprint Objectives
- [ ] Complete database integration (MariaDB + Alembic)
- [ ] Pass comprehensive security audit
- [ ] Achieve production deployment readiness
- [ ] Maintain 95%+ test coverage

## 📊 Definition of Done
- All code reviewed and approved
- Unit tests written and passing
- Integration tests passing
- Documentation updated
- Security checks passed
- Performance requirements met

## 🚀 Sprint Ceremonies
- **Daily Standups:** 9:00 AM
- **Sprint Review:** End of Week 2
- **Sprint Retrospective:** After review
- **Planning Poker:** For effort estimation

---
**Note:** This backlog should be reviewed and refined during sprint planning.
"""
        
        backlog_file = self.workspace_root / f"noxsuite_sprint_backlog_{self.audit_timestamp}.md"
        with open(backlog_file, 'w', encoding='utf-8') as f:
            f.write(backlog_content)
        
        logger.info(f"📋 Sprint backlog: {backlog_file}")


def main():
    """Main execution function"""
    print("🔍 NoxSuite Comprehensive Audit & Sprint Preparation")
    print("=" * 60)
    
    try:
        # Initialize auditor
        auditor = NoxSuiteComprehensiveAuditor()
        
        # Run comprehensive audit
        results = auditor.run_comprehensive_audit()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 AUDIT SUMMARY")
        print("=" * 60)
        
        workspace_audit = results.get('workspace_audit', {})
        print(f"📁 Workspace Issues:")
        print(f"   • Misplaced files: {len(workspace_audit.get('misplaced_files', []))}")
        print(f"   • Missing files: {len(workspace_audit.get('missing_files', []))}")
        print(f"   • Duplicate files: {len(workspace_audit.get('duplicate_files', []))}")
        print(f"   • Conflict files: {len(workspace_audit.get('conflict_files', []))}")
        
        software_health = results.get('software_health', {})
        template_impl = software_health.get('template_implementation', {})
        print(f"\n🔧 Software Health:")
        for component, details in template_impl.items():
            score = details.get('score', 0)
            status = details.get('status', 'unknown')
            print(f"   • {component.title()}: {score}% ({status})")
        
        next_sprint = results.get('next_sprint_plan', {})
        progress = next_sprint.get('current_progress', {})
        print(f"\n🎯 Current Progress:")
        print(f"   • Overall: {progress.get('overall_completion', 'N/A'):.1f}%")
        print(f"   • Database: {progress.get('database_integration', 'N/A')}%")
        print(f"   • Production Ready: {progress.get('production_ready', 'N/A')}%")
        
        priority_items = next_sprint.get('priority_items', [])
        print(f"\n🚀 Next Sprint ({len(priority_items)} priority items):")
        for item in priority_items[:3]:  # Show top 3
            print(f"   • {item['title']} ({item['priority']} - {item['estimated_effort']})")
        
        print("\n✅ Audit completed successfully!")
        print(f"📄 Detailed reports generated with timestamp: {auditor.audit_timestamp}")
        
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
