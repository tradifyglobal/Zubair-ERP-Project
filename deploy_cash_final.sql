INSERT INTO accounting_account (account_number, name, account_type, description, entity_id, currency_id, is_active, opening_balance, created_at, updated_at)
SELECT '100001', 'Cash', 'ASSET', 'Cash account for receiving cash from shareholders', ae.id, ac.id, true, 0.00, NOW(), NOW()
FROM accounting_entity ae, accounting_currency ac
WHERE ae.code='INT-001' AND ac.code='INR' AND NOT EXISTS (SELECT 1 FROM accounting_account WHERE account_number='100001' AND entity_id=ae.id);

SELECT 'SUCCESS: CASH ACCOUNT DEPLOYED' AS status;
SELECT account_number, name, account_type, is_active FROM accounting_account WHERE account_number IN ('100001','1000','1100') ORDER BY account_number;