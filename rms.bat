@echo off
title Restaurant RMS Launcher
cd /d "%~dp0"

echo Starting Restaurant RMS...
echo.

:: Launch Python Application directly (ngrok is handled inside Python via pyngrok)
".venv\Scripts\python.exe" "launcher\rms_launcher.py"

pause