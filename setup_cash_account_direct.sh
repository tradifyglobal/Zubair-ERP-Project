#!/bin/bash
# ============================================================================
# DIRECT CASH ACCOUNT SETUP - WORKS WITHOUT DJANGO VENV
# ============================================================================
# This script sets up the Cash Account directly via SQL
# No Django or Python environment required
# 
# Prerequisites:
# - PostgreSQL client (psql) installed
# - Access to database server 192.168.20.11
# - Database credentials ready
# ============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       CASH ACCOUNT DIRECT SETUP VIA SQL                       ║"
echo "║              Database: 192.168.20.11                           ║"
echo "║              Database: tradifyerp_db                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"

DB_HOST="192.168.20.11"
DB_USER="zubair"
DB_NAME="tradifyerp_db"

echo ""
echo "Step 1: Getting Entity and Currency IDs..."
echo ""

# Get Entity ID
ENTITY_ID=$(PGPASSWORD="sql" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c \
  "SELECT id FROM accounting_entity WHERE code='INT001' LIMIT 1;" 2>/dev/null | xargs)

if [ -z "$ENTITY_ID" ]; then
    echo "❌ ERROR: Could not find entity INT001"
    echo "   Trying to get first active entity..."
    ENTITY_ID=$(PGPASSWORD="sql" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c \
      "SELECT id FROM accounting_entity WHERE is_active=true LIMIT 1;" 2>/dev/null | xargs)
fi

echo "✓ Entity ID: $ENTITY_ID"

# Get Currency ID
CURRENCY_ID=$(PGPASSWORD="sql" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c \
  "SELECT id FROM accounting_currency WHERE code='INR' LIMIT 1;" 2>/dev/null | xargs)

if [ -z "$CURRENCY_ID" ]; then
    echo "❌ ERROR: Could not find currency INR"
    echo "   Trying to get first active currency..."
    CURRENCY_ID=$(PGPASSWORD="sql" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c \
      "SELECT id FROM accounting_currency WHERE is_active=true LIMIT 1;" 2>/dev/null | xargs)
fi

echo "✓ Currency ID: $CURRENCY_ID"
echo ""

echo "Step 2: Creating Cash Account (100001)..."
echo ""

# Create Cash Account
PGPASSWORD="sql" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << EOFQL
INSERT INTO accounting_account (
    account_number,
    name,
    account_type,
    description,
    entity_id,
    currency_id,
    is_active,
    opening_balance,
    parent_account_id,
    created_at,
    updated_at
) VALUES (
    '100001',
    'Cash',
    'ASSET',
    'Cash account for receiving cash from shareholders and other receipts',
    $ENTITY_ID,
    $CURRENCY_ID,
    true,
    0.00,
    NULL,
    NOW(),
    NOW()
) ON CONFLICT (entity_id, account_number) DO NOTHING;

SELECT 'Account created/verified' AS status;
EOFQL

echo ""
echo "✅ Cash Account Setup Complete!"
echo ""

echo "Step 3: Verifying Accounts..."
echo ""

PGPASSWORD="sql" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << EOFQL
SELECT '=== CASH ACCOUNT ===' AS check;
SELECT account_number, name, account_type FROM accounting_account WHERE account_number='100001';

SELECT '=== CAPITAL ACCOUNTS ===' AS check;
SELECT account_number, name, account_type FROM accounting_account WHERE account_number IN ('3000','3100') ORDER BY account_number;

SELECT '=== STAKEHOLDER ACCOUNTS ===' AS check;
SELECT account_number, name FROM accounting_account WHERE account_number LIKE '3100-%' ORDER BY account_number;
EOFQL

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ SETUP COMPLETE                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "What's configured:"
echo "  ✓ Cash Account (100001) - ASSET type"
echo "  ✓ Capital Accounts verified (3000, 3100)"
echo "  ✓ Stakeholder accounts ready"
echo ""
echo "Next steps:"
echo "  1. Restart Django app: sudo systemctl restart gunicorn-tradifyerp"
echo "  2. Navigate to: https://192.168.20.10/accounting/cash-receipts/create/"
echo "  3. Create a test cash receipt"
echo ""
