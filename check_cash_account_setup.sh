#!/bin/bash
# SQL Commands to create Cash Account and verify configuration
# Run on production database: postgresql server at 192.168.2.59

echo "Connecting to TradifyERP Database..."
echo "Host: 192.168.2.59"
echo "User: zubair"
echo ""

# First, let's verify the default entity
echo "=== CHECKING DEFAULT ENTITY ==="
psql -h 192.168.2.59 -U zubair -d tradifyerp_db -c \
  "SELECT id, code, name FROM accounting_entity WHERE is_active=true LIMIT 1;"

# Get entity ID for INT001
ENTITY_ID=$(psql -h 192.168.2.59 -U zubair -d tradifyerp_db -t -c \
  "SELECT id FROM accounting_entity WHERE code='INT001' AND is_active=true LIMIT 1;" 2>/dev/null)

echo ""
echo "=== ENTITY ID: $ENTITY_ID ==="
echo ""

# Get currency ID for INR
CURRENCY_ID=$(psql -h 192.168.2.59 -U zubair -d tradifyerp_db -t -c \
  "SELECT id FROM accounting_currency WHERE code='INR' AND is_active=true LIMIT 1;" 2>/dev/null)

echo "=== CURRENCY ID (INR): $CURRENCY_ID ==="
echo ""

# Check if Cash Account (100001) already exists
echo "=== CHECKING IF CASH ACCOUNT EXISTS ==="
psql -h 192.168.2.59 -U zubair -d tradifyerp_db -c \
  "SELECT id, account_number, name, account_type FROM accounting_account WHERE account_number='100001';"

echo ""
echo "=== CHECKING CAPITAL ACCOUNTS ==="
psql -h 192.168.2.59 -U zubair -d tradifyerp_db -c \
  "SELECT account_number, name, account_type FROM accounting_account WHERE account_number IN ('3000', '3100') ORDER BY account_number;"

echo ""
echo "=== CHECKING CASH RECEIPT LINES (SAMPLE) ==="
psql -h 192.168.2.59 -U zubair -d tradifyerp_db -c \
  "SELECT id, account_id, credit_account_id, debit_amount, credit_amount, status FROM accounting_cashreceiptline LIMIT 5;"
