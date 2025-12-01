"""
Entity Selection Views
Handles post-login entity selection and session management
"""

from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib import messages
from accounting.models import Entity, UserEntity
from accounting.permission_utils import get_user_accessible_entities


class EntitySelectionView(LoginRequiredMixin, View):
    """Allow user to select which entity to manage after login."""
    template_name = 'accounting/entity_selection.html'
    login_url = 'account_login'
    
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get user's accessible entities
        entities = get_user_accessible_entities(request.user)
        
        # Convert to list if it's a queryset for consistent handling
        if hasattr(entities, 'model'):  # It's a queryset
            entities = list(entities)
        
        # If user has NO accessible entities, show error message
        if len(entities) == 0:
            context = {
                'entities': [],
                'no_access': True,
                'error_title': 'No Entity Assignments',
                'error_message': f'You do not have access to any entities yet. Please contact your administrator to assign you to one or more entities.'
            }
            return render(request, self.template_name, context)
        
        # If only one entity, auto-select it
        if len(entities) == 1:
            entity = entities[0]
            request.session['selected_entity_id'] = entity.id
            request.session['selected_entity_code'] = entity.code
            request.session['selected_entity_name'] = entity.name
            request.session.modified = True
            return redirect('accounting:dashboard')
        
        # Check if user has entity restrictions
        user_has_restrictions = UserEntity.objects.filter(user=request.user, entity__is_active=True).exists()
        
        context = {
            'entities': entities,
            'current_entity': request.session.get('selected_entity_id'),
            'user_has_restrictions': user_has_restrictions
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        entity_id = request.POST.get('entity_id')
        
        try:
            entity = Entity.objects.get(id=entity_id, is_active=True)
            
            # Check if user has access to this entity
            user_entity = UserEntity.objects.filter(user=request.user, entity=entity).first()
            user_accessible_entities = get_user_accessible_entities(request.user)
            
            # Get list of entity IDs the user can access
            if isinstance(user_accessible_entities, list):
                accessible_entity_ids = [e.id for e in user_accessible_entities]
            else:
                accessible_entity_ids = list(user_accessible_entities.values_list('id', flat=True))
            
            # Verify user has access to the entity
            if entity.id not in accessible_entity_ids and not request.user.is_superuser:
                messages.error(request, 'You do not have access to this entity.')
                entities = get_user_accessible_entities(request.user)
                # Convert to list if it's a queryset
                if hasattr(entities, 'model'):
                    entities = list(entities)
                context = {
                    'entities': entities,
                    'error': 'Invalid entity selected - Access Denied',
                    'current_entity': request.session.get('selected_entity_id')
                }
                return render(request, self.template_name, context)
            
            # Check if entity switching is allowed
            if user_entity and not user_entity.can_switch:
                # Only allow if this is the user's default entity
                if not user_entity.is_default:
                    messages.error(request, 'Entity switching is disabled for your account.')
                    return redirect('accounting:dashboard')
            
            # Store in session
            request.session['selected_entity_id'] = entity.id
            request.session['selected_entity_code'] = entity.code
            request.session['selected_entity_name'] = entity.name
            
            # Check if there's a page to return to
            redirect_url = request.session.get('redirect_after_entity_selection')
            if redirect_url:
                # Clean up the session
                del request.session['redirect_after_entity_selection']
                request.session.modified = True
                return redirect(redirect_url)
            
            request.session.modified = True
            return redirect('accounting:dashboard')
        except Entity.DoesNotExist:
            entities = get_user_accessible_entities(request.user)
            # Convert to list if it's a queryset
            if hasattr(entities, 'model'):
                entities = list(entities)
            context = {
                'entities': entities,
                'error': 'Invalid entity selected',
                'current_entity': request.session.get('selected_entity_id')
            }
            return render(request, self.template_name, context)


class EntitySwitchView(LoginRequiredMixin, View):
    """Quick entity switch endpoint."""
    
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        entity_id = request.POST.get('entity_id')
        
        try:
            entity = Entity.objects.get(id=entity_id, is_active=True)
            
            # Get user's accessible entities
            user_accessible_entities = get_user_accessible_entities(request.user)
            
            # Get list of entity IDs the user can access
            if isinstance(user_accessible_entities, list):
                accessible_entity_ids = [e.id for e in user_accessible_entities]
            else:
                accessible_entity_ids = list(user_accessible_entities.values_list('id', flat=True))
            
            # Verify user has access to the entity
            if entity.id not in accessible_entity_ids and not request.user.is_superuser:
                messages.error(request, 'You do not have access to this entity.')
                return redirect(request.META.get('HTTP_REFERER', '/accounting/dashboard/'))
            
            # Check if entity switching is allowed
            user_entity = UserEntity.objects.filter(user=request.user, entity=entity).first()
            if user_entity and not user_entity.can_switch:
                messages.error(request, 'Entity switching is disabled for your account.')
                return redirect(request.META.get('HTTP_REFERER', '/accounting/dashboard/'))
            
            request.session['selected_entity_id'] = entity.id
            request.session['selected_entity_code'] = entity.code
            request.session['selected_entity_name'] = entity.name
            request.session.modified = True
            
            # Redirect back to previous page or dashboard
            next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/accounting/dashboard/'))
            return redirect(next_url)
        except Entity.DoesNotExist:
            messages.error(request, 'Entity not found.')
            return redirect(request.META.get('HTTP_REFERER', '/accounting/dashboard/'))
