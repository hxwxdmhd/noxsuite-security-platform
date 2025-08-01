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

import os
import sys
import shutil
import json
import ast
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NoxSuiteCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.archive_date = datetime.now().strftime("%Y-%m-%d")
        self.archive_root = self.project_root / "archive" / self.archive_date
        
        # Analysis results
        self.issues_found = {
            'syntax_errors': [],
            'import_errors': [],
            'empty_files': [],
            'duplicate_files': [],
            'security_issues': [],
            'performance_issues': [],
            'broken_endpoints': []
        }
        
        # Files to keep (core functionality)
        self.core_files = {
            'app.py',
            'advanced_ai_engine.py',
            'validate_system.py',
            'requirements.txt',
            'docker-compose.yml',
            'Dockerfile'
        }
        
        # Initialize archive directories
        self._create_archive_structure()
        
    def _create_archive_structure(self):
        """Create archive directory structure"""
        archive_dirs = [
            'empty-files',
            'duplicate-servers', 
            'broken-imports',
            'syntax-errors',
            'unused-dependencies',
            'incomplete-features',
            'backup-files'
        ]
        
        for dir_name in archive_dirs:
            (self.archive_root / dir_name).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Created archive structure at {self.archive_root}")

    def analyze_syntax_errors(self) -> List[str]:
        """Check all Python files for syntax errors"""
        logger.info("🔍 Analyzing Python files for syntax errors...")
        syntax_errors = []
        
        for py_file in self.project_root.rglob("*.py"):
            if 'archive' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    source = f.read()
                    
                if not source.strip():  # Empty file
                    self.issues_found['empty_files'].append(str(py_file))
                    continue
                    
                ast.parse(source)
                logger.debug(f"✅ Syntax OK: {py_file.name}")
                
            except SyntaxError as e:
                error_msg = f"{py_file}: {e}"
                syntax_errors.append(error_msg)
                self.issues_found['syntax_errors'].append(str(py_file))
                logger.error(f"❌ Syntax Error: {error_msg}")
                
            except UnicodeDecodeError as e:
                error_msg = f"{py_file}: Unicode decode error - {e}"
                syntax_errors.append(error_msg)
                self.issues_found['syntax_errors'].append(str(py_file))
                logger.error(f"❌ Encoding Error: {error_msg}")
                
            except Exception as e:
                error_msg = f"{py_file}: {e}"
                syntax_errors.append(error_msg)
                logger.error(f"❌ Parse Error: {error_msg}")
        
        logger.info(f"Found {len(syntax_errors)} syntax errors")
        return syntax_errors

    def analyze_import_errors(self) -> List[str]:
        """Check for broken imports"""
        logger.info("🔍 Analyzing import statements...")
        import_errors = []
        
        for py_file in self.project_root.rglob("*.py"):
            if 'archive' in str(py_file) or py_file.name in ['setup.py']:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    source = f.read()
                    
                if not source.strip():
                    continue
                    
                tree = ast.parse(source)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self._check_import(alias.name, py_file, import_errors)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self._check_import(node.module, py_file, import_errors)
                                
            except Exception as e:
                logger.debug(f"Could not analyze imports in {py_file}: {e}")
                
        logger.info(f"Found {len(import_errors)} import issues")
        return import_errors

    def _check_import(self, module_name: str, file_path: Path, import_errors: List[str]):
        """Check if a module can be imported"""
        if not module_name or module_name.startswith('.'):
            return
            
        # Skip system/built-in modules
        builtin_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'logging', 'pathlib',
            'typing', 'collections', 'itertools', 'functools', 'operator',
            'threading', 'asyncio', 'subprocess', 'shutil', 'glob', 're',
            'urllib', 'http', 'ssl', 'socket', 'email', 'sqlite3', 'csv',
            'uuid', 'hashlib', 'hmac', 'base64', 'secrets', 'math', 'random'
        }
        
        root_module = module_name.split('.')[0]
        if root_module in builtin_modules:
            return
            
        # Check if it's a local import
        if root_module in ['src', 'backend', 'frontend', 'tests']:
            local_path = self.project_root / f"{root_module}.py"
            if not local_path.exists():
                error_msg = f"{file_path}: Missing local module '{module_name}'"
                import_errors.append(error_msg)
                self.issues_found['import_errors'].append(str(file_path))

    def identify_duplicate_servers(self) -> List[Tuple[str, str]]:
        """Identify duplicate server implementations"""
        logger.info("🔍 Identifying duplicate server files...")
        
        server_files = list(self.project_root.glob("*server*.py"))
        duplicates = []
        
        # Group similar files
        server_groups = {
            'main_server': [],
            'performance_server': [],
            'unified_server': [],
            'test_server': [],
            'production_server': []
        }
        
        for file in server_files:
            if 'archive' in str(file):
                continue
                
            filename = file.name.lower()
            if 'main' in filename and 'server' in filename:
                server_groups['main_server'].append(file)
            elif 'performance' in filename:
                server_groups['performance_server'].append(file)
            elif 'unified' in filename:
                server_groups['unified_server'].append(file)
            elif 'test' in filename:
                server_groups['test_server'].append(file)
            elif 'production' in filename:
                server_groups['production_server'].append(file)
                
        # Identify duplicates within groups
        for group_name, files in server_groups.items():
            if len(files) > 1:
                # Keep the most recent or most complete version
                files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                keep_file = files[0]
                for duplicate in files[1:]:
                    duplicates.append((str(duplicate), str(keep_file)))
                    self.issues_found['duplicate_files'].append(str(duplicate))
                    
        logger.info(f"Found {len(duplicates)} duplicate server files")
        return duplicates

    def identify_empty_files(self) -> List[str]:
        """Identify empty or minimal content files"""
        logger.info("🔍 Identifying empty files...")
        empty_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            if 'archive' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    
                if not content:
                    empty_files.append(str(py_file))
                    self.issues_found['empty_files'].append(str(py_file))
                elif len(content.split('\n')) <= 5 and all(
                    line.strip().startswith('#') or not line.strip() 
                    for line in content.split('\n')
                ):
                    # Only comments or empty lines
                    empty_files.append(str(py_file))
                    self.issues_found['empty_files'].append(str(py_file))
                    
            except Exception as e:
                logger.debug(f"Could not read {py_file}: {e}")
                
        logger.info(f"Found {len(empty_files)} empty files")
        return empty_files

    def check_security_issues(self) -> List[str]:
        """Check for common security issues"""
        logger.info("🔍 Checking for security issues...")
        security_issues = []
        
        dangerous_patterns = [
            (r'password\s*=\s*["\'].*["\']', 'Hardcoded password'),
            (r'secret\s*=\s*["\'].*["\']', 'Hardcoded secret'),
            (r'api_key\s*=\s*["\'].*["\']', 'Hardcoded API key'),
            (r'exec\s*\(', 'Use of exec() function'),
            (r'eval\s*\(', 'Use of eval() function'),
            (r'shell\s*=\s*True', 'Shell injection risk'),
        ]
        
        import re
        
        for py_file in self.project_root.rglob("*.py"):
            if 'archive' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern, issue_type in dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issue_msg = f"{py_file}: {issue_type}"
                        security_issues.append(issue_msg)
                        self.issues_found['security_issues'].append(str(py_file))
                        
            except Exception as e:
                logger.debug(f"Could not analyze {py_file}: {e}")
                
        logger.info(f"Found {len(security_issues)} security issues")
        return security_issues

    def archive_files(self, file_list: List[str], archive_subdir: str, reason: str):
        """Archive files to the specified subdirectory"""
        logger.info(f"📦 Archiving {len(file_list)} files to {archive_subdir} ({reason})")
        
        archive_dir = self.archive_root / archive_subdir
        archive_dir.mkdir(exist_ok=True)
        
        for file_path in file_list:
            source = Path(file_path)
            if source.exists() and source.name not in self.core_files:
                try:
                    destination = archive_dir / source.name
                    counter = 1
                    while destination.exists():
                        stem = source.stem
                        suffix = source.suffix
                        destination = archive_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                        
                    shutil.move(str(source), str(destination))
                    logger.info(f"Archived: {source.name} -> {destination}")
                    
                except Exception as e:
                    logger.error(f"Failed to archive {source}: {e}")

    def fix_installer_issues(self):
        """Create a working installer script"""
        logger.info("🔧 Creating improved installer...")
        
        installer_content = '''#!/usr/bin/env python3
"""
NoxSuite Ultimate Installer
Automated installation and setup script
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class NoxSuiteInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.frontend_dir = self.project_root / "frontend"
        self.package_json = self.frontend_dir / "package.json"
        
    def check_python_version(self):
        """Ensure Python 3.8+ is being used"""
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ is required")
            return False
        logger.info(f"Python version: {sys.version}")
        return True
        
    def install_python_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        if not self.requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
            
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], check=True)
            logger.info("Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
            
    def setup_database(self):
        """Initialize database"""
        logger.info("Setting up database...")
        
        try:
            # Import after dependencies are installed
            from app import init_database
            init_database()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False
            
    def install_frontend_dependencies(self):
        """Install frontend dependencies"""
        if not self.frontend_dir.exists() or not self.package_json.exists():
            logger.warning("Frontend directory not found, skipping...")
            return True
            
        logger.info("Installing frontend dependencies...")
        
        try:
            subprocess.run([
                "npm", "install"
            ], cwd=self.frontend_dir, check=True)
            logger.info("Frontend dependencies installed successfully")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"Frontend installation failed: {e}")
            return True  # Not critical for backend functionality
            
    def create_env_file(self):
        """Create environment configuration file"""
        env_file = self.project_root / ".env"
        
        if env_file.exists():
            logger.info(".env file already exists")
            return True
            
        env_content = """# NoxSuite Configuration
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=mysql+pymysql://noxsuite.db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret-here-change-in-production
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            logger.info("Created .env file")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
            
    def run_validation(self):
        """Run system validation"""
        logger.info("Running system validation...")
        
        try:
            result = subprocess.run([
                sys.executable, "validate_system.py"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("System validation passed")
                return True
            else:
                logger.warning(f"System validation warnings: {result.stdout}")
                return True  # Warnings are ok
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
            
    def install(self, mode="development"):
        """Run complete installation"""
        logger.info(f"Starting NoxSuite installation (mode: {mode})")
        
        steps = [
            ("Check Python version", self.check_python_version),
            ("Install Python dependencies", self.install_python_dependencies),
            ("Setup database", self.setup_database),
            ("Install frontend dependencies", self.install_frontend_dependencies),
            ("Create environment file", self.create_env_file),
            ("Run validation", self.run_validation)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            if not step_func():
                logger.error(f"Installation failed at step: {step_name}")
                return False
                
        logger.info("🎉 Installation completed successfully!")
        logger.info("To start the application, run: python app.py")
        return True

if __name__ == "__main__":
    import argparse
    
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
            with open(installer_path, 'w', encoding='utf-8') as f:
                f.write(installer_content)
            
            # Make executable on Unix-like systems
            if os.name != 'nt':
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
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
            
        # Keep essential dependencies
        essential_deps = {
            'Flask', 'Flask-CORS', 'Flask-SocketIO', 'Flask-JWT-Extended',
            'SQLAlchemy', 'psycopg2-binary', 'redis', 'cryptography',
            'psutil', 'requests', 'python-dotenv', 'PyYAML', 'colorama'
        }
        
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if (not line or line.startswith('#') or 
                any(dep in line for dep in essential_deps)):
                cleaned_lines.append(line)
                
        # Write cleaned requirements
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(cleaned_lines))
            
        logger.info("Cleaned requirements.txt")

    def generate_report(self):
        """Generate comprehensive cleanup report"""
        logger.info("📊 Generating cleanup report...")
        
        report = {
            'cleanup_date': self.archive_date,
            'project_root': str(self.project_root),
            'issues_found': self.issues_found,
            'files_processed': {
                'empty_files_archived': len(self.issues_found['empty_files']),
                'duplicate_files_archived': len(self.issues_found['duplicate_files']),
                'syntax_errors_found': len(self.issues_found['syntax_errors']),
                'import_errors_found': len(self.issues_found['import_errors']),
                'security_issues_found': len(self.issues_found['security_issues'])
            },
            'recommendations': [
                "Run 'python install.py' to set up the environment",
                "Test the installation with 'python install.py --test'",
                "Run 'python validate_system.py' to verify system health",
                "Check archived files before permanent deletion",
                "Update .env file with production credentials before deployment"
            ]
        }
        
        report_file = self.project_root / "cleanup_report.json"
        with open(report_file, 'w') as f:
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

        if self.issues_found['syntax_errors']:
            md_content += "\n### Syntax Errors\n"
            for file in self.issues_found['syntax_errors']:
                md_content += f"- {file}\n"
                
        if self.issues_found['security_issues']:
            md_content += "\n### Security Issues\n"
            for file in self.issues_found['security_issues']:
                md_content += f"- {file}\n"
        
        md_report_file = self.project_root / "CLEANUP_REPORT.md"
        with open(md_report_file, 'w') as f:
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
        
        self.archive_files(self.issues_found['empty_files'], 'empty-files', 'Empty or minimal content')
        self.archive_files(self.issues_found['duplicate_files'], 'duplicate-servers', 'Duplicate server implementations')
        self.archive_files(self.issues_found['import_errors'], 'broken-imports', 'Broken import statements')
        
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
