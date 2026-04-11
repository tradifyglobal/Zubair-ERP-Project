#!/bin/bash
# Fix CSRF_TRUSTED_ORIGINS to include 192.168.20.10

SETTINGS_FILE="/var/www/tradifyerp/TradifyERP/settings.py"

# Find the line with CSRF_TRUSTED_ORIGINS and add our entry
# We'll insert after the line that contains 'http://192.168.5.10:8000'

sed -i "/CSRF_TRUSTED_ORIGINS = \[/a\    'http://192.168.20.10'," $SETTINGS_FILE

# Verify the change
echo "CSRF_TRUSTED_ORIGINS updated. New content:"
grep -A 5 "CSRF_TRUSTED_ORIGINS = " $SETTINGS_FILE
