# Database Column Addition - Manual Script for PostgreSQL Superuser
# =====================================================================
# Due to table ownership issues, this column needs to be added by the DB admin or superuser
# 
# Run this as: postgres user on 192.168.20.11
# Example: sudo -u postgres psql -d tradifyerp_db < add_purchase_account_column_admin.sql

BEGIN TRANSACTION;

-- Add the purchase_account_id column to maintenance_asset
ALTER TABLE maintenance_asset
ADD COLUMN IF NOT EXISTS purchase_account_id BIGINT;

-- Create the foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'maintenance_asset' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%purchase_account%'
    ) THEN
        ALTER TABLE maintenance_asset
        ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
        FOREIGN KEY (purchase_account_id)
        REFERENCES accounting_account(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-- Create the index for performance
CREATE INDEX IF NOT EXISTS maintenance_asset_purchase_account_id_idx
ON maintenance_asset(purchase_account_id);

-- Grant privileges to the app user
GRANT SELECT, UPDATE, INSERT ON maintenance_asset TO tradifyerp_user;

COMMIT;

-- Verify
\d maintenance_asset
