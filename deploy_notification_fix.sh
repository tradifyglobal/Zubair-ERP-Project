#!/bin/bash
# Deploy expense notification fixes to production

echo "========================================"
echo "Deploying Expense Notification Fixes"
echo "========================================"
echo ""

SERVER_IP="192.168.2.185"
SERVER_USER="root"
REMOTE_PATH="/var/www/tradifyerp/TradifyERP"

echo "Copying files to production server..."
echo ""

# Copy notifications.py
echo "[1/2] Copying notifications.py..."
scp TradifyERP/expenses/notifications.py ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/expenses/
if [ $? -eq 0 ]; then
    echo "✓ notifications.py copied successfully"
else
    echo "✗ Failed to copy notifications.py"
    exit 1
fi

echo ""

# Copy context_processors.py  
echo "[2/2] Copying context_processors.py..."
scp TradifyERP/expenses/context_processors.py ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/expenses/
if [ $? -eq 0 ]; then
    echo "✓ context_processors.py copied successfully"
else
    echo "✗ Failed to copy context_processors.py"
    exit 1
fi

echo ""
echo "========================================"
echo "Files deployed. Restarting Gunicorn..."
echo "========================================"
echo ""

ssh ${SERVER_USER}@${SERVER_IP} systemctl restart gunicorn

echo ""
echo "========================================"
echo "Restart status:"
ssh ${SERVER_USER}@${SERVER_IP} systemctl status gunicorn | grep Active

echo ""
echo "✓ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Have Burhan clear his browser cache (Ctrl+Shift+Delete)"
echo "2. Logout and login again"
echo "3. Check bell icon - should show notification count"
echo ""
