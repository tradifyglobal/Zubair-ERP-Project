-- Find ALL accounts with "Zubair Zubair" or "Sameer Zubair" in the name
SELECT 
    aa.id,
    aa.account_number, 
    aa.name,
    ae.name as entity_name,
    aa.is_active
FROM accounting_account aa
LEFT JOIN accounting_entity ae ON aa.entity_id = ae.id
WHERE aa.name LIKE '%Zubair Zubair%' OR aa.name LIKE '%Sameer Zubair%'
ORDER BY aa.account_number;
