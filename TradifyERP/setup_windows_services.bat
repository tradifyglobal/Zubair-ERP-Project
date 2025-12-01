@echo off
REM Windows Service Setup Script for TradifyERP
REM Run as Administrator

setlocal enabledelayedexpansion

echo.
echo ====================================
echo TradifyERP Service Setup
echo ====================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as Administrator!
    pause
    exit /b 1
)

echo Installing dependencies...
choco install nssm -y

echo.
echo ====================================
echo Creating Services
echo ====================================
echo.

REM Set paths
set PYTHON_PATH=C:\Python311\python.exe
set PROJECT_PATH=G:\TradifyERP\TradifyERP
set NGINX_PATH=C:\nginx\nginx.exe

REM Create Gunicorn service
echo Creating TradifyERP-Gunicorn service...
nssm install TradifyERP-Gunicorn "%PYTHON_PATH%" "-m gunicorn --config gunicorn_config.py TradifyERP.wsgi:application"
nssm set TradifyERP-Gunicorn AppDirectory "%PROJECT_PATH%"
nssm set TradifyERP-Gunicorn AppEnvironmentExtra DJANGO_ENV=production
nssm set TradifyERP-Gunicorn AppStdout "%PROJECT_PATH%\logs\gunicorn.log"
nssm set TradifyERP-Gunicorn AppStderr "%PROJECT_PATH%\logs\gunicorn_error.log"
nssm set TradifyERP-Gunicorn AppStdoutCreationDisposition 4
nssm set TradifyERP-Gunicorn AppStderrCreationDisposition 4
nssm set TradifyERP-Gunicorn AppRotateFiles 1
nssm set TradifyERP-Gunicorn AppRotateOnline 1
nssm set TradifyERP-Gunicorn AppRotateSeconds 86400
nssm set TradifyERP-Gunicorn AppRotateBytes 0

echo Gunicorn service created successfully!
echo.

REM Create Nginx service
echo Creating TradifyERP-Nginx service...
nssm install TradifyERP-Nginx "%NGINX_PATH%"
nssm set TradifyERP-Nginx AppDirectory "%NGINX_PATH:~0,-9%"
nssm set TradifyERP-Nginx AppStdout "%NGINX_PATH:~0,-9%\logs\nginx.log"
nssm set TradifyERP-Nginx AppStderr "%NGINX_PATH:~0,-9%\logs\nginx_error.log"
nssm set TradifyERP-Nginx AppStdoutCreationDisposition 4
nssm set TradifyERP-Nginx AppStderrCreationDisposition 4
nssm set TradifyERP-Nginx AppRotateFiles 1
nssm set TradifyERP-Nginx AppRotateOnline 1
nssm set TradifyERP-Nginx AppRotateSeconds 86400
nssm set TradifyERP-Nginx AppRotateBytes 0

echo Nginx service created successfully!
echo.

REM Create certificate renewal service
echo Creating Certificate-Renewal service...
nssm install TradifyERP-CertRenewal certbot "renew --quiet"
nssm set TradifyERP-CertRenewal AppDirectory "C:\"
nssm set TradifyERP-CertRenewal Start SERVICE_AUTO_START
nssm set TradifyERP-CertRenewal Type SERVICE_WIN32_OWN_PROCESS

echo Certificate renewal service created successfully!
echo.

REM Start services
echo ====================================
echo Starting Services
echo ====================================
echo.

echo Starting Gunicorn service...
nssm start TradifyERP-Gunicorn
timeout /t 2 >nul

echo Starting Nginx service...
nssm start TradifyERP-Nginx
timeout /t 2 >nul

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Services created:
echo   - TradifyERP-Gunicorn: Python/Gunicorn application server
echo   - TradifyERP-Nginx: Nginx reverse proxy web server
echo   - TradifyERP-CertRenewal: Certificate auto-renewal
echo.
echo To manage services, use:
echo   nssm status TradifyERP-Gunicorn
echo   nssm start TradifyERP-Gunicorn
echo   nssm stop TradifyERP-Gunicorn
echo   nssm restart TradifyERP-Gunicorn
echo   nssm remove TradifyERP-Gunicorn
echo.
echo Your application should now be available at:
echo   https://www.tradifyglobal.com
echo.
echo Press any key to exit...
pause >nul
