-- Query to find the ledger entries
SELECT id, date, account_id, reference_number, description, debit, credit, status 
FROM ledger_entry 
WHERE reference_number IN ('EXP-6-7', 'EXP-5-6', 'EXP-5-5') 
AND account_id = 59224
ORDER BY date DESC;

-- Delete the ledger entries
DELETE FROM ledger_entry 
WHERE reference_number IN ('EXP-6-7', 'EXP-5-6', 'EXP-5-5') 
AND account_id = 59224;
