import os
#!/usr/bin/env python3
"""
NoxSuite Development Integration Test
This script tests the integration of the newly implemented modules.
"""

import json
import sys

from auth.jwt_utils import JWTManager
from auth.user_model import TokenResponse, User, UserCredentials


def test_auth_module():
    """Test the JWT authentication module"""
    print("Testing Auth Module...")

    # Create JWT Manager
    jwt_manager = JWTManager(secret_key = os.getenv("JWT_SECRET_KEY", "development-test-key"))

    # Create a test payload
    payload = {"user_id": "test123", "username": "testuser", "role": "admin"}

    # Create a token
    token = jwt_manager.create_token(payload)
    print(f"Generated JWT Token: {token[:15]}...{token[-15:]}")

    # Verify the token
    decoded = jwt_manager.verify_token(token)

    if decoded and decoded["user_id"] == payload["user_id"]:
        print("✅ JWT Token verification successful")
        return True
    else:
        print("❌ JWT Token verification failed")
        return False


def test_user_model():
    """Test the user model classes"""
    print("\nTesting User Models...")

    # Test User model
    try:
        user = User(
            id="test123", username="testuser", email="test@example.com", role="admin"
        )
        print(f"User model: {user.model_dump()}")
        print("✅ User model created successfully")
    except Exception as e:
        print(f"❌ User model creation failed: {e}")
        return False

    # Test UserCredentials model
    try:
        credentials = UserCredentials(
            username="testuser", password=os.getenv("NOXSUITE_DEFAULT_PASSWORD", "password123"))
        print(f"UserCredentials model: {credentials.model_dump()}")
        print("✅ UserCredentials model created successfully")
    except Exception as e:
        print(f"❌ UserCredentials model creation failed: {e}")
        return False

    # Test TokenResponse model
    try:
        token_response = TokenResponse(
            access_token="sample-jwt-token", expires_in=3600)
        print(f"TokenResponse model: {token_response.model_dump()}")
        print("✅ TokenResponse model created successfully")
        return True
    except Exception as e:
        print(f"❌ TokenResponse model creation failed: {e}")
        return False


def run_tests():
    """Run all integration tests"""
    print("Running NoxSuite Development Integration Tests\n" + "=" * 50)

    results = {"auth_module": test_auth_module(
    ), "user_model": test_user_model()}

    print("\nTest Summary:")
    print("=" * 50)
    for test, result in results.items():
        print(f"{test}: {'✅ PASS' if result else '❌ FAIL'}")

    all_passed = all(results.values())
    print(
        "\nOverall Result:",
        "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED",
    )

    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
