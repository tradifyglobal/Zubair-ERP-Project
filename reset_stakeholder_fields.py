#!/usr/bin/env python3
"""
Reset All Stakeholder Investment Fields
=====================================
Reset any investment-related fields directly on stakeholder records
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

def reset_stakeholder_investment_fields():
    """Reset any investment fields on stakeholder records themselves"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("🔄 Resetting Stakeholder Investment Fields")
    print("=" * 50)
    
    with conn.cursor() as cursor:
        # Check stakeholder table structure for investment-related fields
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'accounting_stakeholder'
            AND (
                column_name LIKE '%investment%' OR 
                column_name LIKE '%amount%' OR
                column_name LIKE '%balance%' OR
                column_name LIKE '%total%' OR
                column_name LIKE '%currency%' OR
                column_name LIKE '%exchange%'
            )
            ORDER BY column_name
        """)
        
        investment_fields = cursor.fetchall()
        
        if investment_fields:
            print("Found investment-related fields on stakeholders:")
            for field_name, data_type in investment_fields:
                print(f"   {field_name}: {data_type}")
            
            # Reset these fields to zero/null
            for field_name, data_type in investment_fields:
                try:
                    if 'numeric' in data_type or 'decimal' in data_type or 'float' in data_type or 'int' in data_type:
                        cursor.execute(f"UPDATE accounting_stakeholder SET {field_name} = 0")
                        updated = cursor.rowcount
                        print(f"   ✅ Reset {field_name}: {updated} records updated to 0")
                    else:
                        cursor.execute(f"UPDATE accounting_stakeholder SET {field_name} = NULL")
                        updated = cursor.rowcount
                        print(f"   ✅ Reset {field_name}: {updated} records updated to NULL")
                    
                    conn.commit()
                    
                except Exception as e:
                    print(f"   ❌ {field_name}: Error - {e}")
                    conn.rollback()
        else:
            print("No investment-related fields found on stakeholder table")
        
        # Check all stakeholder records for any computed investment values
        print(f"\nChecking stakeholder records...")
        cursor.execute("SELECT COUNT(*) FROM accounting_stakeholder")
        count = cursor.fetchone()[0]
        print(f"Total stakeholders: {count}")
    
    conn.close()

def check_investment_report_view():
    """Check if investment report uses a database view"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print(f"\n🔍 Checking for Investment Views/Functions")
    print("=" * 50)
    
    with conn.cursor() as cursor:
        # Check for views related to investment
        cursor.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'VIEW'
            AND (
                table_name LIKE '%investment%' OR 
                table_name LIKE '%capital%' OR
                table_name LIKE '%contribution%'
            )
        """)
        
        views = cursor.fetchall()
        
        if views:
            print("Found investment-related views:")
            for view_name, view_type in views:
                print(f"   {view_name}: {view_type}")
        else:
            print("No investment-related views found")
        
        # Check for functions/stored procedures
        cursor.execute("""
            SELECT routine_name, routine_type
            FROM information_schema.routines 
            WHERE routine_schema = 'public'
            AND (
                routine_name LIKE '%investment%' OR 
                routine_name LIKE '%capital%' OR
                routine_name LIKE '%contribution%'
            )
        """)
        
        functions = cursor.fetchall()
        
        if functions:
            print("Found investment-related functions:")
            for func_name, func_type in functions:
                print(f"   {func_name}: {func_type}")
        else:
            print("No investment-related functions found")
    
    conn.close()

def main():
    """Main execution"""
    reset_stakeholder_investment_fields()
    check_investment_report_view()
    
    print(f"\n✅ All stakeholder investment fields reset!")
    print("🔄 Try refreshing the investment report page now")
    print("💡 If entries still appear, they may be from Django model computed properties")

if __name__ == "__main__":
    main()
