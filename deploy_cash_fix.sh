#!/bin/bash
# Deploy cash position fix to production

echo "Deploying cash position fix..."
echo "Step 1: Copying models.py to production..."

# Copy the file
cp /tmp/models_fixed.py /var/www/tradifyerp/TradifyERP/accounting/models.py

if [ $? -eq 0 ]; then
    echo "✓ File copied successfully"
else
    echo "✗ File copy failed"
    exit 1
fi

echo "Step 2: Restarting Gunicorn..."
systemctl restart gunicorn

if [ $? -eq 0 ]; then
    echo "✓ Gunicorn restarted successfully"
    echo ""
    echo "DEPLOYMENT COMPLETE!"
    echo "The cash position fix has been deployed."
    echo ""
    echo "Next: Test by creating and authorizing a new cash receipt"
else
    echo "✗ Gunicorn restart failed"
    exit 1
fi
