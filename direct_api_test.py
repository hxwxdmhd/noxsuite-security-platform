#!/usr/bin/env python3
"""
Direct API Test Client
====================
Tests FastAPI authentication directly without relying on user model imports.
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectAPIClient:
    """Direct API client for testing authentication"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.admin_creds = {
            "email": "admin@noxsuite.local",
            "password": "Admin123!"
        }
        self.user_creds = {
            "email": "user@noxsuite.local",
            "password": "User123!"
        }
        self.tests_passed = 0
        self.tests_failed = 0
        self.access_token = None
    
    def print_result(self, test_name, success, details=None):
        """Print test result"""
        if success:
            logger.info(f"✅ {test_name}")
            self.tests_passed += 1
        else:
            logger.error(f"❌ {test_name}")
            if details:
                logger.error(f"   Details: {details}")
            self.tests_failed += 1
            
    def test_health(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            success = response.status_code == 200
            
            details = None
            if not success:
                details = f"Status code {response.status_code}, response: {response.text}"
                
            self.print_result("Health check", success, details)
            return success
        except Exception as e:
            self.print_result("Health check", False, str(e))
            return False
    
    def test_admin_login(self):
        """Test admin login"""
        try:
            logger.info(f"Trying to login with: {self.admin_creds}")
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.admin_creds
            )
            
            # Try to log headers and full response
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")
            
            # Try to parse JSON response, otherwise show text
            try:
                resp_json = response.json()
                logger.info(f"Response JSON: {json.dumps(resp_json, indent=2)}")
                success = response.status_code == 200 and "access_token" in resp_json
            except Exception as e:
                logger.error(f"Error parsing JSON: {e}")
                logger.info(f"Response text: {response.text}")
                success = False
            
            details = None
            if not success:
                details = f"Status code {response.status_code}, response: {response.text}"
            else:
                self.access_token = response.json()["access_token"]
                logger.info(f"Access token: {self.access_token[:20]}...")
                
            self.print_result("Admin login", success, details)
            return success
        except Exception as e:
            self.print_result("Admin login", False, str(e))
            return False
    
    def test_user_login(self):
        """Test regular user login"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.user_creds
            )
            
            success = response.status_code == 200 and "access_token" in response.json()
            
            details = None
            if not success:
                details = f"Status code {response.status_code}, response: {response.text}"
                
            self.print_result("User login", success, details)
            return success
        except Exception as e:
            self.print_result("User login", False, str(e))
            return False
    
    def test_auth_me(self):
        """Test auth/me endpoint with token"""
        if not self.access_token:
            self.print_result("Auth/me", False, "No access token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            success = response.status_code == 200
            
            details = None
            if not success:
                details = f"Status code {response.status_code}, response: {response.text}"
            else:
                user_data = response.json()
                logger.info(f"User data: {user_data}")
                
            self.print_result("Auth/me", success, details)
            return success
        except Exception as e:
            self.print_result("Auth/me", False, str(e))
            return False
    
    def test_compat_login(self):
        """Test compatibility login endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": "admin", "password": "Admin123!"}
            )
            
            success = response.status_code == 200 and "access_token" in response.json()
            
            details = None
            if not success:
                details = f"Status code {response.status_code}, response: {response.text}"
                
            self.print_result("Compat login", success, details)
            return success
        except Exception as e:
            self.print_result("Compat login", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("\n===== Running Direct API Tests =====")
        self.test_health()
        self.test_admin_login()
        self.test_user_login()
        self.test_auth_me()
        self.test_compat_login()
        
        # Print summary
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total) * 100 if total > 0 else 0
        
        logger.info("\n===== Test Summary =====")
        logger.info(f"Tests passed: {self.tests_passed}/{total} ({pass_rate:.1f}%)")
        logger.info(f"Tests failed: {self.tests_failed}/{total} ({100 - pass_rate:.1f}%)")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    client = DirectAPIClient()
    success = client.run_all_tests()
    sys.exit(0 if success else 1)
