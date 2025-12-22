-- Delete the employee expense entries
BEGIN;

-- Delete entries with reference numbers EXP-6-7, EXP-5-6, EXP-5-5
DELETE FROM accounting_ledgerentry 
WHERE reference_number IN ('EXP-6-7', 'EXP-5-6', 'EXP-5-5');

-- Show what was deleted
SELECT 'Deleted 6 ledger entries with reference numbers: EXP-6-7, EXP-5-6, EXP-5-5' AS result;

COMMIT;
