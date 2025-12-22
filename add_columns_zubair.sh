#!/bin/bash

# Try accessing PostgreSQL as zubair
echo "Attempting to add columns as zubair user..."
echo ""

export PGPASSWORD="sql"

psql -h localhost -U zubair -d tradifyerp_db << 'SQL_END'
-- Add columns to cashreceiptline
ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT;

-- Add columns to bankreceiptline  
ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT;

-- Verify
SELECT table_name, column_name, data_type FROM information_schema.columns
WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
ORDER BY table_name, column_name;
SQL_END

echo ""
echo "Done!"
