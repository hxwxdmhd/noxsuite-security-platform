#!/usr/bin/env python3
"""
Quick API Test Script
====================
Test the FastAPI server endpoints.
"""

import json

import requests

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_register():
    """Test registration endpoint"""
    print("\nTesting registration endpoint...")
    data = {
        "username": "testuser",
        "email": "test@noxsuite.com",
        "password": "Test123!",
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_login():
    """Test login endpoint"""
    print("\nTesting login endpoint...")
    data = {"email": "admin@noxsuite.local", "password": "Admin123!"}

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print(f"Error: {e}")
    return None


def test_protected_endpoint(token):
    """Test protected endpoint"""
    print("\nTesting protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("NoxSuite FastAPI Quick Test")
    print("=" * 40)

    tests_passed = 0
    total_tests = 0

    # Test health
    total_tests += 1
    if test_health():
        tests_passed += 1
        print("✓ Health check passed")
    else:
        print("✗ Health check failed")

    # Test registration
    total_tests += 1
    if test_register():
        tests_passed += 1
        print("✓ Registration passed")
    else:
        print("✗ Registration failed")

    # Test login
    total_tests += 1
    token = test_login()
    if token:
        tests_passed += 1
        print("✓ Login passed")

        # Test protected endpoint
        total_tests += 1
        if test_protected_endpoint(token):
            tests_passed += 1
            print("✓ Protected endpoint passed")
        else:
            print("✗ Protected endpoint failed")
    else:
        print("✗ Login failed")
        total_tests += 1  # Count the protected endpoint test as failed too
        print("✗ Protected endpoint skipped (no token)")

    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")

    if tests_passed == total_tests:
        print("🎉 All tests passed! FastAPI server is working correctly!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
