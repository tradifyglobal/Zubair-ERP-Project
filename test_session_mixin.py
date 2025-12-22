#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, TrialBalance
from accounting.views import TrialBalanceListView
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_session_entity_mixin():
    print("=== TESTING SESSION ENTITY MIXIN BEHAVIOR ===")
    
    # Check all entities and their trial balances
    entities = Entity.objects.all()
    print(f"All entities: {entities.count()}")
    
    for entity in entities:
        tb_records = TrialBalance.objects.filter(entity=entity)
        print(f"\nEntity: {entity.name} (ID: {entity.id})")
        print(f"  Trial balance records: {tb_records.count()}")
        
        for tb in tb_records:
            print(f"    {tb.as_of_date}: Dr {tb.total_debits} Cr {tb.total_credits} Balanced: {tb.is_balanced}")
    
    # Test the SessionEntityMixin filtering behavior
    print(f"\n=== TESTING QUERYSET FILTERING ===")
    
    # Simulate a request with session entity
    factory = RequestFactory()
    request = factory.get('/accounting/trial-balances/')
    request.user = AnonymousUser()
    
    # Test filtering for each entity
    for entity in entities:
        print(f"\nTesting filtering for entity: {entity.name}")
        
        # Simulate session with this entity selected
        request.session = {'selected_entity_id': entity.id}
        request.entity = entity
        
        # Create view instance
        view = TrialBalanceListView()
        view.request = request
        view.model = TrialBalance
        
        # Test get_queryset
        try:
            queryset = view.get_queryset()
            filtered_count = queryset.count()
            print(f"  Queryset count after filtering: {filtered_count}")
            
            for tb in queryset:
                print(f"    Found: {tb.entity.name} - {tb.as_of_date}")
                
        except Exception as e:
            print(f"  Error testing queryset: {e}")

if __name__ == '__main__':
    test_session_entity_mixin()