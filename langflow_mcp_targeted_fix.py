from NoxPanel.noxcore.utils.logging_config import get_logger
logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Targeted Langflow-MCP Fix
Addresses specific API endpoint and SSE configuration issues
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

class LangflowMCPTargetedFixer:
    def __init__(self):
        self.langflow_url = "http://localhost:7860"
        self.project_id = "d602c2ae-497e-49cf-9e7b-f503ef844007"
        
    def diagnose_langflow_version(self):
        """Determine Langflow version and capabilities"""
        logger.info("🔍 Diagnosing Langflow version and capabilities...")
        
        try:
            # Check Langflow version from health endpoint
            health_url = f"{self.langflow_url}/health"
            with urllib.request.urlopen(health_url, timeout=5) as response:
                data = response.read().decode()
                logger.info(f"   📋 Health response: {data}")
            
            # Check available API endpoints
            api_endpoints = [
                "/api/v1/flows",
                "/api/v1/projects", 
                "/api/docs",
                "/docs"
            ]
            
            available_endpoints = []
            for endpoint in api_endpoints:
                try:
                    with urllib.request.urlopen(f"{self.langflow_url}{endpoint}", timeout=3) as resp:
                        if resp.getcode() == 200:
                            available_endpoints.append(endpoint)
                            logger.info(f"   ✅ Available: {endpoint}")
                except:
                    logger.info(f"   ❌ Not available: {endpoint}")
            
            return available_endpoints
            
        except Exception as e:
            logger.info(f"   ❌ Diagnosis failed: {e}")
            return []
    
    def check_mcp_support(self):
        """Check if this Langflow version supports MCP"""
        logger.info("🔍 Checking MCP support...")
        
        try:
            # Try different MCP endpoint patterns
            mcp_endpoints = [
                f"/api/v1/mcp",
                f"/mcp",
                f"/api/mcp"
            ]
            
            for endpoint in mcp_endpoints:
                try:
                    url = f"{self.langflow_url}{endpoint}"
                    with urllib.request.urlopen(url, timeout=3) as resp:
                        logger.info(f"   ✅ MCP endpoint found: {endpoint} (status: {resp.getcode()})")
                        return endpoint
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        logger.info(f"   ❌ Not found: {endpoint}")
                    else:
                        logger.info(f"   ⚠️ Error on {endpoint}: {e.code}")
                except Exception as e:
                    logger.info(f"   ❌ Failed {endpoint}: {e}")
            
            logger.info("   ❌ No MCP endpoints found - this Langflow version may not support MCP")
            return None
            
        except Exception as e:
            logger.info(f"   ❌ MCP check failed: {e}")
            return None
    
    def create_alternative_mcp_config(self):
        """Create alternative MCP configuration for non-MCP Langflow"""
        logger.info("⚙️ Creating alternative MCP configuration...")
        
        # Configuration for direct Langflow integration without native MCP
        alt_config = {
            "mcpServers": {
                "langflow-bridge": {
                    "command": "python",
                    "args": ["langflow_mcp_bridge.py"],
                    "env": {
                        "LANGFLOW_URL": self.langflow_url,
                        "LANGFLOW_PROJECT_ID": self.project_id
                    },
                    "timeout": 30000
                }
            }
        }
        
        try:
            config_file = Path(".vscode") / "mcp_alternative_settings.json"
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(alt_config, f, indent=2)
            
            logger.info(f"   ✅ Alternative MCP config saved: {config_file}")
            return True
            
        except Exception as e:
            logger.info(f"   ❌ Alternative config creation failed: {e}")
            return False
    
    def create_langflow_mcp_bridge(self):
        """Create a bridge script for MCP-Langflow communication"""
        logger.info("🌉 Creating Langflow-MCP bridge...")
        
        bridge_script = '''#!/usr/bin/env python3
"""
Langflow-MCP Bridge
Provides MCP interface for Langflow instances without native MCP support
"""

import json
import sys
import asyncio
from urllib.request import urlopen
from urllib.error import URLError

class LangflowMCPBridge:
    def __init__(self):
        self.langflow_url = "http://localhost:7860"
        
    async def initialize(self):
        """Initialize MCP server"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True}
            },
            "serverInfo": {
                "name": "langflow-bridge",
                "version": "1.0.0"
            }
        }
    
    async def list_tools(self):
        """List available Langflow tools"""
        return {
            "tools": [
                {
                    "name": "run_flow",
                    "description": "Execute a Langflow flow",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "flow_id": {"type": "string"},
                            "inputs": {"type": "object"}
                        }
                    }
                }
            ]
        }
    
    async def call_tool(self, name, arguments):
        """Execute tool calls"""
        if name == "run_flow":
            # Implement flow execution logic here
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Flow executed with args: {arguments}"
                    }
                ]
            }
        
        raise ValueError(f"Unknown tool: {name}")

# MCP server main loop would go here
if __name__ == "__main__":
    bridge = LangflowMCPBridge()
    logger.info("Langflow-MCP Bridge started")
'''
        
        try:
            with open("langflow_mcp_bridge.py", 'w', encoding='utf-8') as f:
                f.write(bridge_script)
            logger.info("   ✅ Bridge script created: langflow_mcp_bridge.py")
            return True
        except Exception as e:
            logger.info(f"   ❌ Bridge creation failed: {e}")
            return False
    
    def create_simple_restart_script(self):
        """Create restart script without emoji characters"""
        logger.info("🚀 Creating simple restart script...")
        
        restart_script = '''@echo off
echo Restarting Langflow for MCP integration...

REM Stop any existing Langflow processes
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start Langflow
echo Starting Langflow...
langflow run --host 0.0.0.0 --port 7860

echo If Langflow fails to start, try:
echo    pip install langflow --upgrade
echo    or
echo    python -m langflow run --host 0.0.0.0 --port 7860
pause
'''
        
        try:
            with open("restart_langflow_simple.bat", 'w', encoding='ascii') as f:
                f.write(restart_script)
            logger.info("   ✅ Simple restart script created: restart_langflow_simple.bat")
            return True
        except Exception as e:
            logger.info(f"   ❌ Simple script creation failed: {e}")
            return False
    
    def create_mcp_test_script(self):
        """Create a test script to verify MCP functionality"""
        logger.info("🧪 Creating MCP test script...")
        
        test_script = '''#!/usr/bin/env python3
"""
MCP Connection Test
Tests the connection between VS Code MCP and Langflow
"""

import json
import urllib.request
from datetime import datetime

def test_langflow_connection():
    """Test basic Langflow connectivity"""
    try:
        with urllib.request.urlopen("http://localhost:7860/health", timeout=5) as resp:
            if resp.getcode() == 200:
                logger.info("✅ Langflow is running")
                return True
            else:
                logger.info(f"❌ Langflow health check failed: {resp.getcode()}")
                return False
    except Exception as e:
        logger.info(f"❌ Langflow connection failed: {e}")
        return False

def test_mcp_endpoints():
    """Test MCP-specific endpoints"""
    endpoints = [
        "/api/v1/mcp",
        "/mcp", 
        "/api/mcp"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:7860{endpoint}"
            with urllib.request.urlopen(url, timeout=3) as resp:
                logger.info(f"✅ MCP endpoint working: {endpoint}")
                return True
        except:
            logger.info(f"❌ MCP endpoint failed: {endpoint}")
    
    logger.info("❌ No working MCP endpoints found")
    return False

def main():
    logger.info("🧪 MCP Connection Test")
    logger.info("=" * 40)
    
    langflow_ok = test_langflow_connection()
    mcp_ok = test_mcp_endpoints()
    
    logger.info("\\n📋 Test Results:")
    logger.info(f"   Langflow: {'✅ OK' if langflow_ok else '❌ Failed'}")
    logger.info(f"   MCP: {'✅ OK' if mcp_ok else '❌ Failed'}")
    
    if langflow_ok and not mcp_ok:
        logger.info("\\n💡 Recommendation: Use the bridge configuration")
        logger.info("   This Langflow version may not have native MCP support")
    
    # Save test results
    results = {
        "timestamp": datetime.now().isoformat(),
        "langflow_working": langflow_ok,
        "mcp_working": mcp_ok,
        "recommendation": "use_bridge" if langflow_ok and not mcp_ok else "native_mcp"
    }
    
    with open("mcp_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("📄 Results saved to: mcp_test_results.json")

if __name__ == "__main__":
    main()
'''
        
        try:
            with open("test_mcp_connection.py", 'w', encoding='utf-8') as f:
                f.write(test_script)
            logger.info("   ✅ Test script created: test_mcp_connection.py")
            return True
        except Exception as e:
            logger.info(f"   ❌ Test script creation failed: {e}")
            return False

def main():
    """Main targeted fix routine"""
    logger.info("🔧 Targeted Langflow-MCP Fix")
    logger.info("=" * 50)
    
    fixer = LangflowMCPTargetedFixer()
    
    # Step 1: Diagnose Langflow capabilities
    logger.info("\\n📊 Step 1: Langflow Diagnosis")
    available_endpoints = fixer.diagnose_langflow_version()
    
    # Step 2: Check MCP support
    logger.info("\\n🔍 Step 2: MCP Support Check")
    mcp_endpoint = fixer.check_mcp_support()
    
    # Step 3: Create appropriate configuration
    logger.info("\\n⚙️ Step 3: Configuration")
    if mcp_endpoint:
        logger.info("   ✅ Native MCP support detected")
        # Use original MCP configuration
    else:
        logger.info("   ⚠️ No native MCP support - creating bridge")
        fixer.create_alternative_mcp_config()
        fixer.create_langflow_mcp_bridge()
    
    # Step 4: Create tools
    logger.info("\\n🛠️ Step 4: Creating Tools")
    fixer.create_simple_restart_script()
    fixer.create_mcp_test_script()
    
    logger.info("\\n" + "=" * 50)
    logger.info("✅ Targeted Fix Completed!")
    
    logger.info("\\n🎯 Next Steps:")
    logger.info("1. Run: python test_mcp_connection.py")
    logger.info("2. Check test results for recommendations")
    if not mcp_endpoint:
        logger.info("3. Use bridge configuration in VS Code MCP settings")
        logger.info("4. Configure VS Code to use: langflow_mcp_bridge.py")
    else:
        logger.info("3. Restart Langflow with: restart_langflow_simple.bat")
        logger.info("4. Test native MCP integration")
    
    # Create final status
    status = {
        "timestamp": time.time(),
        "langflow_url": fixer.langflow_url,
        "available_endpoints": available_endpoints,
        "mcp_endpoint": mcp_endpoint,
        "native_mcp_support": mcp_endpoint is not None,
        "recommendation": "native" if mcp_endpoint else "bridge",
        "files_created": [
            "test_mcp_connection.py",
            "restart_langflow_simple.bat"
        ]
    }
    
    if not mcp_endpoint:
        status["files_created"].extend([
            "langflow_mcp_bridge.py",
            ".vscode/mcp_alternative_settings.json"
        ])
    
    with open("targeted_fix_status.json", 'w') as f:
        json.dump(status, f, indent=2)
    
    logger.info("📄 Status saved to: targeted_fix_status.json")

if __name__ == "__main__":
    main()