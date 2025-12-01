@echo off
REM Quick Start Script for TradifyERP with Gunicorn + Nginx
REM This starts both services in development/testing mode

setlocal enabledelayedexpansion

echo.
echo ====================================
echo TradifyERP Quick Start
echo ====================================
echo.
echo This script will start:
echo   1. Gunicorn (Port 8001)
echo   2. Nginx (Port 80/443)
echo.
echo Requirements:
echo   - Gunicorn installed
echo   - Nginx installed in C:\nginx
echo   - SSL certificates configured
echo   - Port 80, 443 available
echo.
echo Starting services...
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if logs directory exists
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

REM Start Gunicorn in new window
echo Starting Gunicorn server...
start "Gunicorn - TradifyERP" cmd /k python -m gunicorn --config gunicorn_config.py TradifyERP.wsgi:application

REM Wait a moment for Gunicorn to start
timeout /t 2 >nul

REM Start Nginx in new window
echo Starting Nginx server...
start "Nginx - Reverse Proxy" cmd /k C:\nginx\nginx.exe

timeout /t 2 >nul

echo.
echo ====================================
echo Services Started!
echo ====================================
echo.
echo Application URLs:
echo   HTTP:  http://www.tradifyglobal.com
echo   HTTPS: https://www.tradifyglobal.com
echo.
echo Service Details:
echo   - Gunicorn: Running on 127.0.0.1:8001 (window 1)
echo   - Nginx:    Running as reverse proxy (window 2)
echo.
echo Logs:
echo   - Gunicorn: %SCRIPT_DIR%logs\
echo   - Nginx:    C:\nginx\logs\
echo.
echo To stop services:
echo   - Close the Gunicorn window or press Ctrl+C
echo   - Close the Nginx window or run: C:\nginx\nginx.exe -s stop
echo.
echo To reload Nginx config:
echo   C:\nginx\nginx.exe -s reload
echo.
pause >nul
