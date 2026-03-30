@echo off
title Aspect Bucketing Tool - Install
echo.
echo  Aspect Bucketing Tool - Installer
echo  ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.9+ from https://python.org
    echo  Make sure to tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo  Python found. Installing dependencies...
echo.
pip install flask pillow

if errorlevel 1 (
    echo.
    echo  [ERROR] Installation failed. Try running as Administrator,
    echo  or run:  pip install flask pillow
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   Installation complete!
echo   Run run.bat to start the tool.
echo  ============================================
echo.
pause
