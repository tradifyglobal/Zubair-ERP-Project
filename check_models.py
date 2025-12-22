#!/usr/bin/env python3

import os
import sys
import django

# Setup Django environment
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

print("Checking available models...")

try:
    from accounting import models as accounting_models
    print("Accounting models:")
    for name in dir(accounting_models):
        if not name.startswith('_') and hasattr(getattr(accounting_models, name), '_meta'):
            print(f"  - {name}")
except Exception as e:
    print(f"Error with accounting models: {e}")

try:
    from shareholder import models as shareholder_models
    print("\nShareholder models:")
    for name in dir(shareholder_models):
        if not name.startswith('_') and hasattr(getattr(shareholder_models, name), '_meta'):
            print(f"  - {name}")
except Exception as e:
    print(f"Error with shareholder models: {e}")

try:
    from cash_management import models as cash_models
    print("\nCash Management models:")
    for name in dir(cash_models):
        if not name.startswith('_') and hasattr(getattr(cash_models, name), '_meta'):
            print(f"  - {name}")
except Exception as e:
    print(f"Error with cash_management models: {e}")