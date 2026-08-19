@echo off
title Restaurant RMS Launcher
cd /d "%~dp0"

echo Starting Restaurant RMS...
echo.

".venv\Scripts\python.exe" "launcher\rms_launcher.py"

pause
