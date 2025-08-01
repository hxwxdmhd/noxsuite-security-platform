#!/usr/bin/env python3
"""
NoxSuite Sprint Dashboard
========================

Real-time dashboard for tracking sprint progress and next development phase.
Generated from comprehensive audit results.

Author: NoxSuite Development Team
Date: July 31, 2025
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SprintDashboard:
    """Sprint progress dashboard for NoxSuite"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.dashboard_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def load_audit_results(self) -> Dict:
        """Load latest audit results"""
        # Find latest audit report
        audit_files = list(self.workspace_root.glob('noxsuite_audit_report_*.json'))
        
        if not audit_files:
            print("No audit reports found. Run noxsuite_audit_simplified.py first.")
            return {}
        
        latest_audit = max(audit_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_audit, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading audit results: {e}")
            return {}
    
    def generate_dashboard(self):
        """Generate comprehensive sprint dashboard"""
        audit_results = self.load_audit_results()
        
        if not audit_results:
            return
        
        print("=" * 60)
        print("🚀 NOXSUITE COMPREHENSIVE AUDIT & SPRINT DASHBOARD")
        print("=" * 60)
        
        # Current Status
        self.display_current_status(audit_results)
        
        # Workspace Health
        self.display_workspace_health(audit_results)
        
        # Sprint Planning
        self.display_sprint_plan(audit_results)
        
        # Action Items
        self.display_action_items(audit_results)
        
        # Resources & Timeline
        self.display_resources_timeline()
        
        # Generate HTML dashboard
        self.generate_html_dashboard(audit_results)
    
    def display_current_status(self, audit_results: Dict):
        """Display current project status"""
        print("\n📊 CURRENT PROJECT STATUS")
        print("-" * 40)
        
        sprint_plan = audit_results.get('next_sprint_plan', {})
        progress = sprint_plan.get('current_progress', {})
        
        print(f"Overall Progress: {progress.get('overall_completion', 'N/A')}%")
        print(f"Authentication:   {progress.get('authentication', 'N/A')}% ✅")
        print(f"API Endpoints:    {progress.get('api', 'N/A')}% ✅")
        print(f"Frontend:         {progress.get('frontend', 'N/A')}% ✅")
        print(f"Database:         {progress.get('database', 25)}% ⚠️")
        print(f"Production:       {progress.get('production', 45)}% ⚠️")
        
        # Template Implementation Status
        software_health = audit_results.get('software_health', {})
        template_impl = software_health.get('template_implementation', {})
        
        print("\n🔧 TEMPLATE IMPLEMENTATION STATUS")
        for component, details in template_impl.items():
            score = details.get('score', 0)
            status = details.get('status', 'unknown')
            icon = "✅" if score == 100 else "⚠️" if score > 0 else "❌"
            print(f"{component.title()}: {score}% ({status}) {icon}")
    
    def display_workspace_health(self, audit_results: Dict):
        """Display workspace health metrics"""
        print("\n📁 WORKSPACE HEALTH AUDIT")
        print("-" * 40)
        
        workspace_audit = audit_results.get('workspace_audit', {})
        
        print(f"NoxSuite Files Found: {workspace_audit.get('noxsuite_files_found', 0)}")
        print(f"Misplaced Files:      {len(workspace_audit.get('misplaced_files', []))} ⚠️")
        print(f"Missing Files:        {len(workspace_audit.get('missing_files', []))} ❌")
        print(f"Conflict Files:       {len(workspace_audit.get('conflict_files', []))} 🔥")
        
        if workspace_audit.get('misplaced_files'):
            print("\n📍 Key Misplaced Files:")
            for misplaced in workspace_audit['misplaced_files'][:5]:
                print(f"  • {misplaced['file']} -> {misplaced['expected']}")
        
        if workspace_audit.get('missing_files'):
            print("\n❌ Missing Critical Files:")
            for missing in workspace_audit['missing_files']:
                print(f"  • {missing}")
    
    def display_sprint_plan(self, audit_results: Dict):
        """Display next sprint planning"""
        print("\n🚀 NEXT SPRINT PLAN (2 WEEKS)")
        print("-" * 40)
        
        sprint_plan = audit_results.get('next_sprint_plan', {})
        priority_items = sprint_plan.get('priority_items', [])
        
        print(f"Sprint Duration: {sprint_plan.get('sprint_duration', '2 weeks')}")
        print(f"Target Completion: {sprint_plan.get('estimated_completion', 95)}%")
        print(f"Priority Items: {len(priority_items)}")
        
        print("\n🎯 SPRINT PRIORITIES:")
        for i, item in enumerate(priority_items, 1):
            priority_icon = "🔴" if item['priority'] == 'HIGH' else "🟡" if item['priority'] == 'MEDIUM' else "🟢"
            print(f"{i}. {item['title']} {priority_icon}")
            print(f"   Effort: {item['effort']} | Priority: {item['priority']}")
            print(f"   Tasks: {len(item.get('tasks', []))} items")
            print()
    
    def display_action_items(self, audit_results: Dict):
        """Display immediate action items"""
        print("⚡ IMMEDIATE ACTION ITEMS")
        print("-" * 40)
        
        workspace_audit = audit_results.get('workspace_audit', {})
        database_validation = audit_results.get('database_validation', {})
        
        actions = []
        
        # Workspace cleanup
        if workspace_audit.get('conflict_files'):
            actions.append({
                'priority': 'HIGH',
                'action': f"Clean up {len(workspace_audit['conflict_files'])} conflict files",
                'command': 'find . -name "*.conflict.*" -delete'
            })
        
        # Database setup
        if not database_validation.get('mariadb_config', {}).get('configured'):
            actions.append({
                'priority': 'HIGH',
                'action': 'Set up MariaDB database',
                'command': 'python setup_database.py'
            })
        
        # Security audit
        actions.append({
            'priority': 'HIGH',
            'action': 'Run comprehensive security audit',
            'command': 'python security_audit.py'
        })
        
        # Migration
        if workspace_audit.get('misplaced_files'):
            actions.append({
                'priority': 'MEDIUM',
                'action': 'Migrate files to unified structure',
                'command': 'Review migration plan and execute'
            })
        
        for i, action in enumerate(actions, 1):
            priority_icon = "🔴" if action['priority'] == 'HIGH' else "🟡"
            print(f"{i}. {action['action']} {priority_icon}")
            print(f"   Command: {action['command']}")
            print()
    
    def display_resources_timeline(self):
        """Display resource requirements and timeline"""
        print("📅 RESOURCE REQUIREMENTS & TIMELINE")
        print("-" * 40)
        
        print("Team Requirements:")
        print("  • Backend Developer: 1 FTE")
        print("  • Frontend Developer: 0.5 FTE")
        print("  • DevOps Engineer: 0.5 FTE")
        print("  • QA Engineer: 0.5 FTE")
        print()
        
        print("Infrastructure:")
        print("  • MariaDB Server (new)")
        print("  • CI/CD Pipeline")
        print("  • Monitoring Stack")
        print()
        
        print("Timeline (2 weeks):")
        print("  Week 1: Database Integration + Security Audit")
        print("  Week 2: Production Deployment + Advanced Features")
        print()
        
        print("Budget Estimate: $5,000 - $8,000")
    
    def generate_html_dashboard(self, audit_results: Dict):
        """Generate HTML dashboard"""
        html_content = self.create_html_dashboard(audit_results)
        
        dashboard_file = self.workspace_root / f"noxsuite_dashboard_{self.dashboard_timestamp}.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n📊 HTML Dashboard: {dashboard_file}")
        print("   Open in browser for interactive view")
    
    def create_html_dashboard(self, audit_results: Dict) -> str:
        """Create HTML dashboard content"""
        workspace_audit = audit_results.get('workspace_audit', {})
        software_health = audit_results.get('software_health', {})
        sprint_plan = audit_results.get('next_sprint_plan', {})
        progress = sprint_plan.get('current_progress', {})
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NoxSuite Sprint Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border-radius: 10px;
            color: white;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #007bff;
        }}
        .card.success {{ border-left-color: #28a745; }}
        .card.warning {{ border-left-color: #ffc107; }}
        .card.danger {{ border-left-color: #dc3545; }}
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(45deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }}
        .priority-high {{ color: #dc3545; font-weight: bold; }}
        .priority-medium {{ color: #ffc107; font-weight: bold; }}
        .priority-low {{ color: #28a745; font-weight: bold; }}
        .action-item {{
            margin: 10px 0;
            padding: 15px;
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            border-radius: 5px;
        }}
        h2 {{ color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }}
        h3 {{ color: #6c757d; }}
        .timestamp {{
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 NoxSuite Sprint Dashboard</h1>
            <p>Comprehensive Audit Results & Next Development Sprint</p>
        </div>
        
        <div class="grid">
            <div class="card success">
                <h2>📊 Current Progress</h2>
                <div class="metric">
                    <span>Overall Completion</span>
                    <span><strong>{progress.get('overall_completion', 'N/A')}%</strong></span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress.get('overall_completion', 0)}%"></div>
                </div>
                
                <div class="metric">
                    <span>Authentication</span>
                    <span>{progress.get('authentication', 'N/A')}% ✅</span>
                </div>
                <div class="metric">
                    <span>API Endpoints</span>
                    <span>{progress.get('api', 'N/A')}% ✅</span>
                </div>
                <div class="metric">
                    <span>Frontend</span>
                    <span>{progress.get('frontend', 'N/A')}% ✅</span>
                </div>
                <div class="metric">
                    <span>Database</span>
                    <span>{progress.get('database', 25)}% ⚠️</span>
                </div>
                <div class="metric">
                    <span>Production</span>
                    <span>{progress.get('production', 45)}% ⚠️</span>
                </div>
            </div>
            
            <div class="card warning">
                <h2>📁 Workspace Health</h2>
                <div class="metric">
                    <span>NoxSuite Files</span>
                    <span>{workspace_audit.get('noxsuite_files_found', 0)}</span>
                </div>
                <div class="metric">
                    <span>Misplaced Files</span>
                    <span class="priority-medium">{len(workspace_audit.get('misplaced_files', []))}</span>
                </div>
                <div class="metric">
                    <span>Missing Files</span>
                    <span class="priority-high">{len(workspace_audit.get('missing_files', []))}</span>
                </div>
                <div class="metric">
                    <span>Conflict Files</span>
                    <span class="priority-high">{len(workspace_audit.get('conflict_files', []))}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Sprint Priorities</h2>'''
        
        priority_items = sprint_plan.get('priority_items', [])
        for i, item in enumerate(priority_items, 1):
            priority_class = f"priority-{item['priority'].lower()}"
            html += f'''
                <div class="metric">
                    <span>{i}. {item['title']}</span>
                    <span class="{priority_class}">{item['priority']}</span>
                </div>
                <small>Effort: {item['effort']} | Tasks: {len(item.get('tasks', []))}</small>
                <br><br>'''
        
        html += f'''
            </div>
        </div>
        
        <div class="card danger">
            <h2>⚡ Immediate Actions Required</h2>
            <div class="action-item">
                <strong>🔴 HIGH:</strong> Clean up {len(workspace_audit.get('conflict_files', []))} conflict files
                <br><code>find . -name "*.conflict.*" -delete</code>
            </div>
            <div class="action-item">
                <strong>🔴 HIGH:</strong> Set up MariaDB database
                <br><code>python setup_database.py</code>
            </div>
            <div class="action-item">
                <strong>🔴 HIGH:</strong> Run security audit
                <br><code>python security_audit.py</code>
            </div>
            <div class="action-item">
                <strong>🟡 MEDIUM:</strong> Migrate files to unified structure
                <br><code>Review migration plan and execute</code>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📅 Sprint Timeline</h2>
                <h3>Week 1: Foundation</h3>
                <ul>
                    <li>Database Integration (MariaDB + Alembic)</li>
                    <li>Security Audit & Hardening</li>
                    <li>Workspace Cleanup</li>
                </ul>
                
                <h3>Week 2: Production</h3>
                <ul>
                    <li>Production Deployment Prep</li>
                    <li>CI/CD Pipeline Setup</li>
                    <li>Advanced Features</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>👥 Resource Requirements</h2>
                <div class="metric">
                    <span>Backend Developer</span>
                    <span>1 FTE</span>
                </div>
                <div class="metric">
                    <span>Frontend Developer</span>
                    <span>0.5 FTE</span>
                </div>
                <div class="metric">
                    <span>DevOps Engineer</span>
                    <span>0.5 FTE</span>
                </div>
                <div class="metric">
                    <span>QA Engineer</span>
                    <span>0.5 FTE</span>
                </div>
                <div class="metric">
                    <span><strong>Budget Estimate</strong></span>
                    <span><strong>$5K - $8K</strong></span>
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>'''
        
        return html


def main():
    """Main execution"""
    print("NoxSuite Sprint Dashboard Generator")
    print("=" * 40)
    
    try:
        dashboard = SprintDashboard()
        dashboard.generate_dashboard()
        
        print("\n✅ Dashboard generated successfully!")
        print("\nNext steps:")
        print("1. Review action items above")
        print("2. Execute high-priority tasks")
        print("3. Begin sprint planning")
        
        return 0
        
    except Exception as e:
        print(f"Dashboard generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
