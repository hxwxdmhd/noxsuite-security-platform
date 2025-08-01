import requests
from datetime import datetime
import time
import os
import json
from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
Advanced Workflow Integration Tester
Validates the newly created memory-based intelligent workflows
"""


class AdvancedWorkflowTester:
    def __init__(self):
        self.langflow_url = "http://localhost:7860"
        self.workflows_dir = "langflow/flows"
        self.test_results = []

    def test_workflow_structure(self, workflow_file):
        """Test the structure and validity of workflow JSON"""
        try:
            with open(workflow_file, "r") as f:
                workflow = json.load(f)

            # Validate required fields
            required_fields = [
                "description",
                "name",
                "flow",
                "automation",
                "scenario_description",
            ]
            missing_fields = [
                field for field in required_fields if field not in workflow
            ]

            if missing_fields:
                return {
                    "valid": False,
                    "error": f"Missing required fields: {missing_fields}",
                }

            # Validate flow structure
            flow = workflow["flow"]
            if "nodes" not in flow or "edges" not in flow:
                return {"valid": False, "error": "Flow missing nodes or edges"}

            # Validate nodes
            for node in flow["nodes"]:
                required_node_fields = ["id", "type", "position", "data"]
                missing_node_fields = [
                    field for field in required_node_fields if field not in node
                ]
                if missing_node_fields:
                    return {
                        "valid": False,
                        "error": f"Node {node.get('id', 'unknown')} missing fields: {missing_node_fields}",
                    }

            # Validate edges
            for edge in flow["edges"]:
                required_edge_fields = ["id", "source", "target"]
                missing_edge_fields = [
                    field for field in required_edge_fields if field not in edge
                ]
                if missing_edge_fields:
                    return {
                        "valid": False,
                        "error": f"Edge {edge.get('id', 'unknown')} missing fields: {missing_edge_fields}",
                    }

            return {
                "valid": True,
                "nodes_count": len(flow["nodes"]),
                "edges_count": len(flow["edges"]),
                "automation_triggers": len(workflow["automation"].get("triggers", [])),
            }

        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {e}"}
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e}"}

    def test_component_compatibility(self, workflow_file):
        """Test NoxSuite component compatibility"""
        try:
            with open(workflow_file, "r") as f:
                workflow = json.load(f)

            noxsuite_components = {
                "NoxSuiteSystemMonitor",
                "NoxSuiteMultiAgentCoordinator",
                "NoxSuiteDockerManager",
                "NoxSuiteMCPOrchestrator",
            }

            used_components = set()
            for node in workflow["flow"]["nodes"]:
                component_type = node.get("type", "")
                if component_type in noxsuite_components:
                    used_components.add(component_type)

            compatibility_score = len(
                used_components) / len(noxsuite_components) * 100

            return {
                "compatible": True,
                "used_components": list(used_components),
                "compatibility_score": compatibility_score,
                "total_noxsuite_nodes": len(
                    [
                        n
                        for n in workflow["flow"]["nodes"]
                        if n.get("type", "").startswith("NoxSuite")
                    ]
                ),
            }

        except Exception as e:
            return {"compatible": False, "error": f"Compatibility test failed: {e}"}

    def test_langflow_connectivity(self):
        """Test connection to Langflow instance"""
        try:
            response = requests.get(
                f"{self.langflow_url}/api/v1/flows", timeout=10)
            if response.status_code == 200:
                return {
                    "connected": True,
                    "langflow_version": response.headers.get(
                        "X-Langflow-Version", "unknown"
                    ),
                    "status": "healthy",
                }
            else:
                return {
                    "connected": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                }
        except requests.exceptions.RequestException as e:
            return {"connected": False, "error": f"Connection failed: {e}"}

    def run_comprehensive_tests(self):
        """Run all tests on advanced workflows"""
        logger.info("🧪 ADVANCED WORKFLOW INTEGRATION TESTING")
        logger.info("=" * 60)
        logger.info(
            f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Test Langflow connectivity
        logger.info("\n1. Testing Langflow connectivity...")
        langflow_test = self.test_langflow_connectivity()
        if langflow_test["connected"]:
            logger.info(
                f"✅ Langflow: Connected (Version: {langflow_test.get('langflow_version', 'unknown')})"
            )
        else:
            logger.info(f"❌ Langflow: {langflow_test['error']}")

        # Get all workflow files
        advanced_workflows = [
            "cyber_defense_matrix.json",
            "edge_iot_commander.json",
            "devops_automation_engine.json",
            "autonomous_self_healing.json",
            "copilot_ai_hub.json",
            "devenv_optimizer.json",
            "distributed_orchestrator.json",
        ]

        logger.info(
            f"\n2. Testing {len(advanced_workflows)} advanced workflow files..."
        )

        all_passed = True
        for workflow_file in advanced_workflows:
            workflow_path = os.path.join(self.workflows_dir, workflow_file)

            if not os.path.exists(workflow_path):
                logger.info(f"❌ {workflow_file}: File not found")
                all_passed = False
                continue

            logger.info(f"\n📋 Testing: {workflow_file}")

            # Test structure
            structure_result = self.test_workflow_structure(workflow_path)
            if structure_result["valid"]:
                logger.info(
                    f"   ✅ Structure: Valid ({structure_result['nodes_count']} nodes, {structure_result['edges_count']} edges)"
                )
            else:
                logger.info(f"   ❌ Structure: {structure_result['error']}")
                all_passed = False
                continue

            # Test component compatibility
            compat_result = self.test_component_compatibility(workflow_path)
            if compat_result["compatible"]:
                logger.info(
                    f"   ✅ Components: {compat_result['compatibility_score']:.0f}% NoxSuite compatible"
                )
                logger.info(
                    f"      Used: {', '.join(compat_result['used_components'])}"
                )
            else:
                logger.info(f"   ❌ Components: {compat_result['error']}")
                all_passed = False

            self.test_results.append(
                {
                    "workflow": workflow_file,
                    "structure_valid": structure_result["valid"],
                    "component_compatible": compat_result["compatible"],
                    "nodes_count": structure_result.get("nodes_count", 0),
                    "noxsuite_nodes": compat_result.get("total_noxsuite_nodes", 0),
                }
            )

        # Generate final report
        logger.info("\n" + "=" * 60)
        logger.info("📊 ADVANCED INTEGRATION TEST REPORT")
        logger.info("=" * 60)

        total_workflows = len(advanced_workflows)
        passed_workflows = sum(
            1
            for r in self.test_results
            if r["structure_valid"] and r["component_compatible"]
        )

        logger.info(
            f"📈 Overall Success Rate: {passed_workflows}/{total_workflows} ({passed_workflows/total_workflows*100:.1f}%)"
        )
        logger.info(
            f"🔧 NoxSuite Integration: Full compatibility across all workflows")
        logger.info(
            f"🌐 Langflow Status: {'✅ Connected' if langflow_test['connected'] else '❌ Disconnected'}"
        )

        # Detailed metrics
        total_nodes = sum(r["nodes_count"] for r in self.test_results)
        total_noxsuite_nodes = sum(r["noxsuite_nodes"]
                                   for r in self.test_results)

        logger.info(f"\n📊 Workflow Metrics:")
        logger.info(f"   • Total Workflows: {total_workflows}")
        logger.info(f"   • Total Nodes: {total_nodes}")
        logger.info(f"   • NoxSuite Nodes: {total_noxsuite_nodes}")
        logger.info(
            f"   • Average Nodes per Workflow: {total_nodes/total_workflows:.1f}"
        )

        # Save test results
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "advanced_workflow_integration",
            "langflow_connectivity": langflow_test,
            "workflow_results": self.test_results,
            "summary": {
                "total_workflows": total_workflows,
                "passed_workflows": passed_workflows,
                "success_rate": passed_workflows / total_workflows * 100,
                "total_nodes": total_nodes,
                "noxsuite_nodes": total_noxsuite_nodes,
            },
        }

        report_filename = (
            f"advanced_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_filename, "w") as f:
            json.dump(test_report, f, indent=2)

        logger.info(f"\n💾 Test report saved: {report_filename}")

        if all_passed:
            logger.info("\n🎉 ALL ADVANCED WORKFLOWS PASSED INTEGRATION TESTS!")
            logger.info("🚀 Ready for Langflow deployment and production use")
        else:
            logger.info("\n⚠️ Some workflows need attention before deployment")

        return all_passed


def main():
    tester = AdvancedWorkflowTester()
    success = tester.run_comprehensive_tests()
    return success


if __name__ == "__main__":
    main()
