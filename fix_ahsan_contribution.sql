-- Create the missing capital contribution for Ahsan Ali Khan
-- and update the cash receipt to link them

\echo 'Creating capital contribution for Ahsan Ali Khan (Dec 16, 2025):';

-- Insert the capital contribution
INSERT INTO accounting_capitalcontribution (
    entity_id,
    stakeholder_id,
    contribution_date,
    amount,
    amount_usd,
    currency_id,
    currency_destination_id,
    exchange_rate,
    amount_company_currency,
    status,
    workflow_status,
    payment_mode,
    reference_number,
    notes,
    created_at,
    updated_at,
    source_cash_receipt_id
) VALUES (
    7,  -- entity_id (Testing)
    10, -- stakeholder_id (Ahsan Ali Khan)
    '2025-12-16',
    500000.00,  -- Same amount as cash receipt
    500000.00,  -- amount_usd
    1,  -- currency_id
    1,  -- currency_destination_id
    1.00,
    500000.00,
    'COMPLETED',
    'APPROVED',
    'CASH',
    '3000-03',
    'Capital contribution from cash receipt - Capital investment from shareholder',
    NOW(),
    NOW(),
    6  -- Link to cash receipt ID 6
);

\echo 'Updating cash receipt to link to stakeholder and mark as posted:';

-- Update the cash receipt to link it to the stakeholder and mark as posted
UPDATE accounting_cashreceiptline 
SET 
    stakeholder_id = 10,  -- Ahsan Ali Khan
    is_capital_contribution_posted = true,
    updated_at = NOW()
WHERE id = 6;

\echo 'Verification - New capital contribution created:';
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.source_cash_receipt_id
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.stakeholder_id = 10
ORDER BY cc.id DESC;

\echo 'Verification - Cash receipt updated:';
SELECT 
    crl.id,
    crl.date,
    crl.description,
    crl.debit_amount,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.is_capital_contribution_posted
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.id = 6;