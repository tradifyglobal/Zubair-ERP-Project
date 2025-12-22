#!/usr/bin/env python3
import sqlite3
import os

db_path = '/var/www/tradifyerp/db.sqlite3'

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔄 Populating credit_account for cash receipts...")
print("=" * 60)

try:
    # Get all entities
    cursor.execute("SELECT id, name FROM accounting_entity WHERE is_active = 1")
    entities = cursor.fetchall()
    
    total_updated = 0
    
    for entity_id, entity_name in entities:
        print(f"\n📍 Processing entity: {entity_name} (ID: {entity_id})")
        
        # Find Cash account (try 100001 first, then 1000)
        cursor.execute("""
            SELECT id, account_number, name FROM accounting_account 
            WHERE entity_id = ? AND account_number IN ('100001', '1000') 
            AND is_active = 1
            ORDER BY account_number DESC
            LIMIT 1
        """, (entity_id,))
        
        cash_account = cursor.fetchone()
        
        if not cash_account:
            print(f"   ⚠️  No cash account found (100001 or 1000)")
            continue
        
        cash_id, cash_number, cash_name = cash_account
        print(f"   ✓ Found cash account: {cash_number} - {cash_name}")
        
        # Find receipts without credit_account
        cursor.execute("""
            SELECT COUNT(*) FROM accounting_cashreceiptline 
            WHERE entity_id = ? AND credit_account_id IS NULL
        """, (entity_id,))
        
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"   ✓ All receipts already have credit_account")
            continue
        
        print(f"   📦 Found {count} receipts without credit_account")
        
        # Update them
        cursor.execute("""
            UPDATE accounting_cashreceiptline 
            SET credit_account_id = ? 
            WHERE entity_id = ? AND credit_account_id IS NULL
        """, (cash_id, entity_id))
        
        updated = cursor.rowcount
        total_updated += updated
        print(f"   ✅ Updated {updated} receipts")
    
    # Commit changes
    conn.commit()
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Updated {total_updated} total receipts")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
