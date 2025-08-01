@echo off
REM Python Launcher for NoxSuite
REM Ensures consistent Python environment

set PYTHON_PATH=K:\NoxPanel_Suite_WIP-1\noxsuite_env\Scripts\python.exe
set PYTHONPATH=%cd%;%PYTHONPATH%

REM Check if Python is available
"%PYTHON_PATH%" --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found at %PYTHON_PATH%
    echo Please reinstall Python or update the path
    pause
    exit /b 1
)

REM Launch Python with provided arguments
"%PYTHON_PATH%" %*
