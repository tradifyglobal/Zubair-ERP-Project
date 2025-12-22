-- Deploy Cash Account (100001) for ALL entities with entity mixin support

INSERT INTO accounting_account (account_number, name, account_type, description, entity_id, currency_id, is_active, opening_balance, created_at, updated_at)
SELECT '100001', 'Cash', 'ASSET', 'Cash account for receiving cash from shareholders', ae.id, ac.id, true, 0.00, NOW(), NOW()
FROM accounting_entity ae, accounting_currency ac
WHERE ac.code='INR' AND NOT EXISTS (
    SELECT 1 FROM accounting_account 
    WHERE account_number='100001' AND entity_id=ae.id
);

-- Verify deployment for all entities
SELECT 'CASH ACCOUNT DEPLOYED FOR ALL ENTITIES' AS status;
SELECT ae.code as entity_code, ae.name as entity_name, aa.account_number, aa.name as account_name, aa.account_type, aa.is_active
FROM accounting_entity ae
LEFT JOIN accounting_account aa ON aa.entity_id = ae.id AND aa.account_number='100001'
ORDER BY ae.code;
