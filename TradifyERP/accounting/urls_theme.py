"""
URL patterns for theme management.
Add these to your main urls.py under the accounting app URLs.
"""

from django.urls import path
from accounting.views_theme import (
    theme_list,
    switch_theme,
    update_layout_settings,
    get_user_theme_settings,
    ThemePreviewView,
)

app_name = 'theme'

urlpatterns = [
    # Theme settings page
    path('settings/', theme_list, name='theme_settings'),
    
    # API endpoints
    path('api/switch/', switch_theme, name='switch_theme'),
    path('api/update-layout/', update_layout_settings, name='update_layout'),
    path('api/get-settings/', get_user_theme_settings, name='get_settings'),
    
    # Theme preview
    path('preview/<str:theme_name>/', ThemePreviewView.as_view(), name='preview'),
]
