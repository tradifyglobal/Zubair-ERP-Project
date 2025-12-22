#!/usr/bin/env python3
"""
PostgreSQL Production Database Cleaner
=====================================
Clear transaction data from PostgreSQL production database
Database: 192.168.2.59
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

# Production PostgreSQL connection details
DB_CONFIG = {
    'host': '192.168.2.59',
    'database': 'tradifyerp_db',
    'user': 'tradifyerp_user',
    'password': 'Tradify@PostgreSQL2024',
    'port': 5432
}

def get_connection():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # We want transaction control
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

def list_transaction_tables(conn):
    """List all transaction-related tables"""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND (
                table_name LIKE '%cash%' OR 
                table_name LIKE '%bank%' OR
                table_name LIKE '%ledger%' OR 
                table_name LIKE '%trial%' OR
                table_name LIKE '%capital%' OR 
                table_name LIKE '%investment%' OR
                table_name LIKE '%receipt%' OR 
                table_name LIKE '%payment%' OR
                table_name LIKE '%transaction%' OR 
                table_name LIKE '%contribution%' OR
                table_name LIKE '%audit%' OR
                table_name LIKE '%reconciliation%'
            )
            ORDER BY table_name
        """)
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        return tables

def get_table_counts(conn, tables):
    """Get record counts for tables"""
    counts = {}
    total = 0
    
    with conn.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                counts[table] = count
                total += count
            except Exception as e:
                counts[table] = f"Error: {e}"
    
    return counts, total

def show_current_data(conn):
    """Show current transaction data in database"""
    print("=" * 70)
    print("PRODUCTION DATABASE TRANSACTION DATA")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    print(f"🗄️  Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    tables = list_transaction_tables(conn)
    
    if not tables:
        print("\n✅ No transaction tables found")
        return False
    
    counts, total = get_table_counts(conn, tables)
    
    print(f"\nFound {len(tables)} transaction-related tables:")
    print("-" * 70)
    
    for table in sorted(tables):
        count = counts.get(table, 0)
        if isinstance(count, int):
            print(f"{table:40}: {count:8,} records")
        else:
            print(f"{table:40}: {count}")
    
    print("-" * 70)
    print(f"{'TOTAL TRANSACTION RECORDS':40}: {total:8,}")
    print("=" * 70)
    
    return total > 0

def clear_transaction_data(conn):
    """Clear transaction data from PostgreSQL"""
    
    # Define tables in deletion order (dependencies first)
    deletion_order = [
        # Audit and reconciliation first (may reference everything)
        'accounting_auditlog',
        'accounting_reconciliationmatch',
        'accounting_reconciliationentry', 
        'accounting_reconciliationrecord',
        
        # Reports and forecasts
        'accounting_balancesheet',
        'accounting_profitlossreport',
        'cash_management_liquidityforecastline',
        'cash_management_liquidityforecast',
        'cash_management_fxexposure',
        
        # Transaction lines and payments
        'accounting_cashreceiptline',
        'accounting_cashpaymentline',
        'accounting_bankreceiptline', 
        'accounting_bankpaymentline',
        'accounting_vendorpayment',
        'accounting_cashtransaction',
        
        # Tax and summary data
        'accounting_taxtransaction',
        'accounting_taxsummary',
        
        # Cash management
        'cash_management_paymentschedule',
        'cash_management_cashposition',
        
        # Shareholder data
        'shareholder_capitalcontribution',
        'accounting_capitalcontribution',
        
        # Core accounting
        'accounting_trialbalance',
        'accounting_ledgerentry',
    ]
    
    print("🧹 Starting PostgreSQL transaction data cleanup...")
    
    deleted_summary = {}
    
    try:
        with conn.cursor() as cursor:
            # Get list of tables that actually exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            for table in deletion_order:
                if table in existing_tables:
                    try:
                        # Get count before deletion
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count_before = cursor.fetchone()[0]
                        
                        if count_before > 0:
                            # Delete all records
                            cursor.execute(f"DELETE FROM {table}")
                            deleted_count = cursor.rowcount
                            deleted_summary[table] = deleted_count
                            print(f"   ✅ {table}: Deleted {deleted_count:,} records")
                        else:
                            deleted_summary[table] = 0
                            print(f"   ⏭️  {table}: Already empty")
                            
                    except Exception as e:
                        print(f"   ❌ {table}: Error - {e}")
                        deleted_summary[table] = f"Error: {e}"
                else:
                    print(f"   ⏭️  {table}: Table doesn't exist")
        
        print("✅ Data deletion completed")
        return deleted_summary
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        raise

def reset_sequences(conn):
    """Reset PostgreSQL sequences"""
    print("\n🔄 Resetting PostgreSQL sequences...")
    
    with conn.cursor() as cursor:
        try:
            # Get all sequences that might need resetting
            cursor.execute("""
                SELECT schemaname, sequencename, start_value
                FROM pg_sequences 
                WHERE schemaname = 'public'
                AND (
                    sequencename LIKE '%cash%' OR
                    sequencename LIKE '%bank%' OR  
                    sequencename LIKE '%ledger%' OR
                    sequencename LIKE '%trial%' OR
                    sequencename LIKE '%capital%' OR
                    sequencename LIKE '%audit%'
                )
            """)
            
            sequences = cursor.fetchall()
            
            for schema, sequence_name, start_value in sequences:
                try:
                    cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1")
                    print(f"   ✅ Reset {sequence_name}")
                except Exception as e:
                    print(f"   ❌ {sequence_name}: {e}")
                    
        except Exception as e:
            print(f"❌ Error resetting sequences: {e}")

def main():
    """Main execution function"""
    print("🚀 PostgreSQL Production Database Cleaner")
    print("⚠️  WARNING: This will permanently delete transaction data!")
    print("✅ Master data (accounts, entities, currencies, users) will be preserved")
    print()
    
    # Connect to database
    conn = get_connection()
    
    try:
        # Show current data
        has_data = show_current_data(conn)
        
        if not has_data:
            print("✅ No transaction data found - database is already clean")
            return
        
        # Confirmation prompts
        print("\n🤔 This will delete ALL transaction data from production!")
        print("   • Cash receipts and payments") 
        print("   • Bank transactions")
        print("   • Ledger entries")
        print("   • Trial balances")
        print("   • Capital contributions") 
        print("   • Investment history")
        print("   • Audit logs")
        
        confirm1 = input("\n❓ Type 'YES' to proceed: ")
        if confirm1 != 'YES':
            print("❌ Operation cancelled")
            return
            
        confirm2 = input("❓ Final confirmation - Type 'DELETE' (in caps): ")
        if confirm2 != 'DELETE':
            print("❌ Operation cancelled")
            return
        
        print("\n🚀 Starting cleanup process...")
        
        try:
            # Clear data (transaction already started with autocommit=False)
            summary = clear_transaction_data(conn)
            
            # Reset sequences
            reset_sequences(conn)
            
            # Commit transaction
            conn.commit()
            print("\n✅ Transaction committed successfully")
            
            # Show final summary
            print("\n" + "=" * 70)
            print("✅ DATABASE CLEANUP COMPLETED")
            print("=" * 70)
            
            total_deleted = sum(v for v in summary.values() if isinstance(v, int))
            print(f"📊 Total records deleted: {total_deleted:,}")
            print("🎯 Database is ready for customer delivery")
            print("🔢 Sequences reset to start from 1")
            
            print("\n📋 Deletion Summary:")
            for table, count in summary.items():
                if isinstance(count, int) and count > 0:
                    print(f"   {table:35}: {count:8,} records")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error occurred - transaction rolled back: {e}")
            sys.exit(1)
            
    finally:
        conn.close()

if __name__ == "__main__":
    main()