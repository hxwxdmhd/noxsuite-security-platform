#!/usr/bin/env python3
"""
Test runner for NoxSuite Security Platform
"""
import subprocess
import sys
from pathlib import Path


def run_security_tests():
    """Run security tests"""
    print("🔒 Running security tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/security/', 
        '-v', '--tb=short'
    ], cwd=Path(__file__).parent)
    return result.returncode == 0


def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running unit tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/unit/', 
        '-v', '--tb=short'
    ], cwd=Path(__file__).parent)
    return result.returncode == 0


def run_all_tests():
    """Run all tests"""
    print("🚀 Running all tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/', 
        '-v', '--tb=short'
    ], cwd=Path(__file__).parent)
    return result.returncode == 0


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'security':
            success = run_security_tests()
        elif test_type == 'unit':
            success = run_unit_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available types: security, unit")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
