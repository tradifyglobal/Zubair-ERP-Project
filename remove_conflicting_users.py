#!/usr/bin/env python3
"""
Remove conflicting users from fixture
"""

import json

fixture_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_business_only.json'
output_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_ready_to_load.json'

with open(fixture_file, 'r') as f:
    data = json.load(f)

print(f"[*] Total records before: {len(data)}")

# Find users
users_before = [r for r in data if r['model'] == 'auth.user']
print(f"\n[*] Users in fixture:")
for u in users_before:
    print(f"    ID {u['pk']}: {u['fields']['username']}")

# Filter out users that already exist on server (zubair, admin)
filtered_data = []
removed_users = []

for record in data:
    if record['model'] == 'auth.user':
        username = record['fields']['username']
        if username in ['zubair', 'admin']:
            removed_users.append(username)
            print(f"\n[*] Removing user: {username}")
            continue
    
    filtered_data.append(record)

print(f"\n[+] Removed {len(removed_users)} conflicting users")
print(f"[+] Total records after: {len(filtered_data)}")

# Save
with open(output_file, 'w') as f:
    json.dump(filtered_data, f, indent=2)

print(f"[+] Saved to: {output_file}")
