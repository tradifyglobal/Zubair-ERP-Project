#!/usr/bin/env python3
"""Update Entity views to include company_currency field"""

import sys

file_path = '/var/www/tradifyerp/accounting/views.py'

with open(file_path, 'r') as f:
    content = f.read()

# Find and replace the fields in EntityCreateView
old_fields = "fields = ['code', 'name', 'description', 'is_active']"
new_fields = "fields = ['code', 'name', 'description', 'company_currency', 'is_active']"

if old_fields in content:
    content = content.replace(old_fields, new_fields, 2)  # Replace both EntityCreateView and EntityUpdateView
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Successfully updated {file_path}")
    print(f"  Changed: {old_fields}")
    print(f"  To:      {new_fields}")
    sys.exit(0)
else:
    print(f"✗ Could not find fields pattern in {file_path}")
    sys.exit(1)
