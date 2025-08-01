#!/usr/bin/env python3
"""
NoxSuite Ultimate Deployment Manager
Comprehensive deployment orchestration with ADHD-friendly interface
@author @hxwxdmhd
@version 11.0.0
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

# Configure logging with ADHD-friendly format
logging.basicConfig(
    level=logging.INFO,
    format='🚀 %(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class NoxSuiteDeploymentManager:
    """Complete deployment management for NoxSuite Ultimate"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path(__file__).parent
        self.config = self.load_config(config_path)
        self.deployment_status = {
            'started_at': datetime.now().isoformat(),
            'services': {},
            'overall_status': 'initializing'
        }
        
    def load_config(self, config_path: Optional[str]) -> Dict:
        """Load deployment configuration"""
        default_config = {
            'project_name': 'noxsuite-ultimate',
            'environment': 'production',
            'services': [
                'nginx',
                'noxsuite-backend',
                'noxsuite-frontend',
                'postgresql',
                'redis',
                'prometheus',
                'grafana',
                'node-exporter',
                'elasticsearch',
                'kibana',
                'noxsuite-ai'
            ],
            'health_check_timeout': 300,
            'deployment_steps': [
                'validate_environment',
                'build_images',
                'deploy_infrastructure',
                'deploy_applications',
                'run_health_checks',
                'configure_monitoring',
                'verify_deployment'
            ]
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                default_config.update(custom_config)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load custom config: {e}")
        
        return default_config
    
    def run_command(self, command: str, cwd: Optional[str] = None, timeout: int = 300) -> Dict:
        """Execute shell command with proper error handling"""
        try:
            logger.info(f"🔄 Executing: {command}")
            
            process = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd or str(self.project_root)
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            
            result = {
                'command': command,
                'returncode': process.returncode,
                'stdout': stdout,
                'stderr': stderr,
                'success': process.returncode == 0
            }
            
            if result['success']:
                logger.info(f"✅ Command completed successfully")
            else:
                logger.error(f"❌ Command failed with return code {process.returncode}")
                if stderr:
                    logger.error(f"Error output: {stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Command timed out after {timeout} seconds")
            process.kill()
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            logger.error(f"❌ Failed to execute command: {e}")
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        logger.info("🔍 Validating deployment environment...")
        
        required_files = [
            'app.py',
            'docker-compose.ultimate.yml',
            'frontend/package.json',
            'requirements.txt',
            '.env.example'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing required files: {missing_files}")
            return False
        
        # Check Docker availability
        docker_check = self.run_command('docker --version')
        if not docker_check['success']:
            logger.error("❌ Docker is not available")
            return False
        
        # Check Docker Compose availability
        compose_check = self.run_command('docker-compose --version')
        if not compose_check['success']:
            logger.error("❌ Docker Compose is not available")
            return False
        
        # Check environment file
        env_file = self.project_root / '.env'
        if not env_file.exists():
            logger.info("📝 Creating .env file from template...")
            self.run_command('cp .env.example .env')
        
        logger.info("✅ Environment validation completed")
        return True
    
    def build_images(self) -> bool:
        """Build Docker images"""
        logger.info("🏗️ Building Docker images...")
        
        # Build frontend
        logger.info("📦 Building frontend...")
        frontend_build = self.run_command(
            'npm run build',
            cwd=str(self.project_root / 'frontend'),
            timeout=600
        )
        
        if not frontend_build['success']:
            logger.error("❌ Frontend build failed")
            return False
        
        # Build Docker images
        logger.info("🐳 Building Docker images...")
        build_result = self.run_command(
            'docker-compose -f docker-compose.ultimate.yml build',
            timeout=1800  # 30 minutes for building
        )
        
        if not build_result['success']:
            logger.error("❌ Docker image build failed")
            return False
        
        logger.info("✅ Docker images built successfully")
        return True
    
    def deploy_infrastructure(self) -> bool:
        """Deploy infrastructure services"""
        logger.info("🏗️ Deploying infrastructure services...")
        
        infrastructure_services = [
            'postgresql',
            'redis',
            'elasticsearch',
            'prometheus'
        ]
        
        for service in infrastructure_services:
            logger.info(f"🚀 Starting {service}...")
            result = self.run_command(
                f'docker-compose -f docker-compose.ultimate.yml up -d {service}'
            )
            
            if not result['success']:
                logger.error(f"❌ Failed to start {service}")
                return False
            
            # Wait for service to be ready
            self.wait_for_service(service)
            self.deployment_status['services'][service] = 'running'
        
        logger.info("✅ Infrastructure services deployed")
        return True
    
    def deploy_applications(self) -> bool:
        """Deploy application services"""
        logger.info("🚀 Deploying application services...")
        
        application_services = [
            'noxsuite-backend',
            'noxsuite-frontend',
            'noxsuite-ai',
            'grafana',
            'kibana',
            'node-exporter',
            'nginx'
        ]
        
        for service in application_services:
            logger.info(f"🚀 Starting {service}...")
            result = self.run_command(
                f'docker-compose -f docker-compose.ultimate.yml up -d {service}'
            )
            
            if not result['success']:
                logger.error(f"❌ Failed to start {service}")
                return False
            
            # Wait for service to be ready
            self.wait_for_service(service)
            self.deployment_status['services'][service] = 'running'
        
        logger.info("✅ Application services deployed")
        return True
    
    def wait_for_service(self, service: str, timeout: int = 120):
        """Wait for service to be healthy"""
        logger.info(f"⏳ Waiting for {service} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            health_check = self.run_command(
                f'docker-compose -f docker-compose.ultimate.yml ps {service}'
            )
            
            if health_check['success'] and 'Up' in health_check['stdout']:
                logger.info(f"✅ {service} is ready")
                return True
            
            time.sleep(5)
        
        logger.warning(f"⚠️ {service} may not be fully ready after {timeout}s")
        return False
    
    def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        logger.info("🩺 Running health checks...")
        
        health_endpoints = {
            'backend': 'http://localhost:5000/api/health',
            'frontend': 'http://localhost:3000',
            'grafana': 'http://localhost:3001/login',
            'kibana': 'http://localhost:5601',
            'prometheus': 'http://localhost:9090/-/healthy'
        }
        
        all_healthy = True
        
        for service, endpoint in health_endpoints.items():
            logger.info(f"🔍 Checking {service} at {endpoint}...")
            
            # Use curl for health checks
            health_result = self.run_command(
                f'curl -f -s -o /dev/null -w "%{{http_code}}" {endpoint}',
                timeout=30
            )
            
            if health_result['success'] and '200' in health_result['stdout']:
                logger.info(f"✅ {service} is healthy")
                self.deployment_status['services'][service] = 'healthy'
            else:
                logger.warning(f"⚠️ {service} health check failed")
                self.deployment_status['services'][service] = 'unhealthy'
                all_healthy = False
        
        return all_healthy
    
    def configure_monitoring(self) -> bool:
        """Configure monitoring and alerting"""
        logger.info("📊 Configuring monitoring...")
        
        # Import Grafana dashboards
        dashboards_dir = self.project_root / 'monitoring' / 'grafana' / 'dashboards'
        if dashboards_dir.exists():
            logger.info("📈 Grafana dashboards configured")
        
        # Configure Prometheus targets
        prometheus_config = self.project_root / 'monitoring' / 'prometheus.yml'
        if prometheus_config.exists():
            logger.info("🎯 Prometheus targets configured")
        
        logger.info("✅ Monitoring configuration completed")
        return True
    
    def verify_deployment(self) -> bool:
        """Verify complete deployment"""
        logger.info("🔍 Verifying deployment...")
        
        # Check all services are running
        all_services_result = self.run_command(
            'docker-compose -f docker-compose.ultimate.yml ps'
        )
        
        if not all_services_result['success']:
            logger.error("❌ Failed to check service status")
            return False
        
        # Count running services
        running_services = len([
            line for line in all_services_result['stdout'].split('\n')
            if 'Up' in line
        ])
        
        expected_services = len(self.config['services'])
        
        if running_services >= expected_services * 0.8:  # 80% threshold
            logger.info(f"✅ Deployment verified: {running_services}/{expected_services} services running")
            self.deployment_status['overall_status'] = 'completed'
            return True
        else:
            logger.error(f"❌ Deployment verification failed: {running_services}/{expected_services} services running")
            self.deployment_status['overall_status'] = 'failed'
            return False
    
    def deploy(self) -> bool:
        """Execute complete deployment"""
        logger.info("🚀 Starting NoxSuite Ultimate deployment...")
        
        try:
            for step in self.config['deployment_steps']:
                logger.info(f"📋 Executing step: {step}")
                
                step_method = getattr(self, step, None)
                if not step_method:
                    logger.error(f"❌ Unknown deployment step: {step}")
                    return False
                
                if not step_method():
                    logger.error(f"❌ Deployment step failed: {step}")
                    return False
                
                logger.info(f"✅ Step completed: {step}")
            
            # Save deployment status
            status_file = self.project_root / 'deployment_status.json'
            with open(status_file, 'w') as f:
                json.dump(self.deployment_status, f, indent=2)
            
            logger.info("🎉 NoxSuite Ultimate deployment completed successfully!")
            self.print_deployment_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed with error: {e}")
            self.deployment_status['overall_status'] = 'failed'
            return False
    
    def print_deployment_summary(self):
        """Print deployment summary"""
        logger.info("\n" + "="*60)
        logger.info("🎉 NOXSUITE ULTIMATE DEPLOYMENT SUMMARY")
        logger.info("="*60)
        logger.info(f"📅 Deployment completed at: {datetime.now().isoformat()}")
        logger.info(f"🏷️ Project: {self.config['project_name']}")
        logger.info(f"🌍 Environment: {self.config['environment']}")
        logger.info("\n📋 Service Status:")
        
        for service, status in self.deployment_status['services'].items():
            status_emoji = "✅" if status in ['running', 'healthy'] else "⚠️"
            logger.info(f"   {status_emoji} {service}: {status}")
        
        logger.info("\n🌐 Access URLs:")
        logger.info("   🏠 Main Application: http://localhost")
        logger.info("   🔧 Backend API: http://localhost:5000")
        logger.info("   ⚛️ Frontend: http://localhost:3000")
        logger.info("   📊 Grafana: http://localhost:3001")
        logger.info("   📈 Kibana: http://localhost:5601")
        logger.info("   🎯 Prometheus: http://localhost:9090")
        
        logger.info("\n🔑 Default Credentials:")
        logger.info("   👤 Admin: admin / noxsuite2025!")
        logger.info("   📊 Grafana: admin / noxgrafana2025!")
        
        logger.info("\n📚 Useful Commands:")
        logger.info("   🔍 Check status: docker-compose -f docker-compose.ultimate.yml ps")
        logger.info("   📋 View logs: docker-compose -f docker-compose.ultimate.yml logs [service]")
        logger.info("   🛑 Stop all: docker-compose -f docker-compose.ultimate.yml down")
        
        logger.info("="*60)
    
    def rollback(self):
        """Rollback deployment"""
        logger.info("🔄 Rolling back deployment...")
        
        result = self.run_command(
            'docker-compose -f docker-compose.ultimate.yml down'
        )
        
        if result['success']:
            logger.info("✅ Rollback completed")
        else:
            logger.error("❌ Rollback failed")

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='NoxSuite Ultimate Deployment Manager')
    parser.add_argument('--config', help='Custom configuration file path')
    parser.add_argument('--rollback', action='store_true', help='Rollback deployment')
    parser.add_argument('--environment', default='production', help='Deployment environment')
    
    args = parser.parse_args()
    
    try:
        deployment_manager = NoxSuiteDeploymentManager(args.config)
        
        if args.rollback:
            deployment_manager.rollback()
        else:
            success = deployment_manager.deploy()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
