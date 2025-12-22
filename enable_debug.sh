#!/bin/bash
# Enable Django DEBUG mode temporarily

# Backup current settings
sudo cp /var/www/tradifyerp/tradifyerp/settings.py /var/www/tradifyerp/tradifyerp/settings.py.backup

# Enable DEBUG
sudo sed -i 's/DEBUG = False/DEBUG = True/g' /var/www/tradifyerp/tradifyerp/settings.py

# Also ensure ALLOWED_HOSTS includes the domain
sudo sed -i "s/ALLOWED_HOSTS = \[/ALLOWED_HOSTS = ['tradifyglobal.com', '192.168.2.69', /g" /var/www/tradifyerp/tradifyerp/settings.py

# Restart Gunicorn
sudo systemctl restart gunicorn

echo "DEBUG mode enabled. Settings backed up to settings.py.backup"
echo "Remember to disable DEBUG after fixing the issue!"
