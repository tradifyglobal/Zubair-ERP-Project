#!/usr/bin/env python
"""
Script to migrate accounts from old SQLite database to PostgreSQL
"""
import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, Entity
from django.db import connection

# Connect to old SQLite database
old_db_path = '/var/www/tradifyerp/TradifyERP/db.sqlite3'
print(f"Connecting to old SQLite database: {old_db_path}")

sqlite_conn = sqlite3.connect(old_db_path)
sqlite_conn.row_factory = sqlite3.Row
cursor = sqlite_conn.cursor()

# Get all accounts from SQLite
cursor.execute("SELECT * FROM accounting_account")
sqlite_accounts = cursor.fetchall()

print(f"Found {len(sqlite_accounts)} accounts in old SQLite database")

if len(sqlite_accounts) == 0:
    print("No accounts to migrate!")
    sqlite_conn.close()
    exit(0)

# Get the INT-001 entity (we'll use this as default if entity_id is missing)
int_entity = Entity.objects.filter(code='INT-001').first()
if not int_entity:
    print("Error: INT-001 entity not found!")
    exit(1)

print(f"Using entity: {int_entity.name} ({int_entity.code})")

# Migrate accounts
print("\nMigrating accounts...")
migrated = 0
skipped = 0
errors = 0

for row in sqlite_accounts:
    try:
        # Get column names from the row
        cols = [description[0] for description in cursor.description]
        account_data = dict(zip(cols, row))
        
        # Get account number - this is the unique identifier
        account_number = account_data.get('account_number')
        if not account_number:
            print(f"  ✗ Skipped account without account_number")
            skipped += 1
            continue
        
        # Check if account already exists by account_number
        if Account.objects.filter(account_number=account_number).exists():
            print(f"  ⊘ Skipped {account_number} - already exists")
            skipped += 1
            continue
        
        # Create new account
        account = Account(
            account_number=account_number,
            name=account_data.get('name', ''),
            description=account_data.get('description', ''),
            account_type=account_data.get('account_type', 'Asset'),
            parent_account_id=account_data.get('parent_account_id'),
            entity_id=account_data.get('entity_id') or int_entity.id,
            opening_balance=account_data.get('opening_balance', 0),
            currency_id=account_data.get('currency_id'),
            is_active=account_data.get('is_active', True),
            created_at=account_data.get('created_at'),
            updated_at=account_data.get('updated_at'),
        )
        account.save()
        migrated += 1
        print(f"  ✓ Migrated {account_number} - {account.name}")
    except Exception as e:
        errors += 1
        print(f"  ✗ Error migrating {account_data.get('account_number', 'unknown')}: {str(e)}")

sqlite_conn.close()

print(f"\n✓ Migration complete:")
print(f"  Migrated: {migrated} accounts")
print(f"  Skipped: {skipped} accounts")
print(f"  Errors: {errors}")
print(f"  Total in database now: {Account.objects.count()}")
