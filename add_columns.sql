ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS source_cash_receipt_id INTEGER;
ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS source_bank_receipt_id INTEGER;
ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS is_auto_posted BOOLEAN DEFAULT FALSE;
\d accounting_capitalcontribution
