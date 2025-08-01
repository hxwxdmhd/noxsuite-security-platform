import json
import os
import time
from datetime import datetime

import psutil
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="NoxGuard Production API",
    version="1.0.0",
    description="Production NoxGuard Backend API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = time.time()


def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "uptime": time.time() - start_time,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    metrics = get_system_metrics()
    health_status = (
        "healthy"
        if metrics["cpu_percent"] < 80 and metrics["memory_percent"] < 80
        else "degraded"
    )

    return JSONResponse(
        {
            "status": health_status,
            "uptime": metrics["uptime"],
            "environment": os.getenv("ENVIRONMENT", "production"),
            "service": "noxguard-backend",
            "metrics": metrics,
            "version": "1.0.0",
        }
    )


@app.get("/")
async def root():
    return {
        "message": "NoxGuard Production API",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/api/status")
async def api_status():
    metrics = get_system_metrics()
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "deployment": "production",
        "metrics": metrics,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/metrics")
async def get_metrics():
    return get_system_metrics()


@app.get("/api/dashboard")
async def dashboard():
    metrics = get_system_metrics()
    return {
        "dashboard": "NoxGuard Production Dashboard",
        "services": {
            "backend": "running",
            "monitoring": "active",
            "security": "enabled",
        },
        "system_health": 100 - max(metrics["cpu_percent"], metrics["memory_percent"]),
        "metrics": metrics,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
