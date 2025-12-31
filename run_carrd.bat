@echo off
REM Carrd Automation Launcher Script for Windows
REM This script validates the configuration and runs the automation

echo ================================================
echo   Carrd.co Automation Launcher
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed
    echo Please install Python 3.11 or higher from python.org
    pause
    exit /b 1
)

echo Python found
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python validate_config.py
if %errorlevel% neq 0 (
    echo.
    echo Configuration validation failed
    echo.
    set /p install="Do you want to install dependencies now? (y/n): "
    if /i "%install%"=="y" (
        echo Installing dependencies...
        pip install -r requirements.txt
        echo.
        echo Dependencies installed successfully!
        echo.
        echo Please configure your settings:
        echo   1. Add recipient emails to emails.txt
        echo   2. (Optional) Add proxies to proxy\proxies.txt
        echo   3. Edit SITE\title.txt for your site name
        echo   4. Customize message in carrd_automation.py
        echo.
        echo Then run this script again.
        pause
        exit /b 0
    ) else (
        echo Installation cancelled
        pause
        exit /b 1
    )
)

echo.
echo ================================================
echo   Starting Carrd Automation
echo ================================================
echo.

REM Run the automation
python carrd_automation.py

echo.
echo ================================================
echo   Automation Complete
echo ================================================
echo.
echo Check carrd_automation.log for details
echo Processed emails are tracked in processed_emails.json
echo.
pause
