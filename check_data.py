#!/usr/bin/env python
"""
Check available stakeholders and accounts to create proper test.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Entity, Account, Stakeholder

def check_available_data():
    """Check available stakeholders and accounts."""
    
    print("=== CHECKING AVAILABLE DATA ===")
    
    entity = Entity.objects.get(id=7)  # Testing entity
    
    print(f"\nActive Stakeholders:")
    for s in Stakeholder.objects.filter(entity=entity, status='ACTIVE')[:5]:
        print(f"  ID: {s.id}, Name: '{s.full_name}'")
    
    print(f"\nCapital Accounts:")
    for a in Account.objects.filter(entity=entity, name__icontains='Capital', is_active=True)[:5]:
        print(f"  ID: {a.id}, Name: '{a.name}'")

if __name__ == '__main__':
    check_available_data()