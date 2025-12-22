#!/usr/bin/env python3
"""
Extract only business data from fixture (no Django framework tables)
Keep: auth.User, accounting, ar, ap, crm, sales, etc.
Skip: django_*, contenttypes.* (except auth.User), sessions, etc.
"""

import json

input_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_full.json'
output_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_business_only.json'

# Models to keep (business data only)
BUSINESS_MODELS = [
    'auth.user',
    'auth.group',
    'auth.permission',
    'auth.user_groups',
    'auth.user_permissions',
    'accounting.',  # All accounting submodules
    'ar.',
    'ap.',
    'cash_management.',
    'crm.',
    'expenses.',
    'hr.',
    'inventory.',
    'manufacturing.',
    'procurement.',
    'projects.',
    'sales.',
    'shareholder.',
    'us.',
    'maintenance.',
    'utils.',
]

print(f"[*] Reading fixture: {input_file}")

with open(input_file, 'r') as f:
    data = json.load(f)

print(f"[+] Total records: {len(data)}")

filtered_data = []
removed_count = 0

for record in data:
    model = record.get('model', '').lower()
    
    # Keep if matches business models
    keep = False
    for business_model in BUSINESS_MODELS:
        if model == business_model or model.startswith(business_model):
            keep = True
            break
    
    if keep:
        filtered_data.append(record)
    else:
        removed_count += 1
        if removed_count <= 10:
            print(f"[*] Skipping: {model}")

print(f"\n[+] Kept records: {len(filtered_data)}")
print(f"[+] Removed framework records: {removed_count}")

# Save filtered data
print(f"\n[*] Writing business-only fixture: {output_file}")
with open(output_file, 'w') as f:
    json.dump(filtered_data, f, indent=2)

print("[+] Done!")
print(f"\nUsage: python manage.py loaddata prod_data_business_only.json --settings=TradifyERP.settings_production")
