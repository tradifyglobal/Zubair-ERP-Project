#!/bin/bash
set -e

echo "Deploying fixed template files..."

# Deploy main sidebars
sudo cp /tmp/sidebar.html /var/www/tradifyerp/templates/partials/sidebar.html
sudo cp /tmp/hori-sidebar.html /var/www/tradifyerp/templates/partials/hori-sidebar.html

# Deploy accounting dashboard templates
sudo cp /tmp/dashboard.html /var/www/tradifyerp/accounting/templates/accounting/dashboard.html
sudo cp /tmp/dashboard_simple.html /var/www/tradifyerp/accounting/templates/accounting/dashboard_simple.html
sudo cp /tmp/gl_dashboard.html /var/www/tradifyerp/accounting/templates/accounting/gl_dashboard.html

# Also deploy to Minia if it exists
if [ -d /var/www/tradifyerp/Minia-Django/Admin/templates/partials ]; then
    sudo cp /tmp/sidebar.html /var/www/tradifyerp/Minia-Django/Admin/templates/partials/sidebar.html
    sudo cp /tmp/hori-sidebar.html /var/www/tradifyerp/Minia-Django/Admin/templates/partials/hori-sidebar.html
fi

echo "✓ Templates deployed"

echo ""
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo ""
echo "Waiting for Gunicorn to restart..."
sleep 3

echo ""
echo "Testing dashboard endpoint..."
curl -s -I http://localhost:8000/accounting/dashboard/ | head -1

echo ""
echo "✓ Deployment complete"
