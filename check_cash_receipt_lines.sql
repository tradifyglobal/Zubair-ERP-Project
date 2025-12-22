-- Check cash receipt lines that might be related to capital contributions
\echo 'Checking cash receipt lines from Dec 15, 2025:'

SELECT 
    crl.id,
    crl.receipt_date,
    crl.description,
    crl.amount,
    crl.status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.stakeholder_id
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.receipt_date = '2025-12-15'
ORDER BY crl.id;

\echo ''
\echo 'Checking all cash receipt lines with test descriptions:'
SELECT 
    crl.id,
    crl.receipt_date,
    crl.description,
    crl.amount,
    crl.status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.stakeholder_id
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.description ILIKE '%test%'
ORDER BY crl.receipt_date DESC;

\echo ''
\echo 'Checking cash receipt lines for our specific stakeholders:'
SELECT 
    crl.id,
    crl.receipt_date,
    crl.description,
    crl.amount,
    crl.status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.stakeholder_id
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.stakeholder_id IN (3, 7, 18)  -- Syed Safi, Ansaar Mohammed, Burhanuddin Shaik
ORDER BY crl.receipt_date DESC;

\echo ''
\echo 'Checking if capital contributions link to cash receipt lines:'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.source_cash_receipt_id
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.source_cash_receipt_id IS NOT NULL
ORDER BY cc.contribution_date DESC;