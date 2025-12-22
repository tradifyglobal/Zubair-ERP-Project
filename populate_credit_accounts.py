#!/usr/bin/env python3
"""
Populate credit_account for existing cash receipts
Sets all cash receipts to use the Cash account (1000 or 100001)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashReceiptLine, Account, Entity

def populate_credit_accounts():
    """Populate credit_account for all cash receipts missing it."""
    
    print("🔄 Populating credit_account for cash receipts...")
    print("=" * 60)
    
    # Get all entities
    entities = Entity.objects.filter(is_active=True)
    total_updated = 0
    
    for entity in entities:
        print(f"\n📍 Processing entity: {entity.name}")
        
        # Try to find Cash account
        # First try 100001 (preferred)
        cash_account = Account.objects.filter(
            entity=entity,
            account_number='100001',
            is_active=True
        ).first()
        
        # If not found, try 1000
        if not cash_account:
            cash_account = Account.objects.filter(
                entity=entity,
                account_number='1000',
                is_active=True
            ).first()
        
        if not cash_account:
            print(f"   ⚠️  No cash account found (1000 or 100001)")
            continue
        
        print(f"   ✓ Found cash account: {cash_account.account_number} - {cash_account.name}")
        
        # Find receipts without credit_account
        receipts_without_credit = CashReceiptLine.objects.filter(
            entity=entity,
            credit_account__isnull=True
        )
        
        count = receipts_without_credit.count()
        if count == 0:
            print(f"   ✓ All receipts already have credit_account")
            continue
        
        print(f"   📦 Found {count} receipts without credit_account")
        
        # Update them
        updated = receipts_without_credit.update(credit_account=cash_account)
        total_updated += updated
        
        print(f"   ✅ Updated {updated} receipts")
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Updated {total_updated} total receipts")
    print("=" * 60)

if __name__ == '__main__':
    populate_credit_accounts()
