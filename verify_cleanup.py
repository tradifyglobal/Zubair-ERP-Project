#!/usr/bin/env python3
"""
Verify Database Cleanup
======================
Check if transaction data was successfully cleared
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Production PostgreSQL connection details
DB_CONFIG = {
    'host': '192.168.2.59',
    'database': 'tradifyerp_db',
    'user': 'tradifyerp_user',
    'password': 'Tradify@PostgreSQL2024',
    'port': 5432
}

def verify_cleanup():
    """Verify that transaction data has been cleared"""
    print("🔍 Verifying Database Cleanup")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Key transaction tables to check
        key_tables = [
            'accounting_cashreceiptline',
            'accounting_cashpaymentline', 
            'accounting_bankreceiptline',
            'accounting_bankpaymentline',
            'accounting_ledgerentry',
            'accounting_trialbalance',
            'accounting_capitalcontribution',
            'accounting_auditlog'
        ]
        
        total_remaining = 0
        
        with conn.cursor() as cursor:
            for table in key_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"{table:35}: {count:8,} records")
                    total_remaining += count
                except Exception as e:
                    print(f"{table:35}: Error - {e}")
        
        print("-" * 50)
        print(f"{'TOTAL REMAINING RECORDS':35}: {total_remaining:8,}")
        
        if total_remaining == 0:
            print("\n✅ SUCCESS: Database is completely clean!")
            print("🎯 Ready for customer delivery")
        else:
            print(f"\n⚠️  WARNING: {total_remaining} records still remain")
            
        # Check if master data is preserved
        print("\n🔍 Verifying Master Data Preserved:")
        master_tables = [
            'accounting_account',
            'accounting_entity', 
            'accounting_currency',
            'auth_user'
        ]
        
        for table in master_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:35}: {count:8,} records")
            except Exception as e:
                print(f"{table:35}: Error - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_cleanup()