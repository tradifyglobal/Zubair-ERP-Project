@echo off
echo Downloading production sidebar files for inspection...

REM Download current sidebar files
scp zubair@192.168.2.69:/var/www/tradifyerp/templates/partials/sidebar.html sidebar_production.html
scp zubair@192.168.2.69:/var/www/tradifyerp/templates/partials/hori-sidebar.html hori_sidebar_production.html

echo Files downloaded. Check sidebar_production.html and hori_sidebar_production.html

REM Check for syntax errors
ssh zubair@192.168.2.69 "python3 -c \"from django.template import Template; t=Template(open('/var/www/tradifyerp/templates/partials/sidebar.html').read()); print('sidebar.html: OK')\" 2>&1 || echo 'sidebar.html: ERROR'"
ssh zubair@192.168.2.69 "python3 -c \"from django.template import Template; t=Template(open('/var/www/tradifyerp/templates/partials/hori-sidebar.html').read()); print('hori-sidebar.html: OK')\" 2>&1 || echo 'hori-sidebar.html: ERROR'"

echo Template check complete
