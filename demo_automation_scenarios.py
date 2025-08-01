from pathlib import Path
from datetime import datetime
import time
import os
import json
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

"""
NoxSuite Custom Automation Scenarios - Demo Script
Demonstrates advanced workflow automation scenarios with real examples
"""


class NoxSuiteScenarioDemo:
    """Demonstration class for NoxSuite automation scenarios"""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.flows_dir = self.project_root / "langflow" / "flows"
        self.demo_data_dir = self.project_root / "demo_data"
        self.demo_data_dir.mkdir(exist_ok=True)

        # Demo scenarios
        self.scenarios = {
            "ai_code_scanner": {
                "name": "AI-Powered Code Quality & Security Scanner",
                "file": "ai_code_scanner.json",
                "demo_type": "code_analysis",
            },
            "smart_autoscaler": {
                "name": "Intelligent Load Balancer with Auto-Scaling",
                "file": "smart_autoscaler.json",
                "demo_type": "performance_optimization",
            },
            "security_guardian": {
                "name": "Proactive Security Threat Detection & Response",
                "file": "security_guardian.json",
                "demo_type": "security_monitoring",
            },
            "smart_data_pipeline": {
                "name": "Intelligent Data Pipeline with ML Analytics",
                "file": "smart_data_pipeline.json",
                "demo_type": "data_analytics",
            },
        }

    def create_demo_data(self):
        """Create sample data for demonstrations"""
        logger.info("📊 Creating demo data for scenarios...")

        # 1. Sample vulnerable code for AI Code Scanner
        vulnerable_code = """
# Vulnerable Python code example
import subprocess
import pickle
import os
import shlex

def execute_command(user_input):
    # Security fix: Safe command execution with input validation
    if not user_input or len(user_input.strip()) == 0:
        return b"Error: Empty command"
    
    # Parse command safely
    try:
        cmd_parts = shlex.split(user_input)
        # Allow only safe commands for demo purposes
        safe_commands = ['echo', 'ls', 'pwd', 'date', 'whoami']
        if cmd_parts[0] not in safe_commands:
            return b"Error: Command not allowed in demo mode"
        
        result = subprocess.run(cmd_parts, capture_output=True, timeout=5)
        return result.stdout
    except (ValueError, subprocess.TimeoutExpired) as e:
        return f"Error: {str(e)}".encode()

def load_data(file_path):
    # Security vulnerability: Pickle deserialization
    with open(file_path, 'rb') as f:
        data = pickle.load(f)  # Unsafe!
    return data

def get_secret():
    # Security fixed: Use environment variables
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    return api_key

# Performance issue: Inefficient loop
def slow_function(data_list):
    result = []
    for i in range(len(data_list)):
        for j in range(len(data_list)):
            if data_list[i] == data_list[j] and i != j:
                result.append(data_list[i])
    return result
"""

        with open(self.demo_data_dir / "vulnerable_code.py", "w") as f:
            f.write(vulnerable_code)

        # 2. Sample performance metrics for Autoscaler
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_usage": [45, 67, 89, 92, 85, 78, 65],
                "memory_usage": [55, 72, 88, 91, 87, 74, 62],
                "response_time": [120, 250, 450, 650, 520, 380, 200],
                "concurrent_users": [100, 200, 500, 800, 600, 400, 250],
            },
            "scaling_events": [
                {"time": "10:15", "action": "scale_up", "instances": "2->4"},
                {"time": "11:30", "action": "scale_up", "instances": "4->6"},
                {"time": "14:20", "action": "scale_down", "instances": "6->3"},
            ],
        }

        with open(self.demo_data_dir / "performance_metrics.json", "w") as f:
            json.dump(performance_data, f, indent=2)

        # 3. Sample security logs for Security Guardian
        security_logs = [
            {
                "timestamp": "2025-07-29T19:30:15Z",
                "level": "WARNING",
                "event": "Multiple failed login attempts",
                "source_ip": "192.168.1.100",
                "threat_level": "medium",
            },
            {
                "timestamp": "2025-07-29T19:32:22Z",
                "level": "CRITICAL",
                "event": "SQL injection attempt detected",
                "source_ip": "10.0.0.50",
                "threat_level": "high",
            },
            {
                "timestamp": "2025-07-29T19:35:10Z",
                "level": "INFO",
                "event": "Suspicious file upload",
                "source_ip": "172.16.0.25",
                "threat_level": "low",
            },
            {
                "timestamp": "2025-07-29T19:38:45Z",
                "level": "CRITICAL",
                "event": "Privilege escalation attempt",
                "source_ip": "192.168.1.100",
                "threat_level": "critical",
            },
        ]

        with open(self.demo_data_dir / "security_logs.json", "w") as f:
            json.dump(security_logs, f, indent=2)

        # 4. Sample data for ML Pipeline
        sample_data = {
            "customer_data": [
                {"id": 1, "age": 25, "purchases": 150, "category": "electronics"},
                {"id": 2, "age": 34, "purchases": 320, "category": "clothing"},
                {"id": 3, "age": 45, "purchases": 89, "category": "books"},
                {"id": 4, "age": 28, "purchases": 445, "category": "electronics"},
                {"id": 5, "age": 52, "purchases": 67, "category": "home"},
            ],
            "anomalies_detected": [
                {
                    "customer_id": 2,
                    "anomaly_type": "spending_spike",
                    "confidence": 0.85,
                },
                {
                    "customer_id": 4,
                    "anomaly_type": "unusual_pattern",
                    "confidence": 0.72,
                },
            ],
            "predictions": {
                "next_week_sales": 15600,
                "churn_risk_customers": [1, 5],
                "trending_categories": ["electronics", "clothing"],
            },
        }

        with open(self.demo_data_dir / "ml_analytics_data.json", "w") as f:
            json.dump(sample_data, f, indent=2)

        logger.info("✅ Demo data created successfully!")

    def demonstrate_scenario(self, scenario_key):
        """Demonstrate a specific automation scenario"""
        scenario = self.scenarios[scenario_key]
        logger.info(f"\n🎯 DEMONSTRATING: {scenario['name']}")
        logger.info("=" * 60)

        # Load scenario configuration
        flow_file = self.flows_dir / scenario["file"]
        with open(flow_file, "r") as f:
            flow_config = json.load(f)

        logger.info(f"📋 Scenario: {flow_config['description']}")
        logger.info(f"🔧 Demo Type: {scenario['demo_type']}")

        if scenario_key == "ai_code_scanner":
            self._demo_code_scanner()
        elif scenario_key == "smart_autoscaler":
            self._demo_autoscaler()
        elif scenario_key == "security_guardian":
            self._demo_security_guardian()
        elif scenario_key == "smart_data_pipeline":
            self._demo_data_pipeline()

    def _demo_code_scanner(self):
        """Demonstrate AI Code Scanner scenario"""
        logger.info("\n🔍 AI Code Scanner Demo:")
        logger.info("1. Monitoring code changes...")
        logger.info("2. Detecting vulnerabilities in vulnerable_code.py:")

        vulnerabilities = [
            "❌ CRITICAL: Command injection vulnerability (line 8)",
            "❌ HIGH: Unsafe pickle deserialization (line 13)",
            "❌ MEDIUM: Hardcoded API credentials (line 18)",
            "⚠️ PERFORMANCE: Inefficient O(n²) algorithm (line 24)",
        ]

        for vuln in vulnerabilities:
            logger.info(f"   {vuln}")
            time.sleep(1)

        logger.info("\n🤖 AI Analysis Results:")
        logger.info("   ✅ Auto-generated security fixes available")
        logger.info("   ✅ Performance optimization suggestions ready")
        logger.info("   ✅ Code quality score: 3.2/10 (Critical issues found)")

    def _demo_autoscaler(self):
        """Demonstrate Smart Autoscaler scenario"""
        logger.info("\n📈 Smart Autoscaler Demo:")
        logger.info("1. Monitoring performance metrics...")
        logger.info("2. Current system status:")
        logger.info("   CPU: 89% | Memory: 91% | Response: 650ms")
        logger.info("3. 🧠 AI Prediction: Traffic spike detected!")
        logger.info("4. 🚀 Auto-scaling action: 4 -> 6 instances")
        logger.info("5. ⚖️ Load balancing: Redistributing traffic")
        logger.info("6. 💰 Cost optimization: $50/hour -> $75/hour (justified)")
        logger.info("   ✅ Performance improved: Response time 650ms -> 200ms")

    def _demo_security_guardian(self):
        """Demonstrate Security Guardian scenario"""
        logger.info("\n🛡️ Security Guardian Demo:")
        logger.info("1. Monitoring security events...")
        logger.info("2. 🚨 THREAT DETECTED:")
        logger.info("   Type: SQL Injection Attempt")
        logger.info("   Source: 10.0.0.50")
        logger.info("   Severity: HIGH")
        logger.info("3. 🤖 AI Analysis: Known attack pattern identified")
        logger.info("4. 🚫 Automated Response:")
        logger.info("   ✅ IP blocked immediately")
        logger.info("   ✅ Container isolated")
        logger.info("   ✅ Incident logged")
        logger.info("   ✅ Security team notified")
        logger.info("5. 🔄 Recovery: System hardened against similar attacks")

    def _demo_data_pipeline(self):
        """Demonstrate Smart Data Pipeline scenario"""
        logger.info("\n📊 Smart Data Pipeline Demo:")
        logger.info("1. Processing incoming customer data...")
        logger.info("2. 🧠 ML Analysis in progress:")
        logger.info("   ✅ Data cleaned and validated")
        logger.info("   ✅ Features extracted")
        logger.info("   ⚠️ Anomalies detected: 2 customers")
        logger.info("3. 🔮 Predictions generated:")
        logger.info("   Next week sales: $15,600")
        logger.info("   Churn risk: 2 customers identified")
        logger.info("   Trending: Electronics, Clothing")
        logger.info("4. 📈 Business insights ready for dashboard")

    def run_full_demo(self):
        """Run complete demonstration of all scenarios"""
        logger.info("🎉 NOXSUITE CUSTOM AUTOMATION SCENARIOS DEMO")
        logger.info("=" * 50)

        # Create demo data
        self.create_demo_data()

        # Demonstrate each scenario
        for scenario_key in self.scenarios.keys():
            self.demonstrate_scenario(scenario_key)
            time.sleep(2)

        logger.info("\n🎯 DEMO SUMMARY:")
        logger.info("✅ 4 Advanced automation scenarios demonstrated")
        logger.info("✅ AI-powered analysis and decision making")
        logger.info("✅ Real-time monitoring and response")
        logger.info("✅ Intelligent resource optimization")
        logger.info("✅ Proactive security threat management")
        logger.info("✅ ML-driven insights and predictions")

        logger.info(f"\n📁 Demo data available in: {self.demo_data_dir}")
        logger.info(f"🔧 Workflow configs in: {self.flows_dir}")
        logger.info(
            "\n🚀 Ready to import into Langflow at http://localhost:7860")


def create_workflow_import_guide():
    """Create a guide for importing workflows into Langflow"""
    guide = """
# 🚀 NoxSuite Custom Automation Scenarios - Import Guide

## Available Scenarios:

### 1. AI-Powered Code Quality & Security Scanner
- **File**: `ai_code_scanner.json`
- **Purpose**: Automatically scans code for vulnerabilities and quality issues
- **Features**: Security analysis, performance optimization, AI-powered fixes

### 2. Intelligent Load Balancer with Auto-Scaling  
- **File**: `smart_autoscaler.json`
- **Purpose**: Predictive scaling based on AI load analysis
- **Features**: Cost optimization, performance prediction, intelligent scaling

### 3. Proactive Security Threat Detection & Response
- **File**: `security_guardian.json` 
- **Purpose**: AI-powered security monitoring and automated response
- **Features**: Threat analysis, automated blocking, incident response

### 4. Intelligent Data Pipeline with ML Analytics
- **File**: `smart_data_pipeline.json`
- **Purpose**: Automated data processing with machine learning insights
- **Features**: Anomaly detection, predictive analytics, business intelligence

## How to Import:

1. Open Langflow UI: http://localhost:7860
2. Login with: noxsuite_admin / noxsuite_secure_2024
3. Click "Import Flow" 
4. Select one of the JSON files from `langflow/flows/`
5. Configure components with your specific settings
6. Run the workflow and observe the automation!

## Demo Data:
- Code samples in `demo_data/vulnerable_code.py`
- Performance metrics in `demo_data/performance_metrics.json`
- Security logs in `demo_data/security_logs.json`
- ML data in `demo_data/ml_analytics_data.json`

## Next Steps:
- Customize workflows for your specific use cases
- Add your own data sources and endpoints
- Extend with additional NoxSuite components
- Create hybrid workflows combining multiple scenarios
"""

    with open("AUTOMATION_SCENARIOS_GUIDE.md", "w") as f:
        f.write(guide)

    logger.info("📚 Import guide created: AUTOMATION_SCENARIOS_GUIDE.md")


if __name__ == "__main__":
    # Run the complete demonstration
    demo = NoxSuiteScenarioDemo()
    demo.run_full_demo()

    # Create import guide
    create_workflow_import_guide()

    logger.info("\n🎉 Custom Automation Scenarios Demo Complete!")
    logger.info("Ready to showcase advanced AI-powered workflow automation!")
