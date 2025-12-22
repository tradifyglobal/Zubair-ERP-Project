#!/usr/bin/env python
import os
import sys

# Add the project directory to the path
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

import django
django.setup()

from django.db import connection

print("Attempting to add columns using Django's transaction management...")
print("="*80)

# Add columns using Django's transaction management
try:
    with connection.cursor() as cursor:
        # Add is_capital_contribution_posted to cashreceiptline
        try:
            cursor.execute("""
                ALTER TABLE accounting_cashreceiptline
                ADD COLUMN is_capital_contribution_posted BOOLEAN DEFAULT FALSE;
            """)
            print("✓ Added is_capital_contribution_posted to cashreceiptline")
            connection.commit()
        except Exception as e:
            if "already exists" in str(e):
                print("✓ is_capital_contribution_posted already exists on cashreceiptline")
            else:
                print(f"✗ Error: {e}")
                connection.rollback()
        
        # Add stakeholder_id to cashreceiptline  
        try:
            cursor.execute("""
                ALTER TABLE accounting_cashreceiptline
                ADD COLUMN stakeholder_id BIGINT;
            """)
            # Add constraint separately
            cursor.execute("""
                ALTER TABLE accounting_cashreceiptline
                ADD CONSTRAINT cashreceiptline_stakeholder_fk
                FOREIGN KEY (stakeholder_id) REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;
            """)
            print("✓ Added stakeholder_id to cashreceiptline")
            connection.commit()
        except Exception as e:
            if "already exists" in str(e):
                print("✓ stakeholder_id already exists on cashreceiptline")
            else:
                print(f"✗ Error: {e}")
                connection.rollback()
        
        # Add is_capital_contribution_posted to bankreceiptline
        try:
            cursor.execute("""
                ALTER TABLE accounting_bankreceiptline
                ADD COLUMN is_capital_contribution_posted BOOLEAN DEFAULT FALSE;
            """)
            print("✓ Added is_capital_contribution_posted to bankreceiptline")
            connection.commit()
        except Exception as e:
            if "already exists" in str(e):
                print("✓ is_capital_contribution_posted already exists on bankreceiptline")
            else:
                print(f"✗ Error: {e}")
                connection.rollback()
        
        # Add stakeholder_id to bankreceiptline
        try:
            cursor.execute("""
                ALTER TABLE accounting_bankreceiptline
                ADD COLUMN stakeholder_id BIGINT;
            """)
            # Add constraint separately
            cursor.execute("""
                ALTER TABLE accounting_bankreceiptline
                ADD CONSTRAINT bankreceiptline_stakeholder_fk
                FOREIGN KEY (stakeholder_id) REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;
            """)
            print("✓ Added stakeholder_id to bankreceiptline")
            connection.commit()
        except Exception as e:
            if "already exists" in str(e):
                print("✓ stakeholder_id already exists on bankreceiptline")
            else:
                print(f"✗ Error: {e}")
                connection.rollback()

except Exception as e:
    print(f"✗ Fatal error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Running schema check to verify...")
print("="*80)

# Now verify
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = 'accounting_cashreceiptline'
        AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
        ORDER BY column_name;
    """)
    result = cursor.fetchall()
    print(f"\nFound {len(result)} columns on cashreceiptline:")
    for row in result:
        print(f"  ✓ {row[0]} ({row[1]})")
    
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = 'accounting_bankreceiptline'
        AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
        ORDER BY column_name;
    """)
    result = cursor.fetchall()
    print(f"\nFound {len(result)} columns on bankreceiptline:")
    for row in result:
        print(f"  ✓ {row[0]} ({row[1]})")
