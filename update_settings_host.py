#!/usr/bin/env python3
"""Update Django settings to point to remote PostgreSQL server"""

settings_file = '/var/www/tradifyerp/TradifyERP/settings.py'

with open(settings_file, 'r') as f:
    content = f.read()

# Replace localhost with remote IP
content = content.replace("'HOST': 'localhost'", "'HOST': '192.168.2.59'")

with open(settings_file, 'w') as f:
    f.write(content)

print("✅ Settings updated: HOST changed from localhost to 192.168.2.59")
