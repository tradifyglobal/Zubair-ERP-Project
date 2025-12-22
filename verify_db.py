#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='192.168.2.59',
        user='tradifyerp_user',
        password='Tradify@PostgreSQL2024',
        database='tradifyerp_db'
    )
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='accounting_capitalcontribution')")
    table_exists = cursor.fetchone()[0]
    print(f"✓ Table exists: {table_exists}")
    
    # Check columns
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='accounting_capitalcontribution' AND column_name IN ('source_cash_receipt_id', 'source_bank_receipt_id', 'is_auto_posted') ORDER BY ordinal_position")
    
    print("✓ New columns:")
    for col_name, data_type in cursor.fetchall():
        print(f"  - {col_name}: {data_type}")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM accounting_capitalcontribution")
    count = cursor.fetchone()[0]
    print(f"✓ Records in table: {count}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Error: {e}")
