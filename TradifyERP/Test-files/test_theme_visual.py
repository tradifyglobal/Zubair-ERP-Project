import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import UserThemePreference, Theme
from django.contrib.auth.models import User
from django.test import Client

# Get user
user = User.objects.get(username='zubair')

# Get preferences
pref = UserThemePreference.objects.get(user=user)
print(f"Current Theme: {pref.theme.name}")
print(f"Sidebar Color: {pref.sidebar_color}")
print(f"Layout Mode: {pref.layout_mode}")
print(f"Layout Size: {pref.layout_size}")

print("\nCSS attributes that should be on body tag:")
print(f"  data-bs-theme: {pref.sidebar_color}")
print(f"  data-sidebar: {pref.sidebar_color}")
print(f"  data-layout: {pref.layout_mode}")
print(f"  data-layout-size: {pref.layout_size}")

# Test the API to switch theme
print("\n--- Testing Theme Switch ---")
client = Client()
client.force_login(user)

# Get current themes
print("\nAvailable themes:")
for theme in Theme.objects.all():
    print(f"  - {theme.name}: {theme.display_name}")

# Check what HTML will be rendered
print("\nExpected HTML body tag:")
print(f'<body data-bs-theme="{pref.sidebar_color}" data-sidebar="{pref.sidebar_color}" data-layout="{pref.layout_mode}" data-layout-size="{pref.layout_size}">')
