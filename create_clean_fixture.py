#!/usr/bin/env python3
"""
Generate a clean fixture file without existing users
"""

import json
import sys

input_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_full.json'
output_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_no_users.json'

print(f"[*] Reading fixture: {input_file}")

with open(input_file, 'r') as f:
    data = json.load(f)

print(f"[+] Total records: {len(data)}")

# Filter out auth_user records with usernames 'admin' and 'zubair'
filtered_data = []
removed_users = []
removed_user_admin_links = []

for record in data:
    model = record.get('model', '')
    fields = record.get('fields', {})
    
    # Remove admin and zubair users
    if model == 'auth.user':
        username = fields.get('username', '')
        if username in ['admin', 'zubair']:
            removed_users.append(username)
            print(f"[*] Removing user: {username}")
            continue
    
    # Remove admin group assignments for removed users
    if model == 'auth.user_groups':
        # Keep these as they reference IDs, not usernames
        filtered_data.append(record)
        continue
    
    filtered_data.append(record)

print(f"[+] Removed {len(removed_users)} conflicting users")
print(f"[+] Remaining records: {len(filtered_data)}")

# Save filtered data
print(f"[*] Writing filtered fixture: {output_file}")
with open(output_file, 'w') as f:
    json.dump(filtered_data, f, indent=2)

print("[+] Done!")
print(f"\nUsage: python manage.py loaddata prod_data_no_users.json --settings=TradifyERP.settings_production")
