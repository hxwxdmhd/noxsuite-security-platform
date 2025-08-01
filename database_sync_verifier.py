#!/usr/bin/env python3
"""
Database Synchronization Verification Tool
==========================================
Tests FastAPI server database connection and user authentication directly
"""

import pymysql
import bcrypt
import sys
import os
import logging

# Add current directory to Python path
sys.path.append(os.getcwd())

try:
    from mariadb_dev_setup import MariaDBDevSetup, User
    setup = MariaDBDevSetup()
    SessionLocal = setup.SessionLocal
    print("✅ MariaDBDevSetup imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSyncVerifier:
    """Verify database synchronization with FastAPI server"""
    
    def __init__(self):
        self.db_session = SessionLocal()
        self.test_results = {
            "database_connection": False,
            "users_found": 0,
            "admin_password_test": False,
            "mfa_password_test": False,
            "server_compatibility": False
        }
    
    def verify_database_connection(self):
        """Test database connectivity"""
        try:
            # Test basic query
            user_count = self.db_session.query(User).count()
            self.test_results["database_connection"] = True
            self.test_results["users_found"] = user_count
            
            logger.info(f"✅ Database connected: {user_count} users found")
            
            # List all users
            users = self.db_session.query(User).all()
            for user in users:
                logger.info(f"User: {user.username} ({user.email}) - MFA: {user.mfa_enabled}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def test_user_authentication(self, username, password):
        """Test user authentication matching FastAPI logic"""
        try:
            # Find user by username (convert to email for FastAPI compatibility)
            if username == "admin":
                email = "admin@noxsuite.local"
            elif username == "mfa_test":
                email = "mfa_test@noxsuite.local"
            else:
                email = f"{username}@noxsuite.local"
            
            user = self.db_session.query(User).filter(User.email == email).first()
            
            if not user:
                logger.error(f"❌ User not found: {email}")
                return False
            
            logger.info(f"Found user: {user.username} ({user.email})")
            logger.info(f"Hash: {user.password_hash[:50]}...")
            
            # Test password verification using bcrypt directly
            is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
            
            if is_valid:
                logger.info(f"✅ Password verification successful for {username}")
                if username == "admin":
                    self.test_results["admin_password_test"] = True
                elif username == "mfa_test":
                    self.test_results["mfa_password_test"] = True
                return True
            else:
                logger.error(f"❌ Password verification failed for {username}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed for {username}: {e}")
            return False
    
    def test_user_model_method(self, username, password):
        """Test using User model's verify_password method if available"""
        try:
            if username == "admin":
                email = "admin@noxsuite.local"
            else:
                email = "mfa_test@noxsuite.local"
                
            user = self.db_session.query(User).filter(User.email == email).first()
            
            if hasattr(user, 'verify_password'):
                result = user.verify_password(password)
                logger.info(f"User.verify_password() for {username}: {result}")
                return result
            else:
                logger.warning(f"User model has no verify_password method")
                return None
                
        except Exception as e:
            logger.error(f"❌ User model method test failed: {e}")
            return None
    
    def run_comprehensive_verification(self):
        """Run complete database sync verification"""
        logger.info("🔍 Starting database synchronization verification...")
        
        # Test database connection
        if not self.verify_database_connection():
            return False
        
        # Test admin authentication
        admin_bcrypt = self.test_user_authentication("admin", "admin123")
        admin_model = self.test_user_model_method("admin", "admin123")
        
        # Test MFA user authentication
        mfa_bcrypt = self.test_user_authentication("mfa_test", "user123")
        mfa_model = self.test_user_model_method("mfa_test", "user123")
        
        # Server compatibility check
        self.test_results["server_compatibility"] = admin_bcrypt and mfa_bcrypt
        
        logger.info("✅ Database sync verification completed")
        
        # Print summary
        print("\n🎯 DATABASE SYNC VERIFICATION SUMMARY")
        print(f"✅ Database connected: {self.test_results['database_connection']}")
        print(f"✅ Users found: {self.test_results['users_found']}")
        print(f"✅ Admin auth (bcrypt): {admin_bcrypt}")
        print(f"✅ Admin auth (model): {admin_model}")
        print(f"✅ MFA auth (bcrypt): {mfa_bcrypt}")
        print(f"✅ MFA auth (model): {mfa_model}")
        print(f"✅ Server compatibility: {self.test_results['server_compatibility']}")
        
        return self.test_results["server_compatibility"]
    
    def __del__(self):
        if hasattr(self, 'db_session'):
            self.db_session.close()

if __name__ == "__main__":
    verifier = DatabaseSyncVerifier()
    success = verifier.run_comprehensive_verification()
    
    if success:
        print("🎯 DATABASE SYNC: ✅ VERIFIED")
    else:
        print("🎯 DATABASE SYNC: ❌ FAILED")
