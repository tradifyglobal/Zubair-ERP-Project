#!/usr/bin/env python3
"""
Fix stakeholder assignment for receipt ID 13 and trigger capital contribution signal
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

def fix_receipt_13():
    """Fix stakeholder assignment for receipt ID 13"""
    try:
        with transaction.atomic():
            receipt = CashReceiptLine.objects.get(id=13)
            print(f"Receipt ID: {receipt.id}")
            print(f"Account: {receipt.account.name} (ID: {receipt.account.id})")
            print(f"Current stakeholder_id: {receipt.stakeholder_id}")
            print(f"Workflow status: {receipt.workflow_status}")
            
            # Find Javeed Baba (stakeholder ID 11)
            stakeholder = Stakeholder.objects.get(id=11, entity=receipt.entity)
            print(f"Found stakeholder: {stakeholder.full_name} (ID: {stakeholder.id})")
            
            # Assign stakeholder
            receipt.stakeholder = stakeholder
            receipt.save()
            
            print(f"✅ Assigned stakeholder {stakeholder.id} to receipt {receipt.id}")
            print("✅ Signal should have fired automatically to create capital contribution!")
            
            return True
            
    except CashReceiptLine.DoesNotExist:
        print(f"❌ Receipt 13 not found")
        return False
    except Stakeholder.DoesNotExist:
        print(f"❌ Stakeholder 11 not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    fix_receipt_13()