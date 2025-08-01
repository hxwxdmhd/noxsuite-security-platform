#!/usr/bin/env python3
"""
Security Violation Fixer
Automatically detects and fixes hardcoded secrets in Python codebase
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SecurityViolationFixer")

# Security patterns to look for
SECURITY_PATTERNS = [
    # API Keys
    (r'(api_key|apikey)\s*=\s*["\']([a-zA-Z0-9_\-]{10,})["\']', "API_KEY"),
    (r'(openai\.api_key|self\.api_key)\s*=\s*["\']([a-zA-Z0-9_\-]{10,})["\']', "OPENAI_API_KEY"),
    
    # JWT Secrets
    (r'(jwt_secret|jwt_key)\s*=\s*["\']([a-zA-Z0-9_\-]{5,})["\']', "JWT_SECRET_KEY"),
    
    # Passwords and secrets
    (r'(password|secret)\s*=\s*["\']([^"\'\s]{5,})["\']', "SECRET"),
    
    # Database credentials - enhanced for MariaDB/MySQL
    (r'(DB_PASSWORD|MYSQL_PASSWORD|MYSQL_ROOT_PASSWORD|MARIADB_PASSWORD)\s*=\s*["\']([^"\'\s]{5,})["\']', "DB_PASSWORD"),
    (r'(?:password|PASSWORD)["\']\s*:\s*["\'](.*?)["\']', "DB_PASSWORD"),
    
    # Database connection strings
    (r'(?:DATABASE_URL|DB_URL|conn_str|connection_string)\s*=\s*["\'](.*?):([^@\s]+)@', "DB_CONNECTION_STRING"),
    (r'mysql\+pymysql:\/\/.*:(.+?)@', "DB_PASSWORD"),
    
    # Docker container credentials
    (r'f"-p\{self\.config\[[\'\"](password)[\'\"]]\}"', "DB_PASSWORD"),
    (r'MYSQL_ROOT_PASSWORD=\{.*?\}', "MYSQL_ROOT_PASSWORD"),
    (r'-e\s+["\']MYSQL_ROOT_PASSWORD=([^"\'\s]+)["\']', "MYSQL_ROOT_PASSWORD"),
    (r'-e\s+["\']MYSQL_PASSWORD=([^"\'\s]+)["\']', "MYSQL_PASSWORD"),
]

# Known safe patterns (don't modify these)
SAFE_PATTERNS = [
    r'os\.environ\.get\(',
    r'os\.getenv\(',
    r'env:',  # For PowerShell environment variables
    r'password_hash',
    r'generate_password_hash',
    r'check_password_hash',
    r'placeholder',
    r'your_password_here',
    r'example\.env',
    r'\.env\.example',
    r'<password>',
    r'if.*?DB_PASSWORD', # Conditionals checking password
    r'config\[[\"\']password[\"\']',  # Config lookup for passwords
    r'--password',  # CLI flags
]


class SecurityViolationFixer:
    """Automatically detects and fixes security violations in Python code"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.violations_found = 0
        self.violations_fixed = 0
        self.files_with_violations = set()
        self.files_fixed = set()
        self.env_vars_needed = set()
        
    def scan_for_violations(self) -> List[Dict[str, Any]]:
        """Scan codebase for security violations"""
        violations = []
        python_files = list(self.workspace_dir.glob("**/*.py"))
        
        logger.info(f"Scanning {len(python_files)} Python files for security violations...")
        
        for py_file in python_files:
            try:
                file_violations = self._check_file_for_violations(py_file)
                if file_violations:
                    violations.extend(file_violations)
                    self.files_with_violations.add(py_file)
            except Exception as e:
                logger.error(f"Error scanning {py_file}: {e}")
                
        self.violations_found = len(violations)
        logger.info(f"Found {self.violations_found} security violations in {len(self.files_with_violations)} files")
        return violations
    
    def _check_file_for_violations(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check a single file for security violations"""
        violations = []
        content = file_path.read_text(errors='ignore')
        
        # Skip if the file is already using environment variables properly
        if any(re.search(pattern, content) for pattern in SAFE_PATTERNS) and not any(
            re.search(pattern[0], content) for pattern in SECURITY_PATTERNS
        ):
            return []
            
        for pattern, env_var_name in SECURITY_PATTERNS:
            try:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Handle case when there might be no groups or fewer groups than expected
                    if match.groups():
                        secret_value = match.group(2) if len(match.groups()) > 1 else match.group(1)
                    else:
                        secret_value = match.group(0)
                    
                    violations.append({
                        "file": str(file_path),
                        "line": line_num,
                        "pattern": pattern,
                        "env_var": env_var_name,
                        "match": match.group(0),
                        "secret_part": secret_value,
                        "replacement": None  # Will be filled in fix_violations
                    })
            except Exception as e:
                logger.error(f"Error processing pattern '{pattern}' in {file_path}: {e}")
                
        return violations
    
    def fix_violations(self, violations: List[Dict[str, Any]], dry_run: bool = False) -> None:
        """Fix identified security violations"""
        logger.info(f"Fixing {len(violations)} security violations...")
        
        for violation in violations:
            file_path = Path(violation["file"])
            content = file_path.read_text(errors='ignore')
            
            # Determine appropriate replacement based on the context
            if 'openai.api_key' in violation["match"]:
                replacement = f'openai.api_key = os.environ.get("{violation["env_var"]}", "")'
            elif 'self.api_key' in violation["match"]:
                replacement = f'self.api_key = os.environ.get("{violation["env_var"]}", "")'
            elif 'api_key' in violation["match"].lower() or 'apikey' in violation["match"].lower():
                replacement = f'{violation["match"].split("=")[0].strip()} = os.environ.get("{violation["env_var"]}", "")'
            elif 'DATABASE_URL' in violation["match"] or 'conn_str' in violation["match"]:
                # Handle database connection strings
                var_name = violation["match"].split('=')[0].strip()
                pwd_var = violation["env_var"]
                user_var = "DB_USER"
                host_var = "DB_HOST"
                db_var = "DB_NAME"
                port_var = "DB_PORT"
                
                replacement = (
                    f'{var_name} = f"mysql+pymysql://{{{os.environ.get("{user_var}", "user")}}}'
                    f':{{{os.environ.get("{pwd_var}", "")}}}@{{{os.environ.get("{host_var}", "localhost")}}}'
                    f':{{{os.environ.get("{port_var}", "3306")}}}/{{{os.environ.get("{db_var}", "db")}}}"'
                )
                
                # Add environment vars we'll need
                self.env_vars_needed.add(user_var)
                self.env_vars_needed.add(pwd_var)
                self.env_vars_needed.add(host_var)
                self.env_vars_needed.add(db_var)
                self.env_vars_needed.add(port_var)
            elif any(db_pattern in violation["match"] for db_pattern in ["DB_PASSWORD", "MYSQL_PASSWORD", "MARIADB_PASSWORD", "MYSQL_ROOT_PASSWORD"]):
                # Handle database password specifically
                variable_name = violation["match"].split("=")[0].strip()
                replacement = f'{variable_name} = os.environ.get("{violation["env_var"]}", "")'
            elif "pymysql://" in violation["match"]:
                # Handle inline connection strings
                parts = violation["match"].split(":", 1)
                if len(parts) > 1:
                    prefix = parts[0]
                    replacement = f'{prefix}: os.environ.get("{violation["env_var"]}", "")'
                else:
                    # Fallback for complex connection strings
                    replacement = f'os.environ.get("{violation["env_var"]}", "")'
            else:
                # General case
                variable_name = violation["match"].split("=")[0].strip()
                replacement = f'{variable_name} = os.environ.get("{violation["env_var"]}", "")'
                
            violation["replacement"] = replacement
            
            # Check if we need to add an import
            if 'os' not in content.split('\n')[0:10]:
                if 'import os' not in content:
                    # Add import statement after existing imports
                    import_match = re.search(r'^(import\s+.*?\n|from\s+.*?\n)+', content, re.MULTILINE)
                    if import_match:
                        end_pos = import_match.end()
                        content = content[:end_pos] + 'import os\n' + content[end_pos:]
                    else:
                        # No imports found, add at the top after any comments/docstrings
                        docstring_match = re.match(r'^(#.*?\n|""".*?"""\n|\'\'\'.*?\'\'\'\n)+', content, re.DOTALL)
                        if docstring_match:
                            end_pos = docstring_match.end()
                            content = content[:end_pos] + '\nimport os\n' + content[end_pos:]
                        else:
                            content = 'import os\n' + content
            
            # Replace the violation
            content = content.replace(violation["match"], replacement)
            
            # Save the changes if not a dry run
            if not dry_run:
                file_path.write_text(content)
                self.violations_fixed += 1
                self.files_fixed.add(file_path)
                self.env_vars_needed.add(violation["env_var"])
                
        logger.info(f"Fixed {self.violations_fixed} violations in {len(self.files_fixed)} files")
        
    def generate_env_example(self) -> str:
        """Generate .env.example file content based on identified variables"""
        content = "# .env.example\n# Copy to .env and fill in your actual values\n\n"
        
        # Group variables logically
        database_vars = []
        api_key_vars = []
        secret_vars = []
        other_vars = []
        
        for env_var in sorted(self.env_vars_needed):
            if any(db_pattern in env_var for db_pattern in ["DB_", "MYSQL_", "MARIADB_"]):
                database_vars.append(env_var)
            elif "API_KEY" in env_var:
                api_key_vars.append(env_var)
            elif "SECRET" in env_var or "PASSWORD" in env_var:
                secret_vars.append(env_var)
            else:
                other_vars.append(env_var)
        
        # Add Database section if needed
        if database_vars:
            content += "# Database Configuration\n"
            for env_var in database_vars:
                if "PASSWORD" in env_var:
                    content += f"{env_var}=your-secure-database-password\n"
                elif "USER" in env_var:
                    content += f"{env_var}=noxsuite_user\n"
                elif "NAME" in env_var or "DATABASE" in env_var:
                    content += f"{env_var}=noxsuite_db\n"
                elif "HOST" in env_var:
                    content += f"{env_var}=localhost\n"
                elif "PORT" in env_var:
                    content += f"{env_var}=3306\n"
                else:
                    content += f"{env_var}=your-{env_var.lower()}-value\n"
            content += "\n"
            
            # Add connection string if DB variables exist
            if any(var in database_vars for var in ["DB_USER", "DB_PASSWORD", "DB_HOST"]):
                content += "# Database Connection String - Will be constructed from the above values\n"
                content += "DATABASE_URL=mysql+pymysql://noxsuite_user:your-secure-database-password@localhost:3306/noxsuite_db\n\n"
            
        # Add API Keys section if needed
        if api_key_vars:
            content += "# API Keys\n"
            for env_var in api_key_vars:
                content += f"{env_var}=your-{env_var.lower().replace('_', '-')}\n"
            content += "\n"
        
        # Add Secrets section if needed
        if secret_vars:
            content += "# Secrets\n"
            for env_var in secret_vars:
                content += f"{env_var}=your-secure-{env_var.lower().replace('_', '-')}\n"
            content += "\n"
        
        # Add Other section if needed
        if other_vars:
            content += "# Other Configuration\n"
            for env_var in other_vars:
                content += f"{env_var}=your-{env_var.lower().replace('_', '-')}\n"
            content += "\n"
                
        return content
    
    def create_env_example_file(self, dry_run: bool = False) -> str:
        """Create .env.example file"""
        env_example_content = self.generate_env_example()
        
        if not dry_run:
            env_file_path = self.workspace_dir / ".env.example"
            env_file_path.write_text(env_example_content)
            logger.info(f"Created .env.example file with {len(self.env_vars_needed)} variables")
            
        return env_example_content
        
    def update_gitignore(self, dry_run: bool = False) -> None:
        """Ensure .env is in .gitignore"""
        gitignore_path = self.workspace_dir / ".gitignore"
        
        if not gitignore_path.exists():
            gitignore_content = "# Environment variables\n.env\n"
            if not dry_run:
                gitignore_path.write_text(gitignore_content)
                logger.info("Created .gitignore file with .env exclusion")
        else:
            gitignore_content = gitignore_path.read_text()
            if ".env" not in gitignore_content:
                gitignore_content += "\n# Environment variables\n.env\n"
                if not dry_run:
                    gitignore_path.write_text(gitignore_content)
                    logger.info("Updated .gitignore to include .env")
    
    def run(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run the security violation fixer"""
        logger.info(f"Starting security violation scan in {self.workspace_dir}")
        
        violations = self.scan_for_violations()
        
        if dry_run:
            logger.info("DRY RUN: Would fix the following violations:")
            for v in violations:
                logger.info(f"{v['file']}:{v['line']} - {v['match']} -> {v['env_var']}")
        else:
            self.fix_violations(violations)
            self.create_env_example_file()
            self.update_gitignore()
            
        return {
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "files_with_violations": len(self.files_with_violations),
            "files_fixed": len(self.files_fixed),
            "env_vars_needed": list(self.env_vars_needed)
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find and fix security violations in Python code")
    parser.add_argument("--workspace", default=".", help="Workspace directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Don't make any changes, just report")
    args = parser.parse_args()
    
    fixer = SecurityViolationFixer(args.workspace)
    results = fixer.run(args.dry_run)
    
    print("\nSummary:")
    print(f"Violations found: {results['violations_found']}")
    if not args.dry_run:
        print(f"Violations fixed: {results['violations_fixed']}")
        print(f"Files fixed: {results['files_fixed']}")
        print(f"Environment variables needed: {', '.join(results['env_vars_needed'])}")
    else:
        print("Run without --dry-run to fix violations")
