import os
import subprocess
import sys

from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)


# Change to project directory
os.chdir("k:\\Project Heimnetz")

# Start the ultra-fast server
logger.info("🚀 Launching Ultra-Fast Server...")
try:
    process = subprocess.Popen(
        [sys.executable, "ultra_fast_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    logger.info(f"✅ Server started with PID: {process.pid}")
    logger.info("🌐 Server should be running on http://localhost:5000")

    # Give it a moment to start
    import time

    time.sleep(2)

    # Check if it's running
    import requests

    try:
        response = requests.get("http://localhost:5000/health", timeout=1)
        logger.info(f"✅ Server responding: {response.status_code}")
    except:
        logger.info("⚠️ Server may still be starting...")

except Exception as e:
    logger.info(f"❌ Error starting server: {e}")

logger.info("🔄 You can now run the Gate 3 audit!")
