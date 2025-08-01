# Enhanced Monitoring System - Quick Start Guide
# Installation and usage instructions
# Date: 2025-07-29 06:49:09 UTC

# Install required dependencies
pip install click psutil requests matplotlib tkinter

# Basic Usage Examples:

# 1. Start Enhanced Monitoring (CLI)
python enhanced_monitoring_cli.py monitor - -patterns = "security,performance,build,api" - -context = 10 - -realtime - -alert-threshold = critical

# 2. Run Intervention Protocol
python enhanced_monitoring_cli.py intervene - -protocol = INT001 - -auto-recovery - -escalation-path = default - -timeout = 300

# 3. Collect System Metrics
python enhanced_monitoring_cli.py metrics - -categories = "system,api,performance" - -interval = 30s - -aggregation = "avg,p95,p99" - -retention = 24h

# 4. Generate Enhanced Report
python enhanced_monitoring_cli.py report - -format = enhanced - -period = 30m - -include = all - -output = monitoring_report.md

# 5. Launch Interactive Dashboard
python enhanced_monitoring_cli.py dashboard

# 6. Validate System Configuration
python enhanced_monitoring_cli.py validate - -check = all

# 7. Direct System Monitoring (Python)
python enhanced_monitoring_system.py

# 8. Interactive Dashboard (Direct)
python enhanced_monitoring_dashboard.py

# PowerShell Quick Commands:
# Start monitoring with logging
#   python enhanced_monitoring_cli.py monitor --duration=3600 > monitoring_session.log 2>&1

# Generate report and save
#   python enhanced_monitoring_cli.py report --format=markdown --output=daily_report.md

# Validation with error checking
#   python enhanced_monitoring_cli.py validate; if ($LASTEXITCODE -ne 0) { Write-Host "Validation Failed" }

# Background monitoring (Windows)
#   Start-Process python -ArgumentList "enhanced_monitoring_system.py" -WindowStyle Hidden

print("🚀 Enhanced Monitoring System - Installation Complete!")
print("📋 Use the commands above to start monitoring your NoxSuite system")
print("🖥️ For interactive monitoring, run: python enhanced_monitoring_dashboard.py")
print("⚡ For CLI operations, run: python enhanced_monitoring_cli.py --help")
