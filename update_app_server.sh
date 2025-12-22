#!/bin/bash
# Script to update app server settings for new database IP

echo "=== Updating Django Settings for new Database IP ==="

# Update settings.py
if [ -f /var/www/tradifyerp/TradifyERP/settings.py ]; then
  sudo sed -i "s/'HOST': '192.168.2.59'/'HOST': '192.168.20.11'/g" /var/www/tradifyerp/TradifyERP/settings.py
  echo "✓ Updated /var/www/tradifyerp/TradifyERP/settings.py"
fi

# Update local_settings.py
if [ -f /var/www/tradifyerp/local_settings.py ]; then
  sudo sed -i "s/'HOST': '192.168.2.59'/'HOST': '192.168.20.11'/g" /var/www/tradifyerp/local_settings.py
  echo "✓ Updated /var/www/tradifyerp/local_settings.py"
fi

# Update local_settings_prod.py
if [ -f /var/www/tradifyerp/local_settings_prod.py ]; then
  sudo sed -i "s/'HOST': '192.168.2.59'/'HOST': '192.168.20.11'/g" /var/www/tradifyerp/local_settings_prod.py
  echo "✓ Updated /var/www/tradifyerp/local_settings_prod.py"
fi

echo ""
echo "=== Restarting Services ==="
sudo systemctl restart gunicorn && echo "✓ Gunicorn restarted"
sudo systemctl restart nginx && echo "✓ Nginx restarted"

echo ""
echo "=== Service Status ==="
sudo systemctl status gunicorn --no-pager | head -n 3
sudo systemctl status nginx --no-pager | head -n 3

echo ""
echo "=== App Server Update Complete ==="
