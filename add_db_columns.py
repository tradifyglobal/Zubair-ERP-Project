#!/usr/bin/env python
"""
Script to add the three new columns to accounting_capitalcontribution table
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db import connection

def add_columns():
    cursor = connection.cursor()
    
    sql_statements = [
        "ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS source_cash_receipt_id INTEGER;",
        "ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS source_bank_receipt_id INTEGER;",
        "ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS is_auto_posted BOOLEAN DEFAULT FALSE;",
    ]
    
    for sql in sql_statements:
        try:
            cursor.execute(sql)
            print(f"✓ {sql.strip()}")
        except Exception as e:
            print(f"✗ Failed: {sql.strip()}")
            print(f"  Error: {e}")
            return False
    
    cursor.close()
    connection.commit()
    print("\n✓ All columns created successfully!")
    return True

if __name__ == '__main__':
    success = add_columns()
    sys.exit(0 if success else 1)
