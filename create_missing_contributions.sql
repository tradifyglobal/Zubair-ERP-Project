-- Create the missing capital contributions directly in PostgreSQL
-- Based on the cash receipts that were created but never converted

\echo 'Creating missing capital contributions for Dec 15, 2025';

-- Get the next available IDs
SELECT 'Current max ID: ' || COALESCE(MAX(id), 0) FROM accounting_capitalcontribution;

-- Insert the missing capital contributions
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
    updated_at
) VALUES 
-- Syed Safi - Capital — 5000.00 Authorized (3000-16)
(
    7,  -- entity_id (Testing)
    3,  -- stakeholder_id (Syed Safi)
    '2025-12-15',
    5000.00,
    5000.00,  -- amount_usd (assuming same as amount)
    1,  -- currency_id (assuming 1 is default currency)
    1,  -- currency_destination_id 
    1.00,
    5000.00,
    'COMPLETED',
    'APPROVED',
    'CASH',
    '3000-16',
    'Capital contribution from test5 cash receipt',
    NOW(),
    NOW()
),
-- Burhanuddin Shaik - Capital — 6000.00 Authorized (3000-18)
(
    7,  -- entity_id (Testing)
    18, -- stakeholder_id (Burhanuddin Shaik)
    '2025-12-15',
    6000.00,
    6000.00,  -- amount_usd
    1,  -- currency_id 
    1,  -- currency_destination_id
    1.00,
    6000.00,
    'COMPLETED',
    'APPROVED',
    'CASH',
    '3000-18',
    'Capital contribution from test5 cash receipt',
    NOW(),
    NOW()
),
-- Ansaar Mohammed - Capital (3000-09)
(
    7,  -- entity_id (Testing)
    7,  -- stakeholder_id (Ansaar Mohammed)
    '2025-12-15',
    3000.00,  -- Corrected amount (was 200 in cash receipt)
    3000.00,  -- amount_usd
    1,  -- currency_id
    1,  -- currency_destination_id
    1.00,
    3000.00,
    'COMPLETED',
    'APPROVED',
    'CASH',
    '3000-09',
    'Capital contribution from test6 cash receipt (corrected amount)',
    NOW(),
    NOW()
);

-- Check what we created
\echo 'Verifying created contributions:';
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.contribution_date = '2025-12-15'
ORDER BY cc.id;

\echo 'Total contributions on Dec 15, 2025:';
SELECT COUNT(*) FROM accounting_capitalcontribution WHERE contribution_date = '2025-12-15';