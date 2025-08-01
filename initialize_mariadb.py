#!/usr/bin/env python3
"""
MariaDB Initializer for NoxSuite
===============================
Creates and initializes MariaDB database with admin and test users
"""

import sys
import os
import logging
import bcrypt
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to Python path
sys.path.append(os.getcwd())

def initialize_database():
    """Initialize MariaDB database with initial users and roles"""
    try:
        # Import models
        from mariadb_dev_setup import User, Role, UserRole, Base, MariaDBDevSetup
        
        # Create DB setup
        setup = MariaDBDevSetup()
        engine = setup.engine
        SessionLocal = setup.SessionLocal
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
        
        # Create session
        db = SessionLocal()
        
        # Check if tables are already populated
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info(f"⚠️ Database already has {existing_users} users")
        else:
            # Create admin user
            admin_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), 
                                       bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username="admin",
                email="admin@noxsuite.local",
                password_hash=admin_hash,
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow()
            )
            db.add(admin)
            
            # Create regular user
            user_hash = bcrypt.hashpw("User123!".encode('utf-8'), 
                                     bcrypt.gensalt()).decode('utf-8')
            user = User(
                username="user",
                email="user@noxsuite.local",
                password_hash=user_hash,
                is_active=True,
                is_admin=False,
                created_at=datetime.utcnow()
            )
            db.add(user)
            
            # Create roles
            admin_role = Role(name="admin", 
                            description="Administrator role with all permissions")
            user_role = Role(name="user", 
                           description="Regular user with limited permissions")
            db.add(admin_role)
            db.add(user_role)
            
            # Commit to get IDs
            db.commit()
            
            # Link users to roles
            admin_user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
            user_user_role = UserRole(user_id=user.id, role_id=user_role.id)
            db.add(admin_user_role)
            db.add(user_user_role)
            
            # Final commit
            db.commit()
            logger.info("✅ Created admin and user accounts with proper roles")
        
        # Validate users
        users = db.query(User).all()
        for user in users:
            logger.info(f"User: {user.username} ({user.email}), Admin: {user.is_admin}")
            
        # Test password verification
        admin = db.query(User).filter_by(username="admin").first()
        if admin:
            if admin.verify_password("Admin123!"):
                logger.info("✅ Admin password verification works")
            else:
                logger.error("❌ Admin password verification failed")
                
        # Close session
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Initializing MariaDB database...")
    
    if initialize_database():
        logger.info("✅ Database initialization complete")
        sys.exit(0)
    else:
        logger.error("❌ Database initialization failed")
        sys.exit(1)
