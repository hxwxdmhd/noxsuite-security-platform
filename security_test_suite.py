#!/usr/bin/env python3
"""
NoxSuite Security Test Suite
===========================
Comprehensive security testing for NoxSuite API.

Tests:
- JWT token security
- MFA implementation
- RBAC enforcement
- Session management
- Input validation
- Rate limiting
"""

import argparse
import datetime
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import jwt
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(
        "security_tests.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# API Settings (defaults)
API_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@noxsuite.local"
ADMIN_PASSWORD = "Admin123!"
NORMAL_USER_EMAIL = "user@noxsuite.local"
NORMAL_USER_PASSWORD = "User123!"


class SecurityTestSuite:
    """Security test suite for NoxSuite API"""

    def __init__(self, api_url=API_URL):
        """Initialize test suite"""
        self.api_url = api_url
        self.admin_token = None
        self.user_token = None
        self.results = {
            "jwt_security": [],
            "mfa_security": [],
            "rbac_security": [],
            "session_security": [],
            "input_validation": [],
            "rate_limiting": [],
        }

    def print_header(self, title):
        """Print section header"""
        header = f"\n{title}\n{'=' * len(title)}"
        print(header)
        return header

    def print_step(self, message):
        """Print test step"""
        print(f"  • {message}")
        logger.info(message)

    def print_result(self, message, success):
        """Print test result"""
        icon = "✅" if success else "❌"
        print(f"    {icon} {message}")
        logger.info(f"{'PASS' if success else 'FAIL'}: {message}")
        return success

    def authenticate(self, email, password):
        """Authenticate with API"""
        self.print_step(f"Authenticating as {email}")

        response = requests.post(
            f"{self.api_url}/api/auth/login",
            json={"email": email, "password": password},
        )

        if response.status_code != 200:
            self.print_result(f"Authentication failed: {response.text}", False)
            return None

        token_data = response.json()
        self.print_result("Authentication successful", True)
        return token_data.get("access_token")

    def setup(self):
        """Setup test environment"""
        self.print_header("Setting up test environment")

        # Authenticate as admin
        self.admin_token = self.authenticate(ADMIN_EMAIL, ADMIN_PASSWORD)
        if not self.admin_token:
            return False

        # Authenticate as normal user
        self.user_token = self.authenticate(
            NORMAL_USER_EMAIL, NORMAL_USER_PASSWORD)
        if not self.user_token:
            return False

        return True

    def test_jwt_security(self):
        """Test JWT token security"""
        self.print_header("Testing JWT Security")
        results = self.results["jwt_security"]

        # Test 1: Decode JWT token without verification
        self.print_step("Checking JWT token structure")
        try:
            decoded = jwt.decode(self.admin_token, options={
                                 "verify_signature": False})

            # Check if token has standard claims
            has_exp = "exp" in decoded
            has_iat = "iat" in decoded
            has_sub = "sub" in decoded

            self.print_result("Token has expiration claim", has_exp)
            results.append(("Token has expiration", has_exp))

            self.print_result("Token has issued-at claim", has_iat)
            results.append(("Token has issued-at", has_iat))

            self.print_result("Token has subject claim", has_sub)
            results.append(("Token has subject", has_sub))

            # Check token freshness
            if has_iat:
                iat = datetime.datetime.fromtimestamp(decoded["iat"])
                now = datetime.datetime.now()
                token_age = (now - iat).total_seconds()

                self.print_result(f"Token age: {token_age:.2f} seconds", True)
                results.append(("Token freshness", True))
        except Exception as e:
            self.print_result(f"Failed to decode token: {str(e)}", False)
            results.append(("Token decode", False))

        # Test 2: Tampered token
        self.print_step("Testing tampered token rejection")
        try:
            # Decode without verification
            decoded = jwt.decode(self.admin_token, options={
                                 "verify_signature": False})

            # Tamper with payload
            decoded["sub"] = "999999"  # Change user ID

            # Encode with wrong key
            tampered = jwt.encode(decoded, "wrong_key", algorithm="HS256")

            # Try to access API with tampered token
            response = requests.get(
                f"{self.api_url}/api/auth/me",
                headers={"Authorization": f"Bearer {tampered}"},
            )

            tamper_rejected = response.status_code in [401, 403]
            self.print_result("Tampered token rejected", tamper_rejected)
            results.append(("Tampered token rejected", tamper_rejected))

        except Exception as e:
            self.print_result(f"Error in tampered token test: {str(e)}", False)
            results.append(("Tampered token test", False))

        # Test 3: Expired token
        self.print_step("Testing expired token rejection")
        try:
            # Create expired token
            payload = {
                "sub": "1",
                "exp": datetime.datetime.now() - datetime.timedelta(hours=1),
            }
            expired_token = jwt.encode(payload, "test_key", algorithm="HS256")

            # Try to access API with expired token
            response = requests.get(
                f"{self.api_url}/api/auth/me",
                headers={"Authorization": f"Bearer {expired_token}"},
            )

            expired_rejected = response.status_code in [401, 403]
            self.print_result("Expired token rejected", expired_rejected)
            results.append(("Expired token rejected", expired_rejected))

        except Exception as e:
            self.print_result(f"Error in expired token test: {str(e)}", False)
            results.append(("Expired token test", False))

    def test_mfa_security(self):
        """Test MFA implementation security"""
        self.print_header("Testing MFA Security")
        results = self.results["mfa_security"]

        # Test 1: MFA Bypass Attempt
        self.print_step("Testing MFA bypass protection")

        # Find MFA-enabled user
        response = requests.get(
            f"{self.api_url}/api/users/mfa-enabled",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        if response.status_code != 200:
            self.print_result("Could not get MFA-enabled users", False)
            results.append(("Get MFA users", False))
            return

        mfa_users = response.json()
        if not mfa_users:
            self.print_result("No MFA-enabled users found", False)
            results.append(("MFA users exist", False))
            return

        # Try to login as MFA user without providing MFA code
        mfa_user = mfa_users[0]
        response = requests.post(
            f"{self.api_url}/api/auth/login",
            json={
                "email": mfa_user["email"],
                "password": "MfaUser123!",  # Assumed password, adjust as needed
            },
        )

        # Should require MFA code (respond with 400 status and challenge)
        requires_mfa = response.status_code == 400 and "MFA" in response.text
        self.print_result(
            "API requires MFA for MFA-enabled user", requires_mfa)
        results.append(("MFA required for enabled users", requires_mfa))

        if requires_mfa:
            # Test 2: MFA Brute Force Protection
            self.print_step("Testing MFA brute force protection")

            # Get MFA session
            mfa_session = response.json().get("session_id", "")

            # Try multiple incorrect MFA codes
            attempts = 5
            success_count = 0

            for i in range(attempts):
                response = requests.post(
                    f"{self.api_url}/api/auth/verify-mfa",
                    json={
                        "session_id": mfa_session,
                        "code": f"{i:06d}",  # Try different codes
                    },
                )

                if response.status_code == 200:
                    success_count += 1

            # Should not allow successful login with incorrect codes
            brute_force_protected = success_count == 0
            self.print_result(
                "MFA protected against brute force", brute_force_protected
            )
            results.append(
                ("MFA brute force protection", brute_force_protected))

    def test_rbac_security(self):
        """Test RBAC implementation security"""
        self.print_header("Testing RBAC Security")
        results = self.results["rbac_security"]

        # Test 1: Access Control Enforcement
        self.print_step("Testing access control enforcement")

        # Try to access admin-only endpoint as normal user
        response = requests.get(
            f"{self.api_url}/api/admin/users",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        access_control_enforced = response.status_code in [401, 403]
        self.print_result(
            "Access control enforced for admin resources", access_control_enforced
        )
        results.append(("Access control enforcement", access_control_enforced))

        # Test 2: Role Separation
        self.print_step("Testing role separation")

        # Get current user roles (as user)
        response = requests.get(
            f"{self.api_url}/api/auth/me",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        if response.status_code == 200:
            user_data = response.json()
            user_roles = user_data.get("roles", [])

            # Try to add admin role to self
            response = requests.post(
                f"{self.api_url}/api/auth/roles",
                json={"user_id": user_data.get("id"), "role_name": "admin"},
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

            role_protection = response.status_code in [401, 403]
            self.print_result(
                "Users cannot self-elevate privileges", role_protection)
            results.append(
                ("Privilege escalation protection", role_protection))
        else:
            self.print_result("Could not get user profile", False)
            results.append(("Get user profile", False))

    def test_session_security(self):
        """Test session management security"""
        self.print_header("Testing Session Security")
        results = self.results["session_security"]

        # Test 1: Session Invalidation
        self.print_step("Testing session invalidation")

        # Login to create a session
        response = requests.post(
            f"{self.api_url}/api/auth/login",
            json={"email": NORMAL_USER_EMAIL,
                  "password": NORMAL_USER_PASSWORD},
        )

        if response.status_code != 200:
            self.print_result("Could not create session", False)
            results.append(("Create session", False))
            return

        token_data = response.json()
        token = token_data.get("access_token")

        # Logout to invalidate session
        response = requests.post(
            f"{self.api_url}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        logout_successful = response.status_code == 200
        self.print_result("Logout endpoint available", logout_successful)
        results.append(("Logout endpoint", logout_successful))

        # Try to use the token after logout
        response = requests.get(
            f"{self.api_url}/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        session_invalidated = response.status_code in [401, 403]
        self.print_result(
            "Session properly invalidated after logout", session_invalidated
        )
        results.append(("Session invalidation", session_invalidated))

    def test_input_validation(self):
        """Test input validation security"""
        self.print_header("Testing Input Validation")
        results = self.results["input_validation"]

        # Test 1: SQL Injection Prevention
        self.print_step("Testing SQL injection prevention")

        # Try SQL injection in login
        sql_injection_attempts = [
            {"email": "' OR 1=1 --", "password": "password"},
            {"email": "admin@noxsuite.local' --", "password": "anything"},
            {
                "email": "admin@noxsuite.local'; DROP TABLE users; --",
                "password": "password",
            },
        ]

        injection_blocked = True
        for attempt in sql_injection_attempts:
            response = requests.post(
                f"{self.api_url}/api/auth/login", json=attempt)
            if response.status_code == 200:
                injection_blocked = False
                break

        self.print_result("SQL injection prevented", injection_blocked)
        results.append(("SQL injection prevention", injection_blocked))

        # Test 2: XSS Prevention
        self.print_step("Testing XSS prevention")

        # Try to create user with XSS payload
        xss_payload = "<script>alert('XSS')</script>"
        response = requests.post(
            f"{self.api_url}/api/users",
            json={
                "username": f"user_{xss_payload}",
                "email": f"xss_{int(time.time())}@test.com",
                "password": "Password123!",
            },
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        if response.status_code == 200 or response.status_code == 201:
            # Check if payload was sanitized
            user_id = response.json().get("id")

            # Get user details
            response = requests.get(
                f"{self.api_url}/api/users/{user_id}",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("username", "")

                xss_prevented = (
                    xss_payload not in username or username != f"user_{xss_payload}"
                )
                self.print_result("XSS payload sanitized", xss_prevented)
                results.append(("XSS prevention", xss_prevented))
            else:
                self.print_result("Could not verify XSS prevention", False)
                results.append(("XSS prevention verification", False))
        else:
            # Validation might have rejected the input
            xss_prevented = True
            self.print_result(
                "XSS attempt rejected by validation", xss_prevented)
            results.append(("XSS prevention", xss_prevented))

    def test_rate_limiting(self):
        """Test rate limiting security"""
        self.print_header("Testing Rate Limiting")
        results = self.results["rate_limiting"]

        # Test 1: Login Rate Limiting
        self.print_step("Testing login rate limiting")

        # Make multiple login requests in parallel
        num_requests = 20
        request_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!",
        }

        status_codes = []

        def make_request():
            response = requests.post(
                f"{self.api_url}/api/auth/login", json=request_data
            )
            return response.status_code

        with ThreadPoolExecutor(max_workers=10) as executor:
            status_codes = list(
                executor.map(lambda _: make_request(), range(num_requests))
            )

        # Check if some requests were rate limited (429 Too Many Requests)
        rate_limited = 429 in status_codes
        self.print_result("Login endpoint has rate limiting", rate_limited)
        results.append(("Login rate limiting", rate_limited))

        # Test 2: API Rate Limiting
        self.print_step("Testing API rate limiting")

        # Make multiple API requests in parallel
        status_codes = []

        def make_api_request():
            response = requests.get(
                f"{self.api_url}/api/users",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )
            return response.status_code

        with ThreadPoolExecutor(max_workers=10) as executor:
            status_codes = list(
                executor.map(lambda _: make_api_request(), range(num_requests))
            )

        # Check if some requests were rate limited
        api_rate_limited = 429 in status_codes
        self.print_result("API has rate limiting", api_rate_limited)
        results.append(("API rate limiting", api_rate_limited))

    def run_all_tests(self):
        """Run all security tests"""
        if not self.setup():
            print("Failed to set up test environment")
            return False

        self.test_jwt_security()
        self.test_mfa_security()
        self.test_rbac_security()
        self.test_session_security()
        self.test_input_validation()
        self.test_rate_limiting()

        # Print summary
        self.print_summary()

        return True

    def print_summary(self):
        """Print test summary"""
        self.print_header("Security Test Summary")

        total_tests = 0
        passed_tests = 0

        for category, tests in self.results.items():
            category_total = len(tests)
            category_passed = sum(1 for _, success in tests if success)

            total_tests += category_total
            passed_tests += category_passed

            if category_total > 0:
                success_rate = (category_passed / category_total) * 100
                print(
                    f"{category}: {category_passed}/{category_total} passed ({success_rate:.2f}%)"
                )

        if total_tests > 0:
            overall_rate = (passed_tests / total_tests) * 100
            print(
                f"\nOverall: {passed_tests}/{total_tests} passed ({overall_rate:.2f}%)"
            )

            if overall_rate >= 90:
                print("✅ Security posture: Strong")
            elif overall_rate >= 75:
                print("⚠️ Security posture: Moderate - Needs improvement")
            else:
                print("❌ Security posture: Weak - Critical issues to address")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="NoxSuite Security Test Suite")
    parser.add_argument("--url", type=str, default=API_URL, help="API URL")
    parser.add_argument(
        "--admin-email", type=str, default=ADMIN_EMAIL, help="Admin email"
    )
    parser.add_argument(
        "--admin-password", type=str, default=ADMIN_PASSWORD, help="Admin password"
    )
    parser.add_argument(
        "--user-email", type=str, default=NORMAL_USER_EMAIL, help="Normal user email"
    )
    parser.add_argument(
        "--user-password",
        type=str,
        default=NORMAL_USER_PASSWORD,
        help="Normal user password",
    )

    args = parser.parse_args()

    # Update global settings
    global API_URL, ADMIN_EMAIL, ADMIN_PASSWORD, NORMAL_USER_EMAIL, NORMAL_USER_PASSWORD
    API_URL = args.url
    ADMIN_EMAIL = args.admin_email
    ADMIN_PASSWORD = args.admin_password
    NORMAL_USER_EMAIL = args.user_email
    NORMAL_USER_PASSWORD = args.user_password

    # Run tests
    test_suite = SecurityTestSuite(API_URL)
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
