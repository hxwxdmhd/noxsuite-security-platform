from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
import time
import json
from datetime import datetime

app = FastAPI(title="NoxGuard Production API", version="1.0.0")

start_time = time.time()
request_count = 0

@app.get("/health")
async def health_check():
    global request_count
    request_count += 1
    
    uptime = time.time() - start_time
    
    return JSONResponse({
        "status": "healthy",
        "service": "noxguard-production-api",
        "version": "1.0.0",
        "uptime": uptime,
        "requests_served": request_count,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
    <head><title>NoxGuard Production API</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h1>NoxGuard Production API</h1>
        <p><strong>Status:</strong> Operational</p>
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Environment:</strong> Production</p>
        <h2>Endpoints:</h2>
        <ul>
            <li><a href="/health">/health</a> - Health check</li>
            <li><a href="/api/status">/api/status</a> - API status</li>
        </ul>
    </body>
    </html>
    """)

@app.get("/api/status")
async def api_status():
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "environment": "production",
        "uptime": time.time() - start_time,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
