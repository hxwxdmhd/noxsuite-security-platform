#!/usr/bin/env python3
"""
TestSprite Simplified Adapter for NoxSuite Auth Testing
======================================================
Simplified test script to validate authentication, RBAC, and MFA functionality
"""

import argparse
import json
import logging
import time
from datetime import datetime

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Settings
API_URL = "http://localhost:8000"

# Test credentials
ADMIN_CREDS = {"email": "admin@noxsuite.local", "password": "Admin123!"}
USER_CREDS = {"email": "user@noxsuite.local", "password": "User123!"}


def print_header(title):
    """Print section header"""
    header = f"\n{title}\n{'=' * len(title)}"
    print(header)
    return header


def print_step(step):
    """Print test step"""
    msg = f">> {step}"
    print(msg)
    return msg


def print_result(message, success=True):
    """Print test result"""
    if success:
        msg = f"✅ {message}"
        print(msg)
    else:
        msg = f"❌ {message}"
        print(msg)
    return (msg, success)


def api_request(method, endpoint, data=None, headers=None, expected_status=None):
    """Make an API request and return response"""
    url = f"{API_URL}/{endpoint}"

    if headers is None:
        headers = {}

    try:
        start_time = time.time()

        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        elapsed = time.time() - start_time

        try:
            response_data = response.json()
        except:
            response_data = {"text": response.text}

        # Check status code if expected
        if expected_status and response.status_code != expected_status:
            logger.warning(
                f"Expected status {expected_status}, got {response.status_code}"
            )
            logger.warning(f"Response: {response_data}")

        return response, response_data, elapsed
    except Exception as e:
        logger.error(f"Error making {method} request to {url}: {e}")
        return None, {"error": str(e)}, 0


def login(credentials):
    """Login with credentials"""
    response, data, elapsed = api_request(
        "post", "api/auth/login", data=credentials, expected_status=200
    )

    if response and response.status_code == 200 and "access_token" in data:
        token = data["access_token"]
        return token, data, elapsed

    return None, data, elapsed


def auth_header(token):
    """Create authentication header"""
    return {"Authorization": f"Bearer {token}"} if token else {}


def test_auth():
    """Test authentication endpoints"""
    section = print_header("Testing Authentication")
    results = []

    # Health check
    step = print_step("Testing health check endpoint")
    response, data, elapsed = api_request("get", "health", expected_status=200)
    success = response and response.status_code == 200
    results.append(print_result("Health check", success))

    # Login as admin - should succeed
    step = print_step("Testing admin login")
    admin_token, admin_data, elapsed = login(ADMIN_CREDS)
    success = admin_token is not None
    results.append(print_result("Admin login", success))

    # Get authenticated user - should succeed
    if admin_token:
        step = print_step("Testing authenticated user info")
        headers = auth_header(admin_token)
        response, data, elapsed = api_request(
            "get", "api/auth/me", headers=headers, expected_status=200
        )
        success = response and response.status_code == 200
        results.append(print_result("Get authenticated user", success))

    # Login with invalid credentials - should fail
    step = print_step("Testing invalid login")
    response, data, elapsed = api_request(
        "post",
        "api/auth/login",
        data={"email": "admin@noxsuite.local", "password": "wrong"},
        expected_status=401,
    )
    success = response and response.status_code == 401
    results.append(print_result("Invalid login rejected", success))

    return {
        "section": section,
        "tests": results,
        "passed": all(result[1] for result in results),
        "total": len(results),
        "passed_count": sum(1 for result in results if result[1]),
    }


def test_rbac():
    """Test RBAC functionality"""
    section = print_header("Testing RBAC Functionality")
    results = []

    # Login as admin
    admin_token, _, _ = login(ADMIN_CREDS)

    # Login as regular user
    user_token, _, _ = login(USER_CREDS)

    # Check if RBAC endpoints are available
    step = print_step("Testing RBAC endpoints availability")
    headers = auth_header(admin_token)
    response, data, elapsed = api_request("get", "api/roles", headers=headers)
    success = response and response.status_code == 200
    results.append(print_result("RBAC endpoints available", success))

    return {
        "section": section,
        "tests": results,
        "passed": all(result[1] for result in results),
        "total": len(results),
        "passed_count": sum(1 for result in results if result[1]),
    }


def test_mfa():
    """Test MFA functionality"""
    section = print_header("Testing MFA Functionality")
    results = []

    # Login as admin
    admin_token, _, _ = login(ADMIN_CREDS)

    # Check if MFA setup endpoint is available
    step = print_step("Testing MFA setup endpoint")
    headers = auth_header(admin_token)
    response, data, elapsed = api_request(
        "get", "api/auth/mfa/setup", headers=headers)
    success = response and (response.status_code ==
                            200 or response.status_code == 400)
    results.append(print_result("MFA setup endpoint available", success))

    return {
        "section": section,
        "tests": results,
        "passed": all(result[1] for result in results),
        "total": len(results),
        "passed_count": sum(1 for result in results if result[1]),
    }


def run_all_tests():
    """Run all tests and generate report"""
    print_header("NoxSuite API Testing Suite")

    start_time = time.time()
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "auth_tests": {},
        "rbac_tests": {},
        "mfa_tests": {},
    }

    # Run authentication tests
    test_results["auth_tests"] = test_auth()

    # Run RBAC tests
    test_results["rbac_tests"] = test_rbac()

    # Run MFA tests
    test_results["mfa_tests"] = test_mfa()

    # Calculate overall metrics
    total_tests = (
        test_results["auth_tests"]["total"]
        + test_results["rbac_tests"]["total"]
        + test_results["mfa_tests"]["total"]
    )

    passed_tests = (
        test_results["auth_tests"]["passed_count"]
        + test_results["rbac_tests"]["passed_count"]
        + test_results["mfa_tests"]["passed_count"]
    )

    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    # Generate summary
    print_header("Test Results Summary")
    print(
        f"Authentication: {test_results['auth_tests']['passed_count']}/{test_results['auth_tests']['total']} tests passed"
    )
    print(
        f"RBAC: {test_results['rbac_tests']['passed_count']}/{test_results['rbac_tests']['total']} tests passed"
    )
    print(
        f"MFA: {test_results['mfa_tests']['passed_count']}/{test_results['mfa_tests']['total']} tests passed"
    )
    print(
        f"Overall: {passed_tests}/{total_tests} tests passed ({pass_rate:.2f}%)")

    # Save results to file
    test_results["overall"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "pass_rate": pass_rate,
        "duration_seconds": time.time() - start_time,
    }

    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    return pass_rate >= 95


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TestSprite Simplified Adapter")
    parser.add_argument("--full", action="store_true", help="Run all tests")
    parser.add_argument("--auth", action="store_true",
                        help="Run authentication tests")
    parser.add_argument("--rbac", action="store_true", help="Run RBAC tests")
    parser.add_argument("--mfa", action="store_true", help="Run MFA tests")
    args = parser.parse_args()

    if args.full or (not args.auth and not args.rbac and not args.mfa):
        success = run_all_tests()
        sys.exit(0 if success else 1)

    if args.auth:
        test_auth()

    if args.rbac:
        test_rbac()

    if args.mfa:
        test_mfa()
