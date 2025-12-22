#!/bin/bash

# Direct PostgreSQL connection to add missing columns
export PGPASSWORD='Tradify@PostgreSQL2024'

echo "Connecting to PostgreSQL database..."
echo "Host: 192.168.20.11"
echo "Database: tradifyerp_db"
echo "User: tradifyerp_user"
echo ""

# First check current columns
echo "Checking current columns before adding..."
psql -h 192.168.20.11 -U tradifyerp_user -d tradifyerp_db -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
ORDER BY table_name, column_name;"

echo ""
echo "Adding missing columns..."
echo ""

# Add to cashreceiptline
psql -h 192.168.20.11 -U tradifyerp_user -d tradifyerp_db << 'SQL'
ALTER TABLE accounting_cashreceiptline
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_cashreceiptline
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

ALTER TABLE accounting_bankreceiptline
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_bankreceiptline  
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Verify results
SELECT 'Column Addition Results:' as Status;
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
ORDER BY table_name, column_name;
SQL

echo ""
echo "Done!"
