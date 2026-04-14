#!/usr/bin/env python
"""Test the investment report view directly with Pristine Planet entity"""

import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from accounting.models import Entity
from shareholder.views import ShareholderInvestmentReportView

# Create a fake request
factory = RequestFactory()
request = factory.get('/shareholder/investment-report/')

# Get Pristine Planet entity
entity = Entity.objects.get(name='Pristine Planet')

# Add session to request
from django.contrib.sessions.middleware import SessionMiddleware
middleware = SessionMiddleware(lambda r: None)
middleware.process_request(request)
request.session['selected_entity_id'] = entity.id
request.session.save()

# Add user
request.user = User.objects.first()

# Call the view
view = ShareholderInvestmentReportView()
view.request = request
context = view.get_context_data()

# Print results
print(f"Entity: {entity.name} (ID: {entity.id})")
print(f"\nInvestment Data in Context: {len(context.get('investment_data', []))} records")

if context.get('investment_data'):
    print("\nRecords with pending amounts:")
    for inv in context['investment_data']:
        pending = inv.get('pending_in_foreign_bank', Decimal('0'))
        if pending > 0:
            print(f"  ✓ {inv['stakeholder'].first_name} {inv['stakeholder'].last_name}: ₹{pending}")
    
    print(f"\nTotal Pending in Foreign Bank: ₹{context.get('total_pending_in_foreign_bank', 0)}")
else:
    print("NO INVESTMENT DATA FOUND!")
