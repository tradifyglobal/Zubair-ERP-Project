#!/usr/bin/env python3
"""
Test comprehensive stakeholder auto-assignment logic
"""
import os
import sys
import django

# Add the Django project path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import transaction
from accounting.models import CashReceiptLine, Stakeholder, Account

def test_auto_assignment_logic():
    """Test the stakeholder auto-assignment logic with different account patterns"""
    
    # Get some test accounts
    capital_accounts = Account.objects.filter(
        entity_id=7,
        name__contains='Capital'
    ).order_by('account_number')[:5]
    
    print("🧪 Testing Stakeholder Auto-Assignment Logic")
    print("=" * 50)
    
    for account in capital_accounts:
        print(f"\n📋 Testing Account: {account.name} (ID: {account.id})")
        
        # Test the matching logic
        stakeholder = find_stakeholder_for_account(account)
        
        if stakeholder:
            print(f"✅ MATCH FOUND: {stakeholder.full_name} (ID: {stakeholder.id})")
        else:
            print(f"❌ NO MATCH FOUND")
            
            # Show available stakeholders for debugging
            stakeholders = Stakeholder.objects.filter(entity=account.entity)
            print(f"   Available stakeholders:")
            for s in stakeholders[:3]:
                print(f"   - {s.full_name}")

def find_stakeholder_for_account(account):
    """Find stakeholder that matches the account name pattern."""
    if not account or not account.name:
        return None
        
    account_name = account.name.strip()
    
    # Extract stakeholder name from account name patterns like:
    # "Dr. Irfan Mohammed - Capital" -> "Dr. Irfan Mohammed"
    # "Javeed Baba - Capital" -> "Javeed Baba"
    if ' - Capital' in account_name:
        stakeholder_name = account_name.replace(' - Capital', '').strip()
    else:
        return None
    
    print(f"   Extracted name: '{stakeholder_name}'")
    
    # Try to find matching stakeholder by name
    # First, try exact match by full name
    stakeholders = Stakeholder.objects.filter(entity=account.entity)
    
    for stakeholder in stakeholders:
        if stakeholder.full_name == stakeholder_name:
            return stakeholder
    
    # If no exact match, try partial matching
    # Split the name and try to match first/last name combinations
    name_parts = stakeholder_name.split()
    if len(name_parts) >= 2:
        first_part = name_parts[0]
        last_part = name_parts[-1]
        
        # Try to match by first and last name
        for stakeholder in stakeholders:
            if (stakeholder.first_name and stakeholder.last_name and 
                first_part.lower() in stakeholder.first_name.lower() and 
                last_part.lower() in stakeholder.last_name.lower()):
                return stakeholder
    
    return None

if __name__ == '__main__':
    test_auto_assignment_logic()