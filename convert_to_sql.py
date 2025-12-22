#!/usr/bin/env python3
"""
Fast JSON to PostgreSQL loader - converts fixture to SQL INSERT statements
"""

import json
import sys
from pathlib import Path

fixture_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_business_only.json'

print("[*] Reading fixture...")
with open(fixture_file) as f:
    data = json.load(f)

# Group by model
from collections import defaultdict
by_model = defaultdict(list)
for record in data:
    by_model[record['model']].append(record)

print(f"[+] {len(data)} records loaded")
print(f"[+] {len(by_model)} models")

# Create SQL script
sql_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\load_fixture.sql'

with open(sql_file, 'w') as f:
    f.write("-- Auto-generated SQL from fixture\n")
    f.write("-- Load data from prod_data_business_only.json\n\n")
    
    for model, records in sorted(by_model.items()):
        f.write(f"-- Model: {model} ({len(records)} records)\n")
        
        if model == 'auth.user':
            # Skip zubair and admin users
            for record in records:
                if record['fields'].get('username') not in ['zubair', 'admin']:
                    f.write(f"-- User: {record['fields']['username']}\n")
                    break
        
        f.write(f"\n")

print(f"[+] SQL script created: {sql_file}")
print(f"[+] Size: {Path(sql_file).stat().st_size} bytes")
print("\n[*] Script is too complex to auto-generate.")
print("[*] Using Django loaddata is faster - let's try with async background process...")
