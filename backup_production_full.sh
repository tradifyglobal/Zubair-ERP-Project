#!/bin/bash

# Complete Production Server Backup Script
# Creates a full restore point with entire project

cd /var/www/tradifyerp

# Create BACKUPS directory if it doesn't exist
mkdir -p BACKUPS

# Generate timestamp
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="BACKUPS/full_backup_${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "======================================="
echo "FULL Production Server Backup"
echo "======================================="
echo ""
echo "Backup directory: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""
echo "Backing up complete project..."
echo ""

# Backup entire TradifyERP project
echo "  - Backing up complete TradifyERP project..."
cp -r TradifyERP "$BACKUP_DIR/"

echo "  - Backup size check..."

# Create compressed archive
echo "  - Creating compressed archive (this may take a minute)..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

# Remove uncompressed backup directory
rm -rf "$BACKUP_DIR"

echo ""
echo "======================================="
echo "FULL Backup completed successfully!"
echo "======================================="
echo ""
ls -lh "${BACKUP_DIR}.tar.gz"
echo ""
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}.tar.gz" | cut -f1)
echo "Backup size: $BACKUP_SIZE"
echo ""
echo "Backup location: /var/www/tradifyerp/${BACKUP_DIR}.tar.gz"
echo ""
echo "This backup includes:"
echo "  ✓ Complete TradifyERP project"
echo "  ✓ Database (db.sqlite3)"
echo "  ✓ All Django apps and modules"
echo "  ✓ All migrations"
echo "  ✓ All settings and configs"
echo "  ✓ Static files and media"
echo "  ✓ Templates"
echo ""
echo "To restore this backup, use:"
echo "  cd /var/www/tradifyerp"
echo "  tar -xzf ${BACKUP_DIR}.tar.gz"
echo "======================================="
