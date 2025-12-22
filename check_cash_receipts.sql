-- Check cash receipts that might be linked to capital contributions
\echo 'Checking cash receipts that might be related to missing capital contributions:'

SELECT 
    cr.id,
    cr.receipt_date,
    cr.description,
    cr.amount,
    cr.status,
    crl.id as line_id,
    crl.description as line_description,
    crl.amount as line_amount,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.id as capital_contribution_id
FROM accounting_cashreceipt cr
JOIN accounting_cashreceiptline crl ON cr.id = crl.cash_receipt_id
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
LEFT JOIN accounting_capitalcontribution cc ON cc.source_cash_receipt_id = cr.id
WHERE cr.description ILIKE '%test%'
   OR crl.description ILIKE '%test%'
ORDER BY cr.receipt_date DESC;

\echo ''
\echo 'Checking all cash receipts from Dec 15, 2025:'
SELECT 
    cr.id,
    cr.receipt_date,
    cr.description,
    cr.amount,
    cr.status,
    crl.stakeholder_id,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.amount as line_amount
FROM accounting_cashreceipt cr
JOIN accounting_cashreceiptline crl ON cr.id = crl.cash_receipt_id
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE cr.receipt_date = '2025-12-15'
ORDER BY cr.id;

\echo ''
\echo 'Checking if any capital contributions are linked to cash receipts:'
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.source_cash_receipt_id,
    cr.description as cash_receipt_description
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
LEFT JOIN accounting_cashreceipt cr ON cc.source_cash_receipt_id = cr.id
WHERE cc.source_cash_receipt_id IS NOT NULL
ORDER BY cc.contribution_date DESC;