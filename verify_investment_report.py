#!/usr/bin/env python3
"""
Verify Investment Report Data
===========================
Check what data the investment report will show
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

def check_investment_report_data():
    """Check what data will appear on investment report"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("🔍 Investment Report Data Check")
    print("=" * 50)
    
    with conn.cursor() as cursor:
        # Check stakeholders and their investment limits
        cursor.execute("""
            SELECT 
                s.first_name,
                s.last_name,
                s.status,
                COALESCE(sil.target_investment_amount, 0) as target_amount,
                COALESCE(sil.total_invested, 0) as total_invested,
                COALESCE(sil.balance_to_invest, 0) as balance_to_invest
            FROM accounting_stakeholder s
            LEFT JOIN accounting_shareholderinvestmentlimit sil ON s.id = sil.stakeholder_id
            ORDER BY s.first_name, s.last_name
        """)
        
        results = cursor.fetchall()
        
        print(f"Found {len(results)} stakeholders:")
        print("-" * 80)
        print(f"{'Name':<30} {'Status':<10} {'Target':<12} {'Invested':<12} {'Balance':<12}")
        print("-" * 80)
        
        total_target = 0
        total_invested = 0
        
        for row in results:
            name = f"{row[0]} {row[1]}"
            status = row[2]
            target = float(row[3] or 0)
            invested = float(row[4] or 0)
            balance = float(row[5] or 0)
            
            print(f"{name:<30} {status:<10} {target:<12,.2f} {invested:<12,.2f} {balance:<12,.2f}")
            
            total_target += target
            total_invested += invested
        
        print("-" * 80)
        print(f"{'TOTALS':<30} {'':<10} {total_target:<12,.2f} {total_invested:<12,.2f}")
        
        # Check for any capital contributions
        cursor.execute("SELECT COUNT(*) FROM accounting_capitalcontribution")
        contrib_count = cursor.fetchone()[0]
        
        print(f"\nCapital Contributions: {contrib_count} records")
        
        # Check shareholder app tables if they exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'shareholder_%'
            ORDER BY table_name
        """)
        
        shareholder_tables = [row[0] for row in cursor.fetchall()]
        
        if shareholder_tables:
            print(f"\nShareholder App Tables:")
            for table in shareholder_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   {table:<35}: {count:8,} records")
                except:
                    print(f"   {table:<35}: Error")
    
    conn.close()
    
    if total_invested == 0 and total_target == 0:
        print(f"\n✅ SUCCESS: Investment report should show zero amounts")
        print("🎯 All investment data cleared while preserving stakeholders")
    else:
        print(f"\n⚠️  WARNING: Some investment amounts still showing")

if __name__ == "__main__":
    check_investment_report_data()
