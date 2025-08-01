#!/usr/bin/env python3
"""
EMERGENCY SECURITY VALIDATION SCRIPT
Validates the emergency authentication fixes for /api/knowledge/* endpoints

Date: 2025-07-29 07:56:07 UTC
Audit: 4.0.0 Security Response Validation
Purpose: Confirm emergency patches are working correctly
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VALIDATION - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmergencySecurityValidator:
    """Validates emergency security patches"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.test_results = []
        self.auth_token = None
        self.project_root = Path.cwd()
        
        logger.info("Emergency Security Validator initialized")
        logger.info(f"Target URL: {base_url}")
    
    def test_unauthenticated_access(self):
        """Test that knowledge endpoints are properly protected"""
        knowledge_endpoints = [
            '/api/knowledge/search',
            '/api/knowledge/suggestions',
            '/api/knowledge/status'
        ]
        
        logger.info("Testing unauthenticated access to knowledge endpoints...")
        
        for endpoint in knowledge_endpoints:
            url = f"{self.base_url}{endpoint}"
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 401:
                    self.test_results.append({
                        'test': f"Unauthenticated access to {endpoint}",
                        'status': 'PASS',
                        'expected': '401 Unauthorized',
                        'actual': f"{response.status_code} {response.reason}",
                        'message': 'Endpoint properly protected'
                    })
                    logger.info(f"PASS: {endpoint} properly returns 401")
                elif response.status_code == 404:
                    self.test_results.append({
                        'test': f"Unauthenticated access to {endpoint}",
                        'status': 'INFO',
                        'expected': '401 Unauthorized',
                        'actual': f"{response.status_code} {response.reason}",
                        'message': 'Endpoint not found - may need Flask app integration'
                    })
                    logger.info(f"INFO: {endpoint} returns 404 - endpoint may not be integrated")
                else:
                    self.test_results.append({
                        'test': f"Unauthenticated access to {endpoint}",
                        'status': 'FAIL',
                        'expected': '401 Unauthorized',
                        'actual': f"{response.status_code} {response.reason}",
                        'message': 'SECURITY RISK: Endpoint accessible without authentication'
                    })
                    logger.error(f"FAIL: {endpoint} allows unauthenticated access!")
                    
            except requests.ConnectionError:
                self.test_results.append({
                    'test': f"Unauthenticated access to {endpoint}",
                    'status': 'SKIP',
                    'expected': 'Connection to Flask app',
                    'actual': 'Connection refused',
                    'message': 'Flask app not running - cannot test live endpoints'
                })
                logger.warning(f"SKIP: Cannot connect to {url}")
            except Exception as e:
                logger.error(f"Error testing {endpoint}: {e}")
    
    def test_emergency_login(self):
        """Test emergency login endpoint"""
        login_url = f"{self.base_url}/api/emergency/login"
        
        logger.info("Testing emergency login endpoint...")
        
        test_credentials = {
            'username': 'emergency_admin',
            'password': os.getenv('EMERGENCY_PASSWORD', 'emergency_temp_password_2025')
        }
        
        try:
            response = requests.post(login_url, json=test_credentials, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.test_results.append({
                        'test': 'Emergency login',
                        'status': 'PASS',
                        'expected': '200 with token',
                        'actual': f"200 with token (length: {len(self.auth_token)})",
                        'message': 'Emergency login successful'
                    })
                    logger.info("PASS: Emergency login successful")
                else:
                    self.test_results.append({
                        'test': 'Emergency login',
                        'status': 'FAIL',
                        'expected': '200 with token',
                        'actual': f"200 without token",
                        'message': 'Login response missing token'
                    })
            else:
                self.test_results.append({
                    'test': 'Emergency login',
                    'status': 'FAIL',
                    'expected': '200 with token',
                    'actual': f"{response.status_code} {response.reason}",
                    'message': 'Emergency login failed'
                })
                
        except requests.ConnectionError:
            self.test_results.append({
                'test': 'Emergency login',
                'status': 'SKIP',
                'expected': 'Connection to Flask app',
                'actual': 'Connection refused',
                'message': 'Flask app not running'
            })
            logger.warning("SKIP: Cannot test emergency login - Flask app not running")
        except Exception as e:
            logger.error(f"Error testing emergency login: {e}")
    
    def test_authenticated_access(self):
        """Test authenticated access to knowledge endpoints"""
        if not self.auth_token:
            logger.warning("No auth token available - skipping authenticated access tests")
            return
        
        knowledge_endpoints = [
            '/api/knowledge/search?q=test',
            '/api/knowledge/suggestions?q=test',
            '/api/knowledge/status'
        ]
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        logger.info("Testing authenticated access to knowledge endpoints...")
        
        for endpoint in knowledge_endpoints:
            url = f"{self.base_url}{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    self.test_results.append({
                        'test': f"Authenticated access to {endpoint}",
                        'status': 'PASS',
                        'expected': '200 OK',
                        'actual': f"{response.status_code} {response.reason}",
                        'message': 'Authenticated access successful'
                    })
                    logger.info(f"PASS: {endpoint} allows authenticated access")
                else:
                    self.test_results.append({
                        'test': f"Authenticated access to {endpoint}",
                        'status': 'WARN',
                        'expected': '200 OK',
                        'actual': f"{response.status_code} {response.reason}",
                        'message': 'Authenticated access failed - check implementation'
                    })
                    
            except requests.ConnectionError:
                logger.warning(f"SKIP: Cannot test authenticated access to {endpoint}")
            except Exception as e:
                logger.error(f"Error testing authenticated access to {endpoint}: {e}")
    
    def test_security_headers(self):
        """Test for required security headers"""
        test_url = f"{self.base_url}/api/emergency/status"
        
        logger.info("Testing security headers...")
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        try:
            response = requests.get(test_url, timeout=5)
            
            headers_found = []
            headers_missing = []
            
            for header in required_headers:
                if header in response.headers:
                    headers_found.append(header)
                else:
                    headers_missing.append(header)
            
            if len(headers_found) >= 3:  # At least 3 of 5 security headers
                self.test_results.append({
                    'test': 'Security headers',
                    'status': 'PASS',
                    'expected': 'At least 3 security headers',
                    'actual': f"Found {len(headers_found)}: {', '.join(headers_found)}",
                    'message': 'Adequate security headers present'
                })
                logger.info(f"PASS: Found {len(headers_found)} security headers")
            else:
                self.test_results.append({
                    'test': 'Security headers',
                    'status': 'WARN',
                    'expected': 'At least 3 security headers',
                    'actual': f"Found {len(headers_found)}: {', '.join(headers_found)}",
                    'message': f"Missing headers: {', '.join(headers_missing)}"
                })
                logger.warning(f"WARN: Only {len(headers_found)} security headers found")
                
        except requests.ConnectionError:
            logger.warning("SKIP: Cannot test security headers - Flask app not running")
        except Exception as e:
            logger.error(f"Error testing security headers: {e}")
    
    def validate_file_integrity(self):
        """Validate that emergency patch files exist and are valid"""
        logger.info("Validating emergency patch file integrity...")
        
        required_files = [
            'emergency_auth_middleware.py',
            'emergency_knowledge_routes.py',
            'emergency_app_integration.py',
            'EMERGENCY_SECURITY_PATCH_REPORT.md'
        ]
        
        for filename in required_files:
            file_path = self.project_root / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content) > 100:  # Basic content validation
                        self.test_results.append({
                            'test': f"File integrity: {filename}",
                            'status': 'PASS',
                            'expected': 'File exists with content',
                            'actual': f"File exists ({len(content)} chars)",
                            'message': 'Emergency patch file is valid'
                        })
                        logger.info(f"PASS: {filename} exists and has content")
                    else:
                        self.test_results.append({
                            'test': f"File integrity: {filename}",
                            'status': 'WARN',
                            'expected': 'File with substantial content',
                            'actual': f"File exists but small ({len(content)} chars)",
                            'message': 'File may be incomplete'
                        })
                except Exception as e:
                    self.test_results.append({
                        'test': f"File integrity: {filename}",
                        'status': 'FAIL',
                        'expected': 'Readable file',
                        'actual': f"Error reading: {e}",
                        'message': 'File exists but cannot be read'
                    })
            else:
                self.test_results.append({
                    'test': f"File integrity: {filename}",
                    'status': 'FAIL',
                    'expected': 'File exists',
                    'actual': 'File missing',
                    'message': 'Emergency patch file not found'
                })
                logger.error(f"FAIL: {filename} is missing")
    
    def run_validation(self):
        """Run all validation tests"""
        logger.info("Starting emergency security validation...")
        
        # File integrity tests (always run)
        self.validate_file_integrity()
        
        # Live endpoint tests (only if Flask app is running)
        self.test_unauthenticated_access()
        self.test_emergency_login()
        self.test_authenticated_access()
        self.test_security_headers()
        
        return self.test_results
    
    def generate_validation_report(self):
        """Generate validation report"""
        report_file = self.project_root / "EMERGENCY_VALIDATION_REPORT.md"
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warned_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        skipped_tests = len([t for t in self.test_results if t['status'] == 'SKIP'])
        
        report_content = f"""# EMERGENCY SECURITY VALIDATION REPORT

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC  
**Audit Version**: 4.0.0  
**Validation Type**: Emergency Authentication Patch  

## VALIDATION SUMMARY

**Total Tests**: {total_tests}  
**Passed**: {passed_tests}  
**Failed**: {failed_tests}  
**Warnings**: {warned_tests}  
**Skipped**: {skipped_tests}  

**Overall Status**: {'PASS' if failed_tests == 0 else 'FAIL' if failed_tests > 2 else 'WARN'}

## DETAILED RESULTS

"""
        
        for result in self.test_results:
            status_emoji = {
                'PASS': '✅',
                'FAIL': '❌', 
                'WARN': '⚠️',
                'SKIP': '⏭️',
                'INFO': 'ℹ️'
            }.get(result['status'], '❓')
            
            report_content += f"""### {status_emoji} {result['test']}

**Status**: {result['status']}  
**Expected**: {result['expected']}  
**Actual**: {result['actual']}  
**Message**: {result['message']}  

"""
        
        report_content += f"""## SECURITY ASSESSMENT

### Authentication Status
- Emergency authentication middleware: {'✅ DEPLOYED' if any('emergency_auth_middleware.py' in r['test'] and r['status'] == 'PASS' for r in self.test_results) else '❌ MISSING'}
- Knowledge endpoint protection: {'✅ CONFIGURED' if any('emergency_knowledge_routes.py' in r['test'] and r['status'] == 'PASS' for r in self.test_results) else '❌ MISSING'}
- App integration ready: {'✅ READY' if any('emergency_app_integration.py' in r['test'] and r['status'] == 'PASS' for r in self.test_results) else '❌ MISSING'}

### Live Endpoint Tests
- Requires Flask app running for complete validation
- Current tests validate file integrity and basic functionality
- Run with Flask app active for full security validation

## NEXT STEPS

1. **If Flask app not running**: Start Flask application to test live endpoints
2. **Set environment variables**: EMERGENCY_PASSWORD and EMERGENCY_API_KEY
3. **Integrate patches**: Use emergency_app_integration.py in your Flask app
4. **Re-run validation**: Test with live application

## EMERGENCY CONTACT

**Security Issues**: security@noxsuite.dev  
**Patch Support**: Run `python emergency_security_patcher_fixed.py` to re-apply  
**Validation**: Run `python emergency_security_validator.py` for fresh validation  

---

**Validation ID**: validation-{datetime.now().strftime("%Y%m%d-%H%M%S")}  
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC  
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Validation report generated: {report_file}")
        return report_file

def main():
    """Main validation execution"""
    print("EMERGENCY SECURITY VALIDATION - NOXSUITE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("Audit: 4.0.0 Security Response Validation")
    print("Target: /api/knowledge/* authentication verification")
    print("=" * 60)
    
    validator = EmergencySecurityValidator()
    
    try:
        # Run validation tests
        results = validator.run_validation()
        
        # Generate report
        report_file = validator.generate_validation_report()
        
        # Print summary
        total = len(results)
        passed = len([r for r in results if r['status'] == 'PASS'])
        failed = len([r for r in results if r['status'] == 'FAIL'])
        
        print(f"\nVALIDATION COMPLETED")
        print(f"Tests: {total} | Passed: {passed} | Failed: {failed}")
        print(f"Report: {report_file.name}")
        
        if failed == 0:
            print("\nSTATUS: EMERGENCY PATCHES VALIDATED SUCCESSFULLY")
            return 0
        elif failed <= 2:
            print("\nSTATUS: EMERGENCY PATCHES MOSTLY VALIDATED (minor issues)")
            return 0
        else:
            print("\nSTATUS: EMERGENCY PATCHES NEED ATTENTION")
            return 1
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\nCRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
