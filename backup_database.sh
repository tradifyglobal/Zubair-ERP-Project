#!/bin/bash

# TradifyERP Database Backup Script
# Purpose: Create full SQL dump of tradifyerp_db
# Usage: ./backup_database.sh
# Location: Run on DB server (192.168.20.11)

set -e

BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/tradifyerp_db_backup_$TIMESTAMP.sql"
BACKUP_COMPRESSED="$BACKUP_DIR/tradifyerp_db_backup_$TIMESTAMP.sql.gz"

echo "============================================"
echo "TradifyERP Database Backup"
echo "============================================"
echo ""
echo "Backup Directory: $BACKUP_DIR"
echo "Backup File: $BACKUP_FILE"
echo "Database: tradifyerp_db"
echo "User: zubair"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Method 1: Try with password from environment
if [ -n "$PGPASSWORD" ]; then
    echo "Using PGPASSWORD environment variable..."
    pg_dump -h localhost -U zubair tradifyerp_db > "$BACKUP_FILE"
    
# Method 2: Try with .pgpass file
elif [ -f "$HOME/.pgpass" ]; then
    echo "Using .pgpass file for authentication..."
    export PGPASSFILE="$HOME/.pgpass"
    pg_dump -h localhost -U zubair tradifyerp_db > "$BACKUP_FILE"
    
# Method 3: Try without password (trusted connection)
else
    echo "Attempting trusted connection..."
    pg_dump -h localhost -U zubair tradifyerp_db > "$BACKUP_FILE"
fi

# Compress backup
if [ -f "$BACKUP_FILE" ]; then
    echo ""
    echo "Compressing backup..."
    gzip "$BACKUP_FILE"
    
    # Get file size
    BACKUP_SIZE=$(du -h "$BACKUP_COMPRESSED" | cut -f1)
    LINE_COUNT=$(wc -l < "$BACKUP_COMPRESSED" || echo "0")
    
    echo ""
    echo "✓ Backup Complete!"
    echo "  Compressed File: $BACKUP_COMPRESSED"
    echo "  Size: $BACKUP_SIZE"
    echo ""
    
    # Verify backup has content
    if [ $(stat -f%z "$BACKUP_COMPRESSED" 2>/dev/null || stat -c%s "$BACKUP_COMPRESSED") -gt 1000 ]; then
        echo "✓ Backup verified - file size looks good"
    else
        echo "⚠ WARNING: Backup file is very small, might not contain data"
    fi
else
    echo "✗ Backup failed - could not create file"
    exit 1
fi

echo ""
echo "Backup Location: $BACKUP_COMPRESSED"
echo "============================================"
