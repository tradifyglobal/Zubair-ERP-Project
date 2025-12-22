-- Verify migration columns exist
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'accounting_cashpaymentline' 
  AND column_name IN ('payment_purpose', 'stakeholder_id', 'is_capital_contribution_posted')
ORDER BY column_name;

SELECT '--- CashPaymentLine columns ---' as separator;

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'accounting_bankpaymentline' 
  AND column_name IN ('payment_purpose', 'stakeholder_id', 'is_capital_contribution_posted')
ORDER BY column_name;

SELECT '--- BankPaymentLine columns ---' as separator;

-- Count rows in each table
SELECT 'CashPaymentLine records:' as info, COUNT(*) as count FROM accounting_cashpaymentline
UNION ALL
SELECT 'BankPaymentLine records:', COUNT(*) FROM accounting_bankpaymentline;
