#!/usr/bin/env python3
import os

# Read the models.py file
with open('f:/ERP-Production/Zubair-ERP-Project/TradifyERP/accounting/models.py', 'r') as f:
    content = f.read()

# Write to temp location
with open('/tmp/models_fixed.py', 'w') as f:
    f.write(content)

print("File ready for deployment")
