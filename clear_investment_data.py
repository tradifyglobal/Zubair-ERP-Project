#!/usr/bin/env python3
"""
Clear Investment Transaction Data Only
=====================================
Clear only investment transactions, preserve stakeholder master data
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

def clear_investment_transactions():
    """Clear investment transaction data but preserve stakeholder master data"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("🎯 Clearing Investment Transaction Data")
    print("=" * 50)
    print("⚠️  Preserving stakeholder master data (names, contact info)")
    print("🗑️  Clearing investment amounts, limits, and transactions")
    
    try:
        with conn.cursor() as cursor:
            # 1. Reset investment limits to zero
            cursor.execute("SELECT COUNT(*) FROM accounting_shareholderinvestmentlimit")
            limit_count = cursor.fetchone()[0]
            
            if limit_count > 0:
                print(f"\n📊 Resetting {limit_count} investment limits...")
                cursor.execute("""
                    UPDATE accounting_shareholderinvestmentlimit 
                    SET target_investment_amount = 0,
                        total_invested = 0,
                        balance_to_invest = 0
                """)
                conn.commit()
                print("   ✅ Investment limits reset to zero")
            
            # 2. Check if there are any shareholder app tables with investment data
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'shareholder_%'
                AND table_name NOT LIKE '%stakeholder%'
                ORDER BY table_name
            """)
            
            shareholder_tables = [row[0] for row in cursor.fetchall()]
            
            if shareholder_tables:
                print(f"\n🔍 Found {len(shareholder_tables)} shareholder app tables:")
                
                for table in shareholder_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"   {table:35}: {count:8,} records")
                        
                        if count > 0 and 'contribution' in table.lower():
                            cursor.execute(f"DELETE FROM {table}")
                            deleted = cursor.rowcount
                            conn.commit()
                            print(f"   ✅ Cleared {deleted} contribution records")
                            
                    except Exception as e:
                        print(f"   ❌ {table}: {e}")
            
            # 3. Check for any remaining investment-related data
            print(f"\n🔍 Checking for remaining investment data...")
            
            # Look for tables with 'investment' in the name
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%investment%'
                ORDER BY table_name
            """)
            
            investment_tables = [row[0] for row in cursor.fetchall()]
            
            for table in investment_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"   {table:35}: {count:8,} records")
                        
                        # Clear investment transaction data but not master config
                        if 'history' in table.lower() or 'transaction' in table.lower():
                            cursor.execute(f"DELETE FROM {table}")
                            deleted = cursor.rowcount
                            conn.commit()
                            print(f"   ✅ Cleared {deleted} investment transaction records")
                            
                except Exception as e:
                    print(f"   ❌ {table}: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_cleanup():
    """Verify the cleanup results"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print(f"\n🔍 Verification Results:")
    print("=" * 50)
    
    with conn.cursor() as cursor:
        # Check investment limits
        cursor.execute("""
            SELECT COUNT(*) as count,
                   SUM(target_investment_amount) as target_total,
                   SUM(total_invested) as invested_total
            FROM accounting_shareholderinvestmentlimit
        """)
        
        result = cursor.fetchone()
        print(f"Investment Limits: {result[0]} records")
        print(f"  Total Target Amount: {result[1] or 0}")
        print(f"  Total Invested: {result[2] or 0}")
        
        # Check stakeholders (should be preserved)
        cursor.execute("SELECT COUNT(*) FROM accounting_stakeholder")
        stakeholder_count = cursor.fetchone()[0]
        print(f"Stakeholders (preserved): {stakeholder_count} records")
        
        # Check for any remaining contribution/investment records
        tables_to_check = [
            'shareholder_capitalcontribution',
            'shareholder_investment',
            'shareholder_investmenthistory'
        ]
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"⚠️  {table}: {count} records still exist")
                else:
                    print(f"✅ {table}: Clean")
            except:
                # Table doesn't exist, which is fine
                pass
    
    conn.close()

def main():
    """Main execution"""
    print("🧹 Investment Data Cleaner (Preserve Master Data)")
    print("=" * 60)
    
    confirm = input("❓ Clear investment transactions but preserve stakeholders? (YES/no): ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    clear_investment_transactions()
    verify_cleanup()
    
    print(f"\n✅ Investment transaction data cleanup completed!")
    print("🎯 Investment report should now show zero amounts")
    print("📋 Stakeholder master data preserved")

if __name__ == "__main__":
    main()
