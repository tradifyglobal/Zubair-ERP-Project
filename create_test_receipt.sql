-- Create a test cash receipt for signal testing
INSERT INTO accounting_cashreceiptline (
    entity_id, 
    account_id, 
    currency_id, 
    stakeholder_id, 
    date, 
    description, 
    debit_amount, 
    credit_amount, 
    status, 
    workflow_status, 
    reference_number, 
    notes, 
    created_at, 
    updated_at, 
    is_capital_contribution_posted
) VALUES (
    7,                                                -- Testing entity
    1,                                                -- Account ID
    2,                                                -- INR currency
    10,                                               -- Ahsan Ali Khan stakeholder
    '2025-12-16',                                    -- date
    'Test Signal Auto-Creation',                      -- description  
    1000.00,                                         -- debit_amount
    1000.00,                                         -- credit_amount
    'DRAFT',                                         -- status
    'DRAFT',                                         -- workflow_status
    'TEST-AUTO-SIGNAL',                              -- reference_number
    'Testing automatic capital contribution creation', -- notes
    NOW(),                                           -- created_at
    NOW(),                                           -- updated_at
    false                                            -- is_capital_contribution_posted
);

-- Get the ID of the inserted record
SELECT id, description, stakeholder_id, workflow_status, is_capital_contribution_posted 
FROM accounting_cashreceiptline 
WHERE reference_number = 'TEST-AUTO-SIGNAL';