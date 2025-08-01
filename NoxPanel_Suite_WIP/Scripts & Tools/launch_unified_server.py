from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Ultimate Suite v11.0 - Production Launch Script
==============================================
Simple standalone launcher for testing and deployment
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('heimnetz_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    REASONING CHAIN:
    1. Problem: Function main needs clear operational definition
    2. Analysis: Implementation requires specific logic for main operation
    3. Solution: Implement main with enterprise-grade patterns and error handling
    4. Validation: Test main with edge cases and performance requirements
    
    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Main launcher function"""
    logger.info("=" * 60)
    logger.info("ULTIMATE SUITE v11.0 - UNIFIED SERVER LAUNCHER")
    logger.info("=" * 60)
    logger.info(f"Starting at: {datetime.now()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info()
    
    try:
        # Test imports
        logger.info("Testing imports...")
        
        try:
            from unified_plugin_system import UnifiedPluginManager
            logger.info("✓ UnifiedPluginManager import successful")
        except Exception as e:
            logger.info(f"✗ UnifiedPluginManager import failed: {e}")
            return False
            
        try:
            from models_unified import DatabaseManager
            logger.info("✓ DatabaseManager import successful")
        except Exception as e:
            logger.info(f"✗ DatabaseManager import failed: {e}")
            # Continue without database for now
            
        try:
            from main_unified_server import UnifiedServer, ServerConfig
            logger.info("✓ UnifiedServer import successful")
        except Exception as e:
            logger.info(f"✗ UnifiedServer import failed: {e}")
            return False
        
        logger.info()
        logger.info("All critical imports successful!")
        logger.info()
        
        # Initialize configuration
        logger.info("Initializing configuration...")
        config = ServerConfig()
        config.database_url = "mysql+pymysql://heimnetz.db"  # Use SQLite for testing
        config.redis_url = "redis://localhost:6379/0"
        config.debug = True
        config.ssl_enabled = False
        config.host = "127.0.0.1"
        config.port = 5000
        
        logger.info(f"Server will run on: {config.host}:{config.port}")
        logger.info(f"Database: {config.database_url}")
        logger.info(f"Debug mode: {config.debug}")
        logger.info()
        
        # Initialize plugin system
        logger.info("Initializing plugin system...")
        try:
            plugin_dirs = ["plugins", "AI/plugins", "NoxPanel/plugins"]
            plugin_manager = UnifiedPluginManager(plugin_dirs)
            logger.info("✓ Plugin system initialized")
        except Exception as e:
            logger.info(f"✗ Plugin system initialization failed: {e}")
            plugin_manager = None
        
        logger.info()
        
        # Create and start server
        logger.info("Creating unified server...")
        server = UnifiedServer(config)
        
        if plugin_manager:
            server.plugin_manager = plugin_manager
        
        logger.info("✓ Server created successfully")
        logger.info()
        logger.info("Starting server...")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Start the server
        server.run()
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Server shutdown requested by user")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.info(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
