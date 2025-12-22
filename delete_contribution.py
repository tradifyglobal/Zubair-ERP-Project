#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CapitalContribution
from accounting.stakeholder_models import Stakeholder

# Find the entry
stakeholder = Stakeholder.objects.filter(first_name='Fayazuddin', last_name='Zubair').first()
if stakeholder:
    contributions = CapitalContribution.objects.filter(
        stakeholder=stakeholder,
        status='PENDING',
        amount=100
    )
    print(f"Found {contributions.count()} matching contributions:")
    for c in contributions:
        print(f"ID: {c.id}, Amount: {c.amount}, Date: {c.contribution_date}, Status: {c.status}")
        c.delete()
        print(f"Deleted contribution ID: {c.id}")
else:
    print("Stakeholder not found")
