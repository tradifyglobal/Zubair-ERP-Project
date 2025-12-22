@echo off
echo Disabling DEBUG mode and checking sidebar files...

REM Disable DEBUG
ssh zubair@192.168.2.69 "echo erp | sudo -S sed -i 's/DEBUG = True/DEBUG = False/' /var/www/tradifyerp/tradifyerp/settings.py"

REM Restart Gunicorn
ssh zubair@192.168.2.69 "echo erp | sudo -S systemctl restart gunicorn"

REM Wait for restart
timeout /t 5 /nobreak > nul

echo DEBUG disabled and Gunicorn restarted
echo Please try accessing the dashboard now
