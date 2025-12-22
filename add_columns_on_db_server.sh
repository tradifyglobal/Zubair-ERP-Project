#!/bin/bash

# Script to add missing columns to PostgreSQL database
# This will be run on the PostgreSQL server as zubair user

echo "Adding missing columns to accounting tables..."
echo ""

# Try with sudo to postgres user (no password if configured)
sudo -n psql -U postgres -d tradifyerp_db << 'SQL_END'
-- Add columns to cashreceiptline
ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_cashreceiptline 
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT;

-- Add foreign key constraint
ALTER TABLE accounting_cashreceiptline
ADD CONSTRAINT IF NOT EXISTS cashreceiptline_stakeholder_fk 
FOREIGN KEY (stakeholder_id) REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Add columns to bankreceiptline
ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_bankreceiptline 
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT;

-- Add foreign key constraint
ALTER TABLE accounting_bankreceiptline
ADD CONSTRAINT IF NOT EXISTS bankreceiptline_stakeholder_fk 
FOREIGN KEY (stakeholder_id) REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Verify
SELECT table_name, column_name, data_type FROM information_schema.columns
WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
ORDER BY table_name, column_name;
SQL_END

echo ""
echo "Done!"
