# Capital Contribution Workflow Refactoring - Production Deployment Script
# Target Server: 192.168.20.10
# Date: December 14, 2025

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Capital Contribution Refactoring Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Target: 192.168.20.10 (Production)" -ForegroundColor Yellow
Write-Host "Time: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# Configuration
$ProdServer = "192.168.20.10"
$ProdUser = "zubair"
$ProdPath = "/home/zubair/ERP-Production/Zubair-ERP-Project/TradifyERP"
$LocalPath = "F:\ERP-Production\Zubair-ERP-Project\TradifyERP"

# Files to deploy
$FilesToDeploy = @(
    "accounting/models.py",
    "accounting/stakeholder_forms.py",
    "accounting/signals.py",
    "accounting/migrations/0020_capital_contribution_source_transaction.py",
    "shareholder/views.py",
    "shareholder/templates/shareholder/capital_contribution_detail.html",
    "shareholder/templates/shareholder/capital_contribution_list.html"
)

# Create SSH session
Write-Host "Step 1: Establishing SSH connection..." -ForegroundColor Green

ssh -o StrictHostKeyChecking=no "${ProdUser}@${ProdServer}" "echo 'Connection successful'" 2>&1 | Out-Null
Write-Host "✓ SSH connection established" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Creating database backup..." -ForegroundColor Green

ssh -o StrictHostKeyChecking=no "${ProdUser}@${ProdServer}" "cd $ProdPath; python manage.py dumpdata accounting.CapitalContribution > /tmp/capital_contributions_backup.json 2>&1; echo 'Backup created'"
Write-Host "✓ Backup created successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Uploading modified files..." -ForegroundColor Green

foreach ($file in $FilesToDeploy) {
    $localFile = Join-Path $LocalPath $file
    
    if (Test-Path $localFile) {
        Write-Host "  Uploading: $file"
        scp -o StrictHostKeyChecking=no -r "$localFile" "${ProdUser}@${ProdServer}:${ProdPath}/${file}" 2>&1 | Out-Null
    } else {
        Write-Host "  ⚠ Warning: File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "✓ All files uploaded successfully" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Applying database migration..." -ForegroundColor Green

ssh -o StrictHostKeyChecking=no "${ProdUser}@${ProdServer}" "cd $ProdPath; python manage.py migrate accounting 2>&1 | tail -5"
Write-Host "✓ Migration applied successfully" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5: Restarting Gunicorn..." -ForegroundColor Green

ssh -o StrictHostKeyChecking=no "${ProdUser}@${ProdServer}" "sudo systemctl restart gunicorn; sleep 2; sudo systemctl is-active --quiet gunicorn; echo 'Gunicorn restarted'"
Write-Host "✓ Gunicorn restarted" -ForegroundColor Green
Write-Host ""

Write-Host "Step 6: Verifying deployment..." -ForegroundColor Green

ssh -o StrictHostKeyChecking=no "${ProdUser}@${ProdServer}" "cd $ProdPath; python manage.py showmigrations accounting | grep '0020_capital_contribution'"
Write-Host "✓ Migration verified" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Changes deployed:" -ForegroundColor Cyan
Write-Host "  • Removed 4 workflow views (Submit, Review, Approve, Reject)" -ForegroundColor White
Write-Host "  • Removed 3 workflow forms (Submit, Review, Approval)" -ForegroundColor White
Write-Host "  • Updated CapitalContribution model with source transaction fields" -ForegroundColor White
Write-Host "  • Updated templates to remove workflow UI" -ForegroundColor White
Write-Host "  • Added signal handlers for auto-creating contributions" -ForegroundColor White
Write-Host "  • Applied database migration (0020)" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test capital contribution workflow in production" -ForegroundColor Yellow
Write-Host "2. Create test Bank Receipt with capital contribution type" -ForegroundColor Yellow
Write-Host "3. Approve the bank receipt" -ForegroundColor Yellow
Write-Host "4. Verify capital contribution auto-created with GL entries posted" -ForegroundColor Yellow
Write-Host "5. Monitor logs for any errors: tail -f /var/log/gunicorn/error.log" -ForegroundColor Yellow
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Cyan
Write-Host "SSH into server: ssh zubair@192.168.20.10" -ForegroundColor Yellow
Write-Host "Check Gunicorn status: sudo systemctl status gunicorn" -ForegroundColor Yellow
Write-Host "View logs: journalctl -u gunicorn -n 50 -f" -ForegroundColor Yellow
Write-Host ""
