-- Find entries with the reference numbers mentioned
SELECT id, entry_date, account_id, reference_number, description, entry_type, amount, is_posted 
FROM accounting_ledgerentry 
WHERE reference_number IN ('EXP-6-7', 'EXP-5-6', 'EXP-5-5')
ORDER BY entry_date DESC;
