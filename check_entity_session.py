#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, TrialBalance, LedgerEntry

def check_entity_session_behavior():
    print("=== CHECKING ENTITY SESSION BEHAVIOR ===")
    
    # Check all entities
    entities = Entity.objects.all()
    print(f"All entities ({entities.count()}):")
    for entity in entities:
        print(f"  {entity.id}: {entity.name} (active: {entity.is_active})")
        
        # Check ledger entries for each entity
        entries_count = LedgerEntry.objects.filter(entity=entity).count()
        print(f"    Ledger entries: {entries_count}")
        
        # Check trial balance records for each entity
        tb_count = TrialBalance.objects.filter(entity=entity).count()
        print(f"    Trial balance records: {tb_count}")
        
        if tb_count > 0:
            latest_tb = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date').first()
            print(f"    Latest TB: {latest_tb.as_of_date} | Dr {latest_tb.total_debits} Cr {latest_tb.total_credits} | Balanced: {latest_tb.is_balanced}")
        print()
    
    # Check which entity has the "active" flag vs which has data
    active_entities = entities.filter(is_active=True)
    print(f"Active entities: {active_entities.count()}")
    for entity in active_entities:
        entries = LedgerEntry.objects.filter(entity=entity).count()
        print(f"  {entity.name}: {entries} entries")

if __name__ == '__main__':
    check_entity_session_behavior()