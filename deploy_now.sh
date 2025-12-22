#!/bin/bash

echo "=========================================="
echo "  CASH ACCOUNT DEPLOYMENT"
echo "=========================================="
echo ""

export PGPASSWORD='sql'
DB_HOST='192.168.2.59'
DB_USER='zubair'
DB_NAME='tradifyerp_db'

echo "Checking existing accounts..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT account_number, name FROM accounting_account WHERE account_number='100001';"

echo ""
echo "Getting entity and currency IDs..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT id FROM accounting_entity WHERE code='INT001'; SELECT id FROM accounting_currency WHERE code='INR';"

echo ""
echo "Creating Cash Account..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME << SQLEOF
INSERT INTO accounting_account (account_number, name, account_type, description, entity_id, currency_id, is_active, opening_balance, created_at, updated_at)
VALUES (
  '100001',
  'Cash',
  'ASSET',
  'Cash account for receiving cash from shareholders',
  (SELECT id FROM accounting_entity WHERE code='INT001'),
  (SELECT id FROM accounting_currency WHERE code='INR'),
  true,
  0.00,
  NOW(),
  NOW()
) ON CONFLICT DO NOTHING;

SELECT 'Setup Complete' AS status;
SELECT account_number, name, account_type, is_active FROM accounting_account WHERE account_number='100001';
SQLEOF

echo ""
echo "=========================================="
echo "  DEPLOYMENT FINISHED"
echo "=========================================="
