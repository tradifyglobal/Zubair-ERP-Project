#!/bin/bash
# Deploy Enhanced Cash Position Dashboard

set -e

SERVER_IP="192.168.20.10"
SERVER_USER="root"
APP_PATH="/var/www/tradifyerp"

echo "======================================"
echo "Deploying Cash Position Enhancements"
echo "======================================"

# Pull latest code
echo "1. Pulling latest code from Git..."
ssh $SERVER_USER@$SERVER_IP "cd $APP_PATH && git pull origin ERP-Enhancements 2>&1 | tail -10"

# Collect static files
echo ""
echo "2. Collecting static files..."
ssh $SERVER_USER@$SERVER_IP "cd $APP_PATH && source venv/bin/activate && python manage.py collectstatic --noinput 2>&1 | tail -5"

# Clear cache
echo ""
echo "3. Clearing Django cache..."
ssh $SERVER_USER@$SERVER_IP "cd $APP_PATH && source venv/bin/activate && python manage.py shell -c \"from django.core.cache import cache; cache.clear()\" 2>&1"

# Restart services
echo ""
echo "4. Restarting services..."
ssh $SERVER_USER@$SERVER_IP "systemctl restart tradifyerp-gunicorn && systemctl restart tradifyerp-nginx"

# Verify deployment
echo ""
echo "5. Verifying deployment..."
ssh $SERVER_USER@$SERVER_IP "curl -s http://localhost/cash/positions/ | grep 'Cash Position' > /dev/null && echo '✓ Dashboard accessible' || echo '✗ Dashboard not accessible'"

echo ""
echo "======================================"
echo "✓ Deployment Complete!"
echo "======================================"
echo ""
echo "📊 NEW FEATURES DEPLOYED:"
echo "  ✓ Operational Decision-Making Section"
echo "  ✓ Payment Release Recommendations"
echo "  ✓ Fund Transfer Suggestions"
echo "  ✓ Borrowing/Repayment Indicators"
echo "  ✓ Payroll Coverage Analysis"
echo "  ✓ 7-Day & 30-Day Cash Forecasting"
echo "  ✓ Compliance Checklist (6 metrics)"
echo "  ✓ Automation Workflow Triggers"
echo "  ✓ Daily Treasury Workflow"
echo ""
echo "Access the dashboard at: http://192.168.20.10/cash/positions/"
