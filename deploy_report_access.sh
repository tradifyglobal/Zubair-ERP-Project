#!/bin/bash
# Deployment script for Report Access Control Feature
# Run on production server: 192.168.20.10

echo "🚀 Deploying Report Access Control Feature..."
echo "================================================"

# Variables
DEPLOY_PATH="/var/www/tradifyerp"
VENV_PATH="$DEPLOY_PATH/venv"
PYTHON="$VENV_PATH/bin/python"
MANAGE="$PYTHON $DEPLOY_PATH/manage.py"

# Step 1: Stop gunicorn
echo "1️⃣  Stopping gunicorn..."
sudo killall -9 gunicorn 2>/dev/null || true
sleep 2

# Step 2: Pull latest changes
echo "2️⃣  Pulling latest code..."
cd $DEPLOY_PATH
git pull origin ERP-Enhancements || {
    echo "❌ Git pull failed"
    exit 1
}

# Step 3: Install/update Python dependencies (if any new ones)
echo "3️⃣  Checking dependencies..."
$PYTHON -m pip install -q --upgrade pip django 2>/dev/null || true

# Step 4: Run migrations
echo "4️⃣  Running database migrations..."
sudo -u www-data $MANAGE makemigrations accounting || true
sudo -u www-data $MANAGE migrate accounting || {
    echo "⚠️  Migration warning (may already exist)"
}

# Step 5: Clear cache
echo "5️⃣  Clearing caches..."
sudo find $DEPLOY_PATH -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
sudo find $DEPLOY_PATH -name '*.pyc' -delete 2>/dev/null || true
sudo rm -rf $DEPLOY_PATH/staticfiles/CACHE/* 2>/dev/null || true

# Step 6: Collect static files (if needed)
echo "6️⃣  Running collectstatic..."
sudo -u www-data $MANAGE collectstatic --noinput 2>/dev/null || true

# Step 7: Start gunicorn
echo "7️⃣  Starting gunicorn..."
cd $DEPLOY_PATH
nohup $VENV_PATH/bin/gunicorn \
    --workers 5 \
    --bind 127.0.0.1:8000 \
    --timeout 300 \
    --env DJANGO_SETTINGS_MODULE=TradifyERP.settings_production \
    TradifyERP.wsgi:application > $DEPLOY_PATH/gunicorn.log 2>&1 &

sleep 2

# Step 8: Verify
echo "8️⃣  Verifying deployment..."
PROC_COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
if [ $PROC_COUNT -ge 5 ]; then
    echo "✅ Gunicorn running ($PROC_COUNT processes)"
else
    echo "⚠️  Warning: Fewer processes than expected ($PROC_COUNT)"
fi

echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Log in to Django admin: /admin/accounting/reportaccess/"
echo "2. Create ReportAccess records to restrict reports"
echo "3. OR use management command:"
echo "   python manage.py assign_report_access --help"
echo ""
echo "📖 Documentation: REPORT_ACCESS_CONTROL.md"
echo "================================================"
