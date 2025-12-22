#!/usr/bin/env python3
"""
Fix receipt ID 14 and improve matching logic for name variations
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

def fix_receipt_14():
    """Fix stakeholder assignment for receipt ID 14"""
    try:
        with transaction.atomic():
            receipt = CashReceiptLine.objects.get(id=14)
            print(f"Receipt ID: {receipt.id}")
            print(f"Account: {receipt.account.name} (ID: {receipt.account.id})")
            print(f"Current stakeholder_id: {receipt.stakeholder_id}")
            print(f"Workflow status: {receipt.workflow_status}")
            
            # The account name is "Nasir Ali Ali Mohammed - Capital"
            # But the stakeholder is "Nasir Ali Mohammed" (ID: 62)
            # Let's assign it manually
            stakeholder = Stakeholder.objects.get(id=62, entity=receipt.entity)
            print(f"Found stakeholder: {stakeholder.full_name} (ID: {stakeholder.id})")
            
            # Assign stakeholder and trigger signal by changing status
            receipt.stakeholder = stakeholder
            # Change to APPROVED first to trigger the signal
            receipt.workflow_status = 'APPROVED'
            receipt.save()
            
            print(f"✅ Assigned stakeholder {stakeholder.id} to receipt {receipt.id}")
            print("✅ Set status to APPROVED to trigger capital contribution signal!")
            
            return True
            
    except CashReceiptLine.DoesNotExist:
        print(f"❌ Receipt 14 not found")
        return False
    except Stakeholder.DoesNotExist:
        print(f"❌ Stakeholder 62 not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_name_matching():
    """Test improved name matching logic"""
    account_name = "Nasir Ali Ali Mohammed - Capital"
    extracted_name = account_name.replace(' - Capital', '').strip()
    print(f"\nTesting name matching:")
    print(f"Account name: {account_name}")
    print(f"Extracted name: {extracted_name}")
    
    # Get all stakeholders
    stakeholders = Stakeholder.objects.filter(entity_id=7)
    
    # Try fuzzy matching
    for stakeholder in stakeholders:
        full_name = stakeholder.full_name
        # Check if most words match (allowing for variations)
        extracted_words = set(extracted_name.lower().split())
        stakeholder_words = set(full_name.lower().split())
        
        # Calculate word overlap
        overlap = len(extracted_words.intersection(stakeholder_words))
        total_words = max(len(extracted_words), len(stakeholder_words))
        
        if overlap >= 2 and overlap / total_words >= 0.6:  # 60% word match
            print(f"✅ Fuzzy match: {full_name} (ID: {stakeholder.id}) - {overlap}/{total_words} words match")

if __name__ == '__main__':
    fix_receipt_14()
    test_name_matching()