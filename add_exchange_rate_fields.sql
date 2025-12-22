-- Add exchange rate fields to cash management tables
-- CashPaymentLine
ALTER TABLE accounting_cashpaymentline 
ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,6) DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS converted_debit_amount DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS converted_credit_amount DECIMAL(18,2);

-- CashReceiptLine  
ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,6) DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS converted_debit_amount DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS converted_credit_amount DECIMAL(18,2);

-- BankReceiptLine
ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,6) DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS converted_debit_amount DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS converted_credit_amount DECIMAL(18,2);

-- BankPaymentLine
ALTER TABLE accounting_bankpaymentline 
ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,6) DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS converted_debit_amount DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS converted_credit_amount DECIMAL(18,2);

-- Verify columns were added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name IN ('accounting_cashpaymentline', 'accounting_cashreceiptline', 'accounting_bankreceiptline', 'accounting_bankpaymentline')
AND column_name IN ('exchange_rate', 'converted_debit_amount', 'converted_credit_amount')
ORDER BY table_name, column_name;