-- Monitor changes after creating new cash receipt
-- Run this AFTER creating the test cash receipt

\echo 'AFTER - Changes since creating new cash receipt:';

\echo 'Current cash receipt lines count:';
SELECT COUNT(*) as total_cash_receipts FROM accounting_cashreceiptline 
WHERE entity_id = 7;

\echo 'NEW cash receipt lines (show any new ones):';
SELECT 
    crl.id,
    crl.date,
    crl.description,
    crl.debit_amount,
    crl.status,
    crl.workflow_status,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.is_capital_contribution_posted,
    crl.created_at
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.entity_id = 7
  AND crl.id > 5  -- Show only new ones after baseline
ORDER BY crl.id DESC;

\echo 'Current capital contributions count:';
SELECT COUNT(*) as total_contributions FROM accounting_capitalcontribution 
WHERE entity_id = 7;

\echo 'NEW capital contributions (show any new ones):';
SELECT 
    cc.id,
    cc.contribution_date,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    cc.amount,
    cc.status,
    cc.workflow_status,
    cc.reference_number,
    cc.source_cash_receipt_id,
    cc.created_at
FROM accounting_capitalcontribution cc
JOIN accounting_stakeholder s ON cc.stakeholder_id = s.id
WHERE cc.entity_id = 7
  AND cc.id > 23  -- Show only new ones after our manual entries
ORDER BY cc.id DESC;

\echo 'Check if any cash receipts were marked as posted:';
SELECT 
    crl.id,
    crl.description,
    crl.debit_amount,
    s.first_name || ' ' || s.last_name as stakeholder_name,
    crl.is_capital_contribution_posted,
    crl.updated_at
FROM accounting_cashreceiptline crl
LEFT JOIN accounting_stakeholder s ON crl.stakeholder_id = s.id
WHERE crl.entity_id = 7
  AND crl.is_capital_contribution_posted = true
ORDER BY crl.updated_at DESC;