import os
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="NoxGuard Backend", version="1.0.0")

start_time = time.time()


@app.get("/health")
async def health_check():
    return JSONResponse(
        {
            "status": "healthy",
            "uptime": time.time() - start_time,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service": "noxguard-backend",
        }
    )


@app.get("/")
async def root():
    return {"message": "NoxGuard Backend API", "status": "running"}


@app.get("/api/status")
async def api_status():
    return {"api_version": "1.0.0", "status": "operational", "timestamp": time.time()}
