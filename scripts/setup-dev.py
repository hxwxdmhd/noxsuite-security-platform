#!/usr/bin/env python3
"""
Development Environment Setup Script
Automates the setup of the NoxSuite development environment
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def setup_environment():
    """Set up development environment"""
    print("🚀 Setting up NoxSuite development environment...")

    # Install Python dependencies
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install requirements")
        return False

    # Install development dependencies
    dev_deps = [
        "black",
        "isort",
        "flake8",
        "mypy",
        "pytest",
        "pytest-cov",
        "pre-commit",
    ]
    if not run_command(f"pip install {' '.join(dev_deps)}"):
        print("❌ Failed to install dev dependencies")
        return False

    # Copy environment template
    if not Path(".env").exists() and Path(".env.template").exists():
        run_command("cp .env.template .env", check=False)
        print("📄 Created .env from template - please configure it")

    print("✅ Development environment setup complete!")
    return True


if __name__ == "__main__":
    setup_environment()
