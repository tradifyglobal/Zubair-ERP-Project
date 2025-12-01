#!/usr/bin/env python
"""Script to load initial themes into the database."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models_theme import Theme

# Create default themes if they don't exist
Theme.objects.get_or_create(
    name='minia',
    defaults={
        'display_name': 'Minia',
        'description': 'Minia Theme - Default dashboard theme',
        'is_active': True,
        'thumbnail_url': '/static/images/themes/minia-thumbnail.png'
    }
)

Theme.objects.get_or_create(
    name='starterkit',
    defaults={
        'display_name': 'Starter Kit',
        'description': 'Starter Kit Theme - Minimal and clean',
        'is_active': True,
        'thumbnail_url': '/static/images/themes/starterkit-thumbnail.png'
    }
)

print("Themes loaded successfully!")
themes = Theme.objects.all()
for theme in themes:
    print(f"  - {theme.display_name} ({theme.name})")
