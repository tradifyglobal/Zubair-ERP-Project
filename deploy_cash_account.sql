-- Cash Account Deployment Script
-- Created: 2025-12-15
-- Purpose: Create Cash Account (100001) for cash receipt workflow

-- Step 1: Get entity and currency IDs
SELECT id INTO entity_id FROM accounting_entity WHERE code='INT001' LIMIT 1;
SELECT id INTO currency_id FROM accounting_currency WHERE code='INR' LIMIT 1;

-- Step 2: Insert Cash Account if not exists
INSERT INTO accounting_account (
    account_number, name, account_type, description,
    entity_id, currency_id, is_active, opening_balance, 
    parent_account_id, created_at, updated_at
) 
SELECT 
    '100001', 'Cash', 'ASSET', 'Cash account for receiving cash from shareholders',
    entity_id, currency_id, true, 0.00,
    NULL, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM accounting_account WHERE account_number='100001'
)
ON CONFLICT (account_number, entity_id) DO NOTHING;

-- Step 3: Verify setup
SELECT 'Deployment Summary' as category;
SELECT '=================' as status;
SELECT account_number, name, account_type, is_active 
FROM accounting_account 
WHERE account_number IN ('100001','3000','3100')
ORDER BY account_number;

-- Step 4: Check related configurations
SELECT 'Entity Configuration' as category;
SELECT code, name FROM accounting_entity WHERE code='INT001';

SELECT 'Currency Configuration' as category;
SELECT code, name FROM accounting_currency WHERE code='INR';
