"""
Decorators and utilities for checking module permissions.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from accounting.module_permissions import ModulePermission, UserModuleAccessLog


def module_permission_required(module, action='view', redirect_url='accounting:dashboard'):
    """
    Decorator to check if user has permission to access a module and perform an action.
    
    Usage:
        @module_permission_required('accounting', 'add')
        def my_view(request):
            ...
    
    Args:
        module: Module name (e.g., 'accounting', 'hr', 'crm')
        action: Action type ('view', 'add', 'edit', 'delete', 'approve', 'export')
        redirect_url: Where to redirect if permission denied
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Log the access attempt
            def log_access(result, reason=''):
                try:
                    UserModuleAccessLog.objects.create(
                        user=user,
                        module=module,
                        action_attempted=action,
                        result=result,
                        reason=reason,
                        request_path=request.path,
                        request_ip=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                    )
                except:
                    pass  # Don't fail if logging fails
            
            # Check if user is authenticated
            if not user.is_authenticated:
                log_access('DENIED', 'User not authenticated')
                messages.error(request, 'You must be logged in to access this page.')
                return redirect('login')
            
            # Superusers have all permissions
            if user.is_superuser:
                log_access('ALLOWED', 'Superuser access')
                return view_func(request, *args, **kwargs)
            
            # Check module permission
            has_permission = ModulePermission.user_can_perform_action(user, module, action)
            
            if has_permission:
                log_access('ALLOWED', f'Permission granted for {action}')
                return view_func(request, *args, **kwargs)
            else:
                log_access('DENIED', f'No {action} permission for {module}')
                messages.error(
                    request,
                    f'You do not have permission to {action} in the {module} module.'
                )
                return redirect(redirect_url)
        
        return wrapper
    return decorator


def has_module_access(module, action='view'):
    """
    Decorator to check module access, raises PermissionDenied if not allowed.
    Use with class-based views.
    
    Usage:
        class MyView(View):
            @method_decorator(has_module_access('accounting', 'edit'))
            def dispatch(self, *args, **kwargs):
                return super().dispatch(*args, **kwargs)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                raise PermissionDenied('Authentication required')
            
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            has_permission = ModulePermission.user_can_perform_action(user, module, action)
            
            if not has_permission:
                raise PermissionDenied(
                    f'You do not have {action} permission for {module} module'
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


class ModulePermissionMixin:
    """
    Mixin for class-based views to check module permissions.
    
    Usage:
        class MyView(ModulePermissionMixin, ListView):
            module_name = 'accounting'
            required_action = 'view'
    """
    module_name = None
    required_action = 'view'
    permission_denied_message = 'You do not have permission to access this page.'
    
    def dispatch(self, request, *args, **kwargs):
        # Check authentication
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in.')
            return redirect('login')
        
        # Superusers bypass permission checks
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Check module permission
        if self.module_name:
            has_permission = ModulePermission.user_can_perform_action(
                request.user,
                self.module_name,
                self.required_action
            )
            
            if not has_permission:
                # Log the denied access
                try:
                    UserModuleAccessLog.objects.create(
                        user=request.user,
                        module=self.module_name,
                        action_attempted=self.required_action,
                        result='DENIED',
                        reason=f'No {self.required_action} permission',
                        request_path=request.path,
                        request_ip=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                    )
                except:
                    pass
                
                messages.error(request, self.permission_denied_message)
                return redirect('accounting:dashboard')
        
        return super().dispatch(request, *args, **kwargs)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_accessible_modules(user):
    """
    Get list of modules accessible to a user with their permissions.
    Returns a dictionary with module info.
    """
    if user.is_superuser:
        # Superuser has access to all modules
        return {
            module[0]: {
                'name': module[1],
                'code': module[0],
                'can_view': True,
                'can_add': True,
                'can_edit': True,
                'can_delete': True,
                'can_approve': True,
                'can_export': True,
            }
            for module in ModulePermission.MODULE_CHOICES
        }
    
    # Get user's permissions
    permissions = ModulePermission.objects.filter(
        user=user,
        is_active=True,
        can_view=True
    )
    
    accessible_modules = {}
    for perm in permissions:
        accessible_modules[perm.module] = {
            'name': perm.get_module_display(),
            'code': perm.module,
            'can_view': perm.can_view,
            'can_add': perm.can_add,
            'can_edit': perm.can_edit,
            'can_delete': perm.can_delete,
            'can_approve': perm.can_approve,
            'can_export': perm.can_export,
        }
    
    return accessible_modules


def check_action_permission(user, module, action):
    """
    Helper function to check if user can perform an action in a module.
    Returns (allowed: bool, reason: str)
    """
    if not user.is_authenticated:
        return False, 'User not authenticated'
    
    if user.is_superuser:
        return True, 'Superuser access'
    
    has_permission = ModulePermission.user_can_perform_action(user, module, action)
    
    if has_permission:
        return True, f'{action.capitalize()} permission granted'
    else:
        return False, f'No {action} permission for {module}'
