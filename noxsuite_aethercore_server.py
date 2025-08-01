#!/usr/bin/env python3
"""
NoxSuite AetherCore MSP Server
=============================

Model Service Provider (MSP) server for AI model management and inference.
Integrated with MCP and Langflow for complete NoxSuite ecosystem.
"""

from datetime import datetime
import json
import os
import sys

    import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging


    parser = argparse.ArgumentParser(
        description="NoxSuite AetherCore MSP Server")
    parser.add_argument(
        "--port", type=int, default=8001, help="Port to run on (default: 8001)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )

    args = parser.parse_args()

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    server = AetherCoreMSPServer(port=args.port, host=args.host)

    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("🛑 AetherCore MSP Server stopped by user")
        server.status = "stopped"
        server.update_status()
    except Exception as e:
        logger.error(f"Server error: {e}")
        server.status = "error"
        server.update_status()


if __name__ == "__main__":
    main()
