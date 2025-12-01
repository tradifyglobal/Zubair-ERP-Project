#!/usr/bin/env python
"""Check theme preferences in database."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User

# Check all users and their theme preferences
users = User.objects.all()
print(f"Total users: {users.count()}")
print("\nUser Theme Preferences:")
for user in users:
    try:
        pref = UserThemePreference.objects.get(user=user)
        print(f"  - {user.username}: Theme={pref.theme.display_name}, Sidebar={pref.sidebar_color}, Layout={pref.layout_mode}, Size={pref.layout_size}")
    except UserThemePreference.DoesNotExist:
        print(f"  - {user.username}: NO PREFERENCE (will be created on next login)")
