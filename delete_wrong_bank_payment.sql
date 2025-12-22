-- Delete the incorrect bank payment ledger entries (BANK-PAYMENT-4)
DELETE FROM accounting_ledgerentry 
WHERE reference_number = 'BANK-PAYMENT-4' 
AND entity_id = 7;

-- Show remaining entries
SELECT * FROM accounting_ledgerentry WHERE entity_id = 7 ORDER BY id;
