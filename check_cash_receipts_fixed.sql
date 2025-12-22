-- Check cash receipt lines with correct column names
\echo 'Checking cash receipt lines from Dec 15, 2025:'

SELECT 
    crl.id,
    crl.date,
    crl.description,
    crl.debit_amount,
    crl.credit_amount,
    crl.status,
    crl.workflow_status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.stakeholder_id,
    crl.is_capital_contribution_posted
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.date = '2025-12-15'
ORDER BY crl.id;

\echo ''
\echo 'Checking all cash receipt lines with test descriptions:'
SELECT 
    crl.id,
    crl.date,
    crl.description,
    crl.debit_amount,
    crl.credit_amount,
    crl.status,
    crl.workflow_status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.stakeholder_id,
    crl.is_capital_contribution_posted
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.description ILIKE '%test%'
ORDER BY crl.date DESC;

\echo ''
\echo 'Checking cash receipt lines for our specific stakeholders:'
SELECT 
    crl.id,
    crl.date,
    crl.description,
    crl.debit_amount,
    crl.credit_amount,
    crl.status,
    crl.workflow_status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.stakeholder_id,
    crl.is_capital_contribution_posted
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.stakeholder_id IN (3, 7, 18)  -- Syed Safi, Ansaar Mohammed, Burhanuddin Shaik
ORDER BY crl.date DESC;