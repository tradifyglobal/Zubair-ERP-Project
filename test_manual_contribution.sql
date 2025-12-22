-- Test manual capital contribution creation with correct currency
INSERT INTO accounting_capitalcontribution (
    entity_id, 
    stakeholder_id, 
    contribution_date, 
    status, 
    amount, 
    currency_id, 
    currency_destination_id, 
    exchange_rate, 
    amount_company_currency, 
    amount_usd, 
    payment_mode, 
    reference_number, 
    source_cash_receipt_id, 
    is_auto_posted, 
    workflow_status, 
    created_at, 
    updated_at
) VALUES (
    7,              -- entity_id (Testing)
    7,              -- stakeholder_id (Ahsan Ali Khan)  
    '2025-12-16',   -- contribution_date
    'COMPLETED',    -- status
    200.00,         -- amount
    2,              -- currency_id (INR)
    2,              -- currency_destination_id (INR - entity currency)
    1.000000,       -- exchange_rate (same currency)
    200.00,         -- amount_company_currency
    200.00,         -- amount_usd
    'CASH',         -- payment_mode
    'AUTO-TEST-5',  -- reference_number
    5,              -- source_cash_receipt_id
    true,           -- is_auto_posted
    'APPROVED',     -- workflow_status
    NOW(),          -- created_at
    NOW()           -- updated_at
);

-- Update the cash receipt to mark it as posted
UPDATE accounting_cashreceiptline 
SET is_capital_contribution_posted = true 
WHERE id = 5;

-- Verify the result
SELECT 
    cc.id,
    cc.amount,
    c1.code as source_currency,
    c2.code as dest_currency,
    cc.amount_company_currency,
    cc.is_auto_posted,
    cc.source_cash_receipt_id
FROM accounting_capitalcontribution cc
JOIN accounting_currency c1 ON cc.currency_id = c1.id
JOIN accounting_currency c2 ON cc.currency_destination_id = c2.id
WHERE cc.source_cash_receipt_id = 5;