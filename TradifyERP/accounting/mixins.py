"""
SessionEntityMixin - Automatically filter views by session-selected entity
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.db import models
from accounting.models import Entity, UserEntity, ReportAccess
from datetime import date


class SessionEntityMixin:
    """
    Mixin that automatically:
    1. Ensures user has selected an entity
    2. Filters queryset by selected entity (for ListView, DetailView, etc.)
    3. Passes entity info to template context
    4. Validates user has access to the selected entity
    
    Usage in views:
        class MyListView(SessionEntityMixin, ListView):
            model = MyModel
            
    The view will automatically:
    - Filter by session entity
    - Add 'entity' to context
    - Redirect to entity selection if not selected
    - Validate entity access permissions
    
    Works with both list views and template views (display-only).
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Check if entity is selected, redirect to selection if not."""
        # Check if entity is selected in session
        entity_id = request.session.get('selected_entity_id')
        
        if not entity_id:
            # Store the current URL so we can return to it after entity selection
            current_url = request.path
            if request.GET:
                current_url += '?' + request.GET.urlencode()
            request.session['redirect_after_entity_selection'] = current_url
            request.session.modified = True
            # Redirect to entity selection
            return redirect('accounting:select-entity')
        
        # Store entity in request for use in views
        try:
            entity = Entity.objects.get(id=entity_id, is_active=True)
            request.entity = entity
            
            # Check if user has access to this entity (unless superuser)
            if not request.user.is_superuser:
                user_entity = UserEntity.objects.filter(user=request.user, entity=entity).first()
                if not user_entity:
                    # User doesn't have access to this entity, redirect to selection
                    if 'selected_entity_id' in request.session:
                        del request.session['selected_entity_id']
                    if 'selected_entity_code' in request.session:
                        del request.session['selected_entity_code']
                    if 'selected_entity_name' in request.session:
                        del request.session['selected_entity_name']
                    request.session.modified = True
                    return redirect('accounting:select-entity')
            
        except Entity.DoesNotExist:
            # Entity was deleted or deactivated, reset session
            if 'selected_entity_id' in request.session:
                del request.session['selected_entity_id']
            if 'selected_entity_code' in request.session:
                del request.session['selected_entity_code']
            if 'selected_entity_name' in request.session:
                del request.session['selected_entity_name']
            request.session.modified = True
            return redirect('accounting:select-entity')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter queryset by session entity. Only applicable for views with querysets."""
        # Only process if this is a view with a queryset (e.g., ListView)
        queryset = super().get_queryset()
        
        # Check if model has 'entity' field
        if hasattr(self, 'model') and self.model:
            # Check if the model has an 'entity' field
            try:
                self.model._meta.get_field('entity')
                # Model has entity field, filter by session entity
                entity_id = self.request.session.get('selected_entity_id')
                if entity_id:
                    queryset = queryset.filter(entity_id=entity_id)
            except Exception:
                # Model doesn't have entity field, don't filter
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add entity info to context."""
        context = super().get_context_data(**kwargs)
        
        # Add entity to context (will exist if dispatch() succeeded)
        if hasattr(self.request, 'entity'):
            context['entity'] = self.request.entity
        
        context['selected_entity_id'] = self.request.session.get('selected_entity_id')
        context['selected_entity_code'] = self.request.session.get('selected_entity_code')
        context['selected_entity_name'] = self.request.session.get('selected_entity_name')
        
        # Get only entities the user has access to
        if self.request.user.is_superuser:
            context['all_entities'] = Entity.objects.filter(is_active=True)
        else:
            user_entities = UserEntity.objects.filter(user=self.request.user, entity__is_active=True).select_related('entity')
            context['all_entities'] = [ue.entity for ue in user_entities] if user_entities.exists() else []
        
        return context


class ReportAccessMixin(LoginRequiredMixin):
    """
    Mixin to control user access to specific reports.
    
    Usage in views:
        class MyReportView(ReportAccessMixin, TemplateView):
            report_type = 'shareholder_investment'  # From ReportAccess.REPORT_CHOICES
            template_name = 'my_report.html'
    
    Features:
    - Restricts access to users with explicit ReportAccess grant
    - Supports multiple access levels: view_only, edit, full_access
    - Superusers always have access
    - Returns 403 Forbidden if user lacks permission
    - Passes access_level to template context for UI adjustments
    """
    
    report_type = None  # Must be set in subclass
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has access to this report."""
        # Allow superusers full access
        if request.user.is_superuser:
            request.report_access_level = 'full_access'
            return super().dispatch(request, *args, **kwargs)
        
        if not self.report_type:
            raise ValueError(f"{self.__class__.__name__} must define report_type attribute")
        
        # Get current entity
        entity_id = request.session.get('selected_entity_id')
        entity = None
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id, is_active=True)
            except Entity.DoesNotExist:
                pass
        
        # Check if this report has access restrictions
        report_has_restrictions = ReportAccess.objects.filter(
            report_type=self.report_type
        ).exists()
        
        if not report_has_restrictions:
            # No restrictions on this report, everyone can access
            request.report_access_level = 'full_access'
            return super().dispatch(request, *args, **kwargs)
        
        # Report has restrictions, check user's access
        access = ReportAccess.objects.filter(
            user=request.user,
            report_type=self.report_type,
            is_active=True
        )
        
        # Check entity-specific or all-entity access
        if entity:
            access = access.filter(
                models.Q(entity=entity) | models.Q(entity__isnull=True)
            )
        else:
            access = access.filter(entity__isnull=True)
        
        access = access.first()
        
        if not access:
            # User doesn't have access to this report
            return HttpResponseForbidden(
                f"You don't have access to this report. Please contact your administrator."
            )
        
        # Check if access is still valid (not expired)
        if not access.is_valid():
            return HttpResponseForbidden(
                f"Your access to this report has expired or been revoked. Please contact your administrator."
            )
        
        # Access granted, store access level for template use
        request.report_access_level = access.access_level
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add access level to template context."""
        context = super().get_context_data(**kwargs)
        context['report_access_level'] = getattr(self.request, 'report_access_level', 'view_only')
        
        # Add helper booleans for template
        context['can_edit'] = context['report_access_level'] in ['edit', 'full_access']
        context['can_export'] = context['report_access_level'] in ['full_access']
        context['can_view'] = True
        
        return context
