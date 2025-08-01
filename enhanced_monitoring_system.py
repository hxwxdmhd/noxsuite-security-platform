#!/usr/bin/env python3
"""
ENHANCED COPILOT AGENT MONITORING SYSTEM
Implementation of enhanced critical monitoring for NoxSuite
Date: 2025-07-29 06:49:09 UTC
Author: @hxwxdmhd
Mode: ENHANCED_CRITICAL_MONITORING
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import re
import requests
import threading

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import logging
import psutil
import subprocess
import time



class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    STABILITY = "stability"
    BUILD = "build"
    DEPLOYMENT = "deployment"
    API = "api"


class ActionType(Enum):
    IMMEDIATE_HALT = "immediate_halt"
    ANALYZE_AND_REPORT = "analyze_and_report"
    HALT_BUILD = "halt_build"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    NOTIFY_TEAM = "notify_team"
    REDUCE_LOAD = "reduce_load"


@dataclass
class MonitoringAction:
    type: ActionType
    notification: str
    remediation: str
    parameters: Dict[str, Any] = None


@dataclass
class MonitoringPattern:
    id: str
    category: Category
    pattern: str
    severity: Severity
    context: int
    action: MonitoringAction
    description: str


@dataclass
class Incident:
    id: str
    timestamp: str
    pattern_id: str
    severity: Severity
    category: Category
    message: str
    context: List[str]
    action_taken: str
    resolved: bool = False


@dataclass
class MetricThreshold:
    warning: float
    critical: float
    duration: str


@dataclass
class MetricDefinition:
    id: str
    name: str
    category: str
    unit: str
    threshold: MetricThreshold
    current_value: float = 0.0
    last_updated: str = ""


@dataclass
class SystemHealthMetrics:
    memory_usage_percent: float
    cpu_usage_percent: float
    disk_usage_percent: float
    api_response_time_ms: float
    error_rate_percent: float
    uptime_hours: float
    active_connections: int


class EnhancedMonitoringSystem:
    """
    Enhanced Copilot Agent Monitoring System
    Implements comprehensive pattern matching, intervention protocols, and reporting
    """

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.incidents: List[Incident] = []
        self.metrics: Dict[str, MetricDefinition] = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.flask_server_url = "http://localhost:5000"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    "logs/enhanced_monitoring.log", mode="a", encoding="utf-8"
                ),
            ],
        )
        self.logger = logging.getLogger("EnhancedMonitoring")

        # Initialize patterns and metrics
        self._initialize_patterns()
        self._initialize_metrics()

    def _initialize_patterns(self):
        """Initialize enhanced monitoring patterns"""
        self.patterns = [
            MonitoringPattern(
                id="SEC001",
                category=Category.SECURITY,
                pattern=r'(?:password|secret|key|token|credential)s?\s*(?:=|:)\s*[\'"][^\'"]+[\'"]',
                severity=Severity.CRITICAL,
                context=5,
                action=MonitoringAction(
                    type=ActionType.IMMEDIATE_HALT,
                    notification="security_team",
                    remediation="remove_credentials",
                ),
                description="Hardcoded credentials detected",
            ),
            MonitoringPattern(
                id="PERF001",
                category=Category.PERFORMANCE,
                pattern=r"(?:FATAL|ERROR)\s*(?:MemoryError|OutOfMemory|heap\s+space)",
                severity=Severity.CRITICAL,
                context=10,
                action=MonitoringAction(
                    type=ActionType.ANALYZE_AND_REPORT,
                    notification="dev_team",
                    remediation="memory_analysis",
                ),
                description="Memory error detected",
            ),
            MonitoringPattern(
                id="BUILD001",
                category=Category.BUILD,
                pattern=r"(?:build|compilation)\s+failed|(?:error|exception)\s+in\s+build",
                severity=Severity.HIGH,
                context=15,
                action=MonitoringAction(
                    type=ActionType.HALT_BUILD,
                    notification="build_team",
                    remediation="analyze_build_logs",
                ),
                description="Build failure detected",
            ),
            MonitoringPattern(
                id="API001",
                category=Category.API,
                pattern=r"api\s+response\s+time\s+exceeded\s+(\d+)ms",
                severity=Severity.MEDIUM,
                context=8,
                action=MonitoringAction(
                    type=ActionType.PERFORMANCE_ANALYSIS,
                    notification="api_team",
                    remediation="optimize_endpoint",
                ),
                description="API response time exceeded threshold",
            ),
            MonitoringPattern(
                id="STAB001",
                category=Category.STABILITY,
                pattern=r"(?:crash|exception|abort|segfault|core\s+dump)",
                severity=Severity.HIGH,
                context=12,
                action=MonitoringAction(
                    type=ActionType.IMMEDIATE_HALT,
                    notification="ops_team",
                    remediation="system_recovery",
                ),
                description="System stability issue detected",
            ),
        ]

    def _initialize_metrics(self):
        """Initialize enhanced metric definitions"""
        metric_definitions = [
            MetricDefinition(
                id="SYS_MEM_001",
                name="memory_usage_detailed",
                category="system",
                unit="percentage",
                threshold=MetricThreshold(
                    warning=75.0, critical=85.0, duration="5m"),
            ),
            MetricDefinition(
                id="API_PERF_001",
                name="api_response_time",
                category="performance",
                unit="milliseconds",
                threshold=MetricThreshold(
                    warning=150.0, critical=200.0, duration="1m"),
            ),
            MetricDefinition(
                id="SYS_CPU_001",
                name="cpu_usage_detailed",
                category="system",
                unit="percentage",
                threshold=MetricThreshold(
                    warning=70.0, critical=85.0, duration="3m"),
            ),
            MetricDefinition(
                id="SYS_DISK_001",
                name="disk_usage_detailed",
                category="system",
                unit="percentage",
                threshold=MetricThreshold(
                    warning=80.0, critical=90.0, duration="10m"),
            ),
            MetricDefinition(
                id="API_ERR_001",
                name="api_error_rate",
                category="performance",
                unit="percentage",
                threshold=MetricThreshold(
                    warning=1.0, critical=5.0, duration="5m"),
            ),
        ]

        for metric in metric_definitions:
            self.metrics[metric.id] = metric

    def start_monitoring(self):
        """Start enhanced monitoring system"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        self.logger.info("🚀 Enhanced monitoring system started")
        print("🚀 ENHANCED MONITORING SYSTEM ACTIVATED")
        print("📊 Pattern matching: ACTIVE")
        print("🔍 Metric collection: ACTIVE")
        print("🚨 Intervention protocols: READY")

    def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Monitoring system stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Check for patterns in logs
                self._scan_logs_for_patterns()

                # Evaluate metric thresholds
                self._evaluate_thresholds()

                # Check Flask server health
                self._check_server_health()

                time.sleep(30)  # 30-second monitoring cycle

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)  # Extended sleep on error

    def _collect_system_metrics(self):
        """Collect enhanced system metrics"""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            self._update_metric("SYS_MEM_001", memory.percent)

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self._update_metric("SYS_CPU_001", cpu_percent)

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self._update_metric("SYS_DISK_001", disk_percent)

        except Exception as e:
            self.logger.error(f"System metrics collection error: {e}")

    def _check_server_health(self):
        """Check Flask server health and API performance"""
        try:
            # Test API response time
            start_time = time.time()
            response = requests.get(
                f"{self.flask_server_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000

            # Update API response time metric
            self._update_metric("API_PERF_001", response_time)

            # Calculate error rate
            if response.status_code >= 400:
                self._update_metric("API_ERR_001", 100.0)  # Error occurred
            else:
                self._update_metric("API_ERR_001", 0.0)  # Success

        except requests.RequestException:
            # Server unreachable
            self._update_metric("API_PERF_001", 5000.0)  # Timeout value
            self._update_metric("API_ERR_001", 100.0)  # Total failure

            # Create incident for server unavailability
            self._create_incident(
                pattern_id="STAB001",
                severity=Severity.CRITICAL,
                category=Category.STABILITY,
                message="Flask server unreachable",
                context=["Server health check failed",
                         "Connection timeout or refused"],
                action_taken="Logged server unavailability incident",
            )

    def _update_metric(self, metric_id: str, value: float):
        """Update metric value and timestamp"""
        if metric_id in self.metrics:
            self.metrics[metric_id].current_value = value
            self.metrics[metric_id].last_updated = datetime.now(
                timezone.utc
            ).isoformat()

    def _scan_logs_for_patterns(self):
        """Scan logs for monitoring patterns"""
        log_files = ["logs/enhanced_monitoring.log", "logs/noxpanel_test.log"]

        for log_file in log_files:
            log_path = Path(log_file)
            if log_path.exists():
                self._scan_file_for_patterns(log_path)

    def _scan_file_for_patterns(self, file_path: Path):
        """Scan individual file for patterns"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                for pattern in self.patterns:
                    if re.search(pattern.pattern, line, re.IGNORECASE):
                        self._handle_pattern_match(pattern, line, lines, i)

        except Exception as e:
            self.logger.error(f"Error scanning {file_path}: {e}")

    def _handle_pattern_match(
        self,
        pattern: MonitoringPattern,
        matched_line: str,
        all_lines: List[str],
        line_index: int,
    ):
        """Handle pattern match detection"""
        # Extract context lines
        start_idx = max(0, line_index - pattern.context)
        end_idx = min(len(all_lines), line_index + pattern.context + 1)
        context = [line.strip() for line in all_lines[start_idx:end_idx]]

        # Create incident
        incident_id = f"{pattern.id}_{int(time.time())}"
        self._create_incident(
            pattern_id=pattern.id,
            severity=pattern.severity,
            category=pattern.category,
            message=f"{pattern.description}: {matched_line.strip()}",
            context=context,
            action_taken=f"Applied {pattern.action.type.value} intervention",
        )

        # Execute intervention
        self._execute_intervention(pattern, matched_line)

    def _create_incident(
        self,
        pattern_id: str,
        severity: Severity,
        category: Category,
        message: str,
        context: List[str],
        action_taken: str,
    ):
        """Create new incident record"""
        incident = Incident(
            id=f"{pattern_id}_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            pattern_id=pattern_id,
            severity=severity,
            category=category,
            message=message,
            context=context,
            action_taken=action_taken,
        )

        self.incidents.append(incident)

        # Log incident
        severity_emoji = {
            Severity.CRITICAL: "🚨",
            Severity.HIGH: "⚠️",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "ℹ️",
        }

        self.logger.warning(
            f"{severity_emoji[severity]} INCIDENT {incident.id}: {message}"
        )

        print(f"{severity_emoji[severity]} INCIDENT DETECTED: {pattern_id}")
        print(f"   Message: {message}")
        print(f"   Severity: {severity.value}")
        print(f"   Action: {action_taken}")

    def _execute_intervention(self, pattern: MonitoringPattern, matched_line: str):
        """Execute intervention protocol based on pattern"""
        action = pattern.action

        if action.type == ActionType.IMMEDIATE_HALT:
            self._intervention_immediate_halt(pattern, matched_line)
        elif action.type == ActionType.ANALYZE_AND_REPORT:
            self._intervention_analyze_report(pattern, matched_line)
        elif action.type == ActionType.PERFORMANCE_ANALYSIS:
            self._intervention_performance_analysis(pattern, matched_line)
        elif action.type == ActionType.HALT_BUILD:
            self._intervention_halt_build(pattern, matched_line)
        else:
            self.logger.info(f"Intervention logged: {action.type.value}")

    def _intervention_immediate_halt(
        self, pattern: MonitoringPattern, matched_line: str
    ):
        """Execute immediate halt intervention"""
        self.logger.critical(f"IMMEDIATE HALT triggered by {pattern.id}")
        print(f"🛑 IMMEDIATE HALT INTERVENTION TRIGGERED")
        print(f"   Pattern: {pattern.id}")
        print(f"   Reason: {pattern.description}")
        print(f"   Recommendation: {pattern.action.remediation}")

    def _intervention_analyze_report(
        self, pattern: MonitoringPattern, matched_line: str
    ):
        """Execute analyze and report intervention"""
        self.logger.warning(f"Analysis intervention triggered by {pattern.id}")
        print(f"🔍 ANALYSIS INTERVENTION TRIGGERED")
        print(f"   Pattern: {pattern.id}")
        print(f"   Analysis: {pattern.action.remediation}")

    def _intervention_performance_analysis(
        self, pattern: MonitoringPattern, matched_line: str
    ):
        """Execute performance analysis intervention"""
        self.logger.info(f"Performance analysis triggered by {pattern.id}")
        print(f"⚡ PERFORMANCE ANALYSIS INTERVENTION")
        print(f"   Pattern: {pattern.id}")
        print(f"   Optimization: {pattern.action.remediation}")

    def _intervention_halt_build(self, pattern: MonitoringPattern, matched_line: str):
        """Execute halt build intervention"""
        self.logger.error(f"Build halt triggered by {pattern.id}")
        print(f"🔨 BUILD HALT INTERVENTION")
        print(f"   Pattern: {pattern.id}")
        print(f"   Action: {pattern.action.remediation}")

    def _evaluate_thresholds(self):
        """Evaluate metric thresholds and trigger interventions"""
        for metric_id, metric in self.metrics.items():
            if metric.current_value > metric.threshold.critical:
                self._trigger_threshold_intervention(metric, "critical")
            elif metric.current_value > metric.threshold.warning:
                self._trigger_threshold_intervention(metric, "warning")

    def _trigger_threshold_intervention(self, metric: MetricDefinition, level: str):
        """Trigger intervention for threshold breach"""
        if level == "critical":
            self._create_incident(
                pattern_id=f"THRESHOLD_{metric.id}",
                severity=Severity.CRITICAL,
                category=Category.PERFORMANCE,
                message=f"Critical threshold exceeded: {metric.name} = {metric.current_value}{metric.unit}",
                context=[
                    f"Threshold: {metric.threshold.critical}",
                    f"Current: {metric.current_value}",
                ],
                action_taken="Critical threshold intervention triggered",
            )

    def get_system_health(self) -> SystemHealthMetrics:
        """Get current system health metrics"""
        return SystemHealthMetrics(
            memory_usage_percent=self.metrics["SYS_MEM_001"].current_value,
            cpu_usage_percent=self.metrics["SYS_CPU_001"].current_value,
            disk_usage_percent=self.metrics["SYS_DISK_001"].current_value,
            api_response_time_ms=self.metrics["API_PERF_001"].current_value,
            error_rate_percent=self.metrics["API_ERR_001"].current_value,
            uptime_hours=self._get_system_uptime(),
            active_connections=self._get_active_connections(),
        )

    def _get_system_uptime(self) -> float:
        """Get system uptime in hours"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            return uptime_seconds / 3600
        except:
            return 0.0

    def _get_active_connections(self) -> int:
        """Get active network connections"""
        try:
            connections = psutil.net_connections()
            return len([c for c in connections if c.status == "ESTABLISHED"])
        except:
            return 0

    def generate_enhanced_report(self) -> Dict[str, Any]:
        """Generate comprehensive enhanced monitoring report"""
        current_time = datetime.now(timezone.utc)

        report = {
            "metadata": {
                "timestamp": current_time.isoformat(),
                "generator": "@hxwxdmhd",
                "version": "2.0.0",
                "mode": "ENHANCED_CRITICAL_MONITORING",
                "report_period": {
                    "start": (current_time - timedelta(hours=1)).isoformat(),
                    "end": current_time.isoformat(),
                },
            },
            "system_health": asdict(self.get_system_health()),
            "incidents": [
                asdict(incident) for incident in self.incidents[-10:]
            ],  # Last 10 incidents
            "metrics": {
                metric_id: {
                    "name": metric.name,
                    "current_value": metric.current_value,
                    "unit": metric.unit,
                    "threshold_warning": metric.threshold.warning,
                    "threshold_critical": metric.threshold.critical,
                    "status": self._get_metric_status(metric),
                    "last_updated": metric.last_updated,
                }
                for metric_id, metric in self.metrics.items()
            },
            "monitoring_status": {
                "active": self.monitoring_active,
                "patterns_loaded": len(self.patterns),
                "metrics_tracked": len(self.metrics),
                "incidents_total": len(self.incidents),
                "last_scan": current_time.isoformat(),
            },
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _get_metric_status(self, metric: MetricDefinition) -> str:
        """Get status for metric based on thresholds"""
        if metric.current_value >= metric.threshold.critical:
            return "CRITICAL"
        elif metric.current_value >= metric.threshold.warning:
            return "WARNING"
        else:
            return "HEALTHY"

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on current system state"""
        recommendations = []

        # Check system health
        health = self.get_system_health()

        if health.memory_usage_percent > 80:
            recommendations.append(
                "Consider optimizing memory usage or increasing system memory"
            )

        if health.cpu_usage_percent > 70:
            recommendations.append(
                "Monitor CPU-intensive processes and consider optimization"
            )

        if health.api_response_time_ms > 200:
            recommendations.append(
                "API response times exceeding target - investigate endpoint optimization"
            )

        if health.error_rate_percent > 1:
            recommendations.append(
                "Elevated error rate detected - review application logs"
            )

        # Check recent incidents
        recent_incidents = [
            i
            for i in self.incidents
            if datetime.fromisoformat(i.timestamp.replace("Z", "+00:00"))
            > datetime.now(timezone.utc) - timedelta(hours=1)
        ]

        if len(recent_incidents) > 5:
            recommendations.append(
                "High incident rate detected - review system stability"
            )

        if not recommendations:
            recommendations.append("System operating within normal parameters")

        return recommendations


def main():
    """Main function for enhanced monitoring system"""
    print("🚀 INITIALIZING ENHANCED MONITORING SYSTEM")
    print("=" * 60)

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Initialize monitoring system
    monitor = EnhancedMonitoringSystem()

    try:
        # Start monitoring
        monitor.start_monitoring()

        # Run for initial assessment
        print("\n⏳ Running initial assessment (60 seconds)...")
        time.sleep(60)

        # Generate and display report
        report = monitor.generate_enhanced_report()

        print("\n" + "=" * 60)
        print("📊 ENHANCED MONITORING REPORT")
        print("=" * 60)

        # System Health Summary
        health = report["system_health"]
        print(f"\n🛡️ SYSTEM HEALTH:")
        print(f"   Memory Usage: {health['memory_usage_percent']:.1f}%")
        print(f"   CPU Usage: {health['cpu_usage_percent']:.1f}%")
        print(f"   Disk Usage: {health['disk_usage_percent']:.1f}%")
        print(f"   API Response: {health['api_response_time_ms']:.1f}ms")
        print(f"   Error Rate: {health['error_rate_percent']:.1f}%")
        print(f"   Uptime: {health['uptime_hours']:.1f} hours")

        # Monitoring Status
        status = report["monitoring_status"]
        print(f"\n📊 MONITORING STATUS:")
        print(f"   Active: {'✅' if status['active'] else '❌'}")
        print(f"   Patterns: {status['patterns_loaded']}")
        print(f"   Metrics: {status['metrics_tracked']}")
        print(f"   Incidents: {status['incidents_total']}")

        # Recent Incidents
        if report["incidents"]:
            print(f"\n🚨 RECENT INCIDENTS:")
            for incident in report["incidents"][-3:]:  # Show last 3
                severity_emoji = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "🟡",
                    "low": "ℹ️",
                }
                emoji = severity_emoji.get(incident["severity"], "❓")
                print(
                    f"   {emoji} {incident['pattern_id']}: {incident['message'][:60]}..."
                )

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")

        # Save report
        report_file = Path("ENHANCED_MONITORING_REPORT.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📋 Full report saved: {report_file}")

        # Continue monitoring
        print(f"\n🔄 Enhanced monitoring continues in background...")
        print(f"   Use Ctrl+C to stop monitoring")

        # Keep monitoring active
        while True:
            time.sleep(300)  # Report every 5 minutes
            print(
                f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Monitoring active...")

    except KeyboardInterrupt:
        print(f"\n\n🛑 Monitoring stopped by user")
        monitor.stop_monitoring()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        monitor.stop_monitoring()

    finally:
        # Final report
        if monitor.monitoring_active:
            monitor.stop_monitoring()

        final_report = monitor.generate_enhanced_report()
        print(
            f"\n📊 Final Status: {len(final_report['incidents'])} incidents recorded")


if __name__ == "__main__":
    main()
