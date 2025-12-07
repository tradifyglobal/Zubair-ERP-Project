#!/usr/bin/env python3
import json

with open('/var/www/tradifyerp/TradifyERP/dev_data_export.json') as f:
    data = json.load(f)

# Convert all null boolean field values to False
boolean_fields = {
    'accounting.stakeholder': ['same_as_permanent'],
    'accounting.capitalcontribution': ['is_approved'],
    'sales.invoice': ['paid'],
    'cash_management.cashreceipt': ['paid'],
    'cash_management.cashpayment': ['paid'],
}

fixed_count = 0
for obj in data:
    model = obj.get('model')
    if model in boolean_fields and 'fields' in obj:
        for bool_field in boolean_fields[model]:
            if bool_field in obj['fields'] and obj['fields'][bool_field] is None:
                obj['fields'][bool_field] = False
                fixed_count += 1

print(f"Fixed {fixed_count} null boolean values to False")

# Write back
with open('/var/www/tradifyerp/TradifyERP/dev_data_export_fixed2.json', 'w') as f:
    json.dump(data, f)

print("Saved to dev_data_export_fixed2.json")
