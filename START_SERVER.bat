@echo off
REM Depreciation Scheduler Startup Script for TradifyERP
REM Starts the Django server with automated depreciation scheduler

cls
echo.
echo ============================================================
echo TradifyERP Server with Automated Depreciation
echo ============================================================
echo.

cd /d g:\TradifyERP\TradifyERP

REM Start the depreciation scheduler
echo [1/2] Starting depreciation scheduler...
python manage.py depreciation_scheduler --start
timeout /t 2 /nobreak

REM Start Django server
echo.
echo [2/2] Starting Django server on 0.0.0.0:8000...
echo.
python manage.py runserver 0.0.0.0:8000

pause
