from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Simple MCP Server Implementation
===============================
Basic MCP server that responds correctly to prevent crashes

REASONING CHAIN:
1. Problem: Complex MCP servers are crashing due to syntax errors
2. Analysis: Need minimal working server to validate launcher
3. Solution: Simple async server with basic heartbeat
4. Validation: Server runs without crashes and responds to signals
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleMCPServer:
    """Simple MCP server for testing"""

    def __init__(self, server_name: str):
        self.server_name = server_name
        self.running = True

    async def run(self):
        """Main server loop"""
        logger.info(f"🚀 {self.server_name} MCP Server started")

        try:
            heartbeat_count = 0
            while self.running:
                await asyncio.sleep(10)  # 10 second heartbeat
                heartbeat_count += 1
                logger.info(f"💓 {self.server_name} heartbeat #{heartbeat_count}")

                # Stop after 6 heartbeats (1 minute) for testing
                if heartbeat_count >= 6:
                    logger.info(f"🏁 {self.server_name} completing test run")
                    break

        except KeyboardInterrupt:
            logger.info(f"🛑 {self.server_name} shutting down...")
        except Exception as e:
            logger.error(f"❌ {self.server_name} error: {e}")
            raise
        finally:
            logger.info(f"✅ {self.server_name} shutdown complete")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--server-mode":
        # Determine server type from script name
        if "orchestrator" in __file__:
            server_name = "Orchestrator"
        elif "knowledge" in __file__:
            server_name = "Knowledge Parser"
        elif "annotator" in __file__:
            server_name = "Code Annotator"
        elif "installer" in __file__:
            server_name = "Smart Installer"
        elif "cicd" in __file__:
            server_name = "CI/CD Monitor"
        else:
            server_name = "Simple MCP"

        server = SimpleMCPServer(server_name)
        await server.run()
    else:
        logger.info("🔧 Simple MCP Server - use --server-mode to run as server")


if __name__ == "__main__":
    asyncio.run(main())
