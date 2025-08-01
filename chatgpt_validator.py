
    import os
from NoxPanel.noxcore.utils.logging_config import get_logger
from datetime import datetime
import json
import os
import requests

    import glob
from emergency_copilot_fix import throttler
import time


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
    validated_file = latest_file.replace(
        "autonomous_audit_", "validated_audit_")
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
