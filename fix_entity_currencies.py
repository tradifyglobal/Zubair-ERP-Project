#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Currency

def fix_entity_currencies():
    print("=== FIXING ENTITY CURRENCIES ===")
    
    # Get currencies
    inr = Currency.objects.get(code='INR')
    usd = Currency.objects.get(code='USD')
    
    print(f"INR: {inr} (Symbol: {inr.symbol})")
    print(f"USD: {usd} (Symbol: {usd.symbol})")
    
    # Assign currencies to entities using correct field name
    entities = Entity.objects.all()
    
    for entity in entities:
        print(f"\nEntity: {entity.name}")
        
        if entity.name == "Testing":
            # Testing entity uses INR (based on the data)
            entity.company_currency = inr
            entity.save()
            print(f"✓ Assigned INR to {entity.name}")
        else:
            # Other entities use USD by default
            entity.company_currency = usd
            entity.save() 
            print(f"✓ Assigned USD to {entity.name}")
        
        # Verify the assignment
        entity.refresh_from_db()
        print(f"  Verified: {entity.company_currency.code} ({entity.company_currency.symbol})")

if __name__ == '__main__':
    fix_entity_currencies()