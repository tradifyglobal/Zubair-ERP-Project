#!/usr/bin/env python3
"""
Reset PostgreSQL Sequences as Superuser
======================================
"""

import psycopg2
import sys

# PostgreSQL superuser connection 
DB_CONFIG = {
    'host': '192.168.20.11',
    'database': 'tradifyerp_db',
    'user': 'postgres',  # PostgreSQL superuser
    'password': 'zubair123',  # Update if different
    'port': 5432
}

def reset_sequences():
    """Reset sequences using superuser privileges"""
    print("🔄 Resetting PostgreSQL sequences as superuser...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Reset sequences for transaction tables
            sequences_to_reset = [
                'accounting_auditlog_id_seq',
                'accounting_bankpaymentline_id_seq',
                'accounting_bankreceiptline_id_seq',
                'accounting_cashpaymentline_id_seq',
                'accounting_cashreceiptline_id_seq',
                'accounting_ledgerentry_id_seq',
                'accounting_trialbalance_id_seq',
                'accounting_capitalcontribution_id_seq',
                'accounting_cashtransaction_id_seq',
                'cash_management_cashposition_id_seq',
                'cash_management_paymentschedule_id_seq',
            ]
            
            for sequence in sequences_to_reset:
                try:
                    cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1")
                    print(f"   ✅ Reset {sequence}")
                except Exception as e:
                    if "does not exist" not in str(e):
                        print(f"   ❌ {sequence}: {e}")
                    else:
                        print(f"   ⏭️  {sequence}: Does not exist")
        
        conn.close()
        print("✅ Sequence reset completed!")
        
    except Exception as e:
        print(f"❌ Failed to reset sequences: {e}")
        print("💡 Try running manually: sudo -u postgres psql -d tradifyerp_db")

if __name__ == "__main__":
    reset_sequences()
