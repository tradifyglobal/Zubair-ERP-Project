#!/usr/bin/env python3
"""
Set receipt 14 back to AUTHORIZED status
"""
import os
import sys
import django

# Add the Django project path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashReceiptLine

def update_receipt_status():
    """Update receipt 14 back to AUTHORIZED"""
    try:
        receipt = CashReceiptLine.objects.get(id=14)
        receipt.workflow_status = 'AUTHORIZED'
        receipt.save()
        print(f"✅ Set receipt {receipt.id} back to AUTHORIZED status")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    update_receipt_status()