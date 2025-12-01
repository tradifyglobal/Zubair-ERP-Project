#!/usr/bin/env python
"""Debug script to check what's in the context for a page render."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import RequestFactory
from accounting.context_processors import theme_context
from django.contrib.auth.models import User

# Create a request
factory = RequestFactory()
request = factory.get('/accounting/dashboard/')

# Manually authenticate as zubair
request.user = User.objects.get(username='zubair')

# Call the context processor
context = theme_context(request)

print("Theme Context Processor Output:")
print("=" * 50)
for key, value in context.items():
    print(f"{key}: {value}")
    if key == 'user_theme_pref':
        print(f"  - Type: {type(value)}")
        if value:
            print(f"  - User: {value.user}")
            print(f"  - Theme: {value.theme.display_name}")
            print(f"  - Sidebar Color: {value.sidebar_color}")
            print(f"  - Layout Mode: {value.layout_mode}")
            print(f"  - Layout Size: {value.layout_size}")

print("\n" + "=" * 50)
print("Is available_themes a list?", isinstance(context['available_themes'], list) or hasattr(context['available_themes'], '__iter__'))
print("Number of available themes:", len(list(context['available_themes'])))
