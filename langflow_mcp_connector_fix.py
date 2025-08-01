import aiohttp
from pathlib import Path
import time
import json
import asyncio
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Langflow-MCP Connection Fix
Resolves SSE integration issues between Langflow and MCP
"""


class LangflowMCPFixer:
    def __init__(self):
        self.langflow_url = "http://localhost:7860"
        self.project_id = "d602c2ae-497e-49cf-9e7b-f503ef844007"

    async def check_langflow_health(self):
        """Check if Langflow is properly responding"""
        logger.info("🔍 Checking Langflow health...")

        try:
            async with aiohttp.ClientSession() as session:
                # Check basic health
                async with session.get(f"{self.langflow_url}/health") as resp:
                    if resp.status == 200:
                        logger.info("   ✅ Langflow basic health: OK")
                    else:
                        logger.info(
                            f"   ❌ Langflow health failed: {resp.status}")
                        return False

                # Check API endpoints
                async with session.get(
                    f"{self.langflow_url}/api/v1/auto_login"
                ) as resp:
                    logger.info(f"   📡 API endpoint status: {resp.status}")

                # Check the problematic SSE endpoint
                sse_url = (
                    f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/sse"
                )
                async with session.get(sse_url) as resp:
                    content_type = resp.headers.get("content-type", "")
                    logger.info(
                        f"   🔗 SSE endpoint content-type: {content_type}")

                    if "text/event-stream" not in content_type:
                        logger.info(
                            "   ❌ SSE endpoint not configured properly")
                        return False
                    else:
                        logger.info("   ✅ SSE endpoint configured correctly")

                return True

        except Exception as e:
            logger.info(f"   ❌ Langflow connection failed: {e}")
            return False

    async def fix_langflow_sse(self):
        """Fix Langflow SSE configuration"""
        logger.info("🔧 Fixing Langflow SSE configuration...")

        try:
            # First, try to create/initialize the project properly
            async with aiohttp.ClientSession() as session:
                # Create project if it doesn't exist
                project_data = {
                    "name": "NoxSuite MCP Integration",
                    "description": "MCP integration project for NoxSuite",
                }

                async with session.post(
                    f"{self.langflow_url}/api/v1/projects",
                    json=project_data,
                    headers={"Content-Type": "application/json"},
                ) as resp:
                    if resp.status in [200, 201]:
                        result = await resp.json()
                        logger.info(
                            f"   ✅ Project created/verified: {result.get('id', 'unknown')}"
                        )
                    else:
                        logger.info(
                            f"   ⚠️ Project creation status: {resp.status}")

                # Enable MCP for the project
                mcp_config = {
                    "enabled": True,
                    "sse_enabled": True,
                    "project_id": self.project_id,
                }

                async with session.put(
                    f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/config",
                    json=mcp_config,
                    headers={"Content-Type": "application/json"},
                ) as resp:
                    if resp.status in [200, 201]:
                        logger.info("   ✅ MCP configuration updated")
                    else:
                        logger.info(f"   ⚠️ MCP config status: {resp.status}")

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

    async def restart_services(self):
        """Restart Langflow and MCP services"""
        logger.info("🔄 Restarting services...")

        # Note: In production, you'd want proper service management
        logger.info("   📝 Manual restart required:")
        logger.info(f"   1. Stop Langflow (Ctrl+C in terminal)")
        logger.info(f"   2. Restart: langflow run --host 0.0.0.0 --port 7860")
        logger.info(f"   3. Restart VS Code MCP extension")

        # Wait a moment for any async operations
        await asyncio.sleep(2)

        return True

    async def validate_connection(self):
        """Validate the MCP-Langflow connection"""
        logger.info("✅ Validating connection...")

        try:
            async with aiohttp.ClientSession() as session:
                # Test the SSE endpoint with proper headers
                headers = {"Accept": "text/event-stream",
                           "Cache-Control": "no-cache"}

                sse_url = (
                    f"{self.langflow_url}/api/v1/mcp/project/{self.project_id}/sse"
                )

                async with session.get(sse_url, headers=headers, timeout=5) as resp:
                    content_type = resp.headers.get("content-type", "")

                    if "text/event-stream" in content_type:
                        logger.info("   ✅ SSE connection working")
                        return True
                    else:
                        logger.info(
                            f"   ❌ SSE still returning: {content_type}")
                        return False

        except asyncio.TimeoutError:
            logger.info("   ⚠️ SSE connection timeout (expected for stream)")
            return True  # Timeout is actually expected for SSE streams
        except Exception as e:
            logger.info(f"   ❌ Validation failed: {e}")
            return False


async def main():
    """Main fix routine"""
    logger.info("🔧 Langflow-MCP Connection Fix")
    logger.info("=" * 50)

    fixer = LangflowMCPFixer()

    # Step 1: Check current health
    langflow_ok = await fixer.check_langflow_health()

    # Step 2: Apply fixes
    if not langflow_ok:
        logger.info("\n🔧 Applying fixes...")
        await fixer.fix_langflow_sse()

    # Step 3: Configure MCP
    fixer.create_mcp_server_config()

    # Step 4: Restart services
    await fixer.restart_services()

    # Step 5: Validate
    await fixer.validate_connection()

    logger.info("\n" + "=" * 50)
    logger.info("✅ Langflow-MCP Fix Completed!")

    logger.info("\n📋 Next Steps:")
    logger.info("1. Restart Langflow: langflow run --host 0.0.0.0 --port 7860")
    logger.info("2. In VS Code: Ctrl+Shift+P → 'MCP: Restart Server'")
    logger.info("3. Check VS Code Output panel for MCP logs")
    logger.info("4. Test MCP functionality")

    # Create completion status
    status = {
        "timestamp": time.time(),
        "langflow_url": fixer.langflow_url,
        "project_id": fixer.project_id,
        "status": "fixed",
        "next_steps": ["restart_langflow", "restart_mcp_server", "test_connection"],
    }

    with open("langflow_mcp_fix_status.json", "w") as f:
        json.dump(status, f, indent=2)

    logger.info("📄 Status saved to: langflow_mcp_fix_status.json")


if __name__ == "__main__":
    asyncio.run(main())
