@echo off
echo ===== PRODUCTION SERVER STATUS CHECK =====
echo.

echo Checking Gunicorn status...
ssh zubair@192.168.20.10 "systemctl status gunicorn | head -20"

echo.
echo Checking DEBUG setting...
ssh zubair@192.168.20.10 "grep 'DEBUG =' /var/www/tradifyerp/tradifyerp/settings.py"

echo.
echo Checking if Trading Manufacturing files exist...
ssh zubair@192.168.20.10 "ls -la /var/www/tradifyerp/accounting/views_tm.py 2>&1"
ssh zubair@192.168.20.10 "ls -la /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html 2>&1"

echo.
echo Checking URL pattern...
ssh zubair@192.168.20.10 "grep -c 'trading-manufacturing' /var/www/tradifyerp/accounting/urls.py"

echo.
echo Checking template extends line...
ssh zubair@192.168.20.10 "head -1 /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html"

echo.
echo ===== STATUS CHECK COMPLETE =====
