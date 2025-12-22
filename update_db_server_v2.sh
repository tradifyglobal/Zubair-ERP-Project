#!/bin/bash
# Script to update database server pg_hba.conf for new app server IP
# Assumes sudo is passwordless or credentials are provided

echo "=== Updating PostgreSQL pg_hba.conf ==="

# Find PostgreSQL version
PG_VERSION=$(sudo -u postgres psql --version 2>/dev/null | awk '{print $3}' | cut -d. -f1)

if [ -z "$PG_VERSION" ]; then
  # Try alternative method
  PG_VERSION=$(ls /etc/postgresql/ 2>/dev/null | head -n1)
fi

PG_CONF="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

echo "PostgreSQL Version: $PG_VERSION"
echo "Config file: $PG_CONF"

if [ ! -f "$PG_CONF" ]; then
  echo "ERROR: pg_hba.conf not found at $PG_CONF"
  exit 1
fi

# Check if old entries exist
echo ""
echo "=== Checking for old app server IP (192.168.2.69) ==="
grep '192.168.2.69' $PG_CONF > /dev/null && echo "Found old entries - will update" || echo "No old entries found"

# Replace old app server IP with new one
echo ""
echo "=== Updating pg_hba.conf ==="
sed -i 's/192.168.2.69/192.168.20.10/g' $PG_CONF
echo "✓ Replaced 192.168.2.69 with 192.168.20.10"

# Check if new entry exists, if not add it
if ! grep -q '192.168.20.10' $PG_CONF; then
  echo "host    all    all    192.168.20.10/32    md5" >> $PG_CONF
  echo "✓ Added new entry for 192.168.20.10"
else
  echo "✓ Entry for 192.168.20.10 already exists"
fi

echo ""
echo "=== Current pg_hba.conf entries for 192.168.20.10 ==="
grep '192.168.20.10' $PG_CONF || echo "No entries found"

echo ""
echo "=== Reloading PostgreSQL ==="
sudo systemctl reload postgresql && echo "✓ PostgreSQL reloaded"

echo ""
echo "=== PostgreSQL Status ==="
sudo systemctl status postgresql --no-pager | head -n 3

echo ""
echo "=== Database Server Update Complete ==="
