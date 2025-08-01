from typing import Any, Dict, List
import time
import logging
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Emergency VS Code Copilot 128 Tools Limit Workaround
"""


class CopilotEmergencyThrottler:
    def __init__(self):
        self.tool_count = 0
        self.max_tools = 120  # Safety margin
        self.reset_interval = 300  # 5 minutes
        self.last_reset = time.time()

    def can_execute_tool(self) -> bool:
        """Check if we can safely execute another tool"""
        current_time = time.time()

        # Reset counter every 5 minutes
        if current_time - self.last_reset > self.reset_interval:
            self.tool_count = 0
            self.last_reset = current_time

        return self.tool_count < self.max_tools

    def execute_with_throttle(self, tool_function, *args, **kwargs):
        """Execute tool with automatic throttling"""
        if not self.can_execute_tool():
            logger.info("⚠️ Tool limit reached, waiting for reset...")
            time.sleep(self.reset_interval - (time.time() - self.last_reset))
            self.tool_count = 0
            self.last_reset = time.time()

        self.tool_count += 1
        return tool_function(*args, **kwargs)


# Global throttler instance
throttler = CopilotEmergencyThrottler()
