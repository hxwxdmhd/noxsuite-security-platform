# Enhanced Copilot Agent Monitoring Dashboard
# Interactive monitoring interface with real-time metrics
# Date: 2025-07-29 06:49:09 UTC
# Mode: ENHANCED_CRITICAL_MONITORING

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
from datetime import datetime, timezone
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
import requests

class EnhancedMonitoringDashboard:
    """
    Real-time monitoring dashboard for enhanced copilot agent monitoring
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Enhanced Copilot Agent Monitoring Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Data storage for real-time plotting
        self.time_data = deque(maxlen=60)  # Last 60 data points
        self.memory_data = deque(maxlen=60)
        self.cpu_data = deque(maxlen=60)
        self.api_response_data = deque(maxlen=60)
        
        # Monitoring system reference
        self.monitoring_system = None
        self.update_thread = None
        self.running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🚀 ENHANCED COPILOT AGENT MONITORING",
            font=('Arial', 16, 'bold'),
            bg='#1e1e1e',
            fg='#00ff41'
        )
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Setup tabs
        self.setup_overview_tab()
        self.setup_metrics_tab()
        self.setup_incidents_tab()
        self.setup_logs_tab()
        self.setup_patterns_tab()
        
        # Control buttons
        self.setup_control_buttons(main_frame)
        
    def setup_overview_tab(self):
        """Setup system overview tab"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="🛡️ System Overview")
        
        # Status indicators
        status_frame = ttk.LabelFrame(overview_frame, text="System Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        # Create status labels
        self.status_labels = {}
        status_items = [
            ("monitoring_status", "Monitoring", "❌ INACTIVE"),
            ("memory_status", "Memory", "📊 ---%"),
            ("cpu_status", "CPU", "⚡ ---%"),
            ("api_status", "API", "🌐 --- ms"),
            ("incidents_status", "Incidents", "🚨 0 active"),
            ("uptime_status", "Uptime", "⏰ --- hours")
        ]
        
        for i, (key, label, default) in enumerate(status_items):
            row = i // 3
            col = i % 3
            
            ttk.Label(status_frame, text=f"{label}:").grid(row=row*2, column=col, sticky='w', padx=5)
            self.status_labels[key] = ttk.Label(status_frame, text=default, font=('Arial', 10, 'bold'))
            self.status_labels[key].grid(row=row*2+1, column=col, sticky='w', padx=5)
        
        # Health summary
        health_frame = ttk.LabelFrame(overview_frame, text="Health Summary", padding=10)
        health_frame.pack(fill='x', padx=10, pady=5)
        
        self.health_text = scrolledtext.ScrolledText(
            health_frame, 
            height=8, 
            font=('Consolas', 9),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.health_text.pack(fill='both', expand=True)
        
        # Recommendations
        rec_frame = ttk.LabelFrame(overview_frame, text="Recommendations", padding=10)
        rec_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.recommendations_text = scrolledtext.ScrolledText(
            rec_frame, 
            height=6, 
            font=('Consolas', 9),
            bg='#2d2d2d',
            fg='#00ff41'
        )
        self.recommendations_text.pack(fill='both', expand=True)
        
    def setup_metrics_tab(self):
        """Setup real-time metrics tab with graphs"""
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="📊 Real-time Metrics")
        
        # Create matplotlib figure
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.patch.set_facecolor('#1e1e1e')
        
        # Configure axes
        axes_config = [
            (self.ax1, "Memory Usage (%)", "#ff4444"),
            (self.ax2, "CPU Usage (%)", "#44ff44"),
            (self.ax3, "API Response Time (ms)", "#4444ff"),
            (self.ax4, "System Load", "#ffff44")
        ]
        
        for ax, title, color in axes_config:
            ax.set_title(title, color='white')
            ax.set_facecolor('#2d2d2d')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, metrics_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def setup_incidents_tab(self):
        """Setup incidents monitoring tab"""
        incidents_frame = ttk.Frame(self.notebook)
        self.notebook.add(incidents_frame, text="🚨 Incidents")
        
        # Incidents table
        incidents_table_frame = ttk.LabelFrame(incidents_frame, text="Recent Incidents", padding=10)
        incidents_table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for incidents
        columns = ("Time", "ID", "Severity", "Category", "Message")
        self.incidents_tree = ttk.Treeview(incidents_table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.incidents_tree.heading(col, text=col)
            self.incidents_tree.column(col, width=150)
        
        # Scrollbar for incidents
        incidents_scrollbar = ttk.Scrollbar(incidents_table_frame, orient='vertical', command=self.incidents_tree.yview)
        self.incidents_tree.configure(yscrollcommand=incidents_scrollbar.set)
        
        self.incidents_tree.pack(side='left', fill='both', expand=True)
        incidents_scrollbar.pack(side='right', fill='y')
        
        # Incident details
        details_frame = ttk.LabelFrame(incidents_frame, text="Incident Details", padding=10)
        details_frame.pack(fill='x', padx=10, pady=5)
        
        self.incident_details = scrolledtext.ScrolledText(
            details_frame, 
            height=6, 
            font=('Consolas', 9),
            bg='#2d2d2d',
            fg='#ff4444'
        )
        self.incident_details.pack(fill='both', expand=True)
        
        # Bind selection event
        self.incidents_tree.bind('<<TreeviewSelect>>', self.on_incident_select)
        
    def setup_logs_tab(self):
        """Setup logs monitoring tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 Logs")
        
        # Log display
        logs_display_frame = ttk.LabelFrame(logs_frame, text="System Logs", padding=10)
        logs_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_display_frame, 
            font=('Consolas', 9),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.logs_text.pack(fill='both', expand=True)
        
        # Log controls
        controls_frame = ttk.Frame(logs_frame)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Refresh Logs", command=self.refresh_logs).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="🗑️ Clear Display", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="💾 Save Logs", command=self.save_logs).pack(side='left', padx=5)
        
    def setup_patterns_tab(self):
        """Setup monitoring patterns configuration tab"""
        patterns_frame = ttk.Frame(self.notebook)
        self.notebook.add(patterns_frame, text="🔍 Patterns")
        
        # Patterns list
        patterns_list_frame = ttk.LabelFrame(patterns_frame, text="Active Monitoring Patterns", padding=10)
        patterns_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for patterns
        pattern_columns = ("ID", "Category", "Severity", "Description")
        self.patterns_tree = ttk.Treeview(patterns_list_frame, columns=pattern_columns, show='headings', height=12)
        
        for col in pattern_columns:
            self.patterns_tree.heading(col, text=col)
            self.patterns_tree.column(col, width=150)
        
        self.patterns_tree.pack(fill='both', expand=True)
        
        # Pattern details
        pattern_details_frame = ttk.LabelFrame(patterns_frame, text="Pattern Details", padding=10)
        pattern_details_frame.pack(fill='x', padx=10, pady=5)
        
        self.pattern_details = scrolledtext.ScrolledText(
            pattern_details_frame, 
            height=6, 
            font=('Consolas', 9),
            bg='#2d2d2d',
            fg='#44ff44'
        )
        self.pattern_details.pack(fill='both', expand=True)
        
    def setup_control_buttons(self, parent):
        """Setup control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(control_frame, text="🚀 Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Monitoring", command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="📊 Generate Report", command=self.generate_report).pack(side='left', padx=5)
        ttk.Button(control_frame, text="🔄 Refresh Data", command=self.refresh_data).pack(side='left', padx=5)
        ttk.Button(control_frame, text="⚙️ Settings", command=self.open_settings).pack(side='left', padx=5)
        
        # Status indicator
        self.status_indicator = tk.Label(
            control_frame, 
            text="⭕ READY", 
            font=('Arial', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffff00'
        )
        self.status_indicator.pack(side='right', padx=10)
        
    def start_monitoring(self):
        """Start the monitoring system"""
        try:
            # Import and initialize monitoring system
            from enhanced_monitoring_system import EnhancedMonitoringSystem
            
            self.monitoring_system = EnhancedMonitoringSystem()
            self.monitoring_system.start_monitoring()
            
            # Update UI
            self.running = True
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            self.status_indicator.configure(text="🟢 MONITORING", fg='#00ff41')
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
            
            # Load patterns
            self.load_patterns()
            
            self.log_message("🚀 Enhanced monitoring system started successfully")
            
        except Exception as e:
            self.log_message(f"❌ Error starting monitoring: {e}")
            
    def stop_monitoring(self):
        """Stop the monitoring system"""
        try:
            self.running = False
            
            if self.monitoring_system:
                self.monitoring_system.stop_monitoring()
            
            # Update UI
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
            self.status_indicator.configure(text="🔴 STOPPED", fg='#ff4444')
            
            self.log_message("🛑 Monitoring system stopped")
            
        except Exception as e:
            self.log_message(f"❌ Error stopping monitoring: {e}")
            
    def update_loop(self):
        """Main update loop for real-time data"""
        while self.running:
            try:
                if self.monitoring_system:
                    # Update all displays
                    self.update_status()
                    self.update_metrics()
                    self.update_incidents()
                    
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.log_message(f"❌ Update error: {e}")
                time.sleep(10)
                
    def update_status(self):
        """Update status indicators"""
        if not self.monitoring_system:
            return
            
        try:
            health = self.monitoring_system.get_system_health()
            
            # Update status labels
            self.root.after(0, lambda: self.status_labels["monitoring_status"].configure(text="✅ ACTIVE"))
            self.root.after(0, lambda: self.status_labels["memory_status"].configure(text=f"📊 {health.memory_usage_percent:.1f}%"))
            self.root.after(0, lambda: self.status_labels["cpu_status"].configure(text=f"⚡ {health.cpu_usage_percent:.1f}%"))
            self.root.after(0, lambda: self.status_labels["api_status"].configure(text=f"🌐 {health.api_response_time_ms:.1f}ms"))
            self.root.after(0, lambda: self.status_labels["uptime_status"].configure(text=f"⏰ {health.uptime_hours:.1f}h"))
            
            # Update health summary
            health_summary = f"""
SYSTEM HEALTH SUMMARY
=====================
Memory Usage: {health.memory_usage_percent:.1f}%
CPU Usage: {health.cpu_usage_percent:.1f}%
Disk Usage: {health.disk_usage_percent:.1f}%
API Response: {health.api_response_time_ms:.1f}ms
Error Rate: {health.error_rate_percent:.1f}%
Active Connections: {health.active_connections}
Uptime: {health.uptime_hours:.1f} hours

Status: {'🟢 HEALTHY' if health.memory_usage_percent < 80 and health.cpu_usage_percent < 70 else '🟡 CAUTION' if health.memory_usage_percent < 90 else '🔴 CRITICAL'}
"""
            
            self.root.after(0, lambda: self.update_text_widget(self.health_text, health_summary))
            
        except Exception as e:
            self.log_message(f"❌ Status update error: {e}")
            
    def update_metrics(self):
        """Update real-time metrics graphs"""
        if not self.monitoring_system:
            return
            
        try:
            health = self.monitoring_system.get_system_health()
            current_time = datetime.now()
            
            # Add data points
            self.time_data.append(current_time)
            self.memory_data.append(health.memory_usage_percent)
            self.cpu_data.append(health.cpu_usage_percent)
            self.api_response_data.append(health.api_response_time_ms)
            
            # Update plots
            self.root.after(0, self.update_plots)
            
        except Exception as e:
            self.log_message(f"❌ Metrics update error: {e}")
            
    def update_plots(self):
        """Update matplotlib plots"""
        try:
            if len(self.time_data) < 2:
                return
                
            # Clear axes
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax4.clear()
            
            # Plot data
            self.ax1.plot(self.time_data, self.memory_data, color='#ff4444', linewidth=2)
            self.ax1.set_title("Memory Usage (%)", color='white')
            self.ax1.set_ylim(0, 100)
            
            self.ax2.plot(self.time_data, self.cpu_data, color='#44ff44', linewidth=2)
            self.ax2.set_title("CPU Usage (%)", color='white')
            self.ax2.set_ylim(0, 100)
            
            self.ax3.plot(self.time_data, self.api_response_data, color='#4444ff', linewidth=2)
            self.ax3.set_title("API Response Time (ms)", color='white')
            
            # Combined system load
            if len(self.memory_data) > 0 and len(self.cpu_data) > 0:
                load_data = [(m + c) / 2 for m, c in zip(self.memory_data, self.cpu_data)]
                self.ax4.plot(self.time_data, load_data, color='#ffff44', linewidth=2)
                self.ax4.set_title("System Load (%)", color='white')
                self.ax4.set_ylim(0, 100)
            
            # Configure all axes
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.set_facecolor('#2d2d2d')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_color('white')
                ax.grid(True, alpha=0.3)
            
            self.canvas.draw()
            
        except Exception as e:
            self.log_message(f"❌ Plot update error: {e}")
            
    def update_incidents(self):
        """Update incidents display"""
        if not self.monitoring_system:
            return
            
        try:
            # Clear existing items
            self.root.after(0, lambda: self.incidents_tree.delete(*self.incidents_tree.get_children()))
            
            # Add incidents
            for incident in self.monitoring_system.incidents[-20:]:  # Last 20 incidents
                incident_time = datetime.fromisoformat(incident.timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
                severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🟡", "low": "ℹ️"}
                emoji = severity_emoji.get(incident.severity.value, "❓")
                
                self.root.after(0, lambda i=incident, t=incident_time, e=emoji: 
                    self.incidents_tree.insert('', 0, values=(
                        t, i.id, f"{e} {i.severity.value}", i.category.value, i.message[:50] + "..."
                    ))
                )
                
            # Update incidents count in status
            incident_count = len(self.monitoring_system.incidents)
            self.root.after(0, lambda: self.status_labels["incidents_status"].configure(text=f"🚨 {incident_count} total"))
            
        except Exception as e:
            self.log_message(f"❌ Incidents update error: {e}")
            
    def on_incident_select(self, event):
        """Handle incident selection"""
        try:
            selection = self.incidents_tree.selection()[0]
            incident_id = self.incidents_tree.item(selection)['values'][1]
            
            # Find incident details
            incident = next((i for i in self.monitoring_system.incidents if i.id == incident_id), None)
            
            if incident:
                details = f"""
INCIDENT DETAILS
================
ID: {incident.id}
Timestamp: {incident.timestamp}
Pattern: {incident.pattern_id}
Severity: {incident.severity.value}
Category: {incident.category.value}
Message: {incident.message}

Action Taken: {incident.action_taken}
Resolved: {'Yes' if incident.resolved else 'No'}

Context:
{chr(10).join(incident.context)}
"""
                self.update_text_widget(self.incident_details, details)
                
        except (IndexError, KeyError):
            pass  # No selection or invalid selection
            
    def load_patterns(self):
        """Load monitoring patterns into display"""
        if not self.monitoring_system:
            return
            
        try:
            # Clear existing items
            self.patterns_tree.delete(*self.patterns_tree.get_children())
            
            # Add patterns
            for pattern in self.monitoring_system.patterns:
                severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🟡", "low": "ℹ️"}
                emoji = severity_emoji.get(pattern.severity.value, "❓")
                
                self.patterns_tree.insert('', 'end', values=(
                    pattern.id,
                    pattern.category.value,
                    f"{emoji} {pattern.severity.value}",
                    pattern.description
                ))
                
        except Exception as e:
            self.log_message(f"❌ Patterns load error: {e}")
            
    def refresh_logs(self):
        """Refresh logs display"""
        try:
            log_content = ""
            
            # Try to read monitoring logs
            try:
                with open("logs/enhanced_monitoring.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    log_content = "".join(lines[-100:])  # Last 100 lines
            except FileNotFoundError:
                log_content = "📋 No monitoring logs found yet...\n"
                
            self.update_text_widget(self.logs_text, log_content)
            
        except Exception as e:
            self.log_message(f"❌ Logs refresh error: {e}")
            
    def clear_logs(self):
        """Clear logs display"""
        self.logs_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Save current logs to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                self.log_message(f"💾 Logs saved to {filename}")
                
        except Exception as e:
            self.log_message(f"❌ Save error: {e}")
            
    def refresh_data(self):
        """Refresh all data displays"""
        if self.monitoring_system:
            self.update_status()
            self.update_incidents()
            self.refresh_logs()
            self.log_message("🔄 Data refreshed")
        else:
            self.log_message("❌ No monitoring system active")
            
    def generate_report(self):
        """Generate and display monitoring report"""
        if not self.monitoring_system:
            self.log_message("❌ No monitoring system active")
            return
            
        try:
            report = self.monitoring_system.generate_enhanced_report()
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"ENHANCED_MONITORING_REPORT_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.log_message(f"📊 Report generated: {report_file}")
            
            # Display summary
            recommendations = "\n".join([f"• {rec}" for rec in report.get("recommendations", [])])
            self.update_text_widget(self.recommendations_text, recommendations)
            
        except Exception as e:
            self.log_message(f"❌ Report generation error: {e}")
            
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Monitoring Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#1e1e1e')
        
        ttk.Label(settings_window, text="Monitoring Configuration", font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Label(settings_window, text="Settings panel coming soon...").pack(pady=20)
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=10)
        
    def update_text_widget(self, widget, text):
        """Safely update text widget"""
        widget.delete(1.0, tk.END)
        widget.insert(1.0, text)
        widget.see(tk.END)
        
    def log_message(self, message):
        """Log message to logs display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            self.logs_text.insert(tk.END, log_entry)
            self.logs_text.see(tk.END)
        except:
            pass  # Widget might not be ready yet
            
    def run(self):
        """Start the dashboard"""
        print("🚀 Starting Enhanced Monitoring Dashboard...")
        self.log_message("🚀 Enhanced Monitoring Dashboard initialized")
        self.refresh_logs()
        self.root.mainloop()
        
    def on_closing(self):
        """Handle dashboard closing"""
        if self.running:
            self.stop_monitoring()
        self.root.destroy()

def main():
    """Main function to run the dashboard"""
    dashboard = EnhancedMonitoringDashboard()
    dashboard.root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    dashboard.run()

if __name__ == "__main__":
    main()
