@echo off
echo Restarting Langflow for MCP integration...

REM Stop any existing Langflow processes
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start Langflow
echo Starting Langflow...
langflow run --host 0.0.0.0 --port 7860

echo If Langflow fails to start, try:
echo    pip install langflow --upgrade
echo    or
echo    python -m langflow run --host 0.0.0.0 --port 7860
pause
