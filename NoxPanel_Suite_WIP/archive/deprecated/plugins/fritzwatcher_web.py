"""
FRITZWATCHER Web Interface
==========================

Enhanced web interface for Fritz!Box monitoring and management.
Integrates with the main NoxPanel Dashboard.

Author: MSP-Aware Development Team
Date: July 18, 2025
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
fritzwatcher_bp = Blueprint(
    'fritzwatcher', __name__, url_prefix='/fritzwatcher')

# Global plugin instance (will be set by main server)
fritzwatcher_plugin = None


def set_plugin_instance(plugin):
    """Set the plugin instance for the web interface"""
    global fritzwatcher_plugin
    fritzwatcher_plugin = plugin


@fritzwatcher_bp.route('/')
def dashboard():
    """Main FRITZWATCHER dashboard"""
    return render_template('fritzwatcher/dashboard.html')


@fritzwatcher_bp.route('/api/status')
def api_status():
    """Get router status"""
    if not fritzwatcher_plugin:
        return jsonify({'error': 'Plugin not available'}), 503

    try:
        # Run async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(
            fritzwatcher_plugin.get_router_status())
        loop.close()

        return jsonify(status)
    except Exception as e:
        logger.error(f"Status API error: {e}")
        return jsonify({'error': str(e)}), 500


@fritzwatcher_bp.route('/api/devices')
def api_devices():
    """Get all devices"""
    if not fritzwatcher_plugin:
        return jsonify({'error': 'Plugin not available'}), 503

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        devices = loop.run_until_complete(
            fritzwatcher_plugin.get_all_devices())
        loop.close()

        return jsonify(devices)
    except Exception as e:
        logger.error(f"Devices API error: {e}")
        return jsonify({'error': str(e)}), 500


@fritzwatcher_bp.route('/api/guest-wifi')
def api_guest_wifi_status():
    """Get guest WiFi status"""
    if not fritzwatcher_plugin:
        return jsonify({'error': 'Plugin not available'}), 503

    try:
        router_name = request.args.get('router')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(
            fritzwatcher_plugin.get_guest_wifi_status(router_name))
        loop.close()

        return jsonify(status)
    except Exception as e:
        logger.error(f"Guest WiFi status API error: {e}")
        return jsonify({'error': str(e)}), 500


@fritzwatcher_bp.route('/api/guest-wifi/toggle', methods=['POST'])
def api_guest_wifi_toggle():
    """Toggle guest WiFi"""
    if not fritzwatcher_plugin:
        return jsonify({'error': 'Plugin not available'}), 503

    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        router_name = data.get('router')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            fritzwatcher_plugin.toggle_guest_wifi(enabled, router_name))
        loop.close()

        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Guest WiFi toggle API error: {e}")
        return jsonify({'error': str(e)}), 500


@fritzwatcher_bp.route('/api/roaming-events')
def api_roaming_events():
    """Get roaming events"""
    if not fritzwatcher_plugin:
        return jsonify({'error': 'Plugin not available'}), 503

    try:
        hours = request.args.get('hours', 24, type=int)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        events = loop.run_until_complete(
            fritzwatcher_plugin.get_roaming_events(hours))
        loop.close()

        return jsonify(events)
    except Exception as e:
        logger.error(f"Roaming events API error: {e}")
        return jsonify({'error': str(e)}), 500


@fritzwatcher_bp.route('/api/sync')
def api_sync():
    """Force sync with routers"""
    if not fritzwatcher_plugin:
        return jsonify({'error': 'Plugin not available'}), 503

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fritzwatcher_plugin.sync_now())
        loop.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Sync API error: {e}")
        return jsonify({'error': str(e)}), 500


@fritzwatcher_bp.route('/routers')
def routers():
    """Router management page"""
    return render_template('fritzwatcher/routers.html')


@fritzwatcher_bp.route('/devices')
def devices():
    """Device monitoring page"""
    return render_template('fritzwatcher/devices.html')


@fritzwatcher_bp.route('/roaming')
def roaming():
    """Roaming analysis page"""
    return render_template('fritzwatcher/roaming.html')


@fritzwatcher_bp.route('/settings')
def settings():
    """Settings page"""
    return render_template('fritzwatcher/settings.html')


# Template for main dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FRITZWATCHER - Network Monitoring</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .device-card { 
            border-left: 4px solid #007bff; 
            margin-bottom: 1rem;
        }
        .router-card { 
            border-left: 4px solid #28a745; 
            margin-bottom: 1rem;
        }
        .router-card.offline { 
            border-left-color: #dc3545; 
        }
        .signal-strength {
            display: inline-block;
            width: 60px;
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            position: relative;
            margin-left: 10px;
        }
        .signal-strength::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .signal-strength.excellent::before { width: 100%; background: #28a745; }
        .signal-strength.good::before { width: 75%; background: #28a745; }
        .signal-strength.fair::before { width: 50%; background: #ffc107; }
        .signal-strength.poor::before { width: 25%; background: #dc3545; }
        .auto-refresh {
            animation: spin 2s linear infinite;
            margin-right: 8px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="row">
            <div class="col-12">
                <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div class="container-fluid">
                        <a class="navbar-brand" href="#">
                            <i class="fas fa-wifi"></i> FRITZWATCHER
                        </a>
                        <div class="navbar-nav ms-auto">
                            <a class="nav-link" href="#" onclick="syncNow()">
                                <i class="fas fa-sync-alt" id="sync-icon"></i> Sync
                            </a>
                            <a class="nav-link" href="{{ url_for('fritzwatcher.settings') }}">
                                <i class="fas fa-cog"></i> Settings
                            </a>
                        </div>
                    </div>
                </nav>
            </div>
        </div>

        <!-- Main Content -->
        <div class="row mt-4">
            <!-- Router Status -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-router"></i> Router Status</h5>
                    </div>
                    <div class="card-body" id="router-status">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tools"></i> Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <button class="btn btn-primary w-100 mb-2" onclick="toggleGuestWifi()">
                                    <i class="fas fa-wifi"></i> Toggle Guest WiFi
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-info w-100 mb-2" onclick="refreshDevices()">
                                    <i class="fas fa-sync"></i> Refresh Devices
                                </button>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <a href="{{ url_for('fritzwatcher.roaming') }}" class="btn btn-success w-100">
                                    <i class="fas fa-mobile-alt"></i> Roaming Analysis
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="{{ url_for('fritzwatcher.devices') }}" class="btn btn-warning w-100">
                                    <i class="fas fa-laptop"></i> Device Monitor
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Connected Devices -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-laptop"></i> Connected Devices</h5>
                    </div>
                    <div class="card-body" id="devices-list">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Roaming Events -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-mobile-alt"></i> Recent Roaming Events</h5>
                    </div>
                    <div class="card-body" id="roaming-events">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh interval (30 seconds)
        const REFRESH_INTERVAL = 30000;
        let refreshTimer;

        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadAll();
            startAutoRefresh();
        });

        function loadAll() {
            loadRouterStatus();
            loadDevices();
            loadRoamingEvents();
        }

        function startAutoRefresh() {
            refreshTimer = setInterval(loadAll, REFRESH_INTERVAL);
        }

        function stopAutoRefresh() {
            if (refreshTimer) {
                clearInterval(refreshTimer);
            }
        }

        function loadRouterStatus() {
            fetch('/fritzwatcher/api/status')
                .then(response => response.json())
                .then(data => {
                    let html = '';
                    for (const [name, status] of Object.entries(data)) {
                        const onlineClass = status.online ? 'router-card' : 'router-card offline';
                        const statusIcon = status.online ? 'fas fa-check-circle status-online' : 'fas fa-times-circle status-offline';
                        
                        html += `
                            <div class="card ${onlineClass}">
                                <div class="card-body">
                                    <h6><i class="${statusIcon}"></i> ${name}</h6>
                                    <p class="mb-1">Status: ${status.online ? 'Online' : 'Offline'}</p>
                                    <p class="mb-1">Devices: ${status.device_count || 0}</p>
                                    ${status.device_info ? `<p class="mb-0">Model: ${status.device_info.model || 'Unknown'}</p>` : ''}
                                </div>
                            </div>
                        `;
                    }
                    document.getElementById('router-status').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('router-status').innerHTML = 
                        '<div class="alert alert-danger">Error loading router status</div>';
                    console.error('Error:', error);
                });
        }

        function loadDevices() {
            fetch('/fritzwatcher/api/devices')
                .then(response => response.json())
                .then(data => {
                    let html = '';
                    if (data.length === 0) {
                        html = '<div class="alert alert-info">No devices found</div>';
                    } else {
                        data.forEach(device => {
                            const signalClass = getSignalClass(device.signal_strength);
                            const connectionIcon = device.connection_type === 'WiFi' ? 'fas fa-wifi' : 'fas fa-ethernet';
                            
                            html += `
                                <div class="device-card card">
                                    <div class="card-body">
                                        <div class="row align-items-center">
                                            <div class="col-md-3">
                                                <h6><i class="${connectionIcon}"></i> ${device.hostname || 'Unknown Device'}</h6>
                                                <small class="text-muted">${device.mac_address}</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge bg-primary">${device.router_name}</span>
                                            </div>
                                            <div class="col-md-2">
                                                <span>${device.ip_address}</span>
                                            </div>
                                            <div class="col-md-3">
                                                Signal: <span class="signal-strength ${signalClass}"></span>
                                                <small class="text-muted">${device.signal_strength}%</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge ${device.connected ? 'bg-success' : 'bg-secondary'}">
                                                    ${device.connected ? 'Connected' : 'Disconnected'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    document.getElementById('devices-list').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('devices-list').innerHTML = 
                        '<div class="alert alert-danger">Error loading devices</div>';
                    console.error('Error:', error);
                });
        }

        function loadRoamingEvents() {
            fetch('/fritzwatcher/api/roaming-events?hours=24')
                .then(response => response.json())
                .then(data => {
                    let html = '';
                    if (data.length === 0) {
                        html = '<div class="alert alert-info">No roaming events in the last 24 hours</div>';
                    } else {
                        data.slice(0, 10).forEach(event => {
                            const eventTime = new Date(event.timestamp).toLocaleString();
                            const eventIcon = getEventIcon(event.event_type);
                            
                            html += `
                                <div class="row border-bottom py-2">
                                    <div class="col-md-2">
                                        <i class="${eventIcon}"></i> ${eventTime}
                                    </div>
                                    <div class="col-md-3">
                                        <strong>${event.hostname}</strong><br>
                                        <small class="text-muted">${event.mac_address}</small>
                                    </div>
                                    <div class="col-md-4">
                                        <span class="badge bg-warning">${event.from_router}</span>
                                        <i class="fas fa-arrow-right mx-2"></i>
                                        <span class="badge bg-success">${event.to_router}</span>
                                    </div>
                                    <div class="col-md-3">
                                        <span class="badge bg-info">${event.event_type}</span>
                                        ${event.trigger_reason ? `<br><small class="text-muted">${event.trigger_reason}</small>` : ''}
                                    </div>
                                </div>
                            `;
                        });
                    }
                    document.getElementById('roaming-events').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('roaming-events').innerHTML = 
                        '<div class="alert alert-danger">Error loading roaming events</div>';
                    console.error('Error:', error);
                });
        }

        function getSignalClass(strength) {
            if (strength >= 80) return 'excellent';
            if (strength >= 60) return 'good';
            if (strength >= 40) return 'fair';
            return 'poor';
        }

        function getEventIcon(eventType) {
            switch(eventType) {
                case 'connect': return 'fas fa-plus-circle text-success';
                case 'disconnect': return 'fas fa-minus-circle text-danger';
                case 'roam': return 'fas fa-mobile-alt text-warning';
                default: return 'fas fa-circle text-info';
            }
        }

        function syncNow() {
            const syncIcon = document.getElementById('sync-icon');
            syncIcon.classList.add('auto-refresh');
            
            fetch('/fritzwatcher/api/sync')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadAll();
                        // Show success message
                        const alert = document.createElement('div');
                        alert.className = 'alert alert-success alert-dismissible fade show';
                        alert.innerHTML = `
                            <strong>Sync Complete!</strong> Updated ${data.routers_updated} routers.
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        `;
                        document.body.insertBefore(alert, document.body.firstChild);
                        
                        // Auto-dismiss after 3 seconds
                        setTimeout(() => {
                            alert.remove();
                        }, 3000);
                    }
                })
                .catch(error => {
                    console.error('Sync error:', error);
                })
                .finally(() => {
                    syncIcon.classList.remove('auto-refresh');
                });
        }

        function toggleGuestWifi() {
            // Simple toggle - you might want to make this more sophisticated
            const enabled = confirm('Enable Guest WiFi?');
            
            fetch('/fritzwatcher/api/guest-wifi/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ enabled: enabled })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Guest WiFi ' + (enabled ? 'enabled' : 'disabled'));
                } else {
                    alert('Failed to toggle Guest WiFi');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error toggling Guest WiFi');
            });
        }

        function refreshDevices() {
            loadDevices();
        }
    </script>
</body>
</html>
"""


def create_web_interface():
    """Create the web interface files"""
    templates_dir = Path(__file__).parent.parent / \
        "webpanel" / "templates" / "fritzwatcher"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Create dashboard template
    dashboard_file = templates_dir / "dashboard.html"
    with open(dashboard_file, 'w') as f:
        f.write(DASHBOARD_TEMPLATE)

    logger.info(f"Created FRITZWATCHER web interface at {templates_dir}")


if __name__ == "__main__":
    create_web_interface()
    print("✅ FRITZWATCHER web interface created")
