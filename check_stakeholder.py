#!/usr/bin/env python3
import json

with open('/var/www/tradifyerp/TradifyERP/dev_data_export.json') as f:
    data = json.load(f)

# Find the problematic stakeholder
for obj in data:
    if obj.get('model') == 'accounting.stakeholder' and obj.get('pk') == 1:
        print(json.dumps(obj, indent=2))
        break
