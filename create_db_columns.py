#!/usr/bin/env python3
import psycopg2
import sys

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host='192.168.20.11',
        user='zubair',
        password='sql',
        database='erp_production'
    )
    cursor = conn.cursor()
    
    # Execute ALTER TABLE statements
    sql_statements = [
        "ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS source_cash_receipt_id INTEGER;",
        "ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS source_bank_receipt_id INTEGER;",
        "ALTER TABLE accounting_capitalcontribution ADD COLUMN IF NOT EXISTS is_auto_posted BOOLEAN DEFAULT FALSE;",
    ]
    
    for sql in sql_statements:
        cursor.execute(sql)
        print(f"✓ {sql.strip()}")
    
    # Verify columns were created
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='accounting_capitalcontribution' 
        AND column_name IN ('source_cash_receipt_id', 'source_bank_receipt_id', 'is_auto_posted')
        ORDER BY ordinal_position
    """)
    
    print("\n✓ Verification - New columns created:")
    for col_name, data_type in cursor.fetchall():
        print(f"  - {col_name}: {data_type}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\n✓ All columns created successfully!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
