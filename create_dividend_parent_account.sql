-- Create Parent Dividend Account (6000)
-- Run this SQL on production database

-- First, check if it already exists
SELECT account_number, name, account_type 
FROM accounting_account 
WHERE account_number = '6000' AND entity_id = (SELECT id FROM accounting_entity WHERE name = 'Testing');

-- If not exists, create it
INSERT INTO accounting_account (
    account_number, 
    name, 
    account_type, 
    currency_id, 
    entity_id, 
    is_active, 
    description, 
    opening_balance,
    created_at, 
    updated_at
)
SELECT 
    '6000', 
    'Profit Distribution / Dividends', 
    'EXPENSE',
    (SELECT id FROM accounting_currency WHERE code='INR'),
    (SELECT id FROM accounting_entity WHERE name='Testing'),
    true,
    'Parent account for all shareholder profit distributions and dividends',
    0.00,
    NOW(), 
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM accounting_account 
    WHERE account_number = '6000' 
    AND entity_id = (SELECT id FROM accounting_entity WHERE name = 'Testing')
);

-- Verify creation
SELECT account_number, name, account_type, is_active 
FROM accounting_account 
WHERE account_number = '6000' 
AND entity_id = (SELECT id FROM accounting_entity WHERE name = 'Testing');
