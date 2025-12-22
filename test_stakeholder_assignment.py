#!/usr/bin/env python3
"""
Test stakeholder auto-assignment by updating receipt ID 12
"""
import os
import sys
import django

# Add the Django project path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import transaction
from accounting.models import CashReceiptLine, Stakeholder

def test_stakeholder_assignment():
    """Test auto-assignment of stakeholder for receipt ID 12"""
    try:
        with transaction.atomic():
            receipt = CashReceiptLine.objects.get(id=12)
            print(f"Receipt ID: {receipt.id}")
            print(f"Account: {receipt.account.name} (ID: {receipt.account.id})")
            print(f"Current stakeholder_id: {receipt.stakeholder_id}")
            
            if receipt.account and receipt.account.name:
                account_name = receipt.account.name.strip()
                print(f"Account name: '{account_name}'")
                
                # Extract stakeholder name from account name
                if ' - Capital' in account_name:
                    stakeholder_name = account_name.replace(' - Capital', '').strip()
                    print(f"Extracted stakeholder name: '{stakeholder_name}'")
                    
                    # Find matching stakeholders
                    stakeholders = Stakeholder.objects.filter(entity=receipt.entity)
                    print(f"Total stakeholders in entity: {stakeholders.count()}")
                    
                    for stakeholder in stakeholders:
                        print(f"  - {stakeholder.id}: {stakeholder.full_name} (type: {stakeholder.stakeholder_type})")
                        if stakeholder.full_name == stakeholder_name:
                            print(f"✅ EXACT MATCH FOUND: {stakeholder.full_name}")
                            
                            # Update the receipt
                            receipt.stakeholder = stakeholder
                            receipt.save()
                            
                            print(f"✅ Updated receipt {receipt.id} with stakeholder {stakeholder.id}")
                            return True
                    
                    print("❌ No exact match found")
                else:
                    print("❌ Account name doesn't contain ' - Capital'")
            
            return False
            
    except CashReceiptLine.DoesNotExist:
        print(f"❌ Receipt 12 not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    test_stakeholder_assignment()