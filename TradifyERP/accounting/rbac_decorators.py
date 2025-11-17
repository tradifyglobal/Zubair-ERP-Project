"""
RBAC Decorators for permission checking.
Implements SOX 404 access control.
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_permission(user, entity, resource, model, action):
    """
    Check if user has permission to perform action.
    Returns: (has_permission: bool, permission_obj: Permission or None)
    """
    from .role_models import UserRole, Permission

    # Superusers bypass checks (but still logged)
    if user.is_superuser:
        return True, None

    # Check if user has active role in entity
    user_roles = UserRole.objects.filter(
        user=user,
        entity=entity,
        is_active=True
    ).select_related('role')

    if not user_roles.exists():
        return False, None

    # Check for matching permission
    for user_role in user_roles:
        permission = Permission.objects.filter(
            role=user_role.role,
            resource=resource,
            model=model,
            action=action
        ).first()

        if permission:
            return True, permission

    return False, None


def log_permission_check(user, entity, resource, model, action, result, reason="", request=None):
    """Log permission check to audit trail."""
    from .role_models import UserPermissionLog

    try:
        UserPermissionLog.objects.create(
            user=user,
            entity=entity,
            resource=resource,
            model=model,
            action=action,
            result=result,
            reason=reason,
            request_ip=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
        )
    except Exception as e:
        logger.error(f"Failed to log permission check: {e}")


def require_permission(resource, model, action, get_entity_id=None):
    """
    Decorator to require specific permission.
    
    Args:
        resource: 'accounting', 'shareholder', 'reporting', etc.
        model: 'LedgerEntry', 'CapitalContribution', etc.
        action: 'CREATE', 'READ', 'UPDATE', 'DELETE', 'APPROVE', 'POST', etc.
        get_entity_id: Callable(request, *args, **kwargs) to get entity_id
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Get entity ID
            if get_entity_id:
                try:
                    entity_id = get_entity_id(request, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Failed to get entity_id: {e}")
                    raise PermissionDenied("Entity not found")
            else:
                entity_id = kwargs.get('entity_id') or request.GET.get('entity_id')

            if not entity_id:
                raise PermissionDenied("Entity not specified")

            # Import here to avoid circular imports
            from .models import Entity

            try:
                entity = Entity.objects.get(id=entity_id)
            except Entity.DoesNotExist:
                raise PermissionDenied("Entity not found")

            # Check permission
            has_permission, permission_obj = check_permission(
                request.user,
                entity,
                resource,
                model,
                action
            )

            # Log the permission check
            log_permission_check(
                request.user,
                entity,
                resource,
                model,
                action,
                'GRANTED' if has_permission else 'DENIED',
                request=request
            )

            if not has_permission:
                logger.warning(
                    f"Permission denied: {request.user.username} "
                    f"attempted {action} on {model} in {entity.code}"
                )
                raise PermissionDenied(
                    f"You don't have permission to {action} {model}"
                )

            # Add permission context to request
            request.current_permission = permission_obj

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_permission_class(resource, model, action, get_entity_id=None):
    """
    Class-based view decorator for permission checking.
    """
    def decorator(cls):
        # Wrap the dispatch method
        original_dispatch = cls.dispatch

        @wraps(original_dispatch)
        def new_dispatch(self, request, *args, **kwargs):
            # Get entity ID
            if get_entity_id:
                try:
                    entity_id = get_entity_id(request, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Failed to get entity_id: {e}")
                    raise PermissionDenied("Entity not found")
            else:
                entity_id = kwargs.get('entity_id') or request.GET.get('entity_id')

            if not entity_id:
                raise PermissionDenied("Entity not specified")

            # Import here to avoid circular imports
            from .models import Entity

            try:
                entity = Entity.objects.get(id=entity_id)
            except Entity.DoesNotExist:
                raise PermissionDenied("Entity not found")

            # Check permission
            has_permission, permission_obj = check_permission(
                request.user,
                entity,
                resource,
                model,
                action
            )

            # Log the permission check
            log_permission_check(
                request.user,
                entity,
                resource,
                model,
                action,
                'GRANTED' if has_permission else 'DENIED',
                request=request
            )

            if not has_permission:
                logger.warning(
                    f"Permission denied: {request.user.username} "
                    f"attempted {action} on {model} in {entity.code}"
                )
                raise PermissionDenied(
                    f"You don't have permission to {action} {model}"
                )

            # Add permission context to request
            request.current_permission = permission_obj
            request.current_entity = entity

            return original_dispatch(self, request, *args, **kwargs)

        cls.dispatch = new_dispatch
        return cls

    return decorator


def auditor_read_only(view_func):
    """
    Decorator to enforce read-only access for auditor role.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from .role_models import UserRole

        # Check if user is auditor
        is_auditor = UserRole.objects.filter(
            user=request.user,
            role__name='AUDITOR',
            is_active=True
        ).exists()

        if is_auditor:
            # Allow read-only (GET, HEAD, OPTIONS)
            if request.method not in ['GET', 'HEAD', 'OPTIONS']:
                logger.warning(
                    f"Auditor {request.user.username} attempted "
                    f"{request.method} on {request.path}"
                )
                raise PermissionDenied("Auditors have read-only access")

        return view_func(request, *args, **kwargs)

    return wrapper
