#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create a test client
client = Client()

# First, create or get a test user
user, created = User.objects.get_or_create(username='testuser', defaults={'is_staff': True, 'is_active': True})
if created:
    user.set_password('testpass123')
    user.save()
    print("Created test user: testuser")

# Login
login_success = client.login(username='testuser', password='testpass123')
print(f"Login: {'✅ Success' if login_success else '❌ Failed'}")

# Try to access the form page
response = client.get('/manufacturing/distributors/new/')

print(f"Status Code: {response.status_code}")
print(f"Template Used: {response.template_name if hasattr(response, 'template_name') else 'N/A'}")

# Check if content has the Save button
content = response.content.decode('utf-8')

if 'type="submit"' in content:
    print("\n✅ Submit button found in HTML")
else:
    print("\n❌ Submit button NOT found in HTML")

if 'Save' in content:
    print("✅ 'Save' text found in HTML")
else:
    print("❌ 'Save' text NOT found in HTML")

# Find the main form (not search form)
if '<form method="post"' in content:
    print("✅ POST form found (this is the main form)")
    start = content.find('<form method="post"')
    if start != -1:
        end = content.find('</form>', start) + len('</form>')
        form_html = content[start:end]
        
        # Show the submit button area
        if 'type="submit"' in form_html:
            print("✅ Submit button in POST form")
            submit_start = form_html.find('type="submit"')
            snippet_start = max(0, submit_start - 200)
            snippet_end = min(len(form_html), submit_start + 500)
            print(f"\n📝 Submit button section:\n{form_html[snippet_start:snippet_end]}")
        else:
            print("❌ No submit button in POST form")
            print(f"\n📝 Form HTML (last 1000 chars):\n{form_html[-1000:]}")
else:
    print("\n❌ No POST form found")

# Also check for button with mdi-content-save icon
if 'mdi-content-save' in content:
    print("\n✅ Save icon (mdi-content-save) found in HTML")

# Count form fields
import re
field_count = len(re.findall(r'<input|<select|<textarea', content))
print(f"\n📊 Form fields found: {field_count}")

# Check for distributor_code field
if 'distributor_code' in content or 'id_distributor_code' in content:
    print("✅ Distributor code field found")
else:
    print("❌ Distributor code field NOT found")

# Check for distributor_name field
if 'distributor_name' in content or 'id_distributor_name' in content:
    print("✅ Distributor name field found")
else:
    print("❌ Distributor name field NOT found")
