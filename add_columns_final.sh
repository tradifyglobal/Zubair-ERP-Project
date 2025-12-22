#!/bin/bash

echo "Adding missing columns using zubair superuser account..."
echo ""

export PGPASSWORD="zubair@0862"

psql -h localhost -U zubair -d tradifyerp_db << 'SQL_END'
-- Add columns to cashreceiptline
ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT;

-- Add foreign key
ALTER TABLE accounting_cashreceiptline
ADD CONSTRAINT IF NOT EXISTS cashreceiptline_stakeholder_fk 
FOREIGN KEY (stakeholder_id) REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Add columns to bankreceiptline
ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT;

-- Add foreign key
ALTER TABLE accounting_bankreceiptline
ADD CONSTRAINT IF NOT EXISTS bankreceiptline_stakeholder_fk 
FOREIGN KEY (stakeholder_id) REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Verify
\echo ''
\echo 'VERIFICATION - Columns added:'
SELECT table_name, column_name, data_type FROM information_schema.columns
WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
ORDER BY table_name, column_name;
SQL_END

echo ""
echo "✓ All columns added successfully!"
