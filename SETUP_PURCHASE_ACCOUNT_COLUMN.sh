#!/bin/bash
# ================================================================
# Step-by-Step PostgreSQL Admin Commands to Add Purchase Account Column
# ================================================================
# Run this guide on the DATABASE SERVER (192.168.20.11) AS POSTGRES SUPERUSER
# 
# Prerequisites:
# - SSH access to 192.168.20.11
# - postgres Linux user access (or sudo access)
# - PSQL installed on the database server
#
# ================================================================

echo "=========================================="
echo "PostgreSQL Table Column Addition Setup"
echo "=========================================="
echo ""
echo "This script will help you add the purchase_account_id column"
echo "to the maintenance_asset table."
echo ""
echo "IMPORTANT: Run this on the DATABASE SERVER (192.168.20.11) as postgres user"
echo ""

# Step 1: Connect to database as postgres superuser
cat << 'EOF'
STEP 1: Connect to PostgreSQL and verify table ownership
========================================================
Run this command on 192.168.20.11:

    sudo -u postgres psql -d tradifyerp_db -c "\d+ maintenance_asset"

This will show the table structure. Look at the first line to see the owner.
If it's not "tradifyerp_user", that's why we can't ALTER it from the app.

EOF

# Step 2: Add the column
cat << 'EOF'
STEP 2: Add the purchase_account_id column
===========================================
Run this command on 192.168.20.11:

    sudo -u postgres psql -d tradifyerp_db << 'SQL'
    ALTER TABLE maintenance_asset ADD COLUMN purchase_account_id BIGINT;
    SQL

EOF

# Step 3: Add foreign key
cat << 'EOF'
STEP 3: Add foreign key constraint
===================================
Run this command on 192.168.20.11:

    sudo -u postgres psql -d tradifyerp_db << 'SQL'
    ALTER TABLE maintenance_asset
    ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
    FOREIGN KEY (purchase_account_id)
    REFERENCES accounting_account(id)
    ON DELETE SET NULL;
    SQL

EOF

# Step 4: Create index
cat << 'EOF'
STEP 4: Create index for performance
=====================================
Run this command on 192.168.20.11:

    sudo -u postgres psql -d tradifyerp_db << 'SQL'
    CREATE INDEX maintenance_asset_purchase_account_id_idx
    ON maintenance_asset(purchase_account_id);
    SQL

EOF

# Step 5: Verify
cat << 'EOF'
STEP 5: Verify the changes were successful
===========================================
Run this command on 192.168.20.11:

    sudo -u postgres psql -d tradifyerp_db -c "\d maintenance_asset"

You should see the new column: purchase_account_id | bigint

EOF

# Step 6: Grant permissions
cat << 'EOF'
STEP 6 (OPTIONAL): Grant permissions to ensure all operations work
====================================================================
If you want the tradifyerp_user to be able to manage this table in the future,
run this command on 192.168.20.11:

    sudo -u postgres psql -d tradifyerp_db << 'SQL'
    GRANT SELECT, INSERT, UPDATE, DELETE ON maintenance_asset TO tradifyerp_user;
    GRANT REFERENCES ON accounting_account TO tradifyerp_user;
    SQL

EOF

# All-in-one script
cat << 'EOF'
QUICK: Run everything at once
==============================
If you want to run all steps at once on 192.168.20.11, copy and paste this:

EOF

cat << 'SQLSCRIPT'
sudo -u postgres psql -d tradifyerp_db << 'SQL'
BEGIN TRANSACTION;

-- Add column
ALTER TABLE maintenance_asset ADD COLUMN purchase_account_id BIGINT;

-- Add constraint
ALTER TABLE maintenance_asset
ADD CONSTRAINT maintenance_asset_purchase_account_id_fk
FOREIGN KEY (purchase_account_id)
REFERENCES accounting_account(id)
ON DELETE SET NULL;

-- Create index
CREATE INDEX maintenance_asset_purchase_account_id_idx
ON maintenance_asset(purchase_account_id);

--Verify
\d maintenance_asset

COMMIT;
SQL
SQLSCRIPT

cat << 'EOF'

========================
After running the above commands:

1. On your APP SERVER (192.168.20.10), run:
   ssh root@192.168.20.10 "cd /var/www/tradifyerp && ./venv/bin/python manage.py migrate"

2. Test the feature:
   http://192.168.20.10/maintenance/assets/new/

3. Create a test asset with a Purchase Account

4. Check GL entries at:
   http://192.168.20.10/accounting/ledger_entries/

If everything looks good, you're done!
EOF
