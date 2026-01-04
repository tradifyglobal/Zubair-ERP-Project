#!/bin/bash

# Vendor Code Auto-Generation Deployment Script
# Deploys commit fa43386 to production server 192.168.20.10
# Date: $(date)
# Purpose: Auto-generate vendor codes on /accounting/quick-add-vendor/ page

set -e

PROD_SERVER="192.168.20.10"
PROD_USER="zubair"
PROD_PATH="/var/www/tradifyerp"
PROD_VENV="$PROD_PATH/venv"
COMMIT="fa43386"

echo "======================================"
echo "Vendor Code Auto-Generation Deployment"
echo "======================================"
echo "Target Server: $PROD_SERVER"
echo "Commit: $COMMIT"
echo "Target Path: $PROD_PATH"
echo ""

# 1. Pull latest changes on production server
echo "[1/5] Pulling latest changes from GitHub..."
ssh $PROD_USER@$PROD_SERVER "cd $PROD_PATH && git fetch origin && git checkout $COMMIT"
echo "✓ Code updated to commit $COMMIT"

# 2. Collect static files
echo ""
echo "[2/5] Collecting static files..."
ssh $PROD_USER@$PROD_SERVER "cd $PROD_PATH && source $PROD_VENV/bin/activate && python TradifyERP/manage.py collectstatic --noinput"
echo "✓ Static files collected"

# 3. Restart Gunicorn
echo ""
echo "[3/5] Restarting Gunicorn service..."
ssh $PROD_USER@$PROD_SERVER "sudo systemctl restart tradifyerp"
echo "✓ Gunicorn restarted"

# 4. Verify deployment
echo ""
echo "[4/5] Verifying deployment..."
ssh $PROD_USER@$PROD_SERVER "curl -s -k https://192.168.20.10/accounting/quick-add-vendor/ | grep -q 'Quick Add Vendor' && echo 'Page loads successfully' || echo 'Warning: Page may not be loading'"
echo "✓ Deployment verification complete"

# 5. Check logs
echo ""
echo "[5/5] Checking service logs..."
ssh $PROD_USER@$PROD_SERVER "sudo journalctl -u tradifyerp -n 20 --no-pager"
echo ""
echo "======================================"
echo "✓ Deployment Complete!"
echo "======================================"
echo ""
echo "Feature Details:"
echo "- Auto-generates vendor codes in VEND-XXXX format"
echo "- Sequential numbering per entity"
echo "- Read-only field with Edit override option"
echo "- API endpoint: /accounting/api/generate-vendor-code/"
echo ""
echo "Test the feature:"
echo "1. Navigate to https://192.168.20.10/accounting/quick-add-vendor/"
echo "2. Verify vendor code auto-generates on page load"
echo "3. Fill in Vendor Name and Currency"
echo "4. Submit form to create vendor"
echo "5. Repeat to verify sequential code generation"
echo ""
echo "To rollback if needed:"
echo "  ssh $PROD_USER@$PROD_SERVER 'cd $PROD_PATH && git checkout cf94ef7 && sudo systemctl restart tradifyerp'"
echo ""
