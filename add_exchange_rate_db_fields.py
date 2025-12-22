#!/usr/bin/env python3
"""
Django script to add exchange rate fields to cash management models
Run this directly on the production server to add the database fields
"""

import os
import sys
import django

# Setup Django environment with production settings
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import connection

def add_exchange_rate_fields():
    """Add exchange rate fields to cash management tables"""
    
    print("Database Engine:", connection.settings_dict["ENGINE"])
    print("Database Name:", connection.settings_dict["NAME"])  
    print("Database Host:", connection.settings_dict.get("HOST", "localhost"))
    print("Database Port:", connection.settings_dict.get("PORT", "5432"))
    
    with connection.cursor() as cursor:
        # Test the connection first
        try:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            print("PostgreSQL Version:", result[0])
            print("✅ Successfully connected to PostgreSQL!")
        except Exception as e:
            print("❌ Database connection failed:", e)
            return
        tables = [
            'accounting_cashpaymentline',
            'accounting_cashreceiptline', 
            'accounting_bankreceiptline',
            'accounting_bankpaymentline'
        ]
        
        for table in tables:
            print(f"Adding exchange rate fields to {table}...")
            
            # Add exchange_rate field
            try:
                cursor.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,6) DEFAULT 1.0
                """)
                print(f"  ✅ Added exchange_rate to {table}")
            except Exception as e:
                print(f"  ⚠️ exchange_rate field might already exist in {table}: {e}")
            
            # Add converted_debit_amount field
            try:
                cursor.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN IF NOT EXISTS converted_debit_amount DECIMAL(18,2)
                """)
                print(f"  ✅ Added converted_debit_amount to {table}")
            except Exception as e:
                print(f"  ⚠️ converted_debit_amount field might already exist in {table}: {e}")
            
            # Add converted_credit_amount field
            try:
                cursor.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN IF NOT EXISTS converted_credit_amount DECIMAL(18,2)
                """)
                print(f"  ✅ Added converted_credit_amount to {table}")
            except Exception as e:
                print(f"  ⚠️ converted_credit_amount field might already exist in {table}: {e}")
        
        # Verify fields were added
        print("\nVerifying fields were added:")
        cursor.execute("""
            SELECT table_name, column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name IN ('accounting_cashpaymentline', 'accounting_cashreceiptline', 
                                'accounting_bankreceiptline', 'accounting_bankpaymentline')
            AND column_name IN ('exchange_rate', 'converted_debit_amount', 'converted_credit_amount')
            ORDER BY table_name, column_name
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"  📊 {row[0]}.{row[1]} ({row[2]}) = {row[3]}")
        
        print(f"\n✅ Successfully added exchange rate fields to {len(tables)} tables!")

if __name__ == "__main__":
    try:
        add_exchange_rate_fields()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)