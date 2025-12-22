-- Update account names to remove extra middle names
-- Account 3000-11: Fayazuddin Zubair Zubair Mohammed - Capital → Fayazuddin Zubair Mohammed - Capital
-- Account 3000-12: Imteyazuddin Sameer Zubair Mohammed - Capital → Imteyazuddin Sameer Mohammed - Capital

UPDATE accounting_account 
SET name = 'Fayazuddin Zubair Mohammed - Capital',
    description = 'Capital account for Fayazuddin Zubair Mohammed'
WHERE account_number = '3000-11' AND name LIKE '%Zubair Zubair%';

UPDATE accounting_account 
SET name = 'Imteyazuddin Sameer Mohammed - Capital',
    description = 'Capital account for Imteyazuddin Sameer Mohammed'
WHERE account_number = '3000-12' AND name LIKE '%Sameer Zubair%';

-- Verify the updates
SELECT account_number, name, description FROM accounting_account 
WHERE account_number IN ('3000-11', '3000-12')
ORDER BY account_number;
