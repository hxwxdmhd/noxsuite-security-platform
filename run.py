"""
Run script for NoxSuite MFA and RBAC implementation
"""

import argparse
import os
import subprocess
import sys
import time

import uvicorn

from auth.auth_integration import AuthIntegrationService
from backend.api.main import app as api_app


def init_auth_settings():
    """Initialize auth settings"""
    print("Initializing auth settings...")

    # Check if rbac_config.json exists
    if os.path.exists("rbac_config.json"):
        # Run init_auth.py with import config
        subprocess.run(
            [sys.executable, "init_auth.py", "--import-config", "rbac_config.json"]
        )
    else:
        # Run init_auth.py to create default settings
        subprocess.run([sys.executable, "init_auth.py"])


def run_api_server(host="0.0.0.0", port=8000, reload=True):
    """Run API server"""
    print(f"Starting API server on {host}:{port}...")
    uvicorn.run("backend.api.main:app", host=host, port=port, reload=reload)


def run_tests(test_type=None):
    """Run tests"""
    if test_type == "mfa" or test_type is None:
        print("Running MFA tests...")
        subprocess.run([sys.executable, "test_mfa.py"])

    if test_type == "rbac" or test_type is None:
        print("Running auth/RBAC tests...")
        subprocess.run([sys.executable, "test_auth_rbac.py"])


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run NoxSuite MFA and RBAC implementation"
    )

    # Add subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # API server parser
    api_parser = subparsers.add_parser("api", help="Run API server")
    api_parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to bind to"
    )
    api_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to")
    api_parser.add_argument(
        "--no-reload", action="store_true", help="Disable auto-reload"
    )

    # Init parser
    init_parser = subparsers.add_parser(
        "init", help="Initialize auth settings")

    # Test parser
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "--type", type=str, choices=["mfa", "rbac"], help="Test type to run"
    )

    # Docker parser
    docker_parser = subparsers.add_parser(
        "docker", help="Run with Docker Compose")
    docker_parser.add_argument(
        "--build", action="store_true", help="Build images before starting"
    )

    # Parse arguments
    args = parser.parse_args()

    # Run command
    if args.command == "api":
        init_auth_settings()
        run_api_server(args.host, args.port, not args.no_reload)
    elif args.command == "init":
        init_auth_settings()
    elif args.command == "test":
        run_tests(args.type)
    elif args.command == "docker":
        cmd = ["docker-compose", "up"]
        if args.build:
            cmd.append("--build")
        subprocess.run(cmd)
    else:
        # Default to running API server
        init_auth_settings()
        run_api_server()


if __name__ == "__main__":
    main()
