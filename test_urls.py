#!/usr/bin/env python
"""
Test expenses module URLs and views.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import Client
from django.urls import reverse

# Create a test client
client = Client()

# Try to access expenses dashboard
try:
    url = reverse('expenses:dashboard')
    print(f"Expenses dashboard URL: {url}")
    
    # This will fail without login, but tests if URL exists
    response = client.get(url)
    print(f"Status code (before login): {response.status_code}")
    
except Exception as e:
    print(f"Error accessing expenses:dashboard: {e}")

# Try other expenses URLs
urls_to_test = [
    'expenses:dashboard',
    'expenses:report_list',
    'expenses:report_create',
    'expenses:budget_list',
    'expenses:reimbursement_list',
    'expenses:category_list',
]

print("\nExpenses module URLs:")
for url_name in urls_to_test:
    try:
        url = reverse(url_name)
        print(f"  ✓ {url_name:30} → {url}")
    except Exception as e:
        print(f"  ✗ {url_name:30} → ERROR: {e}")
