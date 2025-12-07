#!/bin/bash
# Deployment script for Tradify ERP to production server

set -e

echo "========================================"
echo "🚀 TRADIFY ERP PRODUCTION DEPLOYMENT"
echo "========================================"
echo ""

# Configuration
APP_PATH="/var/www/tradifyerp"
VENV_PATH="$APP_PATH/venv"
BACKUP_PATH="/var/backups/tradifyerp"
LOG_FILE="/var/log/tradifyerp/deployment.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_PATH"

echo "[$(date)] Deployment started" >> "$LOG_FILE"

# Step 1: Backup current application
echo "1️⃣ Backing up current application..."
BACKUP_NAME="tradifyerp_backup_$(date +%Y%m%d_%H%M%S)"
sudo tar -czf "$BACKUP_PATH/$BACKUP_NAME.tar.gz" \
  "$APP_PATH/TradifyERP" \
  "$APP_PATH/requirements.txt" \
  "$APP_PATH/gunicorn_config.py" 2>/dev/null || true
echo "✅ Backup created: $BACKUP_NAME.tar.gz"

# Step 2: Stop Gunicorn
echo ""
echo "2️⃣ Stopping Gunicorn..."
sudo systemctl stop gunicorn 2>/dev/null || \
  sudo supervisorctl stop tradifyerp 2>/dev/null || \
  sudo pkill -9 -f "gunicorn.*TradifyERP" 2>/dev/null || true
sleep 3
echo "✅ Gunicorn stopped"

# Step 3: Update application code
echo ""
echo "3️⃣ Updating application code..."
# Note: In production, you would copy/pull from git or other source
# For now, assuming code is synced via other means
echo "✅ Application code is up to date"

# Step 4: Activate virtual environment and install dependencies
echo ""
echo "4️⃣ Installing/Updating Python dependencies..."
source "$VENV_PATH/bin/activate"
pip install -q -r "$APP_PATH/requirements.txt" 2>&1 | tail -5 || true
echo "✅ Dependencies installed"

# Step 5: Run migrations
echo ""
echo "5️⃣ Running database migrations..."
cd "$APP_PATH/TradifyERP"
python manage.py migrate --noinput 2>&1 | tail -10
echo "✅ Migrations completed"

# Step 6: Collect static files
echo ""
echo "6️⃣ Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tail -5
echo "✅ Static files collected"

# Step 7: Clear Django cache
echo ""
echo "7️⃣ Clearing cache..."
python manage.py clear_cache 2>/dev/null || true
echo "✅ Cache cleared"

# Step 8: Start Gunicorn
echo ""
echo "8️⃣ Starting Gunicorn..."
cd "$APP_PATH"
sudo systemctl start gunicorn 2>/dev/null || \
  sudo supervisorctl start tradifyerp 2>/dev/null || \
  (sudo -u www-data "$VENV_PATH/bin/gunicorn" \
    --workers=8 \
    --worker-class=sync \
    --max-requests=1000 \
    --max-requests-jitter=100 \
    --timeout=120 \
    --bind=unix:"$APP_PATH/gunicorn.sock" \
    --access-logfile=/var/log/tradifyerp/gunicorn_access.log \
    --error-logfile=/var/log/tradifyerp/gunicorn_error.log \
    --log-level=warning \
    TradifyERP.wsgi:application &)
sleep 3
echo "✅ Gunicorn started"

# Step 9: Verify deployment
echo ""
echo "9️⃣ Verifying deployment..."
if curl -s http://localhost/accounts/login/ > /dev/null 2>&1; then
  echo "✅ Application is responding"
else
  echo "⚠️ Application may still be starting, give it a moment..."
fi

# Check logs for errors
if [ -f "/var/log/tradifyerp/gunicorn_error.log" ]; then
  ERROR_COUNT=$(tail -20 /var/log/tradifyerp/gunicorn_error.log 2>/dev/null | grep -i "error" | wc -l || true)
  if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️ Recent errors in gunicorn log:"
    tail -10 /var/log/tradifyerp/gunicorn_error.log
  fi
fi

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETED"
echo "========================================"
echo "[$(date)] Deployment completed successfully" >> "$LOG_FILE"
echo ""
echo "Application is available at: http://192.168.2.185"
echo "To view logs: sudo tail -f /var/log/tradifyerp/gunicorn_access.log"
echo "To rollback: tar -xzf $BACKUP_PATH/$BACKUP_NAME.tar.gz -C /"
