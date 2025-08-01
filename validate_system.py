#!/usr/bin/env python3
"""
NoxSuite Ultimate System Validation
Comprehensive validation of all components and integrations
@author @hxwxdmhd
@version 11.0.0
"""

import os
import sys
import json
import importlib
from pathlib import Path

def validate_backend():
    """Validate backend components"""
    print("🔍 Validating backend components...")
    
    try:
        # Test basic imports
        import flask
        import flask_cors
        import flask_socketio
        print("✅ Flask ecosystem: OK")
        
        # Test core modules
        sys.path.append(str(Path(__file__).parent))
        import app
        print("✅ NoxSuite app module: OK")
        
        # Test database initialization
        app.init_database()
        print("✅ Database initialization: OK")
        
        # Test state management
        state = app.nox_state
        print(f"✅ State management: OK ({type(state).__name__})")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend validation failed: {e}")
        return False

def validate_ai_engine():
    """Validate AI engine and capabilities"""
    print("🔍 Validating AI engine...")
    
    try:
        # Test AI engine import
        sys.path.append(str(Path(__file__).parent))
        import advanced_ai_engine
        print("✅ AI engine module: OK")
        
        # Test AI engine initialization
        ai_engine = advanced_ai_engine.AdvancedAIEngine()
        print("✅ AI engine initialization: OK")
        
        # Test AI capabilities
        status = ai_engine.get_ai_status()
        print(f"✅ AI status check: OK (models: {status.get('models_loaded', 0)})")
        
        # Test threat detection capability (mock data)
        test_threat_data = {
            'source_ip': '127.0.0.1',
            'user_agent': 'test-agent',
            'request_frequency': 1,
            'payload_size': 1024,
            'response_time': 100,
            'error_count': 0,
            'unique_endpoints': 1,
            'geographic_distance': 0,
            'session_duration': 300
        }
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        threat_result = loop.run_until_complete(ai_engine.analyze_threat(test_threat_data))
        print(f"✅ Threat analysis: OK (type: {threat_result.threat_type})")
        
        # Test performance optimization capability
        test_metrics = {
            'cpu_usage': 50,
            'memory_usage': 60,
            'response_time': 200,
            'error_rate': 1
        }
        
        perf_result = loop.run_until_complete(ai_engine.optimize_performance(test_metrics))
        print(f"✅ Performance optimization: OK (component: {perf_result.component})")
        
        # Test user behavior analysis
        test_behavior = {
            'session_duration': 600,
            'click_frequency': 2.5,
            'page_views': 5,
            'features_used': ['dashboard', 'security'],
            'error_encounters': 0,
            'help_requests': 0,
            'accessibility_features_used': 2,
            'response_time_variance': 50,
            'zoom_level': 100,
            'mouse_usage': 80
        }
        
        behavior_result = loop.run_until_complete(ai_engine.analyze_user_behavior('test_user', test_behavior))
        print(f"✅ User behavior analysis: OK (pattern: {behavior_result.behavior_pattern})")
        
        return True
        
    except Exception as e:
        print(f"❌ AI engine validation failed: {e}")
        return False

def validate_frontend():
    """Validate frontend components"""
    print("🔍 Validating frontend components...")
    
    try:
        frontend_dir = Path(__file__).parent / 'frontend'
        
        # Check package.json
        package_json = frontend_dir / 'package.json'
        if not package_json.exists():
            print("❌ Frontend package.json not found")
            return False
        
        with open(package_json) as f:
            package_data = json.load(f)
        
        required_deps = [
            'react',
            '@mui/material',
            'chart.js',
            'socket.io-client'
        ]
        
        missing_deps = []
        for dep in required_deps:
            if dep not in package_data.get('dependencies', {}):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing frontend dependencies: {missing_deps}")
            return False
        
        print("✅ Frontend dependencies: OK")
        
        # Check component files
        components = [
            'src/App.js',
            'src/components/Dashboard.js',
            'src/components/Security.js',
            'src/components/PluginManager.js',
            'src/contexts/AccessibilityContext.js',
            'src/contexts/SocketContext.js'
        ]
        
        missing_components = []
        for component in components:
            if not (frontend_dir / component).exists():
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Missing frontend components: {missing_components}")
            return False
        
        print("✅ Frontend components: OK")
        return True
        
    except Exception as e:
        print(f"❌ Frontend validation failed: {e}")
        return False

def validate_configuration():
    """Validate configuration files"""
    print("🔍 Validating configuration files...")
    
    try:
        required_files = [
            'docker-compose.ultimate.yml',
            'requirements.txt',
            '.env.example',
            'nginx/nginx.conf'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing configuration files: {missing_files}")
            return False
        
        print("✅ Configuration files: OK")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def validate_deployment_scripts():
    """Validate deployment scripts"""
    print("🔍 Validating deployment scripts...")
    
    try:
        scripts = [
            'deploy_ultimate.py',
            'quick_start.py'
        ]
        
        for script in scripts:
            script_path = Path(script)
            if not script_path.exists():
                print(f"❌ Missing deployment script: {script}")
                return False
            
            # Check if script is executable (on Unix-like systems)
            if hasattr(os, 'access') and not os.access(script_path, os.X_OK):
                print(f"⚠️ Script not executable: {script}")
        
        print("✅ Deployment scripts: OK")
        return True
        
    except Exception as e:
        print(f"❌ Deployment script validation failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 NoxSuite Ultimate System Validation")
    print("=" * 50)
    
    validations = [
        ("Backend Components", validate_backend),
        ("AI Engine", validate_ai_engine),
        ("Frontend Components", validate_frontend),
        ("Configuration Files", validate_configuration),
        ("Deployment Scripts", validate_deployment_scripts)
    ]
    
    all_passed = True
    results = {}
    
    for name, validation_func in validations:
        print(f"\n📋 {name}")
        print("-" * 30)
        
        try:
            result = validation_func()
            results[name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            results[name] = False
            all_passed = False
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    if all_passed:
        print("\n🎉 All validations passed! NoxSuite Ultimate is ready!")
        print("\n🚀 Quick start options:")
        print("   python quick_start.py          # Development mode")
        print("   python deploy_ultimate.py      # Full production deployment")
        print("   cd frontend && npm start       # Frontend development")
        
        return True
    else:
        print("\n⚠️ Some validations failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
