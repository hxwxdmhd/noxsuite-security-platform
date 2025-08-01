#!/usr/bin/env python3
"""
NoxSuite Quick Start Script
Simple deployment for immediate testing and development
@author @hxwxdmhd
@version 11.0.0
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🚀 %(asctime)s | %(message)s'
)

logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Run command with error handling"""
    try:
        logger.info(f"🔄 Running: {command}")
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✅ Command completed successfully")
            return True
        else:
            logger.error(f"❌ Command failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running command: {e}")
        return False

def quick_start():
    """Quick start NoxSuite for testing"""
    project_root = Path(__file__).parent
    
    logger.info("🚀 NoxSuite Ultimate Quick Start")
    logger.info("="*50)
    
    # Step 1: Install backend dependencies
    logger.info("📦 Installing backend dependencies...")
    if not run_command("pip install flask flask-cors flask-socketio psutil", cwd=project_root):
        logger.error("❌ Failed to install dependencies")
        return False
    
    # Step 2: Create environment file
    env_file = project_root / '.env'
    if not env_file.exists():
        logger.info("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("""
# NoxSuite Quick Start Environment
SECRET_KEY=noxsuite-quick-start-key
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://noxsuite.db
""".strip())
    
    # Step 3: Start backend server
    logger.info("🔧 Starting NoxSuite backend...")
    logger.info("🌐 Backend will be available at: http://localhost:5000")
    logger.info("📊 API docs will be available at: http://localhost:5000/api/health")
    logger.info("⚡ Press Ctrl+C to stop")
    
    try:
        # Start the Flask application
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'
        
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=project_root
        )
        
        # Wait for process to complete or be interrupted
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("🛑 Stopping NoxSuite...")
        process.terminate()
        process.wait()
        logger.info("✅ NoxSuite stopped")
    
    return True

if __name__ == '__main__':
    try:
        quick_start()
    except Exception as e:
        logger.error(f"❌ Quick start failed: {e}")
        sys.exit(1)
