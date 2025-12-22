@echo off
echo Restoring original sidebar files from Git...

REM First check git status
cd /d F:\ERP-Production\Zubair-ERP-Project\TradifyERP

REM Reset the sidebar files to the last committed version (before our changes)
git checkout templates/partials/sidebar.html
git checkout templates/partials/hori-sidebar.html

echo Sidebar files restored from Git

REM Now upload the clean versions
cd /d F:\ERP-Production\Zubair-ERP-Project

scp TradifyERP\templates\partials\sidebar.html zubair@192.168.20.10:/tmp/sidebar_clean.html
scp TradifyERP\templates\partials\hori-sidebar.html zubair@192.168.20.10:/tmp/hori-sidebar_clean.html

ssh zubair@192.168.20.10 "echo erp | sudo -S cp /tmp/sidebar_clean.html /var/www/tradifyerp/templates/partials/sidebar.html"
ssh zubair@192.168.20.10 "echo erp | sudo -S cp /tmp/hori-sidebar_clean.html /var/www/tradifyerp/templates/partials/hori-sidebar.html"

REM Disable DEBUG and restart
ssh zubair@192.168.20.10 "echo erp | sudo -S sed -i 's/DEBUG = True/DEBUG = False/' /var/www/tradifyerp/tradifyerp/settings.py"
ssh zubair@192.168.20.10 "echo erp | sudo -S systemctl restart gunicorn"

echo Done. Original sidebars restored, DEBUG disabled, Gunicorn restarted.
