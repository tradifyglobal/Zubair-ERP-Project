"""
Template tags for module permissions.
"""

from django import template
from django.utils.safestring import mark_safe
from accounting.module_permissions import ModulePermission

register = template.Library()


@register.simple_tag
def can_access_module(user, module_code):
    """
    Check if user can access a module (has view permission).
    Usage: {% can_access_module user 'accounting' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return ModulePermission.user_can_access_module(user, module_code)


@register.simple_tag
def can_perform_action(user, module_code, action):
    """
    Check if user can perform a specific action in a module.
    Usage: {% can_perform_action user 'accounting' 'add' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return ModulePermission.user_can_perform_action(user, module_code, action)


@register.filter
def has_module_permission(user, module_code):
    """
    Filter version to check module access.
    Usage: {% if user|has_module_permission:'accounting' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return ModulePermission.user_can_access_module(user, module_code)


@register.filter
def has_action_permission(user, permission_string):
    """
    Filter to check action permission.
    Usage: {% if user|has_action_permission:'accounting:add' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    try:
        module_code, action = permission_string.split(':')
        return ModulePermission.user_can_perform_action(user, module_code, action)
    except:
        return False


@register.simple_tag
def permission_button(user, permission_string, url_name, btn_class, icon_class, text):
    """
    Render a button that shows permission denied alert if user lacks permission.
    Usage: {% permission_button user 'accounting:add' 'accounting:stakeholder_create' 'btn-primary' 'fas fa-plus' 'Add New' %}
    """
    from django.urls import reverse
    
    if not user or not user.is_authenticated:
        return ''
    
    has_permission = False
    if user.is_superuser:
        has_permission = True
    else:
        try:
            module_code, action = permission_string.split(':')
            has_permission = ModulePermission.user_can_perform_action(user, module_code, action)
        except:
            has_permission = False
    
    # Resolve URL
    try:
        url = reverse(url_name)
    except:
        url = url_name  # Use as-is if not a valid URL name
    
    if has_permission:
        # User has permission - render normal link
        return mark_safe(
            f'<a href="{url}" class="btn {btn_class}">'
            f'<i class="{icon_class}"></i> {text}'
            f'</a>'
        )
    else:
        # User lacks permission - render button with Toastr error message
        return mark_safe(
            f'<button type="button" class="btn {btn_class}" '
            f'onclick="'
            f"if (typeof toastr !== 'undefined') {{ "
            f"toastr.error('You do not have permission to perform this action.', 'Access Denied'); "
            f"}} else {{ "
            f"alert('You do not have permission to perform this action.'); "
            f"}} return false;\">"
            f'<i class="{icon_class}"></i> {text}'
            f'</button>'
        )

