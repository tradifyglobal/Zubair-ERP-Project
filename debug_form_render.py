#!/usr/bin/env python
"""
Fetch and analyze the actual HTML sent by the journal voucher form view
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from accounting.views_journal_voucher import JournalVoucherCreateView
from accounting.models import Entity
import re

# Get or create a test entity
entity, _ = Entity.objects.get_or_create(
    id=1,
    defaults={'name': 'Test Entity', 'code': 'TEST'}
)

# Create a request
factory = RequestFactory()
request = factory.get('/accounting/journal-vouchers/create/')
request.user = AnonymousUser()
request.entity = entity
request.session = {}

# Create view and get response
view = JournalVoucherCreateView()
view.request = request
view.object = None
context = view.get_context_data()

# Inspect the formset
formset = context['formset']
first_form = formset.forms[0] if formset.forms else None

if first_form:
    print("=" * 70)
    print("ACTUAL FORM FIELDS IN FORMSET:")
    print("=" * 70)
    print(f"Fields: {list(first_form.fields.keys())}")
    print()
    
    print("=" * 70)
    print("FORM FIELD RENDERING (HTML):")
    print("=" * 70)
    for field_name in first_form.fields:
        field = first_form[field_name]
        print(f"{field_name}: {field.field.widget.__class__.__name__}")
