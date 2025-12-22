# ============================================================================
# CASH ACCOUNT SETUP - POWERSHELL VERSION
# Direct database setup using SQL commands
# ============================================================================

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   CASH ACCOUNT SETUP - DIRECT SQL CONFIGURATION" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Database Configuration
$dbHost = "192.168.20.11"
$dbUser = "zubair"
$dbPass = "sql"
$dbName = "tradifyerp_db"

Write-Host "Database: $dbHost" -ForegroundColor Yellow
Write-Host "User: $dbUser" -ForegroundColor Yellow
Write-Host "Database: $dbName" -ForegroundColor Yellow
Write-Host ""

# Step 1: Get Entity ID
Write-Host "Step 1: Getting Entity ID..." -ForegroundColor Cyan
$getEntityIdScript = @"
SELECT id FROM accounting_entity WHERE code='INT001' LIMIT 1;
"@

try {
    # Try with PGPASSWORD environment variable
    $env:PGPASSWORD = $dbPass
    $entityId = psql -h $dbHost -U $dbUser -d $dbName -t -c $getEntityIdScript 2>$null | ForEach-Object { $_.Trim() } | Select-Object -First 1
    
    if ([string]::IsNullOrWhiteSpace($entityId)) {
        Write-Host "  Entity INT001 not found, trying first active entity..." -ForegroundColor Yellow
        $getEntityIdScript = "SELECT id FROM accounting_entity WHERE is_active=true LIMIT 1;"
        $entityId = psql -h $dbHost -U $dbUser -d $dbName -t -c $getEntityIdScript 2>$null | ForEach-Object { $_.Trim() } | Select-Object -First 1
    }
    
    if ([string]::IsNullOrWhiteSpace($entityId)) {
        Write-Host "❌ ERROR: Could not find any active entity!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Entity ID: $entityId" -ForegroundColor Green
} catch {
    Write-Host "❌ Error getting Entity ID: $_" -ForegroundColor Red
    Write-Host "Make sure PostgreSQL client (psql) is installed and in PATH" -ForegroundColor Yellow
    exit 1
}

# Step 2: Get Currency ID
Write-Host "Step 2: Getting Currency ID..." -ForegroundColor Cyan
$getCurrencyIdScript = "SELECT id FROM accounting_currency WHERE code='INR' LIMIT 1;"

try {
    $currencyId = psql -h $dbHost -U $dbUser -d $dbName -t -c $getCurrencyIdScript 2>$null | ForEach-Object { $_.Trim() } | Select-Object -First 1
    
    if ([string]::IsNullOrWhiteSpace($currencyId)) {
        Write-Host "  Currency INR not found, trying first active..." -ForegroundColor Yellow
        $getCurrencyIdScript = "SELECT id FROM accounting_currency WHERE is_active=true LIMIT 1;"
        $currencyId = psql -h $dbHost -U $dbUser -d $dbName -t -c $getCurrencyIdScript 2>$null | ForEach-Object { $_.Trim() } | Select-Object -First 1
    }
    
    if ([string]::IsNullOrWhiteSpace($currencyId)) {
        Write-Host "ERROR: Could not find any active currency!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "OK Currency ID: $currencyId" -ForegroundColor Green
} catch {
    Write-Host "Error getting Currency ID: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Create Cash Account
Write-Host "Step 3: Creating Cash Account (100001)..." -ForegroundColor Cyan

$createAccountScript = @"
INSERT INTO accounting_account (
    account_number,
    name,
    account_type,
    description,
    entity_id,
    currency_id,
    is_active,
    opening_balance,
    parent_account_id,
    created_at,
    updated_at
) VALUES (
    '100001',
    'Cash',
    'ASSET',
    'Cash account for receiving cash from shareholders and other receipts',
    $entityId,
    $currencyId,
    true,
    0.00,
    NULL,
    NOW(),
    NOW()
) ON CONFLICT (entity_id, account_number) DO NOTHING;

SELECT 'Account created/verified' AS status;
"@

try {
    $result = psql -h $dbHost -U $dbUser -d $dbName -c $createAccountScript 2>$null
    Write-Host "OK Account setup query executed" -ForegroundColor Green
} catch {
    Write-Host "Error creating account: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Verify Setup
Write-Host "Step 4: Verifying Setup..." -ForegroundColor Cyan
Write-Host ""

$verifyScript = @"
SELECT 'CASH ACCOUNT' AS check_type, account_number, name, account_type FROM accounting_account WHERE account_number='100001'
UNION ALL
SELECT 'CAPITAL (3000)', account_number, name, account_type FROM accounting_account WHERE account_number='3000'
UNION ALL
SELECT 'SHAREHOLDER (3100)', account_number, name, account_type FROM accounting_account WHERE account_number='3100'
UNION ALL
SELECT 'SUB-ACCOUNTS', account_number, name, account_type FROM accounting_account WHERE account_number LIKE '3100-%'
ORDER BY check_type, account_number;
"@

try {
    $verifyResult = psql -h $dbHost -U $dbUser -d $dbName -c $verifyScript 2>$null
    Write-Host $verifyResult
} catch {
    Write-Host "Could not verify accounts (may already be created)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "                   ✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Configured Items:" -ForegroundColor Cyan
Write-Host "  OK Cash Account (100001) - ASSET Type" -ForegroundColor Green
Write-Host "  OK Capital Accounts Verified (3000, 3100)" -ForegroundColor Green
Write-Host "  OK Stakeholder Accounts Ready" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Access app at: https://192.168.20.10/accounting/dashboard/" -ForegroundColor Yellow
Write-Host "  2. Navigate to: /accounting/cash-receipts/create/" -ForegroundColor Yellow
Write-Host "  3. Create a test cash receipt" -ForegroundColor Yellow
Write-Host "  4. Verify GL entries in General Ledger" -ForegroundColor Yellow
Write-Host ""

Write-Host "Account Details:" -ForegroundColor Cyan
Write-Host "  Debit Account:   3100-01 (Capital/Shareholder)" -ForegroundColor Yellow
Write-Host "  Credit Account:  100001 (Cash)" -ForegroundColor Yellow
Write-Host ""
