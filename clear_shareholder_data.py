#!/usr/bin/env python3
"""
Clear Remaining Shareholder Investment Data
==========================================
Check and clear all remaining investment/shareholder data
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

def find_shareholder_tables():
    """Find all tables containing shareholder/investment data"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Find all tables that might contain shareholder/investment data
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND (
                table_name LIKE '%shareholder%' OR 
                table_name LIKE '%investment%' OR
                table_name LIKE '%capital%' OR 
                table_name LIKE '%contribution%' OR
                table_name LIKE '%stakeholder%'
            )
            ORDER BY table_name
        """)
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        return tables

def check_table_data(tables):
    """Check what data exists in shareholder tables"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("🔍 Checking Shareholder/Investment Tables:")
    print("=" * 60)
    
    tables_with_data = []
    
    with conn.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:40}: {count:8,} records")
                
                if count > 0:
                    tables_with_data.append((table, count))
                    
                    # Show sample data for tables with records
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    if rows:
                        print(f"   Sample columns: {', '.join(columns[:5])}")
                        
            except Exception as e:
                print(f"{table:40}: Error - {e}")
    
    conn.close()
    return tables_with_data

def clear_shareholder_data(tables_with_data):
    """Clear remaining shareholder investment data"""
    if not tables_with_data:
        print("\n✅ No shareholder data found to clear")
        return
    
    print(f"\n🧹 Found {len(tables_with_data)} tables with data to clear:")
    for table, count in tables_with_data:
        print(f"   {table}: {count} records")
    
    confirm = input(f"\n❓ Clear all {sum(count for _, count in tables_with_data)} records? (YES/no): ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("\n🗑️  Clearing shareholder investment data...")
    
    total_cleared = 0
    
    try:
        for table, expected_count in tables_with_data:
            with conn.cursor() as cursor:
                try:
                    # Clear the table
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
        
        print(f"\n✅ Cleared {total_cleared} total records")
        
    except Exception as e:
        print(f"❌ Error during clearing: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main function"""
    print("🔍 Shareholder Investment Data Cleaner")
    print("=" * 50)
    
    # Find all shareholder-related tables
    tables = find_shareholder_tables()
    
    if not tables:
        print("No shareholder tables found")
        return
    
    # Check what data exists
    tables_with_data = check_table_data(tables)
    
    # Clear the data
    clear_shareholder_data(tables_with_data)
    
    # Final verification
    print(f"\n🔍 Final verification:")
    final_tables = check_table_data(tables)
    
    if not final_tables:
        print("\n✅ SUCCESS: All shareholder investment data cleared!")
        print("🎯 Investment report should now be empty")
    else:
        print(f"\n⚠️  WARNING: Some data still remains")

if __name__ == "__main__":
    main()