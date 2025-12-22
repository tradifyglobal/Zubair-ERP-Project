-- Monitor cash receipts and capital contributions in real-time
-- Run this BEFORE creating the test cash receipt to get baseline

\echo 'BASELINE - Before creating new cash receipt:';

\echo 'Current cash receipt lines count:';
SELECT COUNT(*) as total_cash_receipts FROM accounting_cashreceiptline 
WHERE entity_id = 7;  -- Testing entity

\echo 'Recent cash receipt lines (last 5):';
SELECT 
    crl.id,
    crl.date,
    crl.description,
    crl.debit_amount,
    crl.status,
    crl.workflow_status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.is_capital_contribution_posted
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.entity_id = 7
ORDER BY crl.id DESC
LIMIT 5;

\echo 'Current capital contributions count:';
SELECT COUNT(*) as total_contributions FROM accounting_capitalcontribution 
WHERE entity_id = 7;

\echo 'Recent capital contributions (last 5):';
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
WHERE cc.entity_id = 7
ORDER BY cc.id DESC
LIMIT 5;