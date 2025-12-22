-- Copy the entire accounting_capitalcontribution table from tradify to tradifyerp_db
-- including all data and the 3 new columns we added
CREATE TABLE IF NOT EXISTS public.accounting_capitalcontribution AS
SELECT * FROM tradify.public.accounting_capitalcontribution;

-- Verify the copy
SELECT COUNT(*) as record_count FROM public.accounting_capitalcontribution;
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='accounting_capitalcontribution' 
AND column_name IN ('source_cash_receipt_id', 'source_bank_receipt_id', 'is_auto_posted');
