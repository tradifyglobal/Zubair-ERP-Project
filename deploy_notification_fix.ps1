# Deploy expense notification fixes to production
# Run this PowerShell script to deploy the fixes

$SERVER = "192.168.2.185"
$USER = "root"
$REMOTE_PATH = "/var/www/tradifyerp/TradifyERP"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Expense Notification Fixes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if scp is available
if (-not (Get-Command scp -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: scp command not found. Make sure OpenSSH is installed." -ForegroundColor Red
    exit 1
}

Write-Host "Copying files to $SERVER..." -ForegroundColor Yellow
Write-Host ""

# Copy notifications.py
Write-Host "[1/2] Copying notifications.py..." -ForegroundColor Yellow
scp "TradifyERP\expenses\notifications.py" "${USER}@${SERVER}:${REMOTE_PATH}/expenses/"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ notifications.py copied successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to copy notifications.py" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Copy context_processors.py
Write-Host "[2/2] Copying context_processors.py..." -ForegroundColor Yellow
scp "TradifyERP\expenses\context_processors.py" "${USER}@${SERVER}:${REMOTE_PATH}/expenses/"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ context_processors.py copied successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to copy context_processors.py" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Files deployed. Restarting Gunicorn..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Restart Gunicorn
ssh ${USER}@${SERVER} "systemctl restart gunicorn"

Write-Host ""
Write-Host "Checking Gunicorn status..." -ForegroundColor Yellow
ssh ${USER}@${SERVER} "systemctl status gunicorn | grep Active"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Deployment complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Have Burhan clear his browser cache (Ctrl+Shift+Delete)" 
Write-Host "2. Logout and login again"
Write-Host "3. Check bell icon - should show notification"
Write-Host ""
