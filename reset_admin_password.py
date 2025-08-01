#!/usr/bin/env python3
"""
Reset NoxSuite Admin Password
===========================
Reset the admin password to a known value
"""

import logging
import os
import sys
from datetime import datetime

import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to Python path
sys.path.append(os.getcwd())


def reset_admin_password():
    """Reset admin password to Admin123!"""
    try:
        # Import models
        from mariadb_dev_setup import MariaDBDevSetup, User

        # Create DB setup
        setup = MariaDBDevSetup()
        SessionLocal = setup.SessionLocal

        # Create session
        db = SessionLocal()

        # Find admin user
        admin = db.query(User).filter_by(username="admin").first()

        if not admin:
            logger.error("❌ Admin user not found")
            return False

        # Generate new password hash
        new_hash = bcrypt.hashpw("Admin123!".encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        # Update admin password
        admin.password_hash = new_hash

        # Commit changes
        db.commit()
        logger.info(
            f"✅ Admin password reset for {admin.username} ({admin.email})")

        # Verify password
        if admin.verify_password("Admin123!"):
            logger.info("✅ Password verification successful")
        else:
            logger.error("❌ Password verification failed")
            return False

        # Try to create regular user if missing
        user = db.query(User).filter_by(username="user").first()
        if not user:
            # Create user
            user_hash = bcrypt.hashpw(
                "User123!".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user = User(
                username="user",
                email="user@noxsuite.local",
                password_hash=user_hash,
                is_active=True,
                is_admin=False,
                created_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            logger.info(
                f"✅ Created user account: {user.username} ({user.email})")

        # Close session
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Password reset failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("Resetting admin password...")

    if reset_admin_password():
        logger.info("✅ Admin password reset complete")
        sys.exit(0)
    else:
        logger.error("❌ Admin password reset failed")
        sys.exit(1)
