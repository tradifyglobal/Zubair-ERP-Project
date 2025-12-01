"""
Context processors for module permissions and session entity.
Adds user's accessible modules and session entity to all template contexts.
"""

from accounting.permission_utils import get_user_accessible_modules
from accounting.models import Entity, UserEntity


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


def session_entity_context(request):
    """
    Add session entity information to all templates.
    Available as 'session_entity', 'selected_entity_id', 'selected_entity_code', 'selected_entity_name'.
    Also provides 'all_entities' for entity switching in navbar.
    
    Filters entities based on user assignments:
    - If user is superuser: show all active entities
    - If user has UserEntity assignments: show only assigned entities
    - Otherwise: show all active entities (backward compatibility)
    """
    entity_id = request.session.get('selected_entity_id')
    entity_code = request.session.get('selected_entity_code')
    entity_name = request.session.get('selected_entity_name')
    
    session_entity = None
    if entity_id:
        try:
            session_entity = Entity.objects.get(id=entity_id, is_active=True)
        except Entity.DoesNotExist:
            pass
    
    # Determine which entities to show
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # Superusers see all active entities
            all_entities = Entity.objects.filter(is_active=True).order_by('name')
        else:
            # Check if user has UserEntity assignments
            user_entities = UserEntity.objects.filter(
                user=request.user,
                entity__is_active=True
            ).select_related('entity').order_by('entity__name')
            
            if user_entities.exists():
                # Show only assigned entities
                all_entities = [ue.entity for ue in user_entities]
            else:
                # STRICT MODE: No assignments = No entities visible
                all_entities = []
    else:
        # Not authenticated
        all_entities = Entity.objects.filter(is_active=True).order_by('name')
    
    return {
        'session_entity': session_entity,
        'selected_entity_id': entity_id,
        'selected_entity_code': entity_code,
        'selected_entity_name': entity_name,
        'all_entities': all_entities,
    }


def theme_context(request):
    """
    Add theme information to template context.
    Makes theme settings available in all templates.
    
    Usage in templates:
        - {{ current_theme.name }}
        - {{ user_theme_pref.sidebar_color }}
        - {{ user_theme_pref.layout_mode }}
        - {{ user_theme_pref.layout_size }}
    """
    from accounting.models_theme import UserThemePreference, Theme
    
    context = {
        'available_themes': [],
        'current_theme': None,
        'user_theme_pref': None,
    }
    
    # Only process for authenticated users
    if request.user.is_authenticated:
        try:
            # Get available themes
            context['available_themes'] = Theme.objects.filter(is_active=True)
            
            # Get user's theme preference
            user_pref = UserThemePreference.get_or_create_for_user(request.user)
            context['user_theme_pref'] = user_pref
            context['current_theme'] = user_pref.theme
            
        except Exception:
            # Silently fail - don't break page rendering if theme system has issues
            pass
    
    return context
