@echo off
echo Deploying urls.py to production...
scp F:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\urls.py zubair@192.168.2.69:/tmp/urls_new.py
echo.
echo Copying to production location and restarting Gunicorn...
ssh zubair@192.168.2.69 "echo erp | sudo -S cp /tmp/urls_new.py /var/www/tradifyerp/accounting/urls.py && echo erp | sudo -S systemctl restart gunicorn && echo Done"
echo.
echo Verifying URL pattern...
ssh zubair@192.168.2.69 "grep 'trading-manufacturing' /var/www/tradifyerp/accounting/urls.py"
pause
