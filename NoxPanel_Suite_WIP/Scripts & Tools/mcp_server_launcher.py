#!/usr/bin/env python3
"""
🎯 NoxSuite MCP Server Launcher
Enterprise-grade MCP server orchestration with health monitoring

REASONING CHAIN:
1. Problem: Multiple MCP servers need coordinated launch and monitoring
2. Analysis: Complexity 3.5/5.0 - Multiple processes, health checks, graceful shutdown
3. Solution: Centralized launcher with process management and status monitoring
4. Validation: Health checks, logging, error recovery, graceful shutdown handling

COMPLIANCE: ENHANCED
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Configure logging with Unicode support for Windows
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_server_launcher.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

if not PSUTIL_AVAILABLE:
    logger.warning("psutil not available - resource monitoring disabled")


@dataclass
class MCPServerConfig:
    """Configuration for individual MCP server"""

    name: str
    script_path: str
    description: str
    port: Optional[int] = None
    env_vars: Dict[str, str] = None
    capabilities: List[str] = None
    auto_restart: bool = True
    health_check_interval: int = 30


@dataclass
class ServerStatus:
    """Runtime status of MCP server"""

    name: str
    pid: Optional[int] = None
    status: str = "stopped"  # stopped, starting, running, error, crashed
    start_time: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    restart_count: int = 0
    error_message: Optional[str] = None
    memory_usage: float = 0.0
    cpu_usage: float = 0.0


class MCPServerLauncher:
    """
    Enterprise MCP Server Orchestration System

    REASONING CHAIN:
    1. Problem: Need coordinated management of multiple MCP servers with monitoring
    2. Analysis: Process management, health monitoring, error recovery, graceful shutdown
    3. Solution: Centralized launcher with async process management and status tracking
    4. Validation: Health checks every 30s, automatic restart on failure, metrics collection
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.servers: Dict[str, MCPServerConfig] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.status: Dict[str, ServerStatus] = {}
        self.running = False
        self.status_file = workspace_root / "mcp" / "server_status.json"

        # Ensure status directory exists
        self.status_file.parent.mkdir(exist_ok=True)

        # Initialize default servers
        self._initialize_default_servers()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _initialize_default_servers(self):
        """Initialize default NoxSuite MCP servers"""
        servers = [
            MCPServerConfig(
                name="noxsuite-orchestrator",
                script_path="Scripts & Tools/mcp_autonomous_orchestrator.py",
                description="Autonomous Development Orchestrator",
                capabilities=["workspace_audit", "self_healing", "code_analysis"],
                env_vars={"MCP_SERVER_MODE": "true", "ENABLE_AUTO_HEALING": "true"},
            ),
            MCPServerConfig(
                name="noxsuite-knowledge",
                script_path="Scripts & Tools/semantic_knowledge_parser.py",
                description="Semantic Knowledge Base Manager",
                capabilities=[
                    "knowledge_extraction",
                    "conversation_parsing",
                    "semantic_search",
                ],
                env_vars={
                    "MCP_SERVER_MODE": "true",
                    "KNOWLEDGE_BASE_PATH": "mcp/knowledgebase",
                },
            ),
            MCPServerConfig(
                name="noxsuite-annotator",
                script_path="Scripts & Tools/intelligent_code_annotator.py",
                description="Intelligent Code Annotator with RLVR",
                capabilities=[
                    "code_annotation",
                    "rlvr_injection",
                    "docstring_generation",
                ],
                env_vars={"MCP_SERVER_MODE": "true", "ANNOTATION_MODE": "enhanced"},
            ),
            MCPServerConfig(
                name="noxsuite-installer",
                script_path="Scripts & Tools/noxsuite_smart_installer.py",
                description="Self-Healing Smart Installer",
                capabilities=[
                    "dependency_resolution",
                    "auto_installation",
                    "error_recovery",
                ],
                env_vars={"MCP_SERVER_MODE": "true", "INSTALLER_MODE": "autonomous"},
            ),
            MCPServerConfig(
                name="noxsuite-cicd",
                script_path="Scripts & Tools/mcp_cicd_monitor.py",
                description="CI/CD Continuous Monitor",
                capabilities=["cicd_monitoring", "drift_detection", "auto_fixing"],
                env_vars={"MCP_SERVER_MODE": "true", "MONITORING_ENABLED": "true"},
            ),
        ]

        for server in servers:
            self.servers[server.name] = server
            self.status[server.name] = ServerStatus(name=server.name)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    async def start_server(self, server_name: str) -> bool:
        """
        Start individual MCP server with health monitoring

        REASONING CHAIN:
        1. Problem: Need to start MCP server with proper environment and monitoring
        2. Analysis: Process creation, environment setup, health check initialization
        3. Solution: Subprocess management with async monitoring and error handling
        4. Validation: Process PID tracking, status updates, error logging
        """
        if server_name not in self.servers:
            logger.error(f"Unknown server: {server_name}")
            return False

        server_config = self.servers[server_name]
        status = self.status[server_name]

        # Check if already running
        if status.status == "running":
            logger.info(f"Server {server_name} is already running")
            return True

        try:
            # Update status
            status.status = "starting"
            status.start_time = datetime.now()

            # Prepare environment
            env = dict(os.environ)
            if server_config.env_vars:
                env.update(server_config.env_vars)

            # Build command
            script_path = self.workspace_root / server_config.script_path
            if not script_path.exists():
                raise FileNotFoundError(f"Server script not found: {script_path}")

            cmd = [sys.executable, str(script_path), "--server-mode"]

            # Start process
            logger.info(f"Starting {server_name}: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(self.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Store process and update status
            self.processes[server_name] = process
            status.pid = process.pid
            status.status = "running"
            status.error_message = None

            logger.info(
                f"Server {server_name} started successfully (PID: {process.pid})"
            )
            await self._save_status()

            return True

        except Exception as e:
            logger.error(f"Failed to start {server_name}: {e}")
            status.status = "error"
            status.error_message = str(e)
            await self._save_status()
            return False

    async def stop_server(self, server_name: str) -> bool:
        """Stop individual MCP server gracefully"""
        if server_name not in self.processes:
            logger.info(f"Server {server_name} is not running")
            return True

        try:
            process = self.processes[server_name]
            status = self.status[server_name]

            logger.info(f"Stopping {server_name} (PID: {process.pid})")

            # Try graceful shutdown first
            process.terminate()

            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {server_name}")
                process.kill()
                process.wait()

            # Update status
            del self.processes[server_name]
            status.pid = None
            status.status = "stopped"

            logger.info(f"Server {server_name} stopped successfully")
            await self._save_status()

            return True

        except Exception as e:
            logger.error(f"Failed to stop {server_name}: {e}")
            return False

    async def health_check(self, server_name: str) -> bool:
        """
        Perform health check on MCP server

        REASONING CHAIN:
        1. Problem: Need to monitor server health and detect failures
        2. Analysis: Process monitoring, resource usage tracking, responsiveness check
        3. Solution: PID validation, resource metrics, crash detection
        4. Validation: Status updates, restart on failure, metrics logging
        """
        if server_name not in self.processes:
            return False

        try:
            process = self.processes[server_name]
            status = self.status[server_name]

            # Check if process is still running
            if process.poll() is not None:
                logger.warning(
                    f"Server {server_name} has crashed (exit code: {process.returncode})"
                )
                status.status = "crashed"
                status.error_message = f"Process exited with code {process.returncode}"
                del self.processes[server_name]

                # Auto-restart if enabled
                if self.servers[server_name].auto_restart and status.restart_count < 3:
                    logger.info(
                        f"Auto-restarting {server_name} (attempt {status.restart_count + 1})"
                    )
                    status.restart_count += 1
                    await self.start_server(server_name)

                return False

            # Get resource usage
            if PSUTIL_AVAILABLE:
                try:
                    proc = psutil.Process(process.pid)
                    status.memory_usage = proc.memory_info().rss / 1024 / 1024  # MB
                    status.cpu_usage = proc.cpu_percent()
                except psutil.NoSuchProcess:
                    logger.warning(f"Process {server_name} not found in psutil")
                except Exception as e:
                    logger.debug(f"Resource monitoring error for {server_name}: {e}")
            else:
                # Basic monitoring without psutil
                status.memory_usage = 0.0
                status.cpu_usage = 0.0

            status.last_health_check = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Health check failed for {server_name}: {e}")
            return False

    async def start_all_servers(self):
        """Start all configured MCP servers"""
        logger.info("Starting all MCP servers...")

        tasks = []
        for server_name in self.servers:
            tasks.append(self.start_server(server_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        logger.info(f"Started {success_count}/{len(self.servers)} servers successfully")

    async def stop_all_servers(self):
        """Stop all running MCP servers"""
        logger.info("Stopping all MCP servers...")

        tasks = []
        for server_name in list(self.processes.keys()):
            tasks.append(self.stop_server(server_name))

        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("All servers stopped")

    async def monitor_health(self):
        """Continuous health monitoring loop"""
        while self.running:
            try:
                for server_name in list(self.processes.keys()):
                    await self.health_check(server_name)

                await self._save_status()
                await asyncio.sleep(30)  # Health check every 30 seconds

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)

    async def _save_status(self):
        """Save current server status to file"""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "servers": {
                    name: {
                        "name": status.name,
                        "pid": status.pid,
                        "status": status.status,
                        "start_time": (
                            status.start_time.isoformat() if status.start_time else None
                        ),
                        "last_health_check": (
                            status.last_health_check.isoformat()
                            if status.last_health_check
                            else None
                        ),
                        "restart_count": status.restart_count,
                        "error_message": status.error_message,
                        "memory_usage": status.memory_usage,
                        "cpu_usage": status.cpu_usage,
                    }
                    for name, status in self.status.items()
                },
            }

            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        running_count = sum(1 for s in self.status.values() if s.status == "running")
        total_memory = sum(s.memory_usage for s in self.status.values())
        total_cpu = sum(s.cpu_usage for s in self.status.values())

        return {
            "servers_running": running_count,
            "servers_total": len(self.servers),
            "total_memory_mb": round(total_memory, 2),
            "total_cpu_percent": round(total_cpu, 2),
            "uptime": (
                datetime.now()
                - min(
                    (s.start_time for s in self.status.values() if s.start_time),
                    default=datetime.now(),
                )
            ).total_seconds(),
            "servers": {name: status.status for name, status in self.status.items()},
        }

    async def run(self):
        """
        Main launcher loop with monitoring

        REASONING CHAIN:
        1. Problem: Need orchestrated startup and monitoring of all MCP servers
        2. Analysis: Startup sequence, monitoring loop, graceful shutdown handling
        3. Solution: Async orchestration with health monitoring and signal handling
        4. Validation: All servers start, health monitoring active, graceful shutdown works
        """
        self.running = True

        try:
            # Start all servers
            await self.start_all_servers()

            # Print status summary
            summary = self.get_status_summary()
            logger.info(
                f"MCP Server Launcher Status: {summary['servers_running']}/{summary['servers_total']} servers running"
            )

            # Start health monitoring
            health_task = asyncio.create_task(self.monitor_health())

            # Wait for shutdown signal
            while self.running:
                await asyncio.sleep(1)

            # Cancel health monitoring
            health_task.cancel()

            # Graceful shutdown
            await self.stop_all_servers()

        except Exception as e:
            logger.error(f"Launcher error: {e}")
        finally:
            logger.info("MCP Server Launcher shutdown complete")


async def main():
    """Main entry point"""
    import os

    workspace_root = Path(os.getcwd())
    launcher = MCPServerLauncher(workspace_root)

    logger.info("🚀 NoxSuite MCP Server Launcher Starting...")
    logger.info(f"Workspace: {workspace_root}")
    logger.info(f"Servers configured: {len(launcher.servers)}")

    await launcher.run()


if __name__ == "__main__":
    import os

    asyncio.run(main())
