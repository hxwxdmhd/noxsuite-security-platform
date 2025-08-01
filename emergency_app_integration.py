#!/usr/bin/env python3
"""
EMERGENCY FLASK APP INTEGRATION
Created: 2025-07-29 07:56:01
Purpose: Integration code for emergency authentication
"""

def apply_emergency_integration(app):
    """Apply emergency security integration to Flask app"""
    from emergency_auth_middleware import EmergencyAuthMiddleware, configure_emergency_sessions
    from emergency_knowledge_routes import register_emergency_knowledge_routes
    
    # Initialize emergency authentication
    emergency_auth = EmergencyAuthMiddleware()
    emergency_auth.init_app(app)
    configure_emergency_sessions(app)
    
    # Register emergency knowledge routes
    register_emergency_knowledge_routes(app)
    
    # Emergency login endpoint
    @app.route('/api/emergency/login', methods=['POST'])
    def emergency_login():
        from emergency_auth_middleware import emergency_login_endpoint
        return emergency_login_endpoint()
    
    # Emergency status endpoint
    @app.route('/api/emergency/status', methods=['GET'])
    def emergency_status():
        return {
            'emergency_patch': True,
            'patch_date': '2025-07-29',
            'audit_version': '4.0.0',
            'security_status': 'EMERGENCY_PATCHED'
        }
    
    return app

# Usage: 
# from emergency_app_integration import apply_emergency_integration
# app = apply_emergency_integration(app)
