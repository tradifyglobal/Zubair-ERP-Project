#!/usr/bin/env python3
"""
Find and Clear Investment Report Source Data
==========================================
Find the exact tables feeding the investment report and clear them completely
"""

import psycopg2

# Production PostgreSQL connection details
DB_CONFIG = {
    'host': '192.168.2.59',
    'database': 'tradifyerp_db',
    'user': 'tradifyerp_user',
    'password': 'Tradify@PostgreSQL2024',
    'port': 5432
}

def find_investment_report_sources():
    """Find all possible sources for investment report data"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("🔍 Finding Investment Report Data Sources")
    print("=" * 60)
    
    with conn.cursor() as cursor:
        # Look for tables with currency and exchange_rate columns
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND (column_name LIKE '%currency%' OR column_name LIKE '%exchange%')
            AND (
                table_name LIKE '%investment%' OR 
                table_name LIKE '%capital%' OR 
                table_name LIKE '%contribution%' OR
                table_name LIKE '%shareholder%' OR
                table_name LIKE '%stakeholder%'
            )
            ORDER BY table_name, column_name
        """)
        
        currency_tables = {}
        for table_name, column_name in cursor.fetchall():
            if table_name not in currency_tables:
                currency_tables[table_name] = []
            currency_tables[table_name].append(column_name)
        
        print("Tables with currency/exchange rate fields:")
        for table, columns in currency_tables.items():
            print(f"   {table}: {', '.join(columns)}")
        
        # Check each table for actual data
        print(f"\nChecking data in currency-related tables:")
        tables_with_data = []
        
        for table in currency_tables.keys():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"   {table:40}: {count:8,} records")
                    
                    # Get sample data to see structure
                    cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    if rows:
                        tables_with_data.append((table, count, columns, rows))
                        
                        # Show key fields that might be feeding the report
                        key_fields = [col for col in columns if any(keyword in col.lower() 
                                    for keyword in ['currency', 'exchange', 'amount', 'investment', 'status'])]
                        if key_fields:
                            print(f"      Key fields: {', '.join(key_fields)}")
                else:
                    print(f"   {table:40}: Empty")
                    
            except Exception as e:
                print(f"   {table:40}: Error - {e}")
    
    conn.close()
    return tables_with_data

def clear_investment_report_data(tables_with_data):
    """Clear the actual investment report source data"""
    if not tables_with_data:
        print("\n✅ No investment data found to clear")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    print(f"\n🧹 Clearing Investment Report Source Data")
    print("=" * 60)
    
    # Tables that should be completely cleared (not just amounts zeroed)
    tables_to_clear_completely = []
    
    for table, count, columns, sample_rows in tables_with_data:
        # Check if this table contains actual investment transactions
        has_investment_data = any(col for col in columns if any(keyword in col.lower() 
                                for keyword in ['investment', 'contribution', 'amount', 'exchange']))
        
        # Skip master data tables (entities, stakeholders, etc.)
        is_master_data = 'stakeholder' in table.lower() and 'investment' not in table.lower()
        
        if has_investment_data and not is_master_data:
            tables_to_clear_completely.append((table, count))
            print(f"   Will clear: {table} ({count} records)")
        else:
            print(f"   Will preserve: {table} (master data)")
    
    if not tables_to_clear_completely:
        print("   No transaction tables found to clear")
        return
    
    confirm = input(f"\n❓ Clear {len(tables_to_clear_completely)} investment data tables? (YES/no): ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    try:
        total_cleared = 0
        
        for table, expected_count in tables_to_clear_completely:
            with conn.cursor() as cursor:
                try:
                    # Clear the entire table
                    cursor.execute(f"DELETE FROM {table}")
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    # Verify
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    remaining = cursor.fetchone()[0]
                    
                    print(f"   ✅ {table}: Deleted {deleted_count}, {remaining} remain")
                    total_cleared += deleted_count
                    
                except Exception as e:
                    print(f"   ❌ {table}: Error - {e}")
                    conn.rollback()
        
        print(f"\n✅ Cleared {total_cleared} total investment records")
        
    except Exception as e:
        print(f"❌ Error during clearing: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main function"""
    print("🎯 Investment Report Source Data Cleaner")
    print("=" * 50)
    
    # Find source tables
    tables_with_data = find_investment_report_sources()
    
    # Clear the data
    clear_investment_report_data(tables_with_data)
    
    print(f"\n🔍 Final verification - checking for remaining investment data...")
    
    # Re-check to confirm clearing
    remaining_tables = find_investment_report_sources()
    
    if not any(count > 0 for _, count, _, _ in remaining_tables if 'investment' in _[0] or 'contribution' in _[0]):
        print("\n✅ SUCCESS: All investment report data cleared!")
        print("🎯 Investment report should now be completely empty")
    else:
        print("\n⚠️  Some investment data may still remain")

if __name__ == "__main__":
    main()