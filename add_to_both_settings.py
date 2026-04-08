#!/usr/bin/env python3
"""
Add raw_materials to both settings.py and settings_production.py
"""
files = [
    '/var/www/tradifyerp/TradifyERP/settings.py',
    '/var/www/tradifyerp/TradifyERP/settings_production.py'
]

for settings_file in files:
    try:
        with open(settings_file, 'r') as f:
            lines = f.readlines()
        
        # Check if already there
        if any('raw_materials' in line for line in lines):
            print(f"raw_materials already in {settings_file}")
            continue
        
        # Find ar.apps.ArConfig and add after it
        for i, line in enumerate(lines):
            if 'ar.apps.ArConfig' in line:
                lines.insert(i+1, "    'raw_materials.apps.RawMaterialsConfig',  # Raw Materials Management\n")
                with open(settings_file, 'w') as f:
                    f.writelines(lines)
                print(f"Added to {settings_file}")
                break
    except Exception as e:
        print(f"Error with {settings_file}: {e}")
