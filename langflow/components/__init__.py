from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

"""
NoxSuite Custom Components for Langflow
Provides Docker management, MCP orchestration, system monitoring, and multi-agent coordination
"""

# Import all custom components
try:
    from .noxsuite_docker_manager import NoxSuiteDockerManager
    from .noxsuite_mcp_orchestrator import NoxSuiteMCPOrchestrator
    from .noxsuite_multi_agent_coordinator import NoxSuiteMultiAgentCoordinator
    from .noxsuite_system_monitor import NoxSuiteSystemMonitor

    __all__ = [
        "NoxSuiteDockerManager",
        "NoxSuiteMCPOrchestrator",
        "NoxSuiteSystemMonitor",
        "NoxSuiteMultiAgentCoordinator",
    ]

    logger.info("SUCCESS: NoxSuite components loaded successfully")

except ImportError as e:
    logger.info(f"WARNING: Error importing NoxSuite components: {e}")
    __all__ = []
