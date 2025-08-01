#!/usr/bin/env python3
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
