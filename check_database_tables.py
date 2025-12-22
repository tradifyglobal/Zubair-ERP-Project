#!/usr/bin/env python3

import os
import sys
import django

# Setup Django environment
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db import connection

def list_tables():
    """List all tables in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        all_tables = [row[0] for row in cursor.fetchall()]
        
        print("All Database Tables:")
        print("=" * 50)
        for table in all_tables:
            print(f"  {table}")
        
        print(f"\nTotal: {len(all_tables)} tables")
        
        # Filter for transaction-related tables
        transaction_tables = [t for t in all_tables if any(keyword in t.lower() for keyword in [
            'cash', 'bank', 'ledger', 'trial', 'capital', 'investment', 
            'receipt', 'payment', 'transaction', 'contribution', 'audit'
        ])]
        
        print("\nTransaction-related tables:")
        print("=" * 50)
        for table in transaction_tables:
            print(f"  {table}")
        
        return transaction_tables

def check_table_counts(tables):
    """Check record counts for specific tables"""
    print("\nRecord Counts:")
    print("=" * 50)
    
    total_records = 0
    with connection.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:40}: {count:8,}")
                total_records += count
            except Exception as e:
                print(f"{table:40}: Error - {e}")
    
    print("-" * 50)
    print(f"{'TOTAL RECORDS':40}: {total_records:8,}")
    return total_records

if __name__ == "__main__":
    print("🔍 Database Table Inspector")
    print("=" * 50)
    
    transaction_tables = list_tables()
    
    if transaction_tables:
        total = check_table_counts(transaction_tables)
        if total > 0:
            print(f"\n⚠️  Found {total:,} transaction records that can be cleared")
        else:
            print("\n✅ No transaction data found - database is clean")
    else:
        print("\n✅ No transaction tables found")