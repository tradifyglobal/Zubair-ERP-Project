#!/usr/bin/env python3
"""
Create missing CapitalContribution records for authorized cash receipts
Uses direct PostgreSQL connection
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
import sys

# Database connection
DB_CONFIG = {
    'host': '192.168.20.11',
    'port': 5432,
    'database': 'tradifyerp_db',
    'user': 'tradifyerp_user',
    'password': 'Tradify@PostgreSQL2024'
}

def get_connection():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def find_stakeholder_by_account(conn, account_id, entity_id):
    """Find stakeholder that matches the account name"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get account name
        cur.execute(
            "SELECT name, account_number FROM accounting_account WHERE id = %s",
            (account_id,)
        )
        account = cur.fetchone()
        if not account:
            return None
        
        account_name = account['name'].lower()
        print(f"    Account: {account['account_number']} - {account['name']}")
        
        # Extract possible stakeholder names from account name
        # e.g., "3000-16 Syed Safi - Capital" -> "Syed Safi"
        name_part = account_name.replace(account['account_number'], '').replace('- capital', '').strip()
        
        # Find stakeholder by matching name
        cur.execute("""
            SELECT id, first_name, last_name, company_name, stakeholder_type
            FROM accounting_stakeholder
            WHERE entity_id = %s
            AND (
                CONCAT(first_name, ' ', last_name) ILIKE %s
                OR last_name ILIKE %s
                OR company_name ILIKE %s
            )
            LIMIT 1
        """, (entity_id, f'%{name_part}%', f'%{name_part}%', f'%{name_part}%'))
        
        stakeholder = cur.fetchone()
        cur.close()
        return stakeholder
    except Exception as e:
        print(f"    ❌ Error finding stakeholder: {e}")
        cur.close()
        return None

def create_capital_contribution(conn, receipt):
    """Create CapitalContribution record for a cash receipt"""
    cur = conn.cursor()
    
    try:
        # Insert CapitalContribution
        sql = """
            INSERT INTO accounting_capitalcontribution (
                entity_id, stakeholder_id, amount, currency_id,
                contribution_date, status, workflow_status, 
                description, reference, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
        """
        
        cur.execute(sql, (
            receipt['entity_id'],
            receipt['stakeholder_id'],
            receipt['debit_amount'],
            receipt['currency_id'],
            receipt['date'],
            'COMPLETED',
            'APPROVED',
            f"Cash Receipt: {receipt['description']}",
            f"CASH-RECEIPT-{receipt['id']}"
        ))
        
        # Update cash receipt to mark capital contribution as posted
        cur.execute("""
            UPDATE accounting_cashreceiptline
            SET is_capital_contribution_posted = true
            WHERE id = %s
        """, (receipt['id'],))
        
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        conn.rollback()
        print(f"    ❌ Error creating CapitalContribution: {e}")
        cur.close()
        return False

def process_cash_receipts():
    """Process all authorized cash receipts"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get all authorized cash receipts without capital contribution posted
        sql = """
            SELECT 
                cr.id, cr.date, cr.description, cr.debit_amount, 
                cr.credit_amount, cr.entity_id, cr.account_id, 
                cr.currency_id, cr.stakeholder_id, cr.is_capital_contribution_posted
            FROM accounting_cashreceiptline cr
            WHERE cr.workflow_status = 'AUTHORIZED'
            AND cr.is_capital_contribution_posted = false
            ORDER BY cr.date DESC
        """
        
        cur.execute(sql)
        receipts = cur.fetchall()
        
        print(f"\n📊 Found {len(receipts)} authorized cash receipts without capital contribution\n")
        
        created_count = 0
        updated_count = 0
        
        for receipt in receipts:
            print(f"Receipt #{receipt['id']}: {receipt['description']} ({receipt['date']})")
            print(f"  Amount: {receipt['debit_amount']}")
            
            # If stakeholder already set, just create the contribution
            if receipt['stakeholder_id']:
                print(f"  ✅ Stakeholder already set (ID: {receipt['stakeholder_id']})")
                if create_capital_contribution(conn, receipt):
                    created_count += 1
                    print(f"  ✅ CapitalContribution created")
            else:
                # Try to find and set stakeholder
                stakeholder = find_stakeholder_by_account(conn, receipt['account_id'], receipt['entity_id'])
                
                if stakeholder:
                    stakeholder_name = f"{stakeholder['first_name']} {stakeholder['last_name']}" if stakeholder['stakeholder_type'] == 'INDIVIDUAL' else stakeholder['company_name']
                    print(f"  ✅ Matched to stakeholder: {stakeholder_name}")
                    
                    # Update receipt with stakeholder
                    cur.execute("""
                        UPDATE accounting_cashreceiptline
                        SET stakeholder_id = %s
                        WHERE id = %s
                    """, (stakeholder['id'], receipt['id']))
                    conn.commit()
                    updated_count += 1
                    
                    # Update receipt object for creation
                    receipt['stakeholder_id'] = stakeholder['id']
                    
                    # Create capital contribution
                    if create_capital_contribution(conn, receipt):
                        created_count += 1
                        print(f"  ✅ CapitalContribution created")
                else:
                    print(f"  ❌ No matching stakeholder found")
            
            print()
        
        print("=" * 60)
        print(f"✅ Summary:")
        print(f"   Stakeholders linked: {updated_count}")
        print(f"   CapitalContributions created: {created_count}")
        print("=" * 60)
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("\n🔍 Cash Receipt to CapitalContribution Converter")
    print("=" * 60)
    
    try:
        process_cash_receipts()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
