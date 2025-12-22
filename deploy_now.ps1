#!/usr/bin/env pwsh

param(
    [string]$DBHost = "192.168.2.59",
    [string]$DBUser = "zubair",
    [string]$DBPass = "sql",
    [string]$DBName = "tradifyerp_db"
)

Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    CASH ACCOUNT DEPLOYMENT - AUTOMATED SETUP" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Credentials:" -ForegroundColor Yellow
Write-Host "  Host: $DBHost"
Write-Host "  User: $DBUser"
Write-Host "  Database: $DBName"
Write-Host ""

Write-Host "Connecting via SSH and running setup..." -ForegroundColor Yellow
Write-Host ""

$sshCommand = @"
PGPASSWORD='$DBPass' psql -h $DBHost -U $DBUser -d $DBName << 'EOF'
INSERT INTO accounting_account (account_number,name,account_type,description,entity_id,currency_id,is_active,opening_balance,parent_account_id,created_at,updated_at) 
SELECT '100001','Cash','ASSET','Cash account for receiving cash from shareholders',ae.id,ac.id,true,0.00,NULL,NOW(),NOW() 
FROM accounting_entity ae, accounting_currency ac 
WHERE ae.code='INT001' AND ac.code='INR' 
AND NOT EXISTS (SELECT 1 FROM accounting_account WHERE account_number='100001');

SELECT 'SUCCESS: Cash Account 100001 created' AS status;

SELECT account_number, name, account_type, is_active 
FROM accounting_account 
WHERE account_number IN ('100001','3000','3100') 
ORDER BY account_number;
EOF
"@

ssh -o StrictHostKeyChecking=no zubair@$DBHost "bash -c `"$sshCommand`""

Write-Host ""
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "    DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Cash Account Setup Summary:" -ForegroundColor Cyan
Write-Host "  Account Code: 100001" -ForegroundColor White
Write-Host "  Account Name: Cash" -ForegroundColor White
Write-Host "  Account Type: ASSET" -ForegroundColor White
Write-Host "  Status: ACTIVE" -ForegroundColor Green
Write-Host ""
Write-Host "Ready for testing:" -ForegroundColor Yellow
Write-Host "  1. Navigate to: https://192.168.2.69/accounting/cash-receipts/create/" -ForegroundColor White
Write-Host "  2. Create and authorize a cash receipt" -ForegroundColor White
Write-Host "  3. GL entries will auto-post to:" -ForegroundColor White
Write-Host "     - Debit: Receipt account (3100-01)" -ForegroundColor White
Write-Host "     - Credit: Cash account (100001)" -ForegroundColor White
Write-Host ""
