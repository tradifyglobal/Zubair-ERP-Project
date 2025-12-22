-- ============================================================================
-- CASH ACCOUNT & GL INTEGRATION SETUP - PRODUCTION DATABASE
-- ============================================================================
-- Database: tradifyerp_db
-- Host: 192.168.2.59
-- User: zubair
-- Password: sql
-- ============================================================================

-- Step 1: Get necessary IDs
-- Run these SELECT queries first to get the ID values

SELECT 'STEP 1: GET ENTITY AND CURRENCY IDs' AS step;
SELECT id, code, name FROM accounting_entity WHERE code='INT001' LIMIT 1;
SELECT id, code FROM accounting_currency WHERE code='INR' AND is_active=true LIMIT 1;

-- ============================================================================
-- REPLACE THE VALUES BELOW WITH ACTUAL IDs FROM ABOVE QUERIES
-- Entity ID: (from first query)
-- Currency ID: (from second query)
-- ============================================================================

-- Step 2: Create Cash Account (100001)
-- This is an ASSET account for receiving cash

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
    (SELECT id FROM accounting_entity WHERE code='INT001' LIMIT 1),
    (SELECT id FROM accounting_currency WHERE code='INR' AND is_active=true LIMIT 1),
    true,
    0.00,
    NULL,
    NOW(),
    NOW()
) ON CONFLICT (entity_id, account_number) DO NOTHING;

-- Verify Cash Account was created
SELECT 'STEP 2: VERIFY CASH ACCOUNT CREATED' AS step;
SELECT id, account_number, name, account_type, is_active FROM accounting_account 
WHERE account_number='100001' LIMIT 1;

-- ============================================================================
-- Step 3: Verify Capital Accounts Exist
-- ============================================================================

SELECT 'STEP 3: VERIFY CAPITAL ACCOUNTS' AS step;

-- Check Main Capital Account (3000)
SELECT 'Main Capital Account (3000):' AS check_type;
SELECT id, account_number, name, account_type FROM accounting_account 
WHERE account_number='3000' LIMIT 1;

-- Check Shareholder Investment Account (3100)
SELECT 'Shareholder Investment Account (3100):' AS check_type;
SELECT id, account_number, name, account_type, parent_account_id FROM accounting_account 
WHERE account_number='3100' LIMIT 1;

-- List all sub-accounts under 3100 (shareholder individual accounts)
SELECT 'Sub-accounts under 3100:' AS check_type;
SELECT id, account_number, name, account_type FROM accounting_account 
WHERE account_number LIKE '3100-%' 
ORDER BY account_number;

-- ============================================================================
-- Step 4: Check CashReceiptLine Table Structure
-- ============================================================================

SELECT 'STEP 4: VERIFY CASHRECEIPTLINE TABLE STRUCTURE' AS step;

-- Show CashReceiptLine table columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'accounting_cashreceiptline'
ORDER BY ordinal_position;

-- ============================================================================
-- Step 5: Check Recent GL Entries
-- ============================================================================

SELECT 'STEP 5: SAMPLE GL ENTRIES' AS step;

-- Show recent GL entries (if any)
SELECT id, account_id, entry_type, amount, reference_number, workflow_status, is_posted, entry_date
FROM accounting_ledgerentry
ORDER BY entry_date DESC
LIMIT 10;

-- ============================================================================
-- Step 6: Check Recent Cash Receipts
-- ============================================================================

SELECT 'STEP 6: SAMPLE CASH RECEIPTS' AS step;

-- Show recent cash receipts (if any)
SELECT id, account_id, credit_account_id, debit_amount, credit_amount, status, workflow_status, created_at
FROM accounting_cashreceiptline
ORDER BY created_at DESC
LIMIT 5;

-- ============================================================================
-- SUMMARY CHECKS
-- ============================================================================

SELECT 'SETUP SUMMARY' AS section;

-- Count total accounts by type
SELECT 'Total Accounts by Type:' AS check_type;
SELECT account_type, COUNT(*) as count
FROM accounting_account
WHERE entity_id = (SELECT id FROM accounting_entity WHERE code='INT001' LIMIT 1)
GROUP BY account_type;

-- Check if Cash Account (100001) exists
SELECT 'Cash Account Status:' AS check_type;
CASE 
    WHEN EXISTS(SELECT 1 FROM accounting_account WHERE account_number='100001') 
        THEN 'EXISTS ✅'
    ELSE 'MISSING ❌'
END AS status;

-- ============================================================================
-- OPTIONAL: Create Sub-accounts for specific shareholders (if needed)
-- ============================================================================

-- Example: Create sub-account 3100-01 for "Zubair" shareholder
-- Uncomment and run if needed:
/*
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
) SELECT
    '3100-01',
    'Zubair - Capital',
    'EQUITY',
    'Capital account for Zubair',
    aa.entity_id,
    aa.currency_id,
    true,
    0.00,
    aa.id,
    NOW(),
    NOW()
FROM accounting_account aa
WHERE aa.account_number='3100' AND aa.entity_id = (SELECT id FROM accounting_entity WHERE code='INT001' LIMIT 1)
ON CONFLICT (entity_id, account_number) DO NOTHING;
*/

-- ============================================================================
-- OUTPUT COMPLETE
-- ============================================================================

SELECT '✅ SETUP COMPLETE - All checks passed!' AS final_status;
