import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from NoxPanel.noxcore.utils.logging_config import get_logger

logger = get_logger(__name__)


EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", "venv", "env", "build", "dist"}
TARGET_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".html",
    ".css",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
}
LEGACY_PATTERNS = re.compile(
    r"(copy|backup|old|deprecated|archive|\d{8,}|\d{6,})", re.IGNORECASE
)
CONFIG_EXTS = {".yml", ".yaml", ".toml", ".json"}

REPORT_CATEGORIES = [
    "safe_to_delete",
    "keep_referenced",
    "migration_candidate",
    "unused_config",
    "duplicate",
]

ARCHIVE_DIR = "./archive/deprecated/"


# --- Utility Functions ---
def sha256sum(filepath):
    """
    REASONING CHAIN:
    1. Problem: Function sha256sum needs clear operational definition
    2. Analysis: Implementation requires specific logic for sha256sum operation
    3. Solution: Implement sha256sum with enterprise-grade patterns and error handling
    4. Validation: Test sha256sum with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_last_modified(filepath):
    """
    REASONING CHAIN:
    1. Problem: Data retrieval operation needs reliable access pattern
    2. Analysis: Getter method requires consistent data access and error handling
    3. Solution: Implement get_last_modified with enterprise-grade patterns and error handling
    4. Validation: Test get_last_modified with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Get last modified date as ISO string."""
    return datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()


def is_legacy_name(filename):
    """
    REASONING CHAIN:
    1. Problem: Function is_legacy_name needs clear operational definition
    2. Analysis: Implementation requires specific logic for is_legacy_name operation
    3. Solution: Implement is_legacy_name with enterprise-grade patterns and error handling
    4. Validation: Test is_legacy_name with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Detect legacy naming patterns."""
    return bool(LEGACY_PATTERNS.search(filename))


def parse_imports(filepath):
    """
    REASONING CHAIN:
    1. Problem: Data parsing needs robust transformation logic
    2. Analysis: Parser function requires error-tolerant data processing
    3. Solution: Implement parse_imports with enterprise-grade patterns and error handling
    4. Validation: Test parse_imports with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Parse import/require/include statements from file."""
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Python
                m = re.match(r"\s*import\s+([\w\.]+)", line)
                if m:
                    imports.add(m.group(1))
                m = re.match(r"\s*from\s+([\w\.]+)", line)
                if m:
                    imports.add(m.group(1))
                # JS/TS
                m = re.match(r'\s*require\(["\"]([\w\-/\.]+)["\"]\)', line)
                if m:
                    imports.add(m.group(1))
                m = re.match(r'\s*import\s+.*from\s+["\"]([\w\-/\.]+)["\"]', line)
                if m:
                    imports.add(m.group(1))
                # HTML/CSS
                m = re.match(r'\s*<link.*href=["\"]([\w\-/\.]+)["\"]', line)
                if m:
                    imports.add(m.group(1))
                # YAML/TOML
                m = re.match(r'\s*include:\s+["\"]([\w\-/\.]+)["\"]', line)
                if m:
                    imports.add(m.group(1))
    except Exception:
        pass
    return imports


def scan_files(root):
    """
    REASONING CHAIN:
    1. Problem: Function scan_files needs clear operational definition
    2. Analysis: Implementation requires specific logic for scan_files operation
    3. Solution: Implement scan_files with enterprise-grade patterns and error handling
    4. Validation: Test scan_files with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Recursively scan files, excluding EXCLUDE_DIRS."""
    file_list = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Exclude dirs in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in TARGET_EXTS:
                file_list.append(os.path.join(dirpath, fname))
    return file_list


def analyze_file(filepath, all_imports, hash_map):
    """
    REASONING CHAIN:
    1. Problem: Function analyze_file needs clear operational definition
    2. Analysis: Implementation requires specific logic for analyze_file operation
    3. Solution: Implement analyze_file with enterprise-grade patterns and error handling
    4. Validation: Test analyze_file with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Analyze file for legacy, config, duplicate, and reference status."""
    ext = os.path.splitext(filepath)[1].lower()
    filename = os.path.basename(filepath)
    file_hash = sha256sum(filepath)
    last_mod = get_last_modified(filepath)
    imports = parse_imports(filepath)
    reason = []
    category = None
    # Duplicate detection
    if file_hash in hash_map:
        category = "duplicate"
        reason.append("SHA256 matches another file")
    # Legacy detection
    elif is_legacy_name(filename):
        category = "migration_candidate"
        reason.append("Legacy naming pattern")
    # Unused config
    elif ext in CONFIG_EXTS and filename not in all_imports:
        category = "unused_config"
        reason.append("Config file not referenced")
    # Referenced
    elif filename in all_imports:
        category = "keep_referenced"
        reason.append("Referenced in imports/includes")
    # Safe to delete
    else:
        category = "safe_to_delete"
        reason.append("No references, not legacy, not config")
    return {
        "path": filepath,
        "last_modified": last_mod,
        "hash": file_hash,
        "reason": reason,
        "category": category,
    }


def call_ai_suggester(report):
    """
    REASONING CHAIN:
    1. Problem: Function call_ai_suggester needs clear operational definition
    2. Analysis: Implementation requires specific logic for call_ai_suggester operation
    3. Solution: Implement call_ai_suggester with enterprise-grade patterns and error handling
    4. Validation: Test call_ai_suggester with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Call Supermaven/Langflow/Ollama API to refine suggestions. Abstracted for future extension."""
    # Placeholder: try external API, fallback to local LLM
    # Example: requests.post('http://localhost:11434/api', json=report)
    # For now, just return report unchanged
    return report


def generate_reports(results, metrics):
    """
    REASONING CHAIN:
    1. Problem: Function generate_reports needs clear operational definition
    2. Analysis: Implementation requires specific logic for generate_reports operation
    3. Solution: Implement generate_reports with enterprise-grade patterns and error handling
    4. Validation: Test generate_reports with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Write cleanup_report.json and cleanup_report.md with categorized entries and metrics."""
    # JSON
    with open("cleanup_report.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2)
    # Markdown
    with open("cleanup_report.md", "w", encoding="utf-8") as f:
        f.write(f"# Cleanup Report\n\n")
        for cat in REPORT_CATEGORIES:
            f.write(f"## {cat.replace('_', ' ').title()}\n")
            for entry in results.get(cat, []):
                f.write(
                    f"- `{entry['path']}`\n  - Last Modified: {entry['last_modified']}\n  - Hash: {entry['hash']}\n  - Reason: {', '.join(entry['reason'])}\n"
                )
            f.write("\n")
        f.write("## Performance Metrics\n")
        for k, v in metrics.items():
            f.write(f"- {k}: {v}\n")


def perform_cleanup(results, execute=False):
    """
    REASONING CHAIN:
    1. Problem: Function perform_cleanup needs clear operational definition
    2. Analysis: Implementation requires specific logic for perform_cleanup operation
    3. Solution: Implement perform_cleanup with enterprise-grade patterns and error handling
    4. Validation: Test perform_cleanup with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    """Delete or archive files in safe_to_delete and migration_candidate categories."""
    candidates = results.get("safe_to_delete", []) + results.get(
        "migration_candidate", []
    )
    if not candidates:
        logger.info("No files to delete or archive.")
        return
    logger.info(f"Candidates for deletion/archive: {len(candidates)}")
    for entry in candidates:
        logger.info(f"- {entry['path']} ({', '.join(entry['reason'])})")
    if not execute:
        logger.info("Dry-run mode: No files will be deleted or moved.")
        return
    confirm = input("Proceed with deletion/archive? (y/N): ").strip().lower()
    if confirm != "y":
        logger.info("Aborted by user.")
        return
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    for entry in tqdm(candidates, desc="Cleanup Actions"):
        try:
            rel_path = os.path.relpath(entry["path"], start=os.getcwd())
            archive_path = os.path.join(ARCHIVE_DIR, rel_path)
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            shutil.move(entry["path"], archive_path)
        except Exception as e:
            logger.info(f"Failed to archive {entry['path']}: {e}")


# --- Main CLI ---
def main():
    """
    Enhanced main with AI-driven reasoning patterns

    REASONING CHAIN:
    1. Problem: Function main needs clear operational definition
    2. Analysis: Implementation requires specific logic for main operation
    3. Solution: Implement main with enterprise-grade patterns and error handling
    4. Validation: Test main with edge cases and performance requirements

    ENHANCED: 2025-07-29 - AI-generated reasoning
    """
    parser = argparse.ArgumentParser(description="Advanced NoxPanel Suite Cleanup Tool")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete/archive files (default: dry-run)",
    )
    parser.add_argument("--root", type=str, default=".", help="Project root directory")
    args = parser.parse_args()
    start_time = utc_now().timestamp()
    logger.info("\n=== NoxPanel Suite Cleanup ===\n")
    logger.info(f"Scanning: {args.root}")
    files = scan_files(args.root)
    logger.info(f"Total files found: {len(files)}")
    # Build global import/include set
    all_imports = set()
    for fpath in tqdm(files, desc="Parsing imports/includes"):
        all_imports.update(parse_imports(fpath))
    # Hash map for duplicate detection
    hash_map = {}
    results = defaultdict(list)
    logger.info("Analyzing files...")
    for fpath in tqdm(files, desc="Analyzing files"):
        entry = analyze_file(fpath, all_imports, hash_map)
        hash_map.setdefault(entry["hash"], fpath)
        results[entry["category"]].append(entry)
    # AI-assisted refinement
    results = call_ai_suggester(results)
    end_time = utc_now().timestamp()
    metrics = {
        "scan_time_sec": round(end_time - start_time, 2),
        "total_files_scanned": len(files),
        "candidates_found": sum(
            len(results[cat]) for cat in ["safe_to_delete", "migration_candidate"]
        ),
        "actions_taken": 0,
    }
    generate_reports(results, metrics)
    perform_cleanup(results, execute=args.execute)
    logger.info(
        "\nCleanup complete. See cleanup_report.json and cleanup_report.md for details."
    )


if __name__ == "__main__":
    main()
