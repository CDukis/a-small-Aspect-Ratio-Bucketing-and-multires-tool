@echo off
title Aspect Bucketing Tool
cd /d "%~dp0"

echo.
echo  Aspect Bucketing Tool
echo  ─────────────────────────────────────
echo  Starting server at http://localhost:5137
echo  Browser will open automatically.
echo.
echo  Press Ctrl+C to stop.
echo.

python app.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to start. Have you run install.bat yet?
    pause
)
