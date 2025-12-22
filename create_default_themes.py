#!/usr/bin/env python
"""Create default themes in production database."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.models_theme import Theme, UserThemePreference
from django.contrib.auth.models import User

print("=== CREATING DEFAULT THEMES ===")

# Create Minia theme
minia, created = Theme.objects.get_or_create(
    name='minia',
    defaults={
        'display_name': 'Minia - Dark Professional',
        'description': 'Professional dark theme with clean UI',
        'is_active': True,
        'thumbnail_url': '/static/themes/minia/thumb.png'
    }
)
print(f"Minia theme: {'CREATED' if created else 'EXISTS'}")

# Create Starter Kit theme
starterkit, created = Theme.objects.get_or_create(
    name='starterkit',
    defaults={
        'display_name': 'Starter Kit - Light Clean',
        'description': 'Light theme with clean minimalist design',
        'is_active': True,
        'thumbnail_url': '/static/themes/starterkit/thumb.png'
    }
)
print(f"Starter Kit theme: {'CREATED' if created else 'EXISTS'}")

print("\n=== CREATING USER THEME PREFERENCES ===")

# Create preferences for all active users if they don't exist
users = User.objects.filter(is_active=True)
created_count = 0

for user in users:
    pref, created = UserThemePreference.objects.get_or_create(
        user=user,
        defaults={
            'theme': minia,
            'sidebar_color': 'light',
            'layout_mode': 'vertical',
            'layout_size': 'fluid'
        }
    )
    if created:
        created_count += 1
        print(f"  Created preference for {user.username}")
    else:
        print(f"  {user.username} already has preference")

print(f"\nTotal users processed: {users.count()}")
print(f"New preferences created: {created_count}")

print("\n=== FINAL CHECK ===")
print(f"Total themes: {Theme.objects.count()}")
print(f"Total user preferences: {UserThemePreference.objects.count()}")
print("\n✓ Default themes and user preferences created successfully!")
