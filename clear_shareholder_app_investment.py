#!/usr/bin/env python3
"""
Clear Shareholder App Investment Data
===================================
Check and clear investment data from shareholder app specifically
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

def clear_shareholder_app_data():
    """Clear all investment data from shareholder app tables"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("🧹 Clearing Shareholder App Investment Data")
    print("=" * 50)
    
    with conn.cursor() as cursor:
        # Find all shareholder app tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'shareholder_%'
            ORDER BY table_name
        """)
        
        shareholder_tables = [row[0] for row in cursor.fetchall()]
        
        if not shareholder_tables:
            print("No shareholder app tables found")
            return
        
        print(f"Found {len(shareholder_tables)} shareholder app tables:")
        
        tables_to_clear = []
        
        for table in shareholder_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                print(f"   {table:35}: {count:8,} records")
                
                if count > 0:
                    # Check if it's investment/contribution data (not stakeholder master data)
                    if any(keyword in table.lower() for keyword in ['investment', 'contribution', 'capital']):
                        tables_to_clear.append((table, count))
                        print(f"      → Will clear (investment data)")
                    elif 'stakeholder' in table.lower():
                        print(f"      → Will preserve (master data)")
                    else:
                        # Check table structure to see if it has investment fields
                        cursor.execute(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}'
                            AND (
                                column_name LIKE '%amount%' OR 
                                column_name LIKE '%investment%' OR
                                column_name LIKE '%currency%' OR
                                column_name LIKE '%exchange%'
                            )
                        """)
                        
                        investment_columns = [row[0] for row in cursor.fetchall()]
                        
                        if investment_columns:
                            tables_to_clear.append((table, count))
                            print(f"      → Will clear (has investment fields: {', '.join(investment_columns)})")
                        else:
                            print(f"      → Will preserve (no investment fields)")
                
            except Exception as e:
                print(f"   {table:35}: Error - {e}")
        
        if not tables_to_clear:
            print("\n✅ No shareholder investment data found to clear")
            return
        
        print(f"\n🗑️  Tables to clear:")
        for table, count in tables_to_clear:
            print(f"   {table}: {count} records")
        
        confirm = input(f"\n❓ Clear {len(tables_to_clear)} shareholder investment tables? (YES/no): ")
        if confirm != 'YES':
            print("❌ Operation cancelled")
            return
        
        # Clear the tables
        total_cleared = 0
        
        for table, expected_count in tables_to_clear:
            try:
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
        
        print(f"\n✅ Cleared {total_cleared} total shareholder investment records")
    
    conn.close()

def final_verification():
    """Final verification of all investment-related data"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print(f"\n🔍 Final Verification - All Investment Data")
    print("=" * 50)
    
    with conn.cursor() as cursor:
        # Check all possible investment data sources
        tables_to_check = [
            'accounting_capitalcontribution',
            'accounting_shareholderinvestmentlimit', 
            'accounting_shareholderpaymentcommitment',
            'shareholder_capitalcontribution',
            'shareholder_investment',
            'shareholder_investmenthistory'
        ]
        
        total_remaining = 0
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"⚠️  {table:35}: {count:8,} records REMAIN")
                    total_remaining += count
                else:
                    print(f"✅ {table:35}: Clean")
                    
            except:
                # Table doesn't exist
                print(f"➖ {table:35}: Does not exist")
        
        # Check stakeholders preserved
        try:
            cursor.execute("SELECT COUNT(*) FROM accounting_stakeholder")
            stakeholder_count = cursor.fetchone()[0]
            print(f"📋 Stakeholders preserved: {stakeholder_count} records")
        except:
            pass
    
    conn.close()
    
    if total_remaining == 0:
        print(f"\n🎉 SUCCESS: All investment data completely cleared!")
        print("✅ Investment report should now be completely empty")
        print("📋 Stakeholder master data preserved")
    else:
        print(f"\n⚠️  WARNING: {total_remaining} investment records still remain")

if __name__ == "__main__":
    clear_shareholder_app_data()
    final_verification()