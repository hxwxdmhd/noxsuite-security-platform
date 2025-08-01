#!/usr/bin/env python3
"""
NoxSuite Server Starter
======================
Ensures modules are loaded correctly and starts the FastAPI server.
"""

import os
import sys
import time
import signal
import logging
import importlib
import subprocess
from pathlib import Path
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServerStarter:
    """Start and monitor NoxSuite FastAPI server"""
    
    def __init__(self):
        self.server_process = None
        self.keep_running = True
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def flush_module_cache(self):
        """Flush the Python module cache to ensure fresh imports"""
        modules_to_flush = [
            "mariadb_dev_setup", 
            "noxsuite_fastapi_server",
            "rbac_mfa_extension"
        ]
        
        for module in modules_to_flush:
            if module in sys.modules:
                logger.info(f"Flushing module: {module}")
                del sys.modules[module]
                
        logger.info("Module cache flushed")
        
        # Make sure Python imports find our modules in the current directory
        sys.path.insert(0, os.getcwd())
    
    def verify_imports(self):
        """Verify all necessary modules can be imported"""
        try:
            # Import User model to ensure it has verify_password
            import mariadb_dev_setup
            User = getattr(mariadb_dev_setup, "User", None)
            
            if User and hasattr(User, "verify_password"):
                logger.info("✅ User model with verify_password verified")
            else:
                logger.error("❌ User model missing or missing verify_password")
                return False
            
            # Import RBAC/MFA extension to ensure it has register function
            import rbac_mfa_extension
            register_func = getattr(rbac_mfa_extension, "register_rbac_mfa_routes", None)
            
            if register_func and callable(register_func):
                logger.info("✅ RBAC/MFA extension with register function verified")
            else:
                logger.error("❌ RBAC/MFA extension missing or missing register function")
                return False
                
            return True
        except Exception as e:
            logger.error(f"❌ Import verification failed: {e}")
            return False
    
    def start_server(self):
        """Start the FastAPI server in a new process"""
        log_file = self.log_dir / f"fastapi_server_{int(time.time())}.log"
        
        try:
            with open(log_file, "w") as log:
                # Use a new Python process to ensure clean imports
                cmd = [sys.executable, "noxsuite_fastapi_server.py"]
                
                logger.info(f"Starting FastAPI server: {' '.join(cmd)}")
                logger.info(f"Server logs: {log_file}")
                
                self.server_process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Wait for server to start
                time.sleep(2)
                
                if self.server_process.poll() is None:
                    logger.info("✅ FastAPI server started successfully")
                    return True
                else:
                    logger.error(f"❌ FastAPI server failed to start (exit code: {self.server_process.returncode})")
                    
                    # Print the log content for debugging
                    with open(log_file, "r") as f:
                        logger.error(f"Server log:\n{f.read()}")
                    
                    return False
        except Exception as e:
            logger.error(f"❌ Error starting FastAPI server: {e}")
            return False
    
    def monitor_server(self):
        """Monitor server process and restart if needed"""
        while self.keep_running:
            if self.server_process and self.server_process.poll() is not None:
                logger.warning(f"Server terminated (exit code: {self.server_process.returncode})")
                
                if self.keep_running:
                    logger.info("Restarting server...")
                    time.sleep(1)
                    self.start_server()
            
            time.sleep(1)
    
    def stop_server(self):
        """Stop the FastAPI server"""
        self.keep_running = False
        
        if self.server_process:
            logger.info("Stopping FastAPI server...")
            
            # Send SIGTERM to gracefully shut down
            try:
                self.server_process.terminate()
                
                # Wait for process to terminate
                for _ in range(5):
                    if self.server_process.poll() is not None:
                        break
                    time.sleep(1)
                
                # Force kill if still running
                if self.server_process.poll() is None:
                    self.server_process.kill()
                    logger.warning("Server forcefully terminated")
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
    
    def run(self):
        """Run the server starter"""
        self.flush_module_cache()
        
        if not self.verify_imports():
            logger.error("Import verification failed. Cannot start server.")
            return False
        
        if not self.start_server():
            return False
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_server)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("Server monitor started. Press Ctrl+C to stop.")
        
        try:
            # Keep main thread running
            while self.keep_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
        finally:
            self.stop_server()
        
        return True

def signal_handler(sig, frame):
    """Handle signals for clean shutdown"""
    logger.info("Shutdown signal received...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    starter = ServerStarter()
    sys.exit(0 if starter.run() else 1)
