#!/usr/bin/env python3
"""
Simpler test to check context data by manually calling the view logic
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

# Now we can import Django models
from shareholder.models import ShareholderInvestmentLimit, Stakeholder
from accounting.models import InternationalTransferTracking
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from decimal import Decimal

# Setup a test request with session
factory = RequestFactory()
request = factory.get('/shareholder/investment-report/')

middleware = SessionMiddleware(lambda r: None)
middleware.process_request(request)

# Try to get a superuser
request.user = User.objects.filter(is_superuser=True).first()
if not request.user:
    request.user = User.objects.first()

# Set entity to Pristine Planet
request.session['entity_id'] = 9

print("\n" + "="*70)
print("DEBUGGING INVESTMENT REPORT CONTEXT")
print("="*70)

# Now manually run the logic from ShareholderInvestmentReportView.get_context_data()
entity_id = 9

# Get investment limits for this entity
investment_limits = ShareholderInvestmentLimit.objects.filter(
    entity_id=entity_id
).select_related('stakeholder')

print(f"\nFound {investment_limits.count()} investment limits for entity ID {entity_id}")

# Build the pending_in_foreign_bank data
pending_in_foreign_bank_by_stakeholder = {}

intl_transfers = InternationalTransferTracking.objects.filter(
    capital_contribution__entity_id=entity_id,
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder')

print(f"Found {intl_transfers.count()} international transfers")

for transfer in intl_transfers:
    transfer_stakeholder = transfer.capital_contribution.stakeholder
    destination_amount = transfer.destination_amount
    
    print(f"\nTransfer: {transfer_stakeholder.email} -> {destination_amount}")
    
    # Try to find matching stakeholder in current entity by email
    matching_stakeholder = Stakeholder.objects.filter(
        entity_id=entity_id,
        email=transfer_stakeholder.email
    ).first()
    
    print(f"  - Transfer stakeholder entity: {transfer_stakeholder.entity_id}")
    print(f"  - Transfer stakeholder ID: {transfer_stakeholder.id}")
    print(f"  - Matching stakeholder found in entity {entity_id}: {matching_stakeholder}")
    if matching_stakeholder:
        print(f"  - Matching stakeholder ID: {matching_stakeholder.id}")
    
    # Use current entity's stakeholder if found
    target_stakeholder_id = matching_stakeholder.id if matching_stakeholder else transfer_stakeholder.id
    
    print(f"  - Using stakeholder ID: {target_stakeholder_id}")
    
    if target_stakeholder_id not in pending_in_foreign_bank_by_stakeholder:
        pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] = Decimal('0')
    if destination_amount:
        pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] += Decimal(str(destination_amount))

print(f"\n" + "="*70)
print("PENDING IN FOREIGN BANK BY STAKEHOLDER ID:")
print("="*70)
for stakeholder_id, amount in pending_in_foreign_bank_by_stakeholder.items():
    print(f"Stakeholder ID {stakeholder_id}: {amount} (type: {type(amount).__name__})")

# Now check which stakeholders will have this data in the itmplate
print(f"\n" + "="*70)
print("INVESTMENT DATA THAT WILL BE SENT TO TEMPLATE:")
print("="*70)

target_names = ['Rafi', 'Sanaullah', 'Atif', 'Safi']

for limit in investment_limits:
    stakeholder_name = f"{limit.stakeholder.first_name} {limit.stakeholder.last_name}"
    if any(target in stakeholder_name for target in target_names):
        stakeholder_id = limit.stakeholder.id
        pending = pending_in_foreign_bank_by_stakeholder.get(stakeholder_id, Decimal('0'))
        
        print(f"\n{stakeholder_name} (ID: {stakeholder_id}):")
        print(f"  - pending_in_foreign_bank value: {pending}")
        print(f"  - Type: {type(pending).__name__}")
        print(f"  - Bool: {bool(pending)}")
        print(f"  - pending > 0: {pending > 0 if pending else 'N/A'}")
        print(f"  - Will display badge: {pending and pending > 0}")

print("\n" + "="*70)
