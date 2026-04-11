#!/usr/bin/env python3
import requests
import re
import sys

# Get the page to extract CSRF token
response = requests.get('http://192.168.20.10/accounting/cash-payments/create/')
csrf_match = re.search(r'csrfmiddlewaretoken.*?value="([^"]+)"', response.text)
csrf_token = csrf_match.group(1) if csrf_match else None

if not csrf_token:
    print("Could not find CSRF token!")
    sys.exit(1)

print(f"CSRF Token: {csrf_token[:20]}...")

# Now try to POST a payment
cookies = response.cookies
post_data = {
    'date': '2026-04-08',
    'description': 'Test Payment Direct',
    'debit_amount': '4500',
    'credit_amount': '4500',
    'credit_account': '92070',
    'csrfmiddlewaretoken': csrf_token
}

post_response = requests.post(
    'http://192.168.20.10/accounting/cash-payments/create/',
    data=post_data,
    cookies=cookies
)

print(f"Status Code: {post_response.status_code}")
print(f"Response URL: {post_response.url}")
print(f"Redirected: {post_response.history}")

# Check if there were errors in the response
if 'error' in post_response.text.lower() or 'invalid' in post_response.text.lower():
    # Extract error messages
    errors = re.findall(r'<.*?class.*?error.*?>.*?</.*?>', post_response.text, re.IGNORECASE)
    if errors:
        print("\nErrors found:")
        for error in errors[:5]:
            print(f"  {error[:200]}")
else:
    print("POST appears successful")
