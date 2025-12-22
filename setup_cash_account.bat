@echo off
REM ============================================================================
REM CASH ACCOUNT SETUP - BATCH SCRIPT FOR WINDOWS
REM Uses psql to connect to PostgreSQL database
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo CASH ACCOUNT SETUP
echo ========================================
echo Database: 192.168.20.11
echo User: zubair
echo Database: tradifyerp_db
echo.

set DB_HOST=192.168.20.11
set DB_USER=zubair
set DB_PASS=sql
set DB_NAME=tradifyerp_db

echo Step 1: Creating Cash Account...
echo.

set PGPASSWORD=%DB_PASS%

REM Create Cash Account
psql -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -c "INSERT INTO accounting_account (account_number, name, account_type, description, entity_id, currency_id, is_active, opening_balance, parent_account_id, created_at, updated_at) SELECT '100001', 'Cash', 'ASSET', 'Cash account for receiving cash from shareholders', entity_id, currency_id, true, 0.00, NULL, NOW(), NOW() FROM (SELECT DISTINCT entity_id, currency_id FROM accounting_account LIMIT 1) AS src WHERE NOT EXISTS (SELECT 1 FROM accounting_account WHERE account_number='100001');"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Account setup completed
) else (
    echo [WARNING] Account may already exist or error occurred
)

echo.
echo Step 2: Verifying Setup...
echo.

REM Verify Cash Account
psql -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -c "SELECT account_number, name, account_type FROM accounting_account WHERE account_number IN ('100001','3000','3100') ORDER BY account_number;"

echo.
echo ========================================
echo SETUP COMPLETE
echo ========================================
echo.
echo Next Steps:
echo   1. Navigate to app: https://192.168.20.10/accounting/dashboard/
echo   2. Go to: /accounting/cash-receipts/create/
echo   3. Create a test cash receipt
echo.
echo Accounts configured:
echo   - 100001: Cash (Asset)
echo   - 3100-01: Capital Account
echo.

endlocal
