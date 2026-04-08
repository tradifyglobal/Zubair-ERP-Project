#!/bin/bash
# Direct SQL execution using environment variable for password
# This bypasses the need for interactive password

HOST="192.168.20.11"
DB="tradifyerp_db"
USER="tradifyerp_user"
PASSWORD="Tradify@PostgreSQL2024"

# Export password so psql can use it
export PGPASSWORD="$PASSWORD"

echo "[*] Connecting to database..."
echo "[*] Adding purchase_account_id column..."

psql -h $HOST -U $USER -d $DB -c "
ALTER TABLE maintenance_asset
ADD COLUMN IF NOT EXISTS purchase_account_id BIGINT;
"

if [ $? -eq 0 ]; then
    echo "✓ Column added"
    
    echo "[*] Creating foreign key constraint..."
    psql -h $HOST -U $USER -d $DB -c "
    ALTER TABLE maintenance_asset
    ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
    FOREIGN KEY (purchase_account_id)
    REFERENCES accounting_account(id)
    ON DELETE SET NULL;
    " 2>&1 || echo "⚠ Constraint may already exist"
    
    echo "[*] Creating index..."
    psql -h $HOST -U $USER -d $DB -c "
    CREATE INDEX IF NOT EXISTS maintenance_asset_purchase_account_id_idx
    ON maintenance_asset(purchase_account_id);
    "
    
    echo "✓ Schema updated successfully"
else
    echo "✗ Failed"
    exit 1
fi

# Clean up
unset PGPASSWORD
