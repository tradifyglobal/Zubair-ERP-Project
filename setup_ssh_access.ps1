# Passwordless SSH Setup Script for Windows

Write-Host "=== Passwordless SSH Setup ===" -ForegroundColor Green
Write-Host ""

# Get public key
$pubKeyPath = "$env:USERPROFILE\.ssh\id_rsa.pub"
$pubKey = Get-Content $pubKeyPath

Write-Host "Your public key has been loaded." -ForegroundColor Cyan
Write-Host ""

# App Server Setup
Write-Host ">>> Setting up App Server (192.168.20.10) <<<" -ForegroundColor Yellow
Write-Host "When prompted, enter password: erp"
Write-Host ""

$appServerCmd = @"
mkdir -p ~/.ssh 2>/dev/null; 
cat >> ~/.ssh/authorized_keys << 'EOF'
$pubKey
EOF
chmod 600 ~/.ssh/authorized_keys 2>/dev/null;
echo 'Public key installed successfully!'
"@

ssh root@192.168.20.10 $appServerCmd

Write-Host ""
Write-Host ">>> Setting up DB Server (192.168.20.11) <<<" -ForegroundColor Yellow
Write-Host "When prompted, enter password: sql"
Write-Host ""

$dbServerCmd = @"
mkdir -p ~/.ssh 2>/dev/null;
cat >> ~/.ssh/authorized_keys << 'EOF'
$pubKey
EOF
chmod 600 ~/.ssh/authorized_keys 2>/dev/null;
echo 'Public key installed successfully!'
"@

ssh zubair@192.168.20.11 $dbServerCmd

Write-Host ""
Write-Host "=== Verifying Setup ===" -ForegroundColor Green
Write-Host ""

Write-Host "Testing App Server connection..." -ForegroundColor Cyan
ssh root@192.168.20.10 "echo 'SUCCESS: Connected to App Server (192.168.20.10)'"

Write-Host ""
Write-Host "Testing DB Server connection..." -ForegroundColor Cyan
ssh zubair@192.168.20.11 "echo 'SUCCESS: Connected to DB Server (192.168.20.11)'"

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "You can now connect without entering passwords:" -ForegroundColor Yellow
Write-Host "  ssh root@192.168.20.10"
Write-Host "  ssh zubair@192.168.20.11"
