-- Update account names to match requirements
BEGIN;

-- Update main account names
UPDATE accounting_account SET name = 'GST', description = 'Goods and Services Tax Main Account' 
WHERE account_number = '2200';

UPDATE accounting_account SET name = 'Sales', description = 'Sales Revenue Main Account' 
WHERE account_number = '4000';

UPDATE accounting_account SET name = 'Sales-Return', description = 'Sales Returns and Allowances - Contra account to Sales' 
WHERE account_number = '4100';

UPDATE accounting_account SET name = 'Purchases', description = 'Purchases Main Account' 
WHERE account_number = '5000';

UPDATE accounting_account SET name = 'Purchase-Return', description = 'Purchase Returns and Allowances - Contra account to Purchases' 
WHERE account_number = '5100';

-- Show updated accounts
SELECT account_number, name, account_type, description 
FROM accounting_account 
WHERE account_number IN ('2200', '2200-01', '2200-02', '4000', '4000-01', '4000-02', '4100', '5000', '5000-01', '5000-02', '5100')
ORDER BY account_number;

COMMIT;
