#!/usr/bin/env python3
"""
User Model Verification Tool
===========================
Directly tests authentication with the User model.
"""

import importlib
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_user_model_imports():
    """Test importing the User model"""
    try:
        # Try direct import
        import mariadb_dev_setup

        importlib.reload(mariadb_dev_setup)  # Force reload

        # Check User model
        User = getattr(mariadb_dev_setup, "User", None)
        if User:
            logger.info(f"✅ User model imported: {User}")
        else:
            logger.error("❌ User model not found in mariadb_dev_setup")
            return False

        # Check verify_password method
        verify_password = getattr(User, "verify_password", None)
        if verify_password:
            logger.info(f"✅ verify_password method found: {verify_password}")
        else:
            logger.error("❌ verify_password method not found in User model")
            return False

        # Check if it's callable
        if callable(
            getattr(User(password_hash="$2b$12$test"), "verify_password", None)
        ):
            logger.info("✅ verify_password is callable on User instances")
        else:
            logger.error("❌ verify_password is not callable on User instances")
            return False

        return True
    except Exception as e:
        logger.error(f"❌ Error importing User model: {e}")
        return False


def verify_fastapi_imports():
    """Test importing the FastAPI server"""
    try:
        # Try direct import
        import noxsuite_fastapi_server

        importlib.reload(noxsuite_fastapi_server)  # Force reload

        # Check imported User model
        User = getattr(noxsuite_fastapi_server, "User", None)
        if User:
            logger.info(f"✅ User model imported in FastAPI: {User}")

            # Check verify_password method
            verify_password = getattr(User, "verify_password", None)
            if verify_password:
                logger.info(
                    f"✅ verify_password method found in FastAPI User model: {verify_password}"
                )
            else:
                logger.error(
                    "❌ verify_password method not found in FastAPI User model"
                )
                return False
        else:
            logger.error("❌ User model not imported in FastAPI server")
            return False

        return True
    except Exception as e:
        logger.error(f"❌ Error importing FastAPI server: {e}")
        return False


def verify_rbac_mfa_imports():
    """Test importing the RBAC/MFA extension"""
    try:
        # Try direct import
        import rbac_mfa_extension

        importlib.reload(rbac_mfa_extension)  # Force reload

        # Check register_rbac_mfa_routes function
        register_func = getattr(
            rbac_mfa_extension, "register_rbac_mfa_routes", None)
        if register_func:
            logger.info(
                f"✅ register_rbac_mfa_routes function found: {register_func}")
        else:
            logger.error(
                "❌ register_rbac_mfa_routes function not found in RBAC/MFA extension"
            )
            return False

        return True
    except Exception as e:
        logger.error(f"❌ Error importing RBAC/MFA extension: {e}")
        return False


def test_direct_password_verification():
    """Test password verification directly"""
    try:
        # Create test user with bcrypt hash
        import bcrypt

        import mariadb_dev_setup

        # Get the User class
        User = mariadb_dev_setup.User

        # Generate test hash
        password=os.getenv("NOXSUITE_DEFAULT_PASSWORD", "Admin123!")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Create test user
        test_user = User(
            username="test",
            email="test@example.com",
            password_hash=hashed.decode("utf-8"),
        )

        # Test password verification
        if test_user.verify_password(password):
            logger.info("✅ Password verification works correctly")
            return True
        else:
            logger.error("❌ Password verification failed")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing password verification: {e}")
        return False


if __name__ == "__main__":
    # Clear any cached imports
    for module in [
        "mariadb_dev_setup",
        "noxsuite_fastapi_server",
        "rbac_mfa_extension",
    ]:
        if module in sys.modules:
            del sys.modules[module]

    print("\n===== Testing User Model Import =====")
    user_model_ok = verify_user_model_imports()

    print("\n===== Testing FastAPI Server Import =====")
    fastapi_ok = verify_fastapi_imports()

    print("\n===== Testing RBAC/MFA Extension Import =====")
    rbac_mfa_ok = verify_rbac_mfa_imports()

    print("\n===== Testing Direct Password Verification =====")
    password_ok = test_direct_password_verification()

    # Summary
    print("\n===== Import Verification Summary =====")
    print(f"User Model: {'✅ OK' if user_model_ok else '❌ Failed'}")
    print(f"FastAPI Server: {'✅ OK' if fastapi_ok else '❌ Failed'}")
    print(f"RBAC/MFA Extension: {'✅ OK' if rbac_mfa_ok else '❌ Failed'}")
    print(f"Password Verification: {'✅ OK' if password_ok else '❌ Failed'}")

    if user_model_ok and fastapi_ok and rbac_mfa_ok and password_ok:
        print("\n✅ All imports and verifications succeeded!")
        print(
            "You should now be able to restart the FastAPI server and authentication should work."
        )
    else:
        print("\n❌ Some verifications failed. Check the log for details.")
        print("You may need to restart Python to clear module caches completely.")
