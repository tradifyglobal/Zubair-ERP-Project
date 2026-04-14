#!/usr/bin/env python
"""
Debug CSRF token handling in cash payment form submission.
Tests if CSRF tokens are properly generated and validated.
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

# Get or create a test user
user = User.objects.filter(username='testuser').first()
if not user:
    user = User.objects.create_user(username='testuser', password='Test@123', email='test@example.com')
    print(f"Created test user: {user.username}")

# Get entity (assuming it exists)
from accounting.models import Entity
entity = Entity.objects.filter(is_active=True).first()
if not entity:
    print("ERROR: No active entity found!")
    sys.exit(1)

print(f"Using entity: {entity.name} (ID: {entity.id})")

# Create Django test client
client = Client()

# Step 1: GET the form (this should set CSRF cookie)
print("\n=== STEP 1: GET Cash Payment Form ===")
response = client.get('/accounting/cash-payments/create/', follow=False)
print(f"Status: {response.status_code}")
if response.status_code == 302:
    print(f"Redirected to: {response.get('Location')}")
    # Follow the redirect manually
    response = client.get('/accounting/select-entity/', follow=True)
    print(f"After redirect status: {response.status_code}")

# Login first
print("\n=== STEP 2: Login Test User ===")
login_result = client.login(username='testuser', password='Test@123')
print(f"Login successful: {login_result}")

# Step 2: Try GET again after login
print("\n=== STEP 3: GET Cash Payment Form After Login ===")
response = client.get('/accounting/cash-payments/create/')
print(f"Status: {response.status_code}")
print(f"Cookies: {list(client.cookies.keys())}")
if 'csrftoken' in client.cookies:
    csrf_token = client.cookies['csrftoken'].value
    print(f"CSRF Token from cookie: {csrf_token[:20]}...")

# Extract CSRF token from HTML response
import re
csrf_match = re.search(r"name='csrfmiddlewaretoken' value='([^']*)'", response.content.decode())
if csrf_match:
    form_csrf_token = csrf_match.group(1)
    print(f"CSRF Token from form HTML: {form_csrf_token[:20]}...")
    if csrf_token == form_csrf_token:
        print("✓ Tokens match!")
    else:
        print("✗ Tokens DO NOT match!")
else:
    print("WARNING: Could not extract CSRF token from form HTML!")

# Step 3: Set session data (select entity)
print("\n=== STEP 4: Set Entity in Session ===")
# First, set entity via POST if needed
select_entity_response = client.post(f'/accounting/select-entity/', {
    'entity_id': entity.id
}, follow=True)
print(f"Entity selection status: {select_entity_response.status_code}")

# Now try to get the form
print("\n=== STEP 5: GET Cash Payment Form After Entity Selection ===")
response = client.get('/accounting/cash-payments/create/')
print(f"Status: {response.status_code}")

# Step 4: Try POST with CSRF token
print("\n=== STEP 6: POST Cash Payment Form ===")
post_data = {
    'date': '2026-04-08',
    'description': 'Test Payment from Script',
    'debit_amount': '5000',
    'credit_amount': '5000',
    'credit_account': '',  # Can be empty
    'main_account': '',
    'main_credit_account': '',
    'currency': '',
    'exchange_rate': '',
    'converted_debit_amount': '',
    'converted_credit_amount': '',
    'payment_purpose': 'Testing',
    'stakeholder': '',
    'reference_number': '',
    'notes': 'Testing CSRF issue - Script Test'
}

# Add CSRF token if we have it
if 'form_csrf_token' in locals():
    post_data['csrfmiddlewaretoken'] = form_csrf_token

response = client.post('/accounting/cash-payments/create/', data=post_data)
print(f"Status: {response.status_code}")
if response.status_code == 403:
    print("✗ CSRF Error - 403 Forbidden")
    # Try to extract error message
    if 'CSRF' in response.content.decode():
        print("Server response contains CSRF error")
elif response.status_code == 200:
    print("Form returned - may have validation errors")
    # Check for form errors in response
    if 'invalid' in response.content.decode():
        print("Form has validation errors")
elif response.status_code in [301, 302]:
    print("✓ Redirect - likely successful form submission")
    print(f"Redirect location: {response.get('Location', 'unknown')}")
else:
    print(f"Unexpected status code: {response.status_code}")

# Check if payment was actually created
from accounting.models import CashPaymentLine
payment_count = CashPaymentLine.objects.filter(
    description='Test Payment from Script'
).count()
print(f"\nPayments created with description 'Test Payment from Script': {payment_count}")
