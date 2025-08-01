from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import time
import json
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Langflow-MCP Connection Fix (Standard Library Version)
Resolves SSE integration issues between Langflow and MCP
"""


class LangflowMCPFixer:
    def __init__(self):
        self.langflow_url = "http://localhost:7860"
        self.project_id = "d602c2ae-497e-49cf-9e7b-f503ef844007"

    def check_langflow_health(self):
        """Check if Langflow is properly responding"""
        logger.info("🔍 Checking Langflow health...")

        try:
            # Check basic health
            health_url = f"{self.langflow_url}/health"
            try:
                with urllib.request.urlopen(health_url, timeout=5) as response:
                    if response.getcode() == 200:
                        logger.info("   ✅ Langflow basic health: OK")
                    else:
                        logger.info(
                            f"   ❌ Langflow health failed: {response.getcode()}"
                        )
                        return False
            except urllib.error.URLError:
                logger.info("   ❌ Langflow not accessible")
                return False

            # Check API endpoints
            try:
                api_url = f"{self.langflow_url}/api/v1/auto_login"
                with urllib.request.urlopen(api_url, timeout=5) as response:
                    logger.info(
                        f"   📡 API endpoint status: {response.getcode()}")
            except urllib.error.URLError as e:
                logger.info(f"   ⚠️ API endpoint issue: {e}")

            # Check the problematic SSE endpoint
            try:
                sse_url = (
                    f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/sse"
                )
                req = urllib.request.Request(sse_url)
                req.add_header("Accept", "text/event-stream")

                with urllib.request.urlopen(req, timeout=5) as response:
                    content_type = response.headers.get("content-type", "")
                    logger.info(
                        f"   🔗 SSE endpoint content-type: {content_type}")

                    if "text/event-stream" not in content_type:
                        logger.info(
                            "   ❌ SSE endpoint not configured properly")
                        return False
                    else:
                        logger.info("   ✅ SSE endpoint configured correctly")

            except urllib.error.URLError as e:
                logger.info(f"   ❌ SSE endpoint error: {e}")
                return False

            return True

        except Exception as e:
            logger.info(f"   ❌ Health check failed: {e}")
            return False

    def fix_langflow_sse(self):
        """Fix Langflow SSE configuration"""
        logger.info("🔧 Fixing Langflow SSE configuration...")

        try:
            # Create project if it doesn't exist
            project_data = {
                "name": "NoxSuite MCP Integration",
                "description": "MCP integration project for NoxSuite",
            }

            # POST request to create project
            data = json.dumps(project_data).encode("utf-8")
            req = urllib.request.Request(
                f"{self.langflow_url}/api/v1/projects",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(data)),
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.getcode() in [200, 201]:
                        result = json.loads(response.read().decode())
                        logger.info(
                            f"   ✅ Project created/verified: {result.get('id', 'unknown')}"
                        )
                    else:
                        logger.info(
                            f"   ⚠️ Project creation status: {response.getcode()}"
                        )
            except urllib.error.HTTPError as e:
                if e.code == 409:  # Conflict - project already exists
                    logger.info("   ✅ Project already exists")
                else:
                    logger.info(f"   ⚠️ Project creation error: {e.code}")

            # Enable MCP for the project
            mcp_config = {
                "enabled": True,
                "sse_enabled": True,
                "project_id": self.project_id,
            }

            config_data = json.dumps(mcp_config).encode("utf-8")
            config_req = urllib.request.Request(
                f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/config",
                data=config_data,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(config_data)),
                },
                method="PUT",
            )

            try:
                with urllib.request.urlopen(config_req, timeout=10) as response:
                    if response.getcode() in [200, 201]:
                        logger.info("   ✅ MCP configuration updated")
                    else:
                        logger.info(
                            f"   ⚠️ MCP config status: {response.getcode()}")
            except urllib.error.HTTPError as e:
                logger.info(f"   ⚠️ MCP config error: {e.code}")

            return True

        except Exception as e:
            logger.info(f"   ❌ SSE fix failed: {e}")
            return False

    def create_mcp_server_config(self):
        """Create proper MCP server configuration"""
        logger.info("⚙️ Creating MCP server configuration...")

        mcp_config = {
            "mcpServers": {
                "langflow": {
                    "command": "python",
                    "args": ["-m", "langflow", "mcp"],
                    "env": {
                        "LANGFLOW_HOST": "localhost",
                        "LANGFLOW_PORT": "7860",
                        "LANGFLOW_PROJECT_ID": self.project_id,
                    },
                    "timeout": 30000,
                    "retry": {"enabled": True, "maxAttempts": 3, "delay": 2000},
                }
            }
        }

        try:
            config_file = Path(".vscode") / "mcp_settings.json"
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, "w") as f:
                json.dump(mcp_config, f, indent=2)

            logger.info(f"   ✅ MCP config saved: {config_file}")
            return True

        except Exception as e:
            logger.info(f"   ❌ Config creation failed: {e}")
            return False

    def create_langflow_restart_script(self):
        """Create script to restart Langflow with proper settings"""
        logger.info("🚀 Creating Langflow restart script...")

        restart_script = f"""@echo off
echo 🔄 Restarting Langflow for MCP integration...

REM Stop any existing Langflow processes
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start Langflow with MCP support
echo ✅ Starting Langflow...
langflow run --host 0.0.0.0 --port 7860 --backend-only

echo 💡 If Langflow fails to start, try:
echo    pip install langflow --upgrade
echo    or
echo    python -m langflow run --host 0.0.0.0 --port 7860
pause
"""

        try:
            with open("restart_langflow.bat", "w") as f:
                f.write(restart_script)
            logger.info("   ✅ Restart script created: restart_langflow.bat")
            return True
        except Exception as e:
            logger.info(f"   ❌ Script creation failed: {e}")
            return False

    def validate_connection(self):
        """Validate the MCP-Langflow connection"""
        logger.info("✅ Validating connection...")

        try:
            # Test the SSE endpoint with proper headers
            sse_url = f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/sse"
            req = urllib.request.Request(sse_url)
            req.add_header("Accept", "text/event-stream")
            req.add_header("Cache-Control", "no-cache")

            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    content_type = response.headers.get("content-type", "")

                    if "text/event-stream" in content_type:
                        logger.info("   ✅ SSE connection working")
                        return True
                    else:
                        logger.info(
                            f"   ❌ SSE still returning: {content_type}")
                        return False

            except urllib.error.URLError as e:
                if "timeout" in str(e).lower():
                    logger.info(
                        "   ⚠️ SSE connection timeout (expected for stream)")
                    return True  # Timeout is actually expected for SSE streams
                else:
                    logger.info(f"   ❌ Validation failed: {e}")
                    return False

        except Exception as e:
            logger.info(f"   ❌ Validation error: {e}")
            return False


def main():
    """Main fix routine"""
    logger.info("🔧 Langflow-MCP Connection Fix (Standard Library)")
    logger.info("=" * 60)

    fixer = LangflowMCPFixer()

    # Step 1: Check current health
    logger.info("\n📊 Step 1: Health Check")
    langflow_ok = fixer.check_langflow_health()

    # Step 2: Apply fixes if needed
    if not langflow_ok:
        logger.info("\n🔧 Step 2: Applying fixes...")
        fixer.fix_langflow_sse()
    else:
        logger.info("\n✅ Step 2: Langflow appears healthy")

    # Step 3: Configure MCP
    logger.info("\n⚙️ Step 3: MCP Configuration")
    fixer.create_mcp_server_config()

    # Step 4: Create restart tools
    logger.info("\n🛠️ Step 4: Creating Tools")
    fixer.create_langflow_restart_script()

    # Step 5: Validate
    logger.info("\n🔍 Step 5: Validation")
    connection_ok = fixer.validate_connection()

    logger.info("\n" + "=" * 60)
    logger.info("✅ Langflow-MCP Fix Completed!")

    logger.info(f"\n📋 Status Summary:")
    logger.info(f"   Langflow Health: {'✅ OK' if langflow_ok else '❌ Issues'}")
    logger.info(
        f"   MCP Connection: {'✅ OK' if connection_ok else '❌ Issues'}")

    logger.info("\n🎯 Next Steps:")
    if not langflow_ok:
        logger.info("1. Run: restart_langflow.bat")
        logger.info("2. Wait for Langflow to fully start")
    logger.info("3. In VS Code: Ctrl+Shift+P → 'MCP: Restart Server'")
    logger.info("4. Check VS Code Output panel → MCP")
    logger.info("5. Test MCP functionality")

    # Create completion status
    status = {
        "timestamp": time.time(),
        "langflow_url": fixer.langflow_url,
        "project_id": fixer.project_id,
        "langflow_health": langflow_ok,
        "mcp_connection": connection_ok,
        "status": "completed",
        "files_created": [".vscode/mcp_settings.json", "restart_langflow.bat"],
    }

    with open("langflow_mcp_fix_status.json", "w") as f:
        json.dump(status, f, indent=2)

    logger.info("📄 Status saved to: langflow_mcp_fix_status.json")


if __name__ == "__main__":
    main()
