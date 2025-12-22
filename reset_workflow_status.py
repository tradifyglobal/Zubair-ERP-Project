#!/usr/bin/env python3
"""
Reset cash receipt workflow status to enable frontend approval
"""
import os
import sys
import django
import psycopg2

# Add the Django project path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import transaction
from accounting.models import CashReceiptLine

def reset_receipt_workflow(receipt_id):
    """Reset receipt workflow status to DRAFT for re-approval"""
    try:
        with transaction.atomic():
            receipt = CashReceiptLine.objects.get(id=receipt_id)
            print(f"Current status: {receipt.workflow_status}")
            
            # Reset to DRAFT to allow approval workflow
            receipt.workflow_status = 'DRAFT'
            receipt.save()
            
            print(f"✅ Reset receipt {receipt_id} to DRAFT status")
            print("Now you can approve it from the frontend at:")
            print("https://tradifyglobal.com/accounting/cash-receipts/")
            
    except CashReceiptLine.DoesNotExist:
        print(f"❌ Receipt {receipt_id} not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    reset_receipt_workflow(11)