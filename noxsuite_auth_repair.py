#!/usr/bin/env python3
"""
NoxSuite Authentication System Repair
====================================
Comprehensive repair script to address authentication and authorization issues in NoxSuite
"""

import os
import sys
import json
import time
import pymysql
import bcrypt
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("auth_system_repair.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("AuthSystemRepair")

# Database connection settings
DB_PATH = "mariadb_dev_simulation.db"
API_URL = "http://localhost:8000"

class NoxSuiteAuthRepair:
    """Repair authentication system issues in NoxSuite"""
    
    def __init__(self):
        self.repair_results = {
            "timestamp": datetime.now().isoformat(),
            "database_repairs": [],
            "api_server_status": {},
            "authentication_tests": {},
            "repair_actions": []
        }
    
    def check_api_server(self) -> bool:
        """Check if the API server is running"""
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API server is running")
                self.repair_results["api_server_status"] = {
                    "status": "running",
                    "health_endpoint": "OK",
                    "response": response.json()
                }
                return True
            else:
                logger.warning(f"⚠️ API server returned non-200 status: {response.status_code}")
                self.repair_results["api_server_status"] = {
                    "status": "warning",
                    "health_endpoint": "Non-200 response",
                    "status_code": response.status_code
                }
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API server is not running or not accessible: {e}")
            self.repair_results["api_server_status"] = {
                "status": "error",
                "message": str(e)
            }
            return False
    
    def check_database_connection(self) -> bool:
        """Check if the SQLite database file exists and is accessible"""
        try:
            if not os.path.exists(DB_PATH):
                logger.error(f"❌ Database file not found: {DB_PATH}")
                self.repair_results["database_repairs"].append({
                    "action": "check_connection",
                    "success": False,
                    "message": f"Database file not found: {DB_PATH}"
                })
                return False
            
            conn = pymysql.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT mariadb_version();")
            version = cursor.fetchone()
            conn.close()
            
            logger.info(f"✅ Database connection successful (SQLite {version[0]})")
            self.repair_results["database_repairs"].append({
                "action": "check_connection",
                "success": True,
                "message": f"Database connection successful (SQLite {version[0]})"
            })
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.repair_results["database_repairs"].append({
                "action": "check_connection",
                "success": False,
                "message": f"Database connection failed: {e}"
            })
            return False
    
    def check_users_table(self) -> List[Dict]:
        """Check the users table structure and data"""
        try:
            conn = pymysql.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM mariadb_master WHERE type='table' AND name='users';")
            if not cursor.fetchone():
                logger.error("❌ Users table not found in database")
                conn.close()
                self.repair_results["database_repairs"].append({
                    "action": "check_users_table",
                    "success": False,
                    "message": "Users table not found in database"
                })
                return []
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            required_columns = ["id", "username", "email", "password_hash", "first_name", "last_name", "mfa_enabled"]
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                logger.error(f"❌ Missing columns in users table: {', '.join(missing_columns)}")
                self.repair_results["database_repairs"].append({
                    "action": "check_users_table",
                    "success": False,
                    "message": f"Missing columns in users table: {', '.join(missing_columns)}"
                })
            else:
                logger.info("✅ Users table has all required columns")
            
            # Get user data
            cursor.execute("SELECT id, username, email, password_hash, mfa_enabled FROM users")
            users = []
            for row in cursor.fetchall():
                user = {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "password_hash": row[3][:20] + "..." if row[3] else None,
                    "mfa_enabled": bool(row[4])
                }
                users.append(user)
            
            conn.close()
            
            logger.info(f"Found {len(users)} users in database")
            self.repair_results["database_repairs"].append({
                "action": "check_users_table",
                "success": True,
                "message": f"Found {len(users)} users in database",
                "user_count": len(users)
            })
            
            return users
        except sqlite3.Error as e:
            logger.error(f"❌ Error checking users table: {e}")
            self.repair_results["database_repairs"].append({
                "action": "check_users_table",
                "success": False,
                "message": f"Error checking users table: {e}"
            })
            return []
    
    def fix_admin_password(self) -> bool:
        """Fix the admin user password"""
        try:
            conn = pymysql.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if admin user exists
            cursor.execute("SELECT id, username, password_hash FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            if not admin:
                logger.error("❌ Admin user not found in database")
                self.repair_results["database_repairs"].append({
                    "action": "fix_admin_password",
                    "success": False,
                    "message": "Admin user not found in database"
                })
                conn.close()
                return False
            
            # Generate new admin password hash
            new_password = "admin123"  # In production, would use a secure random password
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update admin password
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
            conn.commit()
            
            logger.info(f"✅ Admin password updated successfully")
            self.repair_results["database_repairs"].append({
                "action": "fix_admin_password",
                "success": True,
                "message": "Admin password updated successfully"
            })
            self.repair_results["repair_actions"].append({
                "type": "password_reset",
                "user": "admin",
                "new_password": new_password
            })
            
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ Error fixing admin password: {e}")
            self.repair_results["database_repairs"].append({
                "action": "fix_admin_password",
                "success": False,
                "message": f"Error fixing admin password: {e}"
            })
            return False
    
    def fix_user_passwords(self) -> bool:
        """Fix regular user passwords"""
        try:
            conn = pymysql.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Find all non-admin users
            cursor.execute("SELECT id, username FROM users WHERE username != 'admin'")
            users = cursor.fetchall()
            
            if not users:
                logger.info("ℹ️ No regular users found to update")
                self.repair_results["database_repairs"].append({
                    "action": "fix_user_passwords",
                    "success": True,
                    "message": "No regular users found to update"
                })
                conn.close()
                return True
            
            fixed_count = 0
            for user_id, username in users:
                # Generate new password hash
                new_password = "user123"  # In production, would use unique secure random passwords
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update user password
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
                fixed_count += 1
                
                self.repair_results["repair_actions"].append({
                    "type": "password_reset",
                    "user": username,
                    "new_password": new_password
                })
            
            conn.commit()
            
            logger.info(f"✅ Updated passwords for {fixed_count} regular users")
            self.repair_results["database_repairs"].append({
                "action": "fix_user_passwords",
                "success": True,
                "message": f"Updated passwords for {fixed_count} regular users",
                "fixed_count": fixed_count
            })
            
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ Error fixing user passwords: {e}")
            self.repair_results["database_repairs"].append({
                "action": "fix_user_passwords",
                "success": False,
                "message": f"Error fixing user passwords: {e}"
            })
            return False
    
    def test_api_auth(self) -> bool:
        """Test API authentication with fixed credentials"""
        admin_creds = {"username": "admin", "password": "admin123"}
        user_creds = {"username": "user", "password": "user123"}
        
        admin_success = self._test_login(admin_creds, "admin")
        user_success = self._test_login(user_creds, "regular user")
        
        return admin_success and user_success
    
    def _test_login(self, credentials: Dict, user_type: str) -> bool:
        """Test login with specific credentials"""
        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json=credentials,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    logger.info(f"✅ {user_type.capitalize()} login successful")
                    self.repair_results["authentication_tests"][f"{user_type}_login"] = {
                        "success": True,
                        "message": f"{user_type.capitalize()} login successful",
                        "status_code": response.status_code
                    }
                    return True
                else:
                    logger.error(f"❌ {user_type.capitalize()} login response missing tokens")
                    self.repair_results["authentication_tests"][f"{user_type}_login"] = {
                        "success": False,
                        "message": f"{user_type.capitalize()} login response missing tokens",
                        "status_code": response.status_code
                    }
                    return False
            else:
                logger.error(f"❌ {user_type.capitalize()} login failed: {response.status_code}")
                self.repair_results["authentication_tests"][f"{user_type}_login"] = {
                    "success": False,
                    "message": f"{user_type.capitalize()} login failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {user_type.capitalize()} login request failed: {e}")
            self.repair_results["authentication_tests"][f"{user_type}_login"] = {
                "success": False,
                "message": f"{user_type.capitalize()} login request failed: {str(e)}"
            }
            return False
    
    def restart_api_server(self) -> bool:
        """Restart the API server if needed"""
        # In a production system, would implement actual server restart
        logger.info("⚠️ API server restart requested - this is a mock implementation")
        self.repair_results["repair_actions"].append({
            "type": "server_restart",
            "timestamp": datetime.now().isoformat(),
            "message": "API server restart requested"
        })
        
        # Wait for server to come back
        time.sleep(2)
        
        # Check if server is responsive
        return self.check_api_server()
    
    def run_comprehensive_repair(self) -> Dict:
        """Run all repair steps"""
        logger.info("🔧 Starting NoxSuite authentication system repair...")
        
        # Step 1: Check API server
        api_status = self.check_api_server()
        
        # Step 2: Check database connection
        db_status = self.check_database_connection()
        if not db_status:
            logger.error("❌ Cannot proceed without database connection")
            return self.repair_results
        
        # Step 3: Check users table
        users = self.check_users_table()
        
        # Step 4: Fix admin password
        admin_fix = self.fix_admin_password()
        
        # Step 5: Fix user passwords
        users_fix = self.fix_user_passwords()
        
        # Step 6: Restart API server if needed
        if not api_status or not (admin_fix and users_fix):
            logger.info("Restarting API server due to repairs...")
            self.restart_api_server()
        
        # Step 7: Test authentication
        auth_test = self.test_api_auth()
        
        # Generate report summary
        success_count = sum(1 for item in self.repair_results["database_repairs"] if item.get("success", False))
        total_count = len(self.repair_results["database_repairs"])
        self.repair_results["summary"] = {
            "success_rate": f"{success_count}/{total_count} ({success_count/total_count*100:.1f}%)",
            "api_server": "running" if api_status else "not running",
            "authentication": "working" if auth_test else "not working",
            "repair_actions": len(self.repair_results["repair_actions"])
        }
        
        logger.info("🏁 NoxSuite authentication system repair completed")
        return self.repair_results
    
    def save_results(self) -> str:
        """Save repair results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"noxsuite_auth_repair_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.repair_results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")
        return filename

def main():
    """Main function"""
    repair = NoxSuiteAuthRepair()
    results = repair.run_comprehensive_repair()
    report_file = repair.save_results()
    
    # Print summary report
    print("\n" + "="*80)
    print(" NoxSuite Authentication System Repair Summary ")
    print("="*80)
    
    summary = results["summary"]
    print(f"Database repairs: {summary['success_rate']}")
    print(f"API server: {summary['api_server']}")
    print(f"Authentication: {summary['authentication']}")
    print(f"Repair actions performed: {summary['repair_actions']}")
    
    print("\nCredentials Reset:")
    for action in results["repair_actions"]:
        if action["type"] == "password_reset":
            print(f"  - {action['user']}: {action['new_password']}")
    
    print(f"\nDetailed results saved to {report_file}")
    print("="*80)
    
    if summary["authentication"] == "working":
        print("\n✅ NoxSuite authentication system has been successfully repaired!")
        return 0
    else:
        print("\n❌ NoxSuite authentication system requires additional repairs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
