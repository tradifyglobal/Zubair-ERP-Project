#!/usr/bin/env python3
"""
Use Django's database connection to add the column
Django should have elevated privileges
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

django.setup()

from django.db import connection

try:
    print("[*] Checking column...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'maintenance_asset' 
            AND column_name = 'purchase_account_id'
        """)
        
        if cursor.fetchone():
            print("✓ Column already exists")
        else:
            print("[*] Column not found, creating...")
            cursor.execute("""
                ALTER TABLE maintenance_asset
                ADD COLUMN purchase_account_id BIGINT
            """)
            print("✓ Column created")
            
            print("[*] Creating foreign key...")
            cursor.execute("""
                ALTER TABLE maintenance_asset
                ADD CONSTRAINT maintenance_asset_purchase_account_fk
                FOREIGN KEY (purchase_account_id)
                REFERENCES accounting_account(id)
                ON DELETE SET NULL
            """)
            print("✓ Foreign key created")
            
            print("[*] Creating index...")
            cursor.execute("""
                CREATE INDEX maintenance_asset_purchase_account_idx
                ON maintenance_asset(purchase_account_id)
            """)
            print("✓ Index created")
    
    print("\n✓ Database schema updated successfully!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
