# Deploy Enhanced Cash Position Dashboard (PowerShell)

$ErrorActionPreference = "Stop"

$SERVER_IP = "192.168.20.10"
$SERVER_USER = "root"
$APP_PATH = "/var/www/tradifyerp"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Deploying Cash Position Enhancements" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Pull latest code
Write-Host "`n1. Pulling latest code from Git..." -ForegroundColor Yellow
ssh root@192.168.20.10 "cd /var/www/tradifyerp && git pull origin ERP-Enhancements 2>&1 | tail -10"

# Collect static files
Write-Host "`n2. Collecting static files..." -ForegroundColor Yellow
ssh root@192.168.20.10 "cd /var/www/tradifyerp && source venv/bin/activate && python manage.py collectstatic --noinput 2>&1 | tail -5"

# Clear cache
Write-Host "`n3. Clearing Django cache..." -ForegroundColor Yellow
ssh root@192.168.20.10 "cd /var/www/tradifyerp && source venv/bin/activate && python manage.py shell -c 'from django.core.cache import cache; cache.clear()' 2>&1"

# Restart services
Write-Host "`n4. Restarting services..." -ForegroundColor Yellow
ssh root@192.168.20.10 "systemctl restart tradifyerp-gunicorn && systemctl restart tradifyerp-nginx"

# Verify deployment
Write-Host "`n5. Verifying deployment..." -ForegroundColor Yellow
ssh root@192.168.20.10 "curl -s http://localhost/cash/positions/ | grep 'Cash Position' > /dev/null && echo '✓ Dashboard accessible' || echo '✗ Dashboard not accessible'"

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "✓ Deployment Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "`n📊 NEW FEATURES DEPLOYED:" -ForegroundColor Green
Write-Host "  ✓ Operational Decision-Making Section"
Write-Host "  ✓ Payment Release Recommendations"
Write-Host "  ✓ Fund Transfer Suggestions"
Write-Host "  ✓ Borrowing/Repayment Indicators"
Write-Host "  ✓ Payroll Coverage Analysis"
Write-Host "  ✓ 7-Day & 30-Day Cash Forecasting"
Write-Host "  ✓ Compliance Checklist (6 metrics)"
Write-Host "  ✓ Automation Workflow Triggers"
Write-Host "  ✓ Daily Treasury Workflow"
Write-Host "`nAccess the dashboard at: http://192.168.20.10/cash/positions/" -ForegroundColor Green
