#!/usr/bin/env python3
import requests
import re
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create a session that persists cookies
session = requests.Session()

# Retry strategy for reliability
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

print("Step 1: Fetching the form page...")
response = session.get('http://192.168.20.10/accounting/cash-payments/create/')
print(f"Initial response status: {response.status_code}")

if response.status_code == 302:
    print("Redirected to login - you need to authenticate first!")
    print(f"Redirect URL: {response.headers.get('Location')}")
    sys.exit(1)

# Extract CSRF token
csrf_match = re.search(r'csrfmiddlewaretoken.*?value="([^"]+)"', response.text)
csrf_token = csrf_match.group(1) if csrf_match else None

if not csrf_token:
    print("Could not find CSRF token!")
    print("Checking if redirected to login...")
    if '/login' in response.text or '/accounts/login' in response.text:
        print("Page shows login form - not authenticated")
    sys.exit(1)

print(f"CSRF Token found: {csrf_token[:20]}...")

# Prepare POST data
post_data = {
    'date': '2026-04-08',
    'description': 'Test Payment via Session',
    'debit_amount': '5500',
    'credit_amount': '5500',
    'credit_account': '92070',
    'csrfmiddlewaretoken': csrf_token
}

print("\nStep 2: Posting payment form...")
post_response = session.post(
    'http://192.168.20.10/accounting/cash-payments/create/',
    data=post_data
)

print(f"POST response status: {post_response.status_code}")
print(f"Response URL after POST: {post_response.url}")

if post_response.status_code == 302:
    print(f"Redirected to: {post_response.headers.get('Location')}")
    if '/login' in post_response.headers.get('Location', ''):
        print("ERROR: Still not authenticated!")
    elif '/cash-payments' in post_response.headers.get('Location', ''):
        print("SUCCESS: Appears to have saved!")

# Show first 500 chars of response
if len(post_response.text) > 100:
    if 'error' in post_response.text.lower():
        print("\nFound 'error' in response")
    if 'cash-payment' in post_response.text.lower():
        print("Found 'cash-payment' reference in response")
