"""
Views for theme management - allows users to switch themes.
All modules will be updated with the selected theme automatically.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from accounting.models_theme import Theme, UserThemePreference
import json


@login_required
def theme_list(request):
    """Display all available themes for user selection"""
    user_pref = UserThemePreference.get_or_create_for_user(request.user)
    available_themes = Theme.objects.filter(is_active=True)
    
    context = {
        'themes': available_themes,
        'current_theme': user_pref.theme,
        'page_title': 'Theme Settings',
    }
    return render(request, 'accounting/theme_settings.html', context)


@login_required
@require_POST
def switch_theme(request):
    """
    Switch user's theme.
    POST Parameters:
        - theme_name: Name of theme to switch to (e.g., 'minia', 'starterkit')
    
    Response:
        - JSON with success status and redirect URL
    """
    try:
        data = json.loads(request.body)
        theme_name = data.get('theme_name')
        
        # Validate theme exists and is active
        theme = Theme.objects.get(name=theme_name, is_active=True)
        
        # Update user's theme preference
        user_pref = UserThemePreference.get_or_create_for_user(request.user)
        user_pref.theme = theme
        
        # Apply theme-specific layout defaults
        if theme_name == 'minia':
            # Minia theme: dark sidebar, vertical, boxed
            user_pref.sidebar_color = 'dark'
            user_pref.layout_mode = 'vertical'
            user_pref.layout_size = 'boxed'
        elif theme_name == 'starterkit':
            # Starter Kit theme: light sidebar, vertical, fluid
            user_pref.sidebar_color = 'light'
            user_pref.layout_mode = 'vertical'
            user_pref.layout_size = 'fluid'
        
        user_pref.save()
        
        messages.success(
            request, 
            f'Theme switched to {theme.display_name}. All modules updated.'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Switched to {theme.display_name}',
            'theme_name': theme_name,
            'redirect_url': request.GET.get('next', '/dashboard/'),
        })
    
    except Theme.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Theme not found or inactive',
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format',
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error switching theme: {str(e)}',
        }, status=500)


@login_required
@require_POST
def update_layout_settings(request):
    """
    Update layout settings (sidebar color, layout mode, etc.)
    All changes are saved per-user and applied globally.
    """
    try:
        data = json.loads(request.body)
        user_pref = UserThemePreference.get_or_create_for_user(request.user)
        
        # Update layout preferences
        if 'sidebar_color' in data:
            user_pref.sidebar_color = data['sidebar_color']
        if 'layout_mode' in data:
            user_pref.layout_mode = data['layout_mode']
        if 'layout_size' in data:
            user_pref.layout_size = data['layout_size']
        
        user_pref.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Layout settings updated',
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format',
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating settings: {str(e)}',
        }, status=500)


@login_required
def get_user_theme_settings(request):
    """Get current user's theme settings as JSON"""
    user_pref = UserThemePreference.get_or_create_for_user(request.user)
    
    return JsonResponse({
        'success': True,
        'theme': user_pref.theme.name,
        'sidebar_color': user_pref.sidebar_color,
        'layout_mode': user_pref.layout_mode,
        'layout_size': user_pref.layout_size,
    })


class ThemePreviewView(View):
    """Preview theme before switching"""
    
    def get(self, request, theme_name):
        """Preview a theme"""
        try:
            theme = Theme.objects.get(name=theme_name, is_active=True)
            context = {
                'page_title': f'Preview: {theme.display_name}',
                'theme': theme,
                'preview_mode': True,
            }
            return render(request, 'accounting/theme_preview.html', context)
        except Theme.DoesNotExist:
            messages.error(request, 'Theme not found')
            return redirect('theme_list')
