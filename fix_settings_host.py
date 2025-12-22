#!/usr/bin/env python3
"""Fix the corrupted HOST line in settings.py"""

settings_file = '/var/www/tradifyerp/TradifyERP/settings.py'

with open(settings_file, 'r') as f:
    lines = f.readlines()

# Find and fix the corrupted HOST line
for i, line in enumerate(lines):
    if "'HOST.*192.168.20.11'" in line:
        lines[i] = "        'HOST': '192.168.20.11',\n"
        print(f"✅ Fixed line {i+1}: HOST setting")
        break

with open(settings_file, 'w') as f:
    f.writelines(lines)

print("✅ Settings file fixed")
