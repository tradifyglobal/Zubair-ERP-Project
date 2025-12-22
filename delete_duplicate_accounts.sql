-- Delete the old/incorrect account records
DELETE FROM accounting_account 
WHERE account_number = '3000-11' AND name = 'Final Delete - Capital';

DELETE FROM accounting_account 
WHERE account_number = '3000-12' AND name = 'Receiver Test - Capital';

-- Verify the cleanup
SELECT account_number, name, description FROM accounting_account 
WHERE account_number IN ('3000-11', '3000-12') 
ORDER BY account_number;
