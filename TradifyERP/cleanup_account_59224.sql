-- Check entries for account 59224
SELECT id, entry_date, account_id, reference_number, description, debit_credit, amount, balance 
FROM ledger_entry 
WHERE account_id = 59224 
ORDER BY entry_date DESC;
