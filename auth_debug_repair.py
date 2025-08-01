#!/usr/bin/env python3
"""
Authentication Debug and Repair Tool
===================================
Diagnoses and fixes password hashing mismatches in FastAPI authentication
"""

import bcrypt
import pymysql
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationDebugger:
    """Debug authentication failures"""
    
    def __init__(self):
        self.debug_results = {
            "timestamp": datetime.now().isoformat(),
            "database_users": [],
            "password_tests": [],
            "hash_analysis": {},
            "fixes_applied": []
        }
    
    def analyze_database_users(self):
        """Analyze users in the current database"""
        try:
            conn = pymysql.connect("mariadb_dev_simulation.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, email, password_hash, mfa_enabled FROM users")
            users = cursor.fetchall()
            
            for user in users:
                user_data = {
                    "id": user[0],
                    "username": user[1], 
                    "email": user[2],
                    "password_hash": user[3][:50] + "...",
                    "mfa_enabled": user[4],
                    "hash_length": len(user[3])
                }
                self.debug_results["database_users"].append(user_data)
                
                logger.info(f"User: {user[1]} ({user[2]})")
                logger.info(f"  Hash length: {len(user[3])}")
                logger.info(f"  MFA enabled: {user[4]}")
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return []
    
    def test_password_verification(self, username, test_passwords):
        """Test password verification for specific user"""
        try:
            conn = pymysql.connect("mariadb_dev_simulation.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"User {username} not found")
                return
            
            stored_hash = result[0]
            
            for password in test_passwords:
                try:
                    # Test bcrypt verification
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
                    
                    test_result = {
                        "username": username,
                        "password": password,
                        "verified": is_valid,
                        "hash_prefix": stored_hash[:29]  # bcrypt identifier
                    }
                    
                    self.debug_results["password_tests"].append(test_result)
                    
                    logger.info(f"Password '{password}' for {username}: {'✅ VALID' if is_valid else '❌ INVALID'}")
                    
                    if is_valid:
                        logger.info(f"🎯 CORRECT PASSWORD FOUND: {password}")
                        
                except Exception as e:
                    logger.error(f"Password test failed for '{password}': {e}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Password verification test failed: {e}")
    
    def generate_correct_hash(self, username, correct_password):
        """Generate correct password hash and update database"""
        try:
            # Generate new hash with correct password
            new_hash = bcrypt.hashpw(correct_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            logger.info(f"Generated new hash for {username}")
            logger.info(f"New hash: {new_hash[:50]}...")
            
            # Update database
            conn = pymysql.connect("mariadb_dev_simulation.db")
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
            conn.commit()
            conn.close()
            
            self.debug_results["fixes_applied"].append({
                "username": username,
                "action": "password_hash_updated",
                "new_hash_prefix": new_hash[:29]
            })
            
            logger.info(f"✅ Password hash updated for {username}")
            
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
    
    def run_authentication_debug(self):
        """Complete authentication debugging"""
        logger.info("🔍 Starting authentication system debug...")
        
        # Analyze current database users
        users = self.analyze_database_users()
        
        # Test admin password variants
        admin_passwords = [
            "admin123",
            "AdminPassword123!",
            "admin",
            "password",
            "noxsuite123",
            "Admin123",
            "admin@123"
        ]
        
        self.test_password_verification("admin", admin_passwords)
        
        # Test MFA user passwords  
        mfa_passwords = [
            "MfaUser123!",
            "mfa_test",
            "password",
            "user123"
        ]
        
        self.test_password_verification("mfa_test", mfa_passwords)
        
        # Generate working credentials
        logger.info("🔧 Generating working test credentials...")
        self.generate_correct_hash("admin", "admin123")
        self.generate_correct_hash("mfa_test", "user123")
        
        # Save debug report
        with open("auth_debug_report.json", "w") as f:
            json.dump(self.debug_results, f, indent=2)
        
        logger.info("✅ Authentication debug completed")
        return self.debug_results

if __name__ == "__main__":
    debugger = AuthenticationDebugger()
    results = debugger.run_authentication_debug()
    
    print("🎯 AUTHENTICATION DEBUG SUMMARY")
    print(f"✅ Users analyzed: {len(results['database_users'])}")
    print(f"✅ Password tests: {len(results['password_tests'])}")
    print(f"✅ Fixes applied: {len(results['fixes_applied'])}")
