#!/bin/bash
set -e

echo "Deploying fixed urls.py..."
sudo cp /tmp/urls_fixed.py /var/www/tradifyerp/accounting/urls.py

echo ""
echo "Verifying deployment..."
echo "1. Checking urls_trial_balance import..."
grep -c "urls_trial_balance" /var/www/tradifyerp/accounting/urls.py && echo "   ✓ Found"

echo "2. Checking old route is commented..."
grep -c "^    # path('trial-balances/'" /var/www/tradifyerp/accounting/urls.py && echo "   ✓ Commented"

echo ""
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo ""
echo "Waiting for Gunicorn to restart..."
sleep 3

echo ""
echo "Testing endpoint..."
curl -s -w "\nHTTP Status: %{http_code}\n" http://localhost:8000/accounting/trial-balances/ | head -15

echo ""
echo "✓ Deployment complete"
