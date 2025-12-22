#!/bin/bash
set -e

echo "Deploying fixed Trial Balance templates..."
sudo cp /tmp/trial_balance_*.html /var/www/tradifyerp/templates/accounting/

echo ""
echo "Verifying deployment..."
ls -lh /var/www/tradifyerp/templates/accounting/trial_balance*.html | wc -l
echo "Templates deployed"

echo ""
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo ""
echo "Waiting for Gunicorn to restart..."
sleep 3

echo ""
echo "Testing endpoints..."
echo "1. Trial Balance List:"
curl -s -I http://localhost:8000/accounting/trial-balance/ | grep HTTP

echo ""
echo "2. Trial Balance Dashboard:"
curl -s -I http://localhost:8000/accounting/trial-balance-dashboard/ | grep HTTP

echo ""
echo "✓ Templates deployed and services restarted successfully"
