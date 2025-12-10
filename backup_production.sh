#!/bin/bash

# Production Server Backup Script
# Creates a restore point with database and critical app files

cd /var/www/tradifyerp

# Create BACKUPS directory if it doesn't exist
mkdir -p BACKUPS

# Generate timestamp
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="BACKUPS/backup_${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "======================================="
echo "Production Server Backup"
echo "======================================="
echo ""
echo "Backup directory: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""
echo "Backing up files..."

# Backup database
echo "  - Backing up database (db.sqlite3)..."
cp TradifyERP/db.sqlite3 "$BACKUP_DIR/"

# Backup settings
echo "  - Backing up settings.py..."
cp TradifyERP/TradifyERP/settings.py "$BACKUP_DIR/" 2>/dev/null || true

echo "  - Backing up local_settings.py..."
cp TradifyERP/TradifyERP/local_settings.py "$BACKUP_DIR/" 2>/dev/null || true

# Backup critical app modules
echo "  - Backing up expenses module..."
cp -r TradifyERP/expenses "$BACKUP_DIR/"

echo "  - Backing up accounting module..."
cp -r TradifyERP/accounting "$BACKUP_DIR/"

# Create compressed archive
echo "  - Creating compressed archive..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

# Remove uncompressed backup directory
rm -rf "$BACKUP_DIR"

echo ""
echo "======================================="
echo "Backup completed successfully!"
echo "======================================="
echo ""
ls -lh "${BACKUP_DIR}.tar.gz"
echo ""
echo "Backup location: /var/www/tradifyerp/${BACKUP_DIR}.tar.gz"
echo ""
echo "To restore this backup, use:"
echo "  cd /var/www/tradifyerp"
echo "  tar -xzf ${BACKUP_DIR}.tar.gz"
echo "======================================="
