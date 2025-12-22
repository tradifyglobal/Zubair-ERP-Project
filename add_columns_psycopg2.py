#!/usr/bin/env python
"""
Direct PostgreSQL connection to add missing columns.
This bypasses Django's migration system and uses psycopg2 directly.
"""

import psycopg2
import sys

# Database connection details
DB_HOST = '192.168.2.59'
DB_NAME = 'tradifyerp_db'
DB_USER = 'tradifyerp_user'
DB_PASSWORD = 'Tradify@PostgreSQL2024'
DB_PORT = '5432'

print("=" * 80)
print("DIRECT POSTGRESQL COLUMN ADDITION")
print("=" * 80)
print(f"\nConnecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}...")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    
    cur = conn.cursor()
    print("✓ Connected successfully!")
    
    # Check current columns
    print("\n" + "=" * 80)
    print("CURRENT COLUMNS")
    print("=" * 80)
    
    cur.execute("""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
        AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
        ORDER BY table_name, column_name;
    """)
    
    results = cur.fetchall()
    if results:
        print("\nFound columns:")
        for row in results:
            print(f"  {row[0]}.{row[1]} ({row[2]})")
    else:
        print("\nNo columns found - will add them now")
    
    # Add columns
    print("\n" + "=" * 80)
    print("ADDING COLUMNS")
    print("=" * 80)
    
    statements = [
        ("cashreceiptline", "is_capital_contribution_posted", 
         "ALTER TABLE accounting_cashreceiptline ADD COLUMN is_capital_contribution_posted BOOLEAN DEFAULT FALSE;"),
        ("cashreceiptline", "stakeholder_id",
         "ALTER TABLE accounting_cashreceiptline ADD COLUMN stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;"),
        ("bankreceiptline", "is_capital_contribution_posted",
         "ALTER TABLE accounting_bankreceiptline ADD COLUMN is_capital_contribution_posted BOOLEAN DEFAULT FALSE;"),
        ("bankreceiptline", "stakeholder_id",
         "ALTER TABLE accounting_bankreceiptline ADD COLUMN stakeholder_id BIGINT REFERENCES accounting_stakeholder(id) ON DELETE SET NULL;"),
    ]
    
    for table, col, statement in statements:
        try:
            cur.execute(statement)
            conn.commit()
            print(f"✓ Added {table}.{col}")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print(f"✓ {table}.{col} already exists")
                conn.rollback()
            else:
                print(f"✗ Error adding {table}.{col}: {e}")
                conn.rollback()
    
    # Verify results
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    cur.execute("""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name IN ('accounting_cashreceiptline', 'accounting_bankreceiptline')
        AND column_name IN ('stakeholder_id', 'is_capital_contribution_posted')
        ORDER BY table_name, column_name;
    """)
    
    results = cur.fetchall()
    print(f"\nFinal column count: {len(results)}")
    for row in results:
        print(f"  ✓ {row[0]}.{row[1]} ({row[2]})")
    
    cur.close()
    conn.close()
    
    print("\n✓ All done!")
    sys.exit(0)
    
except psycopg2.Error as e:
    print(f"\n✗ PostgreSQL connection error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
