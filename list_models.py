#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from django.apps import apps

print("Shareholder app models:")
for model in apps.get_app_config('shareholder').get_models():
    print(f"  - {model.__name__}")

print("\nAccounting app models:")
for model in apps.get_app_config('accounting').get_models():
    if 'trial' in model.__name__.lower() or 'ledger' in model.__name__.lower():
        print(f"  - {model.__name__}")
