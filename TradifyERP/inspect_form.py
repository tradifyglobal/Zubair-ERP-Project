#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Login
client = Client()
user = User.objects.get(username='testuser')
client.force_login(user)

# Get the form page
response = client.get('/manufacturing/distributors/new/')
content = response.content.decode('utf-8')

# Find the POST form
start = content.find('<form method="post"')
end = content.find('</form>', start) + len('</form>')
form_html = content[start:end]

# Extract form to a file for inspection
with open('distributor_form_rendered.html', 'w', encoding='utf-8') as f:
    f.write(form_html)

print("✅ Form HTML saved to distributor_form_rendered.html")

# Count fields
import re
fields = re.findall(r'<input[^>]*name="([^"]*)"', form_html)
print(f"\n📊 Found {len(fields)} input fields:")
for field in fields[:10]:
    print(f"  - {field}")
if len(fields) > 10:
    print(f"  ... and {len(fields) - 10} more")

# Check for button
if '<button type="submit"' in form_html:
    print(f"\n✅ Submit button is present in form HTML")
else:
    print(f"\n❌ Submit button is NOT in form HTML")
