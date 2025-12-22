#!/bin/bash
set -e

echo "=== Fixing Trial Balance URL References in Dashboard ==="

# Copy the fixed dashboard.html to production
echo "Deploying fixed dashboard.html..."
pscp -pw erp "TradifyERP/accounting/templates/accounting/dashboard.html" zubair@192.168.20.10:/tmp/dashboard_fixed.html

# Deploy to production
plink -ssh -l zubair -pw erp 192.168.20.10 << 'EOF'
echo "Copying dashboard.html to production..."
sudo cp /tmp/dashboard_fixed.html /var/www/tradifyerp/templates/accounting/dashboard.html
sudo chown www-data:www-data /var/www/tradifyerp/templates/accounting/dashboard.html

echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn
sleep 2

echo "Verifying fix..."
curl -s 'http://localhost:8000/accounting/dashboard/' 2>&1 | grep -i 'noreverse' || echo "✓ No NoReverseMatch errors detected"
echo "✓ Deployment complete"
EOF
