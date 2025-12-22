#!/usr/bin/env python3
"""
Populate credit_account field for existing cash receipts
Uses PostgreSQL connection to update database
"""
import psycopg2
import sys
from datetime import datetime

# PostgreSQL Connection
DB_HOST = '192.168.20.11'
DB_PORT = 5432
DB_NAME = 'tradifyerp_db'
DB_USER = 'tradifyerp_user'
DB_PASSWORD = 'Tradify@PostgreSQL2024'

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

def get_cash_account_id(conn):
    """Get the Cash account ID (1000)"""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM accounting_account 
            WHERE account_number = '1000' 
            LIMIT 1
        """)
        result = cur.fetchone()
        cur.close()
        
        if result:
            return result[0]
        else:
            print("❌ Cash account (1000) not found in database")
            return None
    except Exception as e:
        print(f"❌ Error finding cash account: {e}")
        return None

def update_cash_receipts(conn):
    """Update cash receipts with credit_account"""
    try:
        cash_account_id = get_cash_account_id(conn)
        if not cash_account_id:
            return False
        
        cur = conn.cursor()
        
        # Update receipts that don't have credit_account set
        print(f"\n📝 Updating cash receipts with Cash account (ID: {cash_account_id})...")
        
        cur.execute(f"""
            UPDATE accounting_cashreceiptline
            SET credit_account_id = {cash_account_id}
            WHERE credit_account_id IS NULL
        """)
        
        updated_count = cur.rowcount
        conn.commit()
        cur.close()
        
        if updated_count > 0:
            print(f"✅ Updated {updated_count} cash receipts")
            return True
        else:
            print("ℹ️  No cash receipts needed updating (all have credit_account set)")
            return True
    except Exception as e:
        print(f"❌ Error updating cash receipts: {e}")
        conn.rollback()
        return False

def verify_updates(conn):
    """Verify that updates were successful"""
    try:
        cur = conn.cursor()
        
        # Check how many receipts now have credit_account
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN credit_account_id IS NOT NULL THEN 1 ELSE 0 END) as with_account,
                SUM(CASE WHEN credit_account_id IS NULL THEN 1 ELSE 0 END) as without_account
            FROM accounting_cashreceiptline
        """)
        
        result = cur.fetchone()
        cur.close()
        
        if result:
            total, with_account, without_account = result
            print(f"\n📊 Verification Results:")
            print(f"   Total Receipts: {total}")
            print(f"   With Credit Account: {with_account}")
            print(f"   Without Credit Account: {without_account or 0}")
            
            if without_account == 0:
                print("\n✅ All receipts now have credit_account set!")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Error verifying updates: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("  Cash Receipt Credit Account Population Script")
    print("=" * 60)
    print(f"\n🔧 Database: {DB_NAME}")
    print(f"   Host: {DB_HOST}:{DB_PORT}")
    print(f"   User: {DB_USER}")
    
    conn = connect_db()
    print("✅ Connected to database\n")
    
    # Perform update
    success = update_cash_receipts(conn)
    
    if success:
        # Verify updates
        verify_updates(conn)
    
    conn.close()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Script completed successfully!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Script encountered errors!")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
