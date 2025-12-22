-- Check all accounts with 3000-11 and 3000-12 across all entities
SELECT 
    aa.id,
    aa.account_number, 
    aa.name,
    aa.description,
    ae.name as entity_name,
    aa.is_active
FROM accounting_account aa
LEFT JOIN accounting_entity ae ON aa.entity_id = ae.id
WHERE aa.account_number IN ('3000-11', '3000-12')
ORDER BY aa.entity_id, aa.account_number;
