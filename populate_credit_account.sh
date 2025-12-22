#!/bin/bash
# Populate credit_account for existing cash receipts from PostgreSQL

echo "=========================================="
echo "  Cash Receipt - Auto-populate Credit Account"
echo "=========================================="
echo ""
echo "Connecting to PostgreSQL database..."
echo "Host: 192.168.20.11"
echo "Database: tradifyerp_db"
echo ""

PGPASSWORD="Tradify@PostgreSQL2024" psql -h 192.168.20.11 -U tradifyerp_user -d tradifyerp_db << EOF

-- Check current status
SELECT 
    'Before Update' AS Status,
    COUNT(*) as total_receipts,
    SUM(CASE WHEN credit_account_id IS NOT NULL THEN 1 ELSE 0 END) as with_credit_account,
    SUM(CASE WHEN credit_account_id IS NULL THEN 1 ELSE 0 END) as without_credit_account
FROM accounting_cashreceiptline;

-- Populate credit_account with the debit account
UPDATE accounting_cashreceiptline
SET credit_account_id = account_id
WHERE credit_account_id IS NULL;

-- Check results
SELECT 
    'After Update' AS Status,
    COUNT(*) as total_receipts,
    SUM(CASE WHEN credit_account_id IS NOT NULL THEN 1 ELSE 0 END) as with_credit_account,
    SUM(CASE WHEN credit_account_id IS NULL THEN 1 ELSE 0 END) as without_credit_account
FROM accounting_cashreceiptline;

-- Show sample records
SELECT 
    'Sample Updated Records' AS Info,
    id,
    date,
    account_id,
    credit_account_id,
    debit_amount,
    description
FROM accounting_cashreceiptline
WHERE credit_account_id IS NOT NULL
LIMIT 5;

EOF

echo ""
echo "=========================================="
echo "✅ Script completed!"
echo "=========================================="
