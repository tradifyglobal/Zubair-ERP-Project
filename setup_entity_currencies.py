#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Currency

def setup_entity_currencies():
    print("=== SETTING UP ENTITY CURRENCIES ===")
    
    # Check available currencies
    currencies = Currency.objects.all()
    print(f"Available currencies: {currencies.count()}")
    
    for currency in currencies:
        print(f"  {currency.code} - {currency.name} (Symbol: {currency.symbol})")
    
    # Get or create default currencies
    usd, created = Currency.objects.get_or_create(
        code='USD',
        defaults={
            'name': 'US Dollar',
            'symbol': '$'
        }
    )
    print(f"\n{'Created' if created else 'Found'} USD currency: {usd}")
    
    inr, created = Currency.objects.get_or_create(
        code='INR',
        defaults={
            'name': 'Indian Rupee',
            'symbol': '₹'
        }
    )
    print(f"{'Created' if created else 'Found'} INR currency: {inr}")
    
    # Assign currencies to entities
    entities = Entity.objects.all()
    
    for entity in entities:
        if entity.name == "Testing":
            # Testing entity uses INR (based on the data we saw)
            entity.currency = inr
            entity.save()
            print(f"\n✓ Assigned INR to {entity.name}")
        else:
            # Other entities use USD by default
            entity.currency = usd
            entity.save()
            print(f"✓ Assigned USD to {entity.name}")
    
    print(f"\n=== UPDATED ENTITY CURRENCIES ===")
    for entity in Entity.objects.all():
        print(f"{entity.name}: {entity.currency.code} ({entity.currency.symbol})")

if __name__ == '__main__':
    setup_entity_currencies()