@echo off
REM Start Django Development Server on All Interfaces
REM This allows access from external IPs and your domain name

setlocal enabledelayedexpansion

set PROJECT_DIR=G:\TradifyERP\TradifyERP

echo.
echo ====================================
echo TradifyERP Development Server
echo ====================================
echo.
echo Starting Django development server on all interfaces (0.0.0.0:8000)
echo.
echo Access URLs:
echo   - Local:     http://127.0.0.1:8000
echo   - IP:        http://174.93.66.9:8000
echo   - Domain:    http://www.tradifyglobal.com:8000
echo   - Localhost: http://localhost:8000
echo.
echo Login at:
echo   http://www.tradifyglobal.com:8000/accounts/login/
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%PROJECT_DIR%"
python manage.py runserver 0.0.0.0:8000

pause
