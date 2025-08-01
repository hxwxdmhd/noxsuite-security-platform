# Enhanced Copilot Agent Monitoring Dashboard
# Interactive monitoring interface with real-time metrics
# Date: 2025-07-29 06:49:09 UTC
# Mode: ENHANCED_CRITICAL_MONITORING

            from enhanced_monitoring_system import EnhancedMonitoringSystem
from datetime import datetime, timezone
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import requests
import threading

            from tkinter import filedialog
from collections import deque
from tkinter import scrolledtext, ttk
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import time
import tkinter as tk


            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[
                    ("Log files", "*.log"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
            )

            if filename:
                with open(filename, "w", encoding="utf-8") as f:
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

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            self.log_message(f"📊 Report generated: {report_file}")

            # Display summary
            recommendations = "\n".join(
                [f"• {rec}" for rec in report.get("recommendations", [])]
            )
            self.update_text_widget(self.recommendations_text, recommendations)

        except Exception as e:
            self.log_message(f"❌ Report generation error: {e}")

    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Monitoring Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#1e1e1e")

        ttk.Label(
            settings_window, text="Monitoring Configuration", font=("Arial", 12, "bold")
        ).pack(pady=10)
        ttk.Label(settings_window,
                  text="Settings panel coming soon...").pack(pady=20)

        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(
            pady=10
        )

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
