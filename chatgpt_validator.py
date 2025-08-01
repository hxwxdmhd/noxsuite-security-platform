from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)

#!/usr/bin/env python3
"""
ChatGPT Cross-Validation Module for NoxSuite MCP Agent
Provides external validation of system audits
"""
import json
import os
import time
from datetime import datetime

import requests

from emergency_copilot_fix import throttler


class ChatGPTValidator:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def validate_system_audit(self, audit_data: dict) -> dict:
        """Cross-validate system audit with ChatGPT"""

        def chatgpt_validation():
            try:
                # Prepare concise summary for ChatGPT
                summary = {
                    "system": "NoxSuite MCP Autonomous Agent",
                    "timestamp": audit_data.get("agent", {}).get("timestamp"),
                    "tool_usage": audit_data.get("agent", {}).get("tool_usage"),
                    "overall_status": audit_data.get("overall_status"),
                    "docker_containers": len(
                        audit_data.get("audit_results", {})
                        .get("docker", {})
                        .get("status", {})
                    ),
                    "langflow_health": audit_data.get("audit_results", {})
                    .get("langflow", {})
                    .get("status"),
                    "mcp_integration": audit_data.get("audit_results", {})
                    .get("mcp", {})
                    .get("status"),
                    "critical_issues": audit_data.get("critical_issues", []),
                }

                prompt = f"""
                Analyze this autonomous agent system audit for a NoxSuite MCP deployment:
                
                {json.dumps(summary, indent=2)}
                
                Please provide:
                1. Risk assessment (Low/Medium/High)
                2. Any red flags or concerns
                3. Recommendations for improvement
                4. Validation of "operational" status
                
                Keep response concise (under 200 words).
                """

                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a system reliability expert analyzing autonomous agent deployments.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 300,
                        "temperature": 0.3,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "validation_timestamp": datetime.now().isoformat(),
                        "chatgpt_analysis": result["choices"][0]["message"]["content"],
                        "external_validation": "completed",
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"API Error: {response.status_code} - {response.text}",
                        "external_validation": "failed",
                    }

            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "external_validation": "failed",
                }

        return throttler.execute_with_throttle(chatgpt_validation)


def validate_latest_audit():
    """Find and validate the latest audit report"""
    import glob
    import os

    # Find latest audit file
    audit_files = glob.glob("autonomous_audit_*.json")
    if not audit_files:
        logger.info("❌ No audit files found")
        return None

    latest_file = max(audit_files, key=os.path.getctime)
    logger.info(f"📋 Validating: {latest_file}")

    # Load audit data
    with open(latest_file, "r") as f:
        audit_data = json.load(f)

    # Perform ChatGPT validation
    validator = ChatGPTValidator()
    validation_result = validator.validate_system_audit(audit_data)

    # Add validation to audit data
    audit_data["chatgpt_validation"] = validation_result

    # Save updated audit with validation
    validated_file = latest_file.replace("autonomous_audit_", "validated_audit_")
    with open(validated_file, "w") as f:
        json.dump(audit_data, f, indent=2)

    logger.info(f"✅ Validation complete: {validated_file}")

    # Display results
    if validation_result.get("status") == "success":
        logger.info("\n🤖 ChatGPT Analysis:")
        logger.info(validation_result["chatgpt_analysis"])
        logger.info(f"\n🔧 Tool usage: {throttler.tool_count}/120")
    else:
        logger.info(f"❌ Validation failed: {validation_result.get('error')}")

    return validation_result


if __name__ == "__main__":
    logger.info("🧠 ChatGPT Cross-Validation - Starting")
    result = validate_latest_audit()

    if result and result.get("status") == "success":
        logger.info("\n🎯 EXTERNAL VALIDATION COMPLETE")
    else:
        logger.info("\n⚠️ External validation issues detected")
