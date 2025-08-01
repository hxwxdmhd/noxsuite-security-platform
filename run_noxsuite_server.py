#!/usr/bin/env python3
"""
NoxSuite API Server with RBAC and MFA
=====================================
Combined script to run the NoxSuite API server with RBAC and MFA extensions.
"""

import os
import sys
import argparse
import uvicorn

def main():
    """Run the FastAPI server with RBAC and MFA extensions"""
    parser = argparse.ArgumentParser(description="NoxSuite API Server with RBAC and MFA")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    # Import main FastAPI server
    import noxsuite_fastapi_server
    
    # Import RBAC and MFA extensions
    try:
        import rbac_mfa_extension
        print("✓ RBAC and MFA extensions loaded")
    except ImportError as e:
        print(f"✗ Failed to load RBAC and MFA extensions: {e}")
        
    # Run server
    reload = not args.no_reload
    print(f"Starting NoxSuite API server on {args.host}:{args.port}")
    uvicorn.run(
        "noxsuite_fastapi_server:app", 
        host=args.host, 
        port=args.port, 
        reload=reload
    )
    
if __name__ == "__main__":
    main()
