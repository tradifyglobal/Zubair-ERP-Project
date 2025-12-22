#!/usr/bin/env python3
"""
Link cash receipts to stakeholders and create missing CapitalContribution records
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution, Stakeholder, Account
from decimal import Decimal
from django.db import transaction

def match_stakeholder_to_receipt(receipt):
    """Match a stakeholder to a cash receipt based on account name."""
    # Get the debit account
    if not receipt.account:
        return None
    
    account = receipt.account
    account_name = account.name.lower()
    
    # Extract stakeholder names from account name
    # Format: "3000-16 Syed Safi - Capital"
    # We want to find "Syed Safi"
    
    # Remove account number and type suffix
    name_part = account_name.replace(account.account_number, '').replace('- capital', '').strip()
    
    if not name_part:
        return None
    
    # Try to find matching stakeholder
    stakeholders = Stakeholder.objects.filter(entity=receipt.entity)
    
    for stakeholder in stakeholders:
        full_name = stakeholder.full_name.lower() if stakeholder.full_name else ""
        company_name = stakeholder.company_name.lower() if stakeholder.company_name else ""
        
        # Check if stakeholder name is in account name
        if full_name and full_name in name_part:
            return stakeholder
        if company_name and company_name in name_part:
            return stakeholder
        
        # Check if last name is in account name
        if stakeholder.last_name and stakeholder.last_name.lower() in name_part:
            return stakeholder
    
    return None

@transaction.atomic
def process_receipts():
    """Process all cash receipts without stakeholders."""
    
    # Find all AUTHORIZED cash receipts without stakeholders
    receipts = CashReceiptLine.objects.filter(
        workflow_status='AUTHORIZED',
        stakeholder__isnull=True
    )
    
    print(f"\n📊 Found {receipts.count()} cash receipts without stakeholders\n")
    
    created_count = 0
    matched_count = 0
    
    for receipt in receipts:
        print(f"Processing: {receipt.description} ({receipt.date})")
        print(f"  Account: {receipt.account} - Amount: {receipt.debit_amount}")
        
        # Try to match stakeholder
        stakeholder = match_stakeholder_to_receipt(receipt)
        
        if stakeholder:
            print(f"  ✅ Matched to: {stakeholder.full_name or stakeholder.company_name}")
            matched_count += 1
            
            # Update receipt with stakeholder
            receipt.stakeholder = stakeholder
            receipt.save()
            
            # Check if CapitalContribution already exists
            cap_contrib = CapitalContribution.objects.filter(
                entity=receipt.entity,
                stakeholder=stakeholder,
                contribution_date=receipt.date,
                amount=receipt.debit_amount
            ).first()
            
            if not cap_contrib and not receipt.is_capital_contribution_posted:
                # Create CapitalContribution record
                try:
                    cap_contrib = CapitalContribution.objects.create(
                        entity=receipt.entity,
                        stakeholder=stakeholder,
                        amount=receipt.debit_amount,
                        currency=receipt.currency,
                        contribution_date=receipt.date,
                        status='COMPLETED',
                        workflow_status='APPROVED',
                        description=f"Cash Receipt: {receipt.description}",
                        reference=f'CASH-RECEIPT-{receipt.id}'
                    )
                    print(f"    ✅ Created CapitalContribution #{cap_contrib.id}")
                    created_count += 1
                except Exception as e:
                    print(f"    ❌ Error creating CapitalContribution: {e}")
                
                # Mark as posted
                receipt.is_capital_contribution_posted = True
                receipt.save()
            else:
                print(f"    ℹ️  CapitalContribution already exists or marked as posted")
        else:
            print(f"  ❌ No matching stakeholder found")
        
        print()
    
    print("=" * 60)
    print(f"✅ Summary:")
    print(f"   Matched to stakeholders: {matched_count}")
    print(f"   CapitalContributions created: {created_count}")
    print("=" * 60)

if __name__ == '__main__':
    print("\n🔍 Cash Receipt Stakeholder Linking Script")
    print("=" * 60)
    
    try:
        process_receipts()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
