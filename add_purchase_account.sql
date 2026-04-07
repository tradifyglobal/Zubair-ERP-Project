-- Add purchase_account column to maintenance_asset table
-- This script should be run with superuser privileges

BEGIN;

-- Add column if it doesn't exist
ALTER TABLE IF EXISTS maintenance_asset
ADD COLUMN IF NOT EXISTS purchase_account_id BIGINT;

-- Add foreign key constraint if not exists
-- Note: This might fail if constraint already exists, which is okay

DO $$
BEGIN
    ALTER TABLE maintenance_asset
    ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
    FOREIGN KEY (purchase_account_id)
    REFERENCES accounting_account(id)
    ON DELETE SET NULL;
EXCEPTION WHEN duplicate_object THEN
    NULL;
END $$;

-- Create index if not exists
CREATE INDEX IF NOT EXISTS maintenance_asset_purchase_account_id_idx
ON maintenance_asset(purchase_account_id);

-- Record the migration as applied
INSERT INTO django_migrations (app, name, applied)
VALUES ('maintenance', '0003_maintenanceasset_purchase_account', NOW())
ON CONFLICT DO NOTHING;

COMMIT;
