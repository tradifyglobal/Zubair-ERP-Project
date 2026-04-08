#!/usr/bin/env python3
"""
Add raw_materials to INSTALLED_APPS
"""
import sys

settings_file = '/var/www/tradifyerp/TradifyERP/settings_production.py'

try:
    with open(settings_file, 'r') as f:
        lines = f.readlines()
    
    # Find ar.apps.ArConfig and add raw_materials after it
    found = False
    for i, line in enumerate(lines):
        if 'ar.apps.ArConfig' in line and 'raw_materials' not in ''.join(lines):
            lines.insert(i+1, "    'raw_materials',  # Raw Materials Management\n")
            found = True
            break
    
    if found or 'raw_materials' in ''.join(lines):
        with open(settings_file, 'w') as f:
            f.writelines(lines)
        print("SUCCESS: raw_materials added to INSTALLED_APPS")
        sys.exit(0)
    else:
        print("ERROR: Could not find ar.apps.ArConfig in settings")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
