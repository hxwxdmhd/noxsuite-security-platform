
from NoxPanel.noxcore.utils.logging_config import get_logger
from pathlib import Path
import datetime
import json

    import argparse
from typing import Any, Dict, List


    parser = argparse.ArgumentParser(description="PRD Auto-Generator")
    parser.add_argument(
        "--from-test-results",
        action="store_true",
        help="Generate PRD from test results",
    )

    args = parser.parse_args()

    generator = PRDAutoGenerator()

    if args.from_test_results:
        logger.info("📋 Generating PRD from test results...")

        # Load test results
        test_results = generator.load_test_results()

        # Generate PRD
        prd_content = generator.generate_prd_document(test_results)

        # Save PRD
        prd_file = generator.save_prd_document(prd_content)

        logger.info(f"✅ PRD generation complete: {prd_file}")

    return generator


if __name__ == "__main__":
    main()
