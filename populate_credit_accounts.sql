-- Populate credit_account for cash receipts
-- This sets the cash account (100001 or 1000) as the credit account
-- for all cash receipts that don't have one

UPDATE accounting_cashreceiptline 
SET credit_account_id = (
    SELECT id FROM accounting_account 
    WHERE accounting_account.entity_id = accounting_cashreceiptline.entity_id
    AND account_number = '100001' 
    AND is_active = true
    LIMIT 1
)
WHERE credit_account_id IS NULL;

-- If 100001 doesn't exist, try 1000
UPDATE accounting_cashreceiptline 
SET credit_account_id = (
    SELECT id FROM accounting_account 
    WHERE accounting_account.entity_id = accounting_cashreceiptline.entity_id
    AND account_number = '1000' 
    AND is_active = true
    LIMIT 1
)
WHERE credit_account_id IS NULL;

-- Show results
SELECT 
    entity_id,
    COUNT(*) as total_receipts,
    COUNT(CASE WHEN credit_account_id IS NOT NULL THEN 1 END) as with_credit_account,
    COUNT(CASE WHEN credit_account_id IS NULL THEN 1 END) as without_credit_account
FROM accounting_cashreceiptline
GROUP BY entity_id;
