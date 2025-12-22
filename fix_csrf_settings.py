#!/usr/bin/env python3
import re

with open("/var/www/tradifyerp/TradifyERP/settings_production.py", "r") as f:
    content = f.read()

# Remove any existing CSRF_TRUSTED_ORIGINS line
content = re.sub(r"CSRF_TRUSTED_ORIGINS = .*\n", "", content)

# Add the correct CSRF_TRUSTED_ORIGINS after CSRF_COOKIE_SECURE
new_line = 'CSRF_COOKIE_SECURE = False\n\nCSRF_TRUSTED_ORIGINS = ["https://tradifyglobal.com", "https://www.tradifyglobal.com", "http://192.168.20.10", "http://localhost"]'
content = re.sub(r"CSRF_COOKIE_SECURE = False", new_line, content)

with open("/var/www/tradifyerp/TradifyERP/settings_production.py", "w") as f:
    f.write(content)

print("CSRF_TRUSTED_ORIGINS fixed successfully")
