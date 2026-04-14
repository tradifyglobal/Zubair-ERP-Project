#!/usr/bin/env python3
"""
Fix raw_materials app registration to use proper app config
"""
settings_file = '/var/www/tradifyerp/TradifyERP/settings_production.py'

with open(settings_file, 'r') as f:
    content = f.read()

# Replace the simple 'raw_materials' with the proper app config
content = content.replace(
    "    'raw_materials',  # Raw Materials Management",
    "    'raw_materials.apps.RawMaterialsConfig',  # Raw Materials Management"
)

with open(settings_file, 'w') as f:
    f.write(content)

print("Updated to use proper app config: raw_materials.apps.RawMaterialsConfig")
