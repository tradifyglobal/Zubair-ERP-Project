-- Delete Capital accounts starting with 3100
-- First check what we have
SELECT account_number, name, account_type FROM accounting_account WHERE account_number LIKE '3100%' ORDER BY account_number;

-- Delete child accounts first (3100-01, 3100-02, etc.)
DELETE FROM accounting_account WHERE account_number LIKE '3100-%';

-- Then delete the parent account (3100)
DELETE FROM accounting_account WHERE account_number = '3100';

-- Verify deletion
SELECT account_number, name, account_type FROM accounting_account WHERE account_number LIKE '3100%' ORDER BY account_number;