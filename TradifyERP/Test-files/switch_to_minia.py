#!/usr/bin/env python
"""Switch zubair user to Minia theme."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User

user = User.objects.get(username='zubair')
theme = Theme.objects.get(name='minia')

pref = UserThemePreference.objects.get(user=user)
pref.theme = theme
pref.sidebar_color = 'dark'
pref.layout_mode = 'vertical'
pref.layout_size = 'boxed'
pref.save()

print("=" * 60)
print("THEME SWITCHED TO MINIA")
print("=" * 60)
print(f"User: {user.username}")
print(f"Theme: {pref.theme.display_name}")
print(f"Sidebar: {pref.sidebar_color}")
print(f"Layout Size: {pref.layout_size}")
print("\nRefresh your browser to see the changes!")
print("=" * 60)
