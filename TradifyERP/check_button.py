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

# Check for Save button in multiple ways
print("CHECKING FOR SAVE BUTTON:\n")

if '<button type="submit"' in content:
    print("[OK] Found: <button type=\"submit\"")
else:
    print("[NO] Not found: <button type=\"submit\"")

if 'mdi-content-save' in content:
    print("[OK] Found: mdi-content-save icon")
else:
    print("[NO] Not found: mdi-content-save icon")

if '>Save<' in content or '> Save <' in content:
    print("[OK] Found: Save text")
else:
    print("[NO] Not found: Save text")

# Check the card-body
if 'card-body' in content:
    print("[OK] Found: card-body")
else:
    print("[NO] Not found: card-body")

# Check for form
if '<form method="post"' in content:
    print("[OK] Found: POST form")
else:
    print("[NO] Not found: POST form")

# Find and display the button area
if '<form method="post"' in content:
    start = content.find('<form method="post"')
    end = content.find('</form>', start) + len('</form>')
    form_html = content[start:end]
    
    # Look for button
    button_pos = form_html.find('<button')
    if button_pos != -1:
        print("\n[OK] Button section found:")
        # Show 500 chars around button
        snippet_start = max(0, button_pos - 100)
        snippet_end = min(len(form_html), button_pos + 400)
        print(form_html[snippet_start:snippet_end])
    else:
        print("\n[NO] No button in form")
        # Show last 1000 chars of form
        print("\nLast 1000 chars of form:")
        print(form_html[-1000:])

# Save full HTML to file for inspection
with open('distributor_form_full.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("\nFull HTML saved to: distributor_form_full.html")
