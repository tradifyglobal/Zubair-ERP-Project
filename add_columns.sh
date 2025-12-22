#!/bin/bash
# Add columns using psql directly with superuser privileges

export PGPASSWORD='Tradify@PostgreSQL2024'

echo "Adding columns to cashreceiptline and bankreceiptline..."

psql -h 192.168.2.59 -U tradifyerp_user -d tradifyerp_db <<'EOF'
ALTER TABLE accounting_cashreceiptline
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_cashreceiptline
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

ALTER TABLE accounting_bankreceiptline
ADD COLUMN IF NOT EXISTS is_capital_contribution_posted BOOLEAN DEFAULT FALSE;

ALTER TABLE accounting_bankreceiptline
ADD COLUMN IF NOT EXISTS stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;

-- Verify
SELECT column_name FROM information_schema.columns 
WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
ORDER BY table_name, column_name;

EOF

echo "Done!"
