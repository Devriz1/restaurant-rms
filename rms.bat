@echo off
title Restaurant RMS Launcher
cd /d "%~dp0"

echo Starting Restaurant RMS...
echo.

:: 1. Start Node.js LocalTunnel in a minimized window
start /min "Node Tunnel" cmd /k "npx localtunnel --port 8000 --subdomain rms"

:: 2. Wait 3 seconds for tunnel initialization
timeout /t 3 /nobreak >nul

:: 3. Launch Python Application
".venv\Scripts\python.exe" "launcher\rms_launcher.py"

pause