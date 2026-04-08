#!/bin/bash
# Deploy Maintenance Asset GL Integration to Production

set -e

# Configuration
DEPLOY_HOST="192.168.20.10"
DEPLOY_USER="root"
DEPLOY_PATH="/var/www/tradifyerp"
VENV_PYTHON="$DEPLOY_PATH/venv/bin/python"
VENV_PIP="$DEPLOY_PATH/venv/bin/pip"

echo "=================================="
echo "Deploying Maintenance Asset GL Integration"
echo "=================================="

# Step 1: Push changes to Git
echo ""
echo "[1/6] Pushing changes to Git repository..."
git add -A
git commit -m "feat: Add GL posting for asset purchases from capital investment" || echo "No changes to commit"
git push origin changes

# Step 2: SSH and pull latest code
echo ""
echo "[2/6] Pulling latest code on production server..."
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && git fetch origin && git checkout changes && git pull origin changes"

# Step 3: Check Python path
echo ""
echo "[3/6] Verifying Python environment..."
ssh $DEPLOY_USER@$DEPLOY_HOST "$VENV_PYTHON --version"

# Step 4: Create migrations
echo ""
echo "[4/6] Creating database migrations..."
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && $VENV_PYTHON TradifyERP/manage.py makemigrations maintenance --noinput"

# Step 5: Apply migrations
echo ""
echo "[5/6] Applying migrations..."
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && $VENV_PYTHON TradifyERP/manage.py migrate maintenance --noinput"

# Step 6: Restart Gunicorn
echo ""
echo "[6/6] Restarting application..."
ssh $DEPLOY_USER@$DEPLOY_HOST "pkill -f gunicorn || true && sleep 2"
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && nohup $VENV_PYTHON TradifyERP/manage.py runserver_plus 0.0.0.0:8000 2>&1 > /var/log/gunicorn.log &" || \
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && nohup $VENV_PYTHON -m gunicorn --workers 4 --bind unix:/tmp/gunicorn.sock TradifyERP.wsgi:application 2>&1 > /var/log/gunicorn.log &"

echo ""
echo "✓ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Visit http://192.168.20.10/maintenance/assets/new/"
echo "2. You should now see 'Purchase Account' field"
echo "3. Select the account from which the asset was purchased"
echo "4. GL entries will be automatically posted"
