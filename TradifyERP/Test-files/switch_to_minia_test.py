import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
import sys
sys.path.insert(0, 'g:\\TradifyERP\\TradifyERP')
django.setup()

from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User

# Get user
user = User.objects.get(username='zubair')

# Get Minia theme
minia_theme = Theme.objects.get(name='Minia')

# Update preferences to Minia (which should be dark + boxed)
pref = UserThemePreference.objects.get(user=user)
pref.theme = minia_theme
pref.sidebar_color = 'dark'
pref.layout_mode = 'vertical'
pref.layout_size = 'boxed'
pref.save()

print("✓ Theme switched to Minia")
print(f"  Sidebar Color: {pref.sidebar_color}")
print(f"  Layout Mode: {pref.layout_mode}")
print(f"  Layout Size: {pref.layout_size}")

print("\nExpected body tag attributes:")
print(f'  data-bs-theme="dark"')
print(f'  data-sidebar="dark"')
print(f'  data-layout="vertical"')
print(f'  data-layout-size="boxed"')

print("\nCSS selectors that should apply:")
print(f"  body[data-bs-theme='dark'] - Dark theme colors")
print(f"  body[data-sidebar='dark'] - Dark sidebar styling")
print(f"  body[data-layout-size='boxed'] - Boxed/centered layout")
