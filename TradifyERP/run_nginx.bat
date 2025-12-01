@echo off
REM Nginx startup script for Windows
REM Place this in your Nginx installation directory or create a shortcut

setlocal

REM Set Nginx directory (adjust path as needed)
set NGINX_DIR=C:\nginx

REM Change to Nginx directory
cd /d "%NGINX_DIR%"

REM Check if nginx.exe exists
if not exist "%NGINX_DIR%\nginx.exe" (
    echo Error: nginx.exe not found in %NGINX_DIR%
    echo Please install Nginx from: http://nginx.org/en/download.html
    pause
    exit /b 1
)

REM Start Nginx
echo Starting Nginx server...
echo.
echo Nginx will be available at:
echo   HTTP:  http://www.tradifyglobal.com (redirects to HTTPS)
echo   HTTPS: https://www.tradifyglobal.com
echo.
echo To stop Nginx, run: nginx -s stop
echo To reload config, run: nginx -s reload
echo.

start "" "%NGINX_DIR%\nginx.exe"

echo Nginx started successfully!
pause
