"""
NoxSuite TypeScript-Python Integration Bridge
Connects TypeScript configuration with Python monitoring system
Date: 2025-07-29 07:01:37 UTC
Author: @hxwxdmhd
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced monitoring system
try:
    from enhanced_monitoring_system import Category, EnhancedMonitoringSystem, Severity
except ImportError as e:
    print(f"⚠️ Enhanced monitoring system not available: {e}")

    # Create mock classes for testing
    class EnhancedMonitoringSystem:
        def __init__(self):
            pass

        def start_monitoring(self):
            pass

        def stop_monitoring(self):
            pass

        def get_system_health(self):
            from collections import namedtuple

            Health = namedtuple(
                "Health",
                [
                    "memory_usage_percent",
                    "cpu_usage_percent",
                    "api_response_time_ms",
                    "error_rate_percent",
                    "uptime_hours",
                ],
            )
            return Health(75.5, 45.2, 120.3, 0.5, 24.7)

        def generate_enhanced_report(self):
            return {
                "status": "mock_report",
                "incidents": [],
                "monitoring_status": {"active": False},
            }

    class Severity:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class Category:
        SECURITY = "security"
        PERFORMANCE = "performance"


@dataclass
class NoxSuiteConfig:
    """Python representation of NoxSuite TypeScript configuration"""

    agent_mode: int
    parallel_workers: int
    chain_depth: int
    api_integration: int
    chunk_tokens: int
    tool_iterations: int
    retry_limit: int
    reasoning_bias: int
    context_cache: int
    debug_level: int
    task_priorities: List[int]
    plugin_modules: List[int]
    safety_flags: int
    heartbeat_interval: int
    max_payload: int
    adaptive_theme: List[int]
    versioning_sync: int
    auto_update: bool

    @classmethod
    def from_seed(cls, seed: str) -> "NoxSuiteConfig":
        """Parse configuration from seed string"""
        parts = seed.split("-")
        return cls(
            agent_mode=int(parts[0]),
            parallel_workers=int(parts[1]),
            chain_depth=int(parts[2]),
            api_integration=int(parts[3]),
            chunk_tokens=int(parts[4]),
            tool_iterations=int(parts[5]),
            retry_limit=int(parts[6]),
            reasoning_bias=int(parts[7]),
            context_cache=int(parts[8]),
            debug_level=int(parts[9]),
            task_priorities=[int(x) for x in parts[10].split(",")],
            plugin_modules=[int(x) for x in parts[11].split(",")],
            safety_flags=int(parts[12]),
            heartbeat_interval=int(parts[13]),
            max_payload=int(parts[14]),
            adaptive_theme=[int(x) for x in parts[15].split(",")],
            versioning_sync=int(parts[16]),
            auto_update=bool(int(parts[17])),
        )


@dataclass
class PluginStatus:
    """Plugin status tracking"""

    id: int
    name: str
    state: str
    last_update: str
    performance_score: float


@dataclass
class ThemeStatus:
    """Theme configuration status"""

    mode: str
    contrast: str
    animations_enabled: bool
    adhd_features_active: bool
    accessibility_score: float


class NoxSuiteIntegrationBridge:
    """
    Integration bridge between TypeScript NoxSuite configuration
    and Python enhanced monitoring system
    """

    def __init__(self):
        self.logger = logging.getLogger("NoxSuiteIntegration")
        self.config: Optional[NoxSuiteConfig] = None
        self.monitoring_system: Optional[EnhancedMonitoringSystem] = None
        self.plugin_registry = {
            2101: "PowerShell_Automation",
            3302: "MariaDB_Integration",
            4501: "WebUI_Framework",
            6200: "LLM_Orchestration",
        }

        # Default seed from TypeScript configuration
        self.default_seed = "91-6-22-95-512-15-5-89-8192-42-85,78,92,67,81-2101,3302,4501,6200-1-8-10000-1,2-9-1"

    async def initialize(self, seed: Optional[str] = None) -> None:
        """Initialize the integration bridge"""
        try:
            # Parse configuration
            config_seed = seed or self.default_seed
            self.config = NoxSuiteConfig.from_seed(config_seed)

            self.logger.info("🚀 Initializing NoxSuite Integration Bridge")
            self.logger.info(f"📊 Agent Mode: {self.config.agent_mode}")
            self.logger.info(f"🔌 Plugins: {len(self.config.plugin_modules)}")
            self.logger.info(f"🎨 Theme Mode: {self.config.adaptive_theme}")

            # Initialize enhanced monitoring
            self.monitoring_system = EnhancedMonitoringSystem()
            self.monitoring_system.start_monitoring()

            # Validate configuration
            await self.validate_configuration()

            # Initialize TypeScript components
            await self.initialize_typescript_components()

            self.logger.info(
                "✅ NoxSuite Integration Bridge initialized successfully")

        except Exception as e:
            self.logger.error(
                f"❌ Failed to initialize integration bridge: {e}")
            raise

    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate NoxSuite configuration against best practices"""
        validation_results = {
            "is_valid": True,
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
        }

        # Validate agent mode
        if self.config.agent_mode < 80:
            validation_results["critical_issues"].append(
                {
                    "code": "AGENT_MODE_TOO_LOW",
                    "message": "Agent mode below 80 may cause performance issues",
                    "current_value": self.config.agent_mode,
                    "recommended_min": 80,
                }
            )
            validation_results["is_valid"] = False

        # Validate API integration
        if self.config.api_integration < 90:
            validation_results["warnings"].append(
                {
                    "code": "API_INTEGRATION_SUBOPTIMAL",
                    "message": "API integration below 90 may limit functionality",
                    "current_value": self.config.api_integration,
                    "recommended_min": 90,
                }
            )

        # Validate parallel workers
        if self.config.parallel_workers < 4:
            validation_results["warnings"].append(
                {
                    "code": "LOW_PARALLEL_WORKERS",
                    "message": "Consider increasing parallel workers for better performance",
                    "current_value": self.config.parallel_workers,
                    "recommended_min": 6,
                }
            )

        # Validate security flags
        if self.config.safety_flags < 1:
            validation_results["critical_issues"].append(
                {
                    "code": "INSUFFICIENT_SAFETY",
                    "message": "Safety flags must be at least 1 for secure operation",
                    "current_value": self.config.safety_flags,
                    "required_min": 1,
                }
            )
            validation_results["is_valid"] = False

        # Add recommendations
        if self.config.context_cache < 8192:
            validation_results["recommendations"].append(
                "Consider increasing context cache for better AI performance"
            )

        if len(self.config.plugin_modules) < 4:
            validation_results["recommendations"].append(
                "Full plugin suite (4 modules) recommended for complete functionality"
            )

        # Log validation results
        if validation_results["is_valid"]:
            self.logger.info("✅ Configuration validation passed")
        else:
            self.logger.error("❌ Configuration validation failed")
            for issue in validation_results["critical_issues"]:
                self.logger.error(f"   🚨 {issue['code']}: {issue['message']}")

        return validation_results

    async def initialize_typescript_components(self) -> None:
        """Initialize TypeScript components via Node.js"""
        try:
            # Check if Node.js is available
            node_path = Path("src/core/NoxSuiteController.ts")
            if not node_path.exists():
                self.logger.warning(
                    "⚠️ TypeScript controller not found, skipping TS initialization"
                )
                return

            # Create initialization script
            init_script = f"""
const {{ initializeNoxSuite }} = require('./src/core/NoxSuiteController.ts');

async function init() {{
    try {{
        const controller = await initializeNoxSuite();
        console.log('✅ TypeScript components initialized');
        
        // Get current configuration
        const config = controller.getConfig();
        console.log('📊 Configuration loaded:', JSON.stringify(config, null, 2));
        
    }} catch (error) {{
        console.error('❌ TypeScript initialization failed:', error);
    }}
}}

init();
"""

            # Write temporary initialization script
            with open("temp_init.js", "w") as f:
                f.write(init_script)

            self.logger.info("📝 TypeScript components initialization prepared")

        except Exception as e:
            self.logger.warning(
                f"⚠️ TypeScript initialization setup failed: {e}")

    async def get_plugin_status(self) -> List[PluginStatus]:
        """Get status of all configured plugins"""
        plugin_statuses = []

        for plugin_id in self.config.plugin_modules:
            plugin_name = self.plugin_registry.get(
                plugin_id, f"Unknown_{plugin_id}")

            # Simulate plugin status check
            status = PluginStatus(
                id=plugin_id,
                name=plugin_name,
                state="active",  # Would be checked dynamically
                last_update=datetime.now(timezone.utc).isoformat(),
                performance_score=85.0 + (plugin_id % 15),  # Simulated score
            )

            plugin_statuses.append(status)

        return plugin_statuses

    async def get_theme_status(self) -> ThemeStatus:
        """Get current theme configuration status"""
        theme_mode = "spicy" if 1 in self.config.adaptive_theme else "steady"

        return ThemeStatus(
            mode=theme_mode,
            contrast="normal",
            animations_enabled=True,
            adhd_features_active=True,
            accessibility_score=92.5,  # Simulated accessibility score
        )

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics combining TS and Python monitoring"""
        if not self.monitoring_system:
            return {}

        # Get Python monitoring system metrics
        health = self.monitoring_system.get_system_health()

        # Get plugin and theme status
        plugins = await self.get_plugin_status()
        theme = await self.get_theme_status()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_health": {
                "memory_usage": health.memory_usage_percent,
                "cpu_usage": health.cpu_usage_percent,
                "api_response_time": health.api_response_time_ms,
                "error_rate": health.error_rate_percent,
                "uptime_hours": health.uptime_hours,
            },
            "noxsuite_config": {
                "agent_mode": self.config.agent_mode,
                "api_integration": self.config.api_integration,
                "parallel_workers": self.config.parallel_workers,
                "plugin_count": len(self.config.plugin_modules),
                "theme_mode": theme.mode,
            },
            "plugins": [asdict(plugin) for plugin in plugins],
            "theme": asdict(theme),
            "performance_score": self._calculate_performance_score(
                health, plugins, theme
            ),
        }

    def _calculate_performance_score(self, health, plugins, theme) -> float:
        """Calculate overall system performance score"""
        # Base score from system health
        health_score = 100 - (
            health.memory_usage_percent * 0.5 + health.cpu_usage_percent * 0.3
        )

        # Plugin performance contribution
        plugin_score = (
            sum(p.performance_score for p in plugins) /
            len(plugins) if plugins else 0
        )

        # Theme accessibility contribution
        theme_score = theme.accessibility_score

        # Configuration quality score
        config_score = (
            min(100, self.config.agent_mode + self.config.api_integration) / 2
        )

        # Weighted average
        overall_score = (
            health_score * 0.4
            + plugin_score * 0.3
            + theme_score * 0.2
            + config_score * 0.1
        )

        return max(0, min(100, overall_score))

    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report"""
        if not self.monitoring_system:
            return {"error": "Monitoring system not initialized"}

        # Get monitoring system report
        monitoring_report = self.monitoring_system.generate_enhanced_report()

        # Get NoxSuite specific metrics
        nox_metrics = await self.get_system_metrics()

        # Combine reports
        comprehensive_report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "generator": "NoxSuite Integration Bridge",
                "version": "1.0.0",
                "integration_mode": "TypeScript-Python",
            },
            "noxsuite_status": nox_metrics,
            "monitoring_data": monitoring_report,
            "configuration": asdict(self.config),
            "validation": await self.validate_configuration(),
            "recommendations": self._generate_integration_recommendations(nox_metrics),
        }

        return comprehensive_report

    def _generate_integration_recommendations(
        self, metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on integrated system analysis"""
        recommendations = []

        perf_score = metrics.get("performance_score", 0)

        if perf_score < 70:
            recommendations.append(
                "System performance below optimal - consider configuration tuning"
            )

        if metrics["system_health"]["memory_usage"] > 80:
            recommendations.append(
                "High memory usage detected - consider increasing parallel workers"
            )

        if metrics["system_health"]["api_response_time"] > 200:
            recommendations.append(
                "API response time exceeding target - optimize endpoint performance"
            )

        plugin_count = len(metrics.get("plugins", []))
        if plugin_count < 4:
            recommendations.append(
                "Consider enabling full plugin suite for complete functionality"
            )

        if metrics["noxsuite_config"]["agent_mode"] < 90:
            recommendations.append(
                "Agent mode could be optimized for better AI performance"
            )

        if not recommendations:
            recommendations.append(
                "System operating optimally - all metrics within target ranges"
            )

        return recommendations

    async def shutdown(self) -> None:
        """Gracefully shutdown the integration bridge"""
        self.logger.info("🛑 Shutting down NoxSuite Integration Bridge")

        if self.monitoring_system:
            self.monitoring_system.stop_monitoring()

        # Clean up temporary files
        temp_file = Path("temp_init.js")
        if temp_file.exists():
            temp_file.unlink()

        self.logger.info("✅ Integration bridge shutdown complete")


async def main():
    """Main function for testing the integration bridge"""
    try:
        print("🚀 NoxSuite TypeScript-Python Integration Bridge")
        print("=" * 55)

        bridge = NoxSuiteIntegrationBridge()

        # Initialize bridge
        print("🔄 Initializing integration bridge...")
        await bridge.initialize()

        # Run for a short period to collect metrics
        print("\n⏳ Collecting system metrics...")
        await asyncio.sleep(5)  # Reduced from 10 seconds

        # Get system metrics
        print("📊 Gathering system metrics...")
        metrics = await bridge.get_system_metrics()

        print("\n📊 NOXSUITE SYSTEM METRICS")
        print("=" * 30)
        print(f"Performance Score: {metrics['performance_score']:.1f}%")
        print(f"Agent Mode: {metrics['noxsuite_config']['agent_mode']}")
        print(
            f"API Integration: {metrics['noxsuite_config']['api_integration']}%")
        print(f"Active Plugins: {metrics['noxsuite_config']['plugin_count']}")
        print(f"Theme Mode: {metrics['noxsuite_config']['theme_mode']}")

        print(f"\n🛡️ SYSTEM HEALTH")
        print(f"Memory Usage: {metrics['system_health']['memory_usage']:.1f}%")
        print(f"CPU Usage: {metrics['system_health']['cpu_usage']:.1f}%")
        print(
            f"API Response: {metrics['system_health']['api_response_time']:.1f}ms")

        # Generate comprehensive report
        print("\n📋 Generating comprehensive report...")
        report = await bridge.generate_comprehensive_report()

        # Save report
        report_file = Path("noxsuite_integration_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📋 Comprehensive report saved: {report_file}")

        # Display recommendations
        recommendations = report.get("recommendations", [])
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   • {rec}")

        print(f"\n✅ Integration bridge test completed successfully")

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        try:
            await bridge.shutdown()
        except:
            pass  # Ignore shutdown errors


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
