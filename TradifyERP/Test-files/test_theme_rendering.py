#!/usr/bin/env python
"""Test theme rendering in base template."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User

# Get a user
user = User.objects.get(username='zubair')
client = Client()
client.force_login(user)

# Get a page that uses the base template
response = client.get('/accounting/dashboard/')

print("Response status code:", response.status_code)
print("Response content length:", len(response.content))

# Check the content
content = response.content.decode('utf-8')

# Find the body tag
import re
body_match = re.search(r'<body[^>]*>', content)
if body_match:
    print("\nBody tag found:")
    print(body_match.group(0))
    
    # Check for theme attributes
    if 'data-sidebar=' in body_match.group(0):
        print("- Has data-sidebar attribute")
    if 'data-layout=' in body_match.group(0):
        print("- Has data-layout attribute")
    if 'data-layout-size=' in body_match.group(0):
        print("- Has data-layout-size attribute")
else:
    print("Body tag NOT found!")
    print("\nFirst 1000 chars of response:")
    print(content[:1000])
