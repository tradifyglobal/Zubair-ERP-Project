-- Add payment_purpose, stakeholder and is_capital_contribution_posted fields to payment tables

-- Add fields to CashPaymentLine
ALTER TABLE accounting_cashpaymentline 
ADD COLUMN IF NOT EXISTS payment_purpose VARCHAR(30);

ALTER TABLE accounting_cashpaymentline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_cashpaymentline 
ADD COLUMN IF NOT EXISTS stakeholder_id INTEGER REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Add fields to BankPaymentLine
ALTER TABLE accounting_bankpaymentline 
ADD COLUMN IF NOT EXISTS payment_purpose VARCHAR(30);

ALTER TABLE accounting_bankpaymentline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_bankpaymentline 
ADD COLUMN IF NOT EXISTS stakeholder_id INTEGER REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Add comments
COMMENT ON COLUMN accounting_cashpaymentline.payment_purpose IS 'Purpose of payment: CAPITAL_WITHDRAWAL, PROFIT_DISTRIBUTION, EXPENSE, etc.';
COMMENT ON COLUMN accounting_cashpaymentline.is_capital_contribution_posted IS 'Whether capital contribution (withdrawal) was auto-posted from this payment';
COMMENT ON COLUMN accounting_cashpaymentline.stakeholder_id IS 'Stakeholder for capital withdrawals/profit distributions';

COMMENT ON COLUMN accounting_bankpaymentline.payment_purpose IS 'Purpose of payment: CAPITAL_WITHDRAWAL, PROFIT_DISTRIBUTION, EXPENSE, etc.';
COMMENT ON COLUMN accounting_bankpaymentline.is_capital_contribution_posted IS 'Whether capital contribution (withdrawal) was auto-posted from this payment';
COMMENT ON COLUMN accounting_bankpaymentline.stakeholder_id IS 'Stakeholder for capital withdrawals/profit distributions';

SELECT 'Migration completed successfully - payment_purpose and stakeholder fields added!' as status;
