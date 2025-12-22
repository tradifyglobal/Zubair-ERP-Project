-- Update account names in tradify database to match
UPDATE accounting_account 
SET name = 'Fayazuddin Zubair Mohammed - Capital',
    description = 'Capital account for Fayazuddin Zubair Mohammed'
WHERE account_number = '3000-11' AND name LIKE '%Zubair Zubair%';

UPDATE accounting_account 
SET name = 'Imteyazuddin Sameer Mohammed - Capital',
    description = 'Capital account for Imteyazuddin Sameer Mohammed'
WHERE account_number = '3000-12' AND name LIKE '%Sameer Zubair%';

-- Delete the duplicate old records
DELETE FROM accounting_account WHERE account_number = '3000-11' AND name = 'Final Delete - Capital';
DELETE FROM accounting_account WHERE account_number = '3000-12' AND name = 'Receiver Test - Capital';

-- Verify
SELECT account_number, name FROM accounting_account 
WHERE account_number IN ('3000-11', '3000-12')
ORDER BY account_number;
