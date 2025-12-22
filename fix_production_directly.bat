@echo off
echo Fixing sidebar files directly on production server...

REM Download current production files as backup
scp zubair@192.168.20.10:/var/www/tradifyerp/templates/partials/sidebar.html sidebar_backup_prod.html
scp zubair@192.168.20.10:/var/www/tradifyerp/templates/partials/hori-sidebar.html hori_sidebar_backup_prod.html

REM Check if production has git
ssh zubair@192.168.20.10 "cd /var/www/tradifyerp && git status" > git_check.txt 2>&1

REM Try to restore using git on production server
ssh zubair@192.168.20.10 "cd /var/www/tradifyerp && echo erp | sudo -S git checkout templates/partials/sidebar.html templates/partials/hori-sidebar.html"

REM Restart Gunicorn
ssh zubair@192.168.20.10 "echo erp | sudo -S systemctl restart gunicorn"

echo Production sidebars restored from Git and Gunicorn restarted
echo Backup files saved locally as sidebar_backup_prod.html and hori_sidebar_backup_prod.html
