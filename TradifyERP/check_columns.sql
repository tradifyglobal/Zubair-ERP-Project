-- Check columns in accounting_ledgerentry
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'accounting_ledgerentry'
ORDER BY ordinal_position;
