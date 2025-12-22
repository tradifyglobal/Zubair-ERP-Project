-- Create a new test cash receipt entry for workflow testing
INSERT INTO accounting_cashreceiptline (
    entity_id, 
    account_id, 
    credit_account_id,
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
    7,                                     -- Testing entity
    91961,                                 -- 3000-03: Ahsan Ali Khan - Capital (debit account)
    91983,                                 -- 100001: Cash (credit account) 
    2,                                     -- INR currency
    10,                                    -- Ahsan Ali Khan stakeholder
    CURRENT_DATE,                          -- today's date
    'Capital investment - Test Workflow',  -- description  
    2500.00,                              -- debit_amount
    2500.00,                              -- credit_amount
    'DRAFT',                              -- status
    'DRAFT',                              -- workflow_status (start as DRAFT)
    'TEST-WORKFLOW-2025',                 -- reference_number
    'Testing the complete cash receipt to capital contribution workflow', -- notes
    NOW(),                                -- created_at
    NOW(),                                -- updated_at
    false                                 -- is_capital_contribution_posted (should become true after signal)
);

-- Get the newly created record
SELECT 
    id, 
    description, 
    stakeholder_id,
    debit_amount,
    workflow_status, 
    is_capital_contribution_posted,
    reference_number
FROM accounting_cashreceiptline 
WHERE reference_number = 'TEST-WORKFLOW-2025';

-- Also show the stakeholder name for reference
SELECT 
    cr.id,
    cr.description,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cr.debit_amount,
    cr.workflow_status,
    cr.is_capital_contribution_posted
FROM accounting_cashreceiptline cr
JOIN accounting_stakeholder s ON cr.stakeholder_id = s.id
WHERE cr.reference_number = 'TEST-WORKFLOW-2025';