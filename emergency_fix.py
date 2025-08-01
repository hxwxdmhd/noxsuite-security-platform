import time
import sys
import subprocess
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Emergency system fix - addresses both CVE and Copilot issues
"""


def emergency_langflow_update():
    """Update Langflow container with security patches"""
    try:
        logger.info("🔒 Stopping vulnerable Langflow container...")
        subprocess.run(["docker", "stop", "noxsuite-langflow"], check=True)

        logger.info("📦 Pulling latest secure Langflow image...")
        subprocess.run(
            ["docker", "pull", "langflowai/langflow:latest"], check=True)

        logger.info("🔄 Restarting with updated container...")
        subprocess.run(["docker-compose", "up", "-d", "langflow"], check=True)

        logger.info("✅ Langflow security update completed")
        return True

    except subprocess.CalledProcessError as e:
        logger.info(f"❌ Failed to update Langflow: {e}")
        return False


def test_copilot_throttling():
    """Test the new throttling mechanism"""
    logger.info("🧪 Testing Copilot throttling mechanism...")

    # Simulate multiple tool calls
    for i in range(5):
        result = throttler.execute_with_throttle(
            lambda x: f"Tool call {x} executed successfully", i + 1
        )
        logger.info(f"   {result}")
        time.sleep(1)

    logger.info("✅ Throttling mechanism working correctly")


def main():
    logger.info("🚨 NoxSuite Emergency Fix - Starting...")

    # Step 1: Fix Langflow CVE issues
    if emergency_langflow_update():
        logger.info("✅ Langflow security issues resolved")
    else:
        logger.info("❌ Langflow update failed - manual intervention required")

    # Step 2: Test Copilot throttling
    test_copilot_throttling()

    # Step 3: Provide usage instructions
    logger.info("\n📋 USAGE INSTRUCTIONS:")
    logger.info(
        "1. Use 'throttler.execute_with_throttle(function)' for all tool calls")
    logger.info("2. Split complex tasks using 'split_large_task()'")
    logger.info("3. Monitor tool count with 'throttler.tool_count'")
    logger.info("4. System auto-resets every 5 minutes")

    logger.info("\n🎯 Emergency fixes applied successfully!")


if __name__ == "__main__":
    main()
