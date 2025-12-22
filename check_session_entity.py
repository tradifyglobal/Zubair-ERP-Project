#!/usr/bin/env python
"""Check session entity and trial balance entity"""
import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import TrialBalance, Entity
from django.contrib.sessions.models import Session

# Check all trial balances
print("=== ALL TRIAL BALANCES ===")
for tb in TrialBalance.objects.all():
    print(f"ID: {tb.id}, Entity: {tb.entity.code} (ID={tb.entity.id}), Date: {tb.as_of_date}, Balanced: {tb.is_balanced}")

print("\n=== ALL ENTITIES ===")
for e in Entity.objects.filter(is_active=True):
    print(f"ID: {e.id}, Code: {e.code}, Name: {e.name}")

print("\n=== ACTIVE SESSIONS ===")
for session in Session.objects.filter(expire_date__gte=django.utils.timezone.now())[:5]:
    data = session.get_decoded()
    entity_id = data.get('selected_entity_id')
    entity_code = data.get('selected_entity_code')
    print(f"Session: {session.session_key[:10]}..., Entity ID: {entity_id}, Code: {entity_code}")
