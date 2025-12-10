#!/usr/bin/env python3
import sys

# Read the header file
with open('/var/www/tradifyerp/TradifyERP/templates/partials/header.html', 'r') as f:
    content = f.read()

# Fix the broken line by removing the line break in the Change Password link
content = content.replace(
    '<a class="dropdown-item" href="{% url \'accounting:user_change_password\' %}"><i class="mdi mdi-lock text-muted font-size-16 align-middle me-1"></i> Change Passw\nord</a>',
    '<a class="dropdown-item" href="{% url \'accounting:user_change_password\' %}"><i class="mdi mdi-lock text-muted font-size-16 align-middle me-1"></i> Change Password</a>'
)

# Write back
with open('/var/www/tradifyerp/TradifyERP/templates/partials/header.html', 'w') as f:
    f.write(content)

print("Fixed header.html")
