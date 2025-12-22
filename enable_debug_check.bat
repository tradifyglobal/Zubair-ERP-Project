@echo off
echo Enabling DEBUG mode...

REM Enable DEBUG
ssh zubair@192.168.2.69 "echo erp | sudo -S sed -i 's/DEBUG = False/DEBUG = True/' /var/www/tradifyerp/tradifyerp/settings.py"

REM Check if DEBUG is enabled
ssh zubair@192.168.2.69 "grep 'DEBUG = ' /var/www/tradifyerp/tradifyerp/settings.py" > debug_status.txt

REM Restart Gunicorn
ssh zubair@192.168.2.69 "echo erp | sudo -S systemctl restart gunicorn"

REM Wait for restart
timeout /t 5 /nobreak > nul

REM Check Gunicorn status
ssh zubair@192.168.2.69 "systemctl status gunicorn" > gunicorn_status.txt

echo Done. Check debug_status.txt and gunicorn_status.txt
type debug_status.txt
