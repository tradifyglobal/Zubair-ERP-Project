#!/bin/bash
# Add purchase_account column to maintenance_asset table

HOST="192.168.20.11"
DB="tradifyerp_db"
USER="zubair"
PASSWORD="sql"

# SQL to add the column
psql -h $HOST -U $USER -d $DB -c "ALTER TABLE maintenance_asset ADD COLUMN purchase_account_id INTEGER;" << EOF
$PASSWORD
EOF

if [ $? -eq 0 ]; then
    # Add foreign key constraint
    psql -h $HOST -U $USER -d $DB -c "ALTER TABLE maintenance_asset ADD CONSTRAINT fk_purchase_account FOREIGN KEY (purchase_account_id) REFERENCES accounting_account(id) ON DELETE SET NULL;" << EOF
$PASSWORD
EOF
    echo "✓ Column added successfully"
else
    echo "✗ Failed to add column"
    exit 1
fi
