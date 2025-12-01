@echo off
REM Gunicorn startup script for Windows
REM Place this in your project root or Scripts folder

setlocal enabledelayedexpansion

REM Set Django settings module
set DJANGO_SETTINGS_MODULE=TradifyERP.settings

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Create logs directory if it doesn't exist
if not exist "%SCRIPT_DIR%logs" (
    mkdir "%SCRIPT_DIR%logs"
)

REM Change to project directory
cd /d "%SCRIPT_DIR%"

REM Start Gunicorn
REM Options:
REM --workers: Number of worker processes (auto-detect based on CPU cores)
REM --bind: Address and port to bind to
REM --timeout: Worker timeout in seconds
REM --access-logfile: Path to access log
REM --error-logfile: Path to error log
REM --log-level: Logging level (debug, info, warning, error, critical)

echo Starting Gunicorn server...
echo.
echo Server will be available at: http://127.0.0.1:8001
echo.
echo Press Ctrl+C to stop the server
echo.

gunicorn ^
    --config gunicorn_config.py ^
    --workers 4 ^
    --bind 127.0.0.1:8001 ^
    --timeout 30 ^
    --access-logfile logs/access.log ^
    --error-logfile logs/error.log ^
    TradifyERP.wsgi:application

pause
