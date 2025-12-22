#!/usr/bin/env python3
"""
Update Django settings to connect to remote PostgreSQL database
Changes HOST from 'localhost' to the actual DB server IP
"""

import sys

settings_file = '/var/www/tradifyerp/TradifyERP/settings.py'

# Read the file
with open(settings_file, 'r') as f:
    content = f.read()

# Find and replace the HOST setting
old_host = "'HOST': 'localhost',"
new_host = "'HOST': '192.168.20.11',"

if old_host in content:
    content = content.replace(old_host, new_host)
    print(f"✅ Changed HOST from 'localhost' to '192.168.20.11'")
else:
    print("❌ Could not find HOST setting")
    sys.exit(1)

# Write back
with open(settings_file, 'w') as f:
    f.write(content)

print("✅ Settings file updated successfully")
