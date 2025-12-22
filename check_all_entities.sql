-- List all entities and their 3000-11, 3000-12 accounts
SELECT 
    ae.id,
    ae.name as entity,
    aa.account_number,
    aa.name as account_name,
    aa.is_active
FROM accounting_entity ae
LEFT JOIN accounting_account aa ON ae.id = aa.entity_id 
    AND aa.account_number IN ('3000-11', '3000-12')
ORDER BY ae.name, aa.account_number;
