#!/usr/bin/env python3
"""
Change cash receipt workflow status directly to APPROVED
This will trigger the signal to create capital contribution
"""
import os
import sys
import django

# Add the Django project path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import transaction
from accounting.models import CashReceiptLine

def set_receipt_approved(receipt_id):
    """Set receipt workflow status to APPROVED to trigger signal"""
    try:
        with transaction.atomic():
            receipt = CashReceiptLine.objects.get(id=receipt_id)
            print(f"Current status: {receipt.workflow_status}")
            
            # Set to APPROVED to trigger auto capital contribution signal
            receipt.workflow_status = 'APPROVED'
            receipt.save()
            
            print(f"✅ Set receipt {receipt_id} to APPROVED status")
            print("This should trigger the signal to create capital contribution automatically")
            
            # The signal will fire after save() and create the capital contribution
            
    except CashReceiptLine.DoesNotExist:
        print(f"❌ Receipt {receipt_id} not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    set_receipt_approved(11)