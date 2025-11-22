"""
Context processors for module permissions.
Adds user's accessible modules to all template contexts.
"""

from accounting.permission_utils import get_user_accessible_modules


def user_module_permissions(request):
    """
    Add user's module permissions to template context.
    Available in all templates as 'user_modules' and 'can_access_module'.
    """
    if request.user.is_authenticated:
        accessible_modules = get_user_accessible_modules(request.user)
        
        # Helper function to check module access in templates
        def can_access_module(module_code):
            return module_code in accessible_modules
        
        # Helper function to check specific action
        def can_perform_action(module_code, action):
            if module_code not in accessible_modules:
                return False
            return accessible_modules[module_code].get(f'can_{action}', False)
        
        return {
            'user_modules': accessible_modules,
            'can_access_module': can_access_module,
            'can_perform_action': can_perform_action,
        }
    
    return {
        'user_modules': {},
        'can_access_module': lambda x: False,
        'can_perform_action': lambda x, y: False,
    }
