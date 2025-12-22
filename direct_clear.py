#!/usr/bin/env python3
"""
Direct PostgreSQL Data Cleaner
=============================
Directly delete transaction data with commit
"""

import psycopg2

# Production PostgreSQL connection details
DB_CONFIG = {
    'host': '192.168.20.11',
    'database': 'tradifyerp_db',
    'user': 'tradifyerp_user',
    'password': 'Tradify@PostgreSQL2024',
    'port': 5432
}

def clear_data_directly():
    """Clear data with explicit commits"""
    print("🧹 Direct PostgreSQL Data Deletion")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Tables to clear in order
    tables_to_clear = [
        'accounting_auditlog',
        'accounting_cashreceiptline',
        'accounting_cashpaymentline', 
        'accounting_bankreceiptline',
        'accounting_bankpaymentline',
        'accounting_capitalcontribution',
        'accounting_trialbalance',
        'accounting_ledgerentry'
    ]
    
    try:
        for table in tables_to_clear:
            with conn.cursor() as cursor:
                # Get count before
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count_before = cursor.fetchone()[0]
                
                if count_before > 0:
                    # Delete all records
                    cursor.execute(f"DELETE FROM {table}")
                    conn.commit()  # Commit after each table
                    
                    # Verify deletion
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count_after = cursor.fetchone()[0]
                    
                    print(f"{table:35}: {count_before:4} → {count_after:4} records")
                else:
                    print(f"{table:35}: Already empty")
        
        print("\n✅ Direct deletion completed!")
        
        # Verify total cleanup
        print("\n🔍 Final Verification:")
        total_remaining = 0
        
        for table in tables_to_clear:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_remaining += count
                if count > 0:
                    print(f"{table:35}: {count:8,} records REMAINING")
        
        if total_remaining == 0:
            print("✅ SUCCESS: All transaction data cleared!")
        else:
            print(f"❌ FAILED: {total_remaining} records still remain")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_data_directly()
