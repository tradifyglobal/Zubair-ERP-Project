#!/usr/bin/env python
"""Update all user layout preferences to horizontal"""

import os
import sys
import django

# Add the project directory to path
sys.path.insert(0, '/var/www/tradifyerp')
os.chdir('/var/www/tradifyerp')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models_theme import UserThemePreference

# Update all vertical layouts to horizontal
updated = UserThemePreference.objects.filter(layout_mode='vertical').update(layout_mode='horizontal')
print(f"Updated {updated} user preferences from vertical to horizontal")

# Also update any None/null values to horizontal
updated_null = UserThemePreference.objects.filter(layout_mode__isnull=True).update(layout_mode='horizontal')
print(f"Updated {updated_null} null layout preferences to horizontal")

print("All users will now see horizontal layout by default")
