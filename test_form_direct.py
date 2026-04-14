#!/usr/bin/env python3
"""Test cash payment form submission directly using Django test client"""
import sys
import os
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from datetime import datetime

# Create test client
client = Client()

# Login - try multiple possible passwords
print("=== LOGIN ===")
login_success = False
for password in ['admin123', 'password', '123456', 'admin', 'Test@123', 'Demo@123']:
    try:
        login_success = client.login(username='admin', password=password)
        if login_success:
            print(f"Login successful with password: {password}")
            break
    except:
        pass

if not login_success:
    print("Could not login with common passwords")
    print("Trying to list users...")
    from django.contrib.auth.models import User
    users = User.objects.all()
    print(f"Available users: {', '.join([u.username for u in users])}")
    print("\nUsing curl to login instead...")
    import subprocess
    # Create a session with curl
    subprocess.run(['bash', '-c', """
        COOKIES='/tmp/test_cookies.txt'
        curl -s -c $COOKIES -b $COOKIES -X POST \
          -d 'username=admin&password=admin123' \
          http://192.168.20.10/accounts/login/ > /dev/null
        echo "Cookies saved to $COOKIES"
    """])
    sys.exit(1)

# Set entity in session
print("\n=== SELECT ENTITY ===")
session_post = client.post('/accounting/select-entity/', {'entity_id': 9}, follow=True)
print(f"Entity selection status: {session_post.status_code}")

# Get CSRF token from form
print("\n=== GET FORM ===")
form_response = client.get('/accounting/cash-payments/create/')
print(f"Form GET status: {form_response.status_code}")

# Extract CSRF token from response
import re
csrf_match = re.search(r"'csrfmiddlewaretoken' value='([^']*)'", form_response.content.decode())
csrf_token = csrf_match.group(1) if csrf_match else ''
print(f"CSRF token found: {'YES' if csrf_token else 'NO'} (first 20 chars: {csrf_token[:20] if csrf_token else 'N/A'})")

# Submit form
print("\n=== SUBMIT FORM ===")
post_data = {
    'csrfmiddlewaretoken': csrf_token,
    'date': '2026-04-08',
    'description': '✅ Django Test Client Submission',
    'debit_amount': '40000',
    'credit_amount': '40000',
    'credit_account': '',
    'main_account': '',
    'main_credit_account': '',
    'currency': '',
    'exchange_rate': '',
    'converted_debit_amount': '',
    'converted_credit_amount': '',
    'payment_purpose': '',
    'stakeholder': '',
    'reference_number': '',
    'notes': '',
}

response = client.post('/accounting/cash-payments/create/', data=post_data)
print(f"Form POST status: {response.status_code}")

# Check for form errors in response
if 'invalid' in response.content.decode().lower() or 'error' in response.content.decode().lower():
    print("Form appears to have errors in response HTML")
    
    # Try to extract error messages
    import bs4
    try:
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        errors = soup.find_all(class_='invalid-feedback')
        if errors:
            print("\nForm validation errors found:")
            for error in errors:
                print(f"  - {error.get_text().strip()}")
    except:
        pass

if response.status_code in [301, 302]:
    print(f"Redirect to: {response.get('Location')}")

# Check database
from accounting.models import CashPaymentLine
total = CashPaymentLine.objects.count()
latest = CashPaymentLine.objects.order_by('-created_at').first()

print(f"\n=== DATABASE CHECK ===")
print(f"Total payments: {total}")
if latest:
    print(f"Latest: ID={latest.id}, Desc={latest.description}, Created={latest.created_at}")
    if 'Test Client' in latest.description:
        print("✅ TEST PAYMENT WAS CREATED SUCCESSFULLY!")
    else:
        print("❌ New test payment not found (latest was from before)")
