-- Add exchange rate fields to all cash management tables

-- Cash Payment Line
ALTER TABLE accounting_cashpaymentline ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(10,4) DEFAULT 1.0000;
ALTER TABLE accounting_cashpaymentline ADD COLUMN IF NOT EXISTS converted_debit_amount NUMERIC(15,2) DEFAULT 0.00;
ALTER TABLE accounting_cashpaymentline ADD COLUMN IF NOT EXISTS converted_credit_amount NUMERIC(15,2) DEFAULT 0.00;

-- Cash Receipt Line
ALTER TABLE accounting_cashreceiptline ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(10,4) DEFAULT 1.0000;
ALTER TABLE accounting_cashreceiptline ADD COLUMN IF NOT EXISTS converted_debit_amount NUMERIC(15,2) DEFAULT 0.00;
ALTER TABLE accounting_cashreceiptline ADD COLUMN IF NOT EXISTS converted_credit_amount NUMERIC(15,2) DEFAULT 0.00;

-- Bank Receipt Line
ALTER TABLE accounting_bankreceiptline ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(10,4) DEFAULT 1.0000;
ALTER TABLE accounting_bankreceiptline ADD COLUMN IF NOT EXISTS converted_debit_amount NUMERIC(15,2) DEFAULT 0.00;
ALTER TABLE accounting_bankreceiptline ADD COLUMN IF NOT EXISTS converted_credit_amount NUMERIC(15,2) DEFAULT 0.00;

-- Bank Payment Line
ALTER TABLE accounting_bankpaymentline ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(10,4) DEFAULT 1.0000;
ALTER TABLE accounting_bankpaymentline ADD COLUMN IF NOT EXISTS converted_debit_amount NUMERIC(15,2) DEFAULT 0.00;
ALTER TABLE accounting_bankpaymentline ADD COLUMN IF NOT EXISTS converted_credit_amount NUMERIC(15,2) DEFAULT 0.00;