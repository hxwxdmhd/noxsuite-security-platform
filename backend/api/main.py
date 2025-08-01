"""
Main API module for NoxSuite
Combines all API routes and initializes authentication services
"""

import json
import os
from datetime import datetime

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth.auth_integration import AuthIntegrationService
from backend.api import admin_routes, auth_routes, user_routes

# Create FastAPI app
app = FastAPI(
    title="NoxSuite API",
    description="NoxSuite REST API with MFA and RBAC",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log errors and return standardized response"""
    # In a real implementation, this would log the error
    print(f"Global exception: {exc}")

    # Return error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred",
            "timestamp": datetime.now().isoformat(),
        },
    )


# Initialize auth service
JWT_SECRET = os.environ.get(
    "JWT_SECRET", "your-super-secret-key-change-in-production")
MFA_ENABLED = os.environ.get(
    "MFA_ENABLED", "True").lower() in ("true", "1", "yes")
TOKEN_EXPIRY = int(os.environ.get("TOKEN_EXPIRY", "3600"))
REFRESH_TOKEN_EXPIRY = int(os.environ.get(
    "REFRESH_TOKEN_EXPIRY", "604800"))  # 7 days

auth_service = AuthIntegrationService(
    jwt_secret=JWT_SECRET,
    mfa_enabled=MFA_ENABLED,
    token_expiry=TOKEN_EXPIRY,
    refresh_token_expiry=REFRESH_TOKEN_EXPIRY,
)

# Initialize route modules
auth_routes.initialize(auth_service)
user_routes.initialize(auth_service)
admin_routes.initialize(auth_service)

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth")
app.include_router(user_routes.router, prefix="/api/users")
app.include_router(admin_routes.router, prefix="/api/admin")


# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": app.version,
        "timestamp": datetime.now().isoformat(),
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "NoxSuite API",
        "description": "NoxSuite REST API with MFA and RBAC",
        "version": app.version,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


# Export API schema to file on startup
@app.on_event("startup")
async def export_schema():
    """Export OpenAPI schema to file on startup"""
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)
    print("OpenAPI schema exported to openapi.json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
