#!/usr/bin/env python3
import json
import sys

with open('/var/www/tradifyerp/TradifyERP/dev_data_export.json') as f:
    data = json.load(f)

# Find and fix boolean fields with "None" string value
fixed = 0
for obj in data:
    if obj.get('model') == 'accounting.stakeholder' and 'fields' in obj:
        fields = obj['fields']
        if 'same_as_permanent' in fields and fields['same_as_permanent'] == 'None':
            fields['same_as_permanent'] = False
            fixed += 1
            print(f"Fixed Stakeholder pk={obj['pk']}: same_as_permanent='None' -> False")

# Look for other boolean fields with None value
bool_fields = ['is_active', 'is_approved', 'is_verified', 'is_paid', 'paid']
for obj in data:
    if 'fields' in obj:
        for bool_field in bool_fields:
            if bool_field in obj['fields'] and obj['fields'][bool_field] == 'None':
                obj['fields'][bool_field] = False
                fixed += 1
                print(f"Fixed {obj['model']} pk={obj['pk']}: {bool_field}='None' -> False")

print(f"\nTotal fields fixed: {fixed}")

# Write fixed data back
with open('/var/www/tradifyerp/TradifyERP/dev_data_export_fixed.json', 'w') as f:
    json.dump(data, f)

print("Saved fixed data to dev_data_export_fixed.json")
