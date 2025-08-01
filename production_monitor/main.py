import json
import time
from datetime import datetime

import psutil
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="NoxGuard Monitor", version="1.0.0")

start_time = time.time()


@app.get("/status")
async def monitor_status():
    return JSONResponse(
        {
            "status": "monitoring_active",
            "uptime": time.time() - start_time,
            "service": "noxguard-monitor",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.get("/")
async def root():
    return {"message": "NoxGuard Production Monitor", "status": "active"}


@app.get("/system")
async def system_status():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
