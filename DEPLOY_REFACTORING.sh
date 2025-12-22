#!/bin/bash
# Capital Contribution Workflow Refactoring - Production Deployment Script
# Deployment Date: $(date)
# Target Server: 192.168.20.10

set -e  # Exit on any error

echo "========================================"
echo "Capital Contribution Refactoring Deploy"
echo "========================================"
echo "Target: 192.168.20.10 (Production)"
echo "Time: $(date)"
echo ""

# Configuration
PROD_SERVER="192.168.20.10"
PROD_USER="zubair"
PROD_PASSWORD="erp"
PROD_PATH="/home/zubair/ERP-Production/Zubair-ERP-Project/TradifyERP"
LOCAL_PATH="/f:/ERP-Production/Zubair-ERP-Project/TradifyERP"

# Files to deploy
FILES_TO_DEPLOY=(
    "accounting/models.py"
    "accounting/stakeholder_forms.py"
    "accounting/signals.py"
    "accounting/migrations/0020_capital_contribution_source_transaction.py"
    "shareholder/views.py"
    "shareholder/templates/shareholder/capital_contribution_detail.html"
    "shareholder/templates/shareholder/capital_contribution_list.html"
)

echo "Step 1: Creating backup..."
ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_SERVER} << 'EOF'
# Create backup of database before migration
cd /home/zubair/ERP-Production/Zubair-ERP-Project/TradifyERP
python manage.py dumpdata accounting.CapitalContribution > /tmp/capital_contributions_backup.json
echo "✓ Capital Contribution data backed up to /tmp/capital_contributions_backup.json"
EOF

echo ""
echo "Step 2: Uploading modified files..."

# Copy files via SCP with password
for file in "${FILES_TO_DEPLOY[@]}"; do
    echo "Uploading: $file"
    scp -o StrictHostKeyChecking=no "${LOCAL_PATH}/${file}" ${PROD_USER}@${PROD_SERVER}:${PROD_PATH}/${file}
done

echo ""
echo "✓ All files uploaded successfully"
echo ""

echo "Step 3: Applying database migration..."
ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_SERVER} << 'EOF'
cd /home/zubair/ERP-Production/Zubair-ERP-Project/TradifyERP

# Apply migrations
echo "Running: python manage.py migrate accounting 0020_capital_contribution_source_transaction"
python manage.py migrate accounting

if [ $? -eq 0 ]; then
    echo "✓ Migration applied successfully"
else
    echo "✗ Migration failed - please check the logs"
    exit 1
fi
EOF

echo ""
echo "Step 4: Restarting Gunicorn..."
ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_SERVER} << 'EOF'
# Restart Gunicorn to load new code
sudo systemctl restart gunicorn

# Wait for service to start
sleep 3

# Check status
if sudo systemctl is-active --quiet gunicorn; then
    echo "✓ Gunicorn restarted successfully"
else
    echo "✗ Gunicorn failed to start"
    sudo systemctl status gunicorn
    exit 1
fi
EOF

echo ""
echo "Step 5: Verifying deployment..."
ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_SERVER} << 'EOF'
cd /home/zubair/ERP-Production/Zubair-ERP-Project/TradifyERP

# Check if application is responding
curl -s http://localhost:8000/accounting/ > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Application responding normally"
else
    echo "⚠ Warning: Could not verify application response"
fi

# Verify migration was applied
python manage.py showmigrations accounting | grep "0020_capital_contribution_source_transaction"
if [ $? -eq 0 ]; then
    echo "✓ Migration verified in database"
fi
EOF

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY"
echo "========================================"
echo ""
echo "Changes deployed:"
echo "  • Removed 4 workflow views (Submit, Review, Approve, Reject)"
echo "  • Removed 3 workflow forms (Submit, Review, Approval)"
echo "  • Updated CapitalContribution model with source transaction fields"
echo "  • Updated templates to remove workflow UI"
echo "  • Added signal handlers for auto-creating contributions"
echo "  • Applied database migration (0020)"
echo ""
echo "Next steps:"
echo "1. Test capital contribution workflow in browser"
echo "2. Create test Bank Receipt as capital investment"
echo "3. Approve the bank receipt"
echo "4. Verify capital contribution auto-created"
echo "5. Monitor application logs for any errors"
echo ""
echo "Rollback procedure (if needed):"
echo "  python manage.py migrate accounting 0019"
echo "  # Then restore from backup:"
echo "  python manage.py loaddata /tmp/capital_contributions_backup.json"
echo ""
