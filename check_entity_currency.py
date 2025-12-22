#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity

def check_entity_currency():
    print("=== CHECKING ENTITY CURRENCY SETUP ===")
    
    entities = Entity.objects.all()
    
    for entity in entities:
        print(f"\nEntity: {entity.name} (ID: {entity.id})")
        print(f"  Code: {entity.code}")
        print(f"  Active: {entity.is_active}")
        
        if hasattr(entity, 'currency') and entity.currency:
            print(f"  Currency: {entity.currency}")
            print(f"  Currency Code: {entity.currency.code}")
            print(f"  Currency Symbol: {entity.currency.symbol}")
        else:
            print(f"  Currency: NOT SET")
            print(f"  This explains why USD is still showing!")
        
        # Check if entity has currency_id field
        if hasattr(entity, 'currency_id'):
            print(f"  Currency ID: {entity.currency_id}")

if __name__ == '__main__':
    check_entity_currency()