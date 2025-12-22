-- View entries for account 59224
SELECT id, entry_date, account_id, reference_number, description, entry_type, amount, is_posted 
FROM accounting_ledgerentry 
WHERE account_id = 59224 
ORDER BY entry_date DESC;
