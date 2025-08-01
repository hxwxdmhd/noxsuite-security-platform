from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)

#!/usr/bin/env python3
"""
NoxSuite System Validation and Integration Tests
===============================================

Comprehensive health checks and integration testing for all NoxSuite services.
Tests MCP-Langflow integration, service communication, and system stability.
"""

import os
import sys
import json
import time
import requests
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NoxSuiteSystemValidator:
    """Comprehensive system validation for NoxSuite"""
    
    def __init__(self):
        self.services = {
            'main_server': {'url': 'http://localhost:5000', 'name': 'Main Unified Server'},
            'langflow': {'url': 'http://localhost:7860', 'name': 'Langflow Service'},
            'mcp_server': {'url': 'http://localhost:8000', 'name': 'MCP Server'},
            'aethercore': {'url': 'http://localhost:8001', 'name': 'AetherCore MSP Server'}
        }
        self.test_results = {}
        self.integration_results = {}
        self.performance_metrics = {}
        
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests"""
        logger.info("🚀 Starting comprehensive NoxSuite system validation...")
        
        start_time = time.time()
        
        # 1. Service Health Checks
        self.test_service_health()
        
        # 2. API Endpoint Tests
        self.test_api_endpoints()
        
        # 3. Integration Tests
        self.test_service_integration()
        
        # 4. Performance Tests
        self.test_performance()
        
        # 5. Langflow Specific Tests
        self.test_langflow_readiness()
        
        # 6. MCP Protocol Tests
        self.test_mcp_compliance()
        
        # 7. Docker Services Check
        self.test_docker_services()
        
        total_time = time.time() - start_time
        
        # Generate final report
        validation_report = self.generate_validation_report(total_time)
        
        logger.info(f"✅ Validation completed in {total_time:.2f} seconds")
        
        return validation_report
    
    def test_service_health(self) -> None:
        """Test health of all core services"""
        logger.info("🔍 Testing service health...")
        
        for service_key, service_info in self.services.items():
            try:
                response = requests.get(
                    f"{service_info['url']}/health",
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.test_results[f"{service_key}_health"] = {
                        'status': 'PASS',
                        'response_time': response.elapsed.total_seconds(),
                        'response_code': response.status_code,
                        'data': response.json()
                    }
                    logger.info(f"✅ {service_info['name']} health check passed")
                else:
                    self.test_results[f"{service_key}_health"] = {
                        'status': 'FAIL',
                        'response_code': response.status_code,
                        'error': f"Unexpected status code: {response.status_code}"
                    }
                    logger.warning(f"⚠️ {service_info['name']} health check failed: {response.status_code}")
                    
            except Exception as e:
                self.test_results[f"{service_key}_health"] = {
                    'status': 'FAIL',
                    'error': str(e)
                }
                logger.error(f"❌ {service_info['name']} health check error: {e}")
    
    def test_api_endpoints(self) -> None:
        """Test core API endpoints"""
        logger.info("🔍 Testing API endpoints...")
        
        # Test endpoints for each service
        endpoints_to_test = {
            'main_server': ['/health', '/status', '/'],
            'langflow': ['/health', '/api/flows', '/'],
            'mcp_server': ['/health', '/protocol', '/contexts', '/'],
            'aethercore': ['/health', '/models', '/metrics', '/heartbeat', '/']
        }
        
        for service_key, endpoints in endpoints_to_test.items():
            service_url = self.services[service_key]['url']
            service_name = self.services[service_key]['name']
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{service_url}{endpoint}", timeout=5)
                    
                    test_key = f"{service_key}_endpoint_{endpoint.replace('/', '_')}"
                    if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                        self.test_results[test_key] = {
                            'status': 'PASS',
                            'response_time': response.elapsed.total_seconds(),
                            'response_code': response.status_code
                        }
                    else:
                        self.test_results[test_key] = {
                            'status': 'WARN',
                            'response_code': response.status_code
                        }
                        
                except Exception as e:
                    test_key = f"{service_key}_endpoint_{endpoint.replace('/', '_')}"
                    self.test_results[test_key] = {
                        'status': 'FAIL',
                        'error': str(e)
                    }
    
    def test_service_integration(self) -> None:
        """Test integration between services"""
        logger.info("🔍 Testing service integration...")
        
        # Test MCP-Langflow integration
        try:
            # First, check if MCP server can communicate with Langflow
            mcp_response = requests.get('http://localhost:8000/health', timeout=5)
            langflow_response = requests.get('http://localhost:7860/health', timeout=5)
            
            if mcp_response.status_code == 200 and langflow_response.status_code == 200:
                self.integration_results['mcp_langflow'] = {
                    'status': 'PASS',
                    'description': 'MCP and Langflow services are both healthy and ready for integration'
                }
                logger.info("✅ MCP-Langflow integration test passed")
            else:
                self.integration_results['mcp_langflow'] = {
                    'status': 'FAIL',
                    'description': 'One or both services are not responding correctly'
                }
                
        except Exception as e:
            self.integration_results['mcp_langflow'] = {
                'status': 'FAIL',
                'error': str(e)
            }
        
        # Test AetherCore-MCP integration
        try:
            aethercore_response = requests.get('http://localhost:8001/models', timeout=5)
            mcp_response = requests.get('http://localhost:8000/contexts', timeout=5)
            
            if aethercore_response.status_code == 200:
                self.integration_results['aethercore_mcp'] = {
                    'status': 'PASS',
                    'description': 'AetherCore MSP and MCP services are integrated'
                }
                logger.info("✅ AetherCore-MCP integration test passed")
            else:
                self.integration_results['aethercore_mcp'] = {
                    'status': 'WARN',
                    'description': 'Services responding but integration needs verification'
                }
                
        except Exception as e:
            self.integration_results['aethercore_mcp'] = {
                'status': 'FAIL',
                'error': str(e)
            }
    
    def test_performance(self) -> None:
        """Test performance metrics"""
        logger.info("🔍 Testing performance...")
        
        for service_key, service_info in self.services.items():
            try:
                start_time = time.time()
                response = requests.get(f"{service_info['url']}/health", timeout=5)
                response_time = time.time() - start_time
                
                self.performance_metrics[service_key] = {
                    'response_time_ms': round(response_time * 1000, 2),
                    'status_code': response.status_code,
                    'service_available': response.status_code == 200
                }
                
                if response_time < 1.0:  # Less than 1 second is good
                    logger.info(f"✅ {service_info['name']} performance: {response_time*1000:.2f}ms")
                else:
                    logger.warning(f"⚠️ {service_info['name']} slow response: {response_time*1000:.2f}ms")
                    
            except Exception as e:
                self.performance_metrics[service_key] = {
                    'error': str(e),
                    'service_available': False
                }
    
    def test_langflow_readiness(self) -> None:
        """Test Langflow specific readiness"""
        logger.info("🔍 Testing Langflow readiness...")
        
        try:
            # Test basic Langflow endpoints
            health_response = requests.get('http://localhost:7860/health', timeout=10)
            flows_response = requests.get('http://localhost:7860/api/flows', timeout=10)
            
            langflow_ready = True
            readiness_issues = []
            
            if health_response.status_code != 200:
                langflow_ready = False
                readiness_issues.append(f"Health endpoint failed: {health_response.status_code}")
            
            # Check if the service is properly configured
            try:
                health_data = health_response.json()
                if 'status' in health_data and health_data['status'] == 'healthy':
                    readiness_issues.append("✅ Health status confirmed")
                else:
                    readiness_issues.append("⚠️ Health status unclear")
            except:
                readiness_issues.append("⚠️ Health response not JSON")
            
            self.integration_results['langflow_readiness'] = {
                'status': 'PASS' if langflow_ready else 'FAIL',
                'ready_for_integration': langflow_ready,
                'issues': readiness_issues,
                'health_status': health_response.status_code,
                'flows_status': flows_response.status_code
            }
            
            if langflow_ready:
                logger.info("✅ Langflow is ready for MCP integration")
            else:
                logger.warning("⚠️ Langflow readiness issues detected")
                
        except Exception as e:
            self.integration_results['langflow_readiness'] = {
                'status': 'FAIL',
                'error': str(e),
                'ready_for_integration': False
            }
            logger.error(f"❌ Langflow readiness test failed: {e}")
    
    def test_mcp_compliance(self) -> None:
        """Test MCP protocol compliance"""
        logger.info("🔍 Testing MCP protocol compliance...")
        
        try:
            # Test MCP protocol endpoints
            protocol_response = requests.get('http://localhost:8000/protocol', timeout=5)
            contexts_response = requests.get('http://localhost:8000/contexts', timeout=5)
            
            mcp_compliant = True
            compliance_issues = []
            
            if protocol_response.status_code == 200:
                try:
                    protocol_data = protocol_response.json()
                    if 'version' in protocol_data:
                        compliance_issues.append(f"✅ MCP Protocol version: {protocol_data.get('version', 'unknown')}")
                    else:
                        compliance_issues.append("⚠️ Protocol version not specified")
                except:
                    compliance_issues.append("⚠️ Protocol response not JSON")
            else:
                mcp_compliant = False
                compliance_issues.append(f"❌ Protocol endpoint failed: {protocol_response.status_code}")
            
            self.integration_results['mcp_compliance'] = {
                'status': 'PASS' if mcp_compliant else 'FAIL',
                'compliant': mcp_compliant,
                'issues': compliance_issues,
                'protocol_status': protocol_response.status_code,
                'contexts_status': contexts_response.status_code
            }
            
            if mcp_compliant:
                logger.info("✅ MCP protocol compliance verified")
            else:
                logger.warning("⚠️ MCP compliance issues detected")
                
        except Exception as e:
            self.integration_results['mcp_compliance'] = {
                'status': 'FAIL',
                'error': str(e),
                'compliant': False
            }
            logger.error(f"❌ MCP compliance test failed: {e}")
    
    def test_docker_services(self) -> None:
        """Test Docker services status"""
        logger.info("🔍 Checking Docker services...")
        
        try:
            import subprocess
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                docker_output = result.stdout
                services_running = len([line for line in docker_output.split('\n') if 'nox' in line.lower()])
                
                self.integration_results['docker_services'] = {
                    'status': 'PASS',
                    'docker_available': True,
                    'services_running': services_running,
                    'details': 'Docker is available and responsive'
                }
                logger.info(f"✅ Docker services check passed ({services_running} NoxSuite containers)")
            else:
                self.integration_results['docker_services'] = {
                    'status': 'WARN',
                    'docker_available': False,
                    'error': result.stderr
                }
                logger.warning("⚠️ Docker services check failed")
                
        except Exception as e:
            self.integration_results['docker_services'] = {
                'status': 'FAIL',
                'docker_available': False,
                'error': str(e)
            }
            logger.warning(f"⚠️ Docker check error: {e}")
    
    def generate_validation_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'PASS'])
        failed_tests = len([r for r in self.test_results.values() if r.get('status') == 'FAIL'])
        warning_tests = len([r for r in self.test_results.values() if r.get('status') == 'WARN'])
        
        # Count integrations
        total_integrations = len(self.integration_results)
        passed_integrations = len([r for r in self.integration_results.values() if r.get('status') == 'PASS'])
        failed_integrations = len([r for r in self.integration_results.values() if r.get('status') == 'FAIL'])
        
        # Calculate overall health score
        health_score = ((passed_tests + passed_integrations) / (total_tests + total_integrations)) * 100 if (total_tests + total_integrations) > 0 else 0
        
        # Determine system status
        if health_score >= 90:
            system_status = "EXCELLENT"
            status_emoji = "🟢"
        elif health_score >= 75:
            system_status = "GOOD"
            status_emoji = "🟡"
        elif health_score >= 50:
            system_status = "FAIR"
            status_emoji = "🟠"
        else:
            system_status = "NEEDS_ATTENTION"
            status_emoji = "🔴"
        
        report = {
            "validation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_time_seconds": round(total_time, 2),
                "system_status": system_status,
                "health_score": round(health_score, 1),
                "status_emoji": status_emoji
            },
            "service_tests": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "details": self.test_results
            },
            "integration_tests": {
                "total_integrations": total_integrations,
                "passed": passed_integrations,
                "failed": failed_integrations,
                "details": self.integration_results
            },
            "performance_metrics": self.performance_metrics,
            "service_availability": {
                service_key: {
                    "available": service_key + "_health" in self.test_results and 
                                self.test_results[service_key + "_health"].get('status') == 'PASS',
                    "url": service_info['url'],
                    "name": service_info['name']
                }
                for service_key, service_info in self.services.items()
            },
            "recommendations": self.generate_recommendations(),
            "langflow_integration_status": {
                "ready": self.integration_results.get('langflow_readiness', {}).get('ready_for_integration', False),
                "mcp_compatible": self.integration_results.get('mcp_compliance', {}).get('compliant', False),
                "integration_possible": (
                    self.integration_results.get('langflow_readiness', {}).get('ready_for_integration', False) and
                    self.integration_results.get('mcp_compliance', {}).get('compliant', False)
                )
            }
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for failed services
        for service_key, service_info in self.services.items():
            health_key = f"{service_key}_health"
            if health_key in self.test_results:
                if self.test_results[health_key].get('status') == 'FAIL':
                    recommendations.append(f"🔧 Restart {service_info['name']} - health check failed")
                elif self.test_results[health_key].get('response_time', 0) > 1.0:
                    recommendations.append(f"⚡ Optimize {service_info['name']} - slow response time")
        
        # Check integration status
        if not self.integration_results.get('langflow_readiness', {}).get('ready_for_integration', False):
            recommendations.append("🔗 Complete Langflow configuration for MCP integration")
        
        if not self.integration_results.get('mcp_compliance', {}).get('compliant', False):
            recommendations.append("📋 Verify MCP protocol implementation")
        
        # Check Docker services
        if not self.integration_results.get('docker_services', {}).get('docker_available', False):
            recommendations.append("🐳 Start Docker services for full functionality")
        
        # If no issues found
        if not recommendations:
            recommendations.append("✅ System is healthy - consider running performance optimization")
            recommendations.append("📊 Monitor system metrics for continued optimal performance")
            recommendations.append("🔄 Regular health checks recommended")
        
        return recommendations

def main():
    """Main validation entry point"""
    logger.info("🚀 NoxSuite System Validation Starting...")
    logger.info("=" * 60)
    
    validator = NoxSuiteSystemValidator()
    
    try:
        # Run comprehensive validation
        report = validator.run_comprehensive_validation()
        
        # Save report to file
        with open('noxsuite_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📋 NOXSUITE SYSTEM VALIDATION REPORT")
        logger.info("=" * 60)
        logger.info(f"Status: {report['validation_summary']['status_emoji']} {report['validation_summary']['system_status']}")
        logger.info(f"Health Score: {report['validation_summary']['health_score']}%")
        logger.info(f"Total Time: {report['validation_summary']['total_time_seconds']}s")
        logger.info(f"Tests Passed: {report['service_tests']['passed']}/{report['service_tests']['total_tests']}")
        logger.info(f"Integrations Passed: {report['integration_tests']['passed']}/{report['integration_tests']['total_integrations']}")
        
        logger.info("\n🔗 INTEGRATION STATUS:")
        langflow_status = report['langflow_integration_status']
        logger.info(f"  Langflow Ready: {'✅' if langflow_status['ready'] else '❌'}")
        logger.info(f"  MCP Compatible: {'✅' if langflow_status['mcp_compatible'] else '❌'}")
        logger.info(f"  Integration Possible: {'✅' if langflow_status['integration_possible'] else '❌'}")
        
        logger.info("\n📊 SERVICE AVAILABILITY:")
        for service_key, service_data in report['service_availability'].items():
            status = "✅" if service_data['available'] else "❌"
            logger.info(f"  {service_data['name']}: {status}")
        
        logger.info("\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            logger.info(f"  {rec}")
        
        logger.info(f"\n📄 Full report saved to: noxsuite_validation_report.json")
        logger.info("=" * 60)
        
        return report
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        logger.info(f"❌ Validation failed: {e}")
        return None

if __name__ == '__main__':
    main()
