import subprocess
import sys
import os
import time
from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)


# Change to project directory
os.chdir("k:\\Project Heimnetz")

# Start the ultra-secure server
logger.info("Starting Ultra-Secure Server...")
try:
    process = subprocess.Popen([sys.executable, "ultra_secure_server.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
    logger.info(f"Server started with PID: {process.pid}")
    logger.info("Server should be running on http://127.0.0.1:5000")
    
    # Give it a moment to start
    time.sleep(3)
    
    # Check if it's running
    import requests
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=2)
        logger.info(f"Server responding: {response.status_code}")
        logger.info("Ready for security testing!")
    except Exception as e:
        logger.info(f"Connection test failed: {e}")
        stdout, stderr = process.communicate(timeout=1)
        if stderr:
            logger.info(f"Server error: {stderr}")
        
except Exception as e:
    logger.info(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
