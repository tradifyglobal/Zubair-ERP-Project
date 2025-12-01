"""
Main Dashboard Views
Handles post-login entity selection from main dashboard
"""

from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from accounting.models import Entity


class MainDashboardView(LoginRequiredMixin, View):
    """Main dashboard - allows user to select entity after login."""
    template_name = 'dashboard.html'
    login_url = 'account_login'
    
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Check if entity already selected
        entity_id = request.session.get('selected_entity_id')
        if entity_id:
            # Redirect to accounting dashboard
            return redirect('accounting:dashboard')
        
        # Get all active entities
        entities = Entity.objects.filter(is_active=True)
        
        # If only one entity, auto-select it
        if entities.count() == 1:
            request.session['selected_entity_id'] = entities.first().id
            request.session['selected_entity_code'] = entities.first().code
            request.session['selected_entity_name'] = entities.first().name
            request.session.modified = True
            return redirect('accounting:dashboard')
        
        context = {
            'entities': entities,
            'current_entity': request.session.get('selected_entity_id')
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        entity_id = request.POST.get('entity_id')
        
        try:
            entity = Entity.objects.get(id=entity_id, is_active=True)
            # Store in session
            request.session['selected_entity_id'] = entity.id
            request.session['selected_entity_code'] = entity.code
            request.session['selected_entity_name'] = entity.name
            request.session.modified = True
            
            return redirect('accounting:dashboard')
        except Entity.DoesNotExist:
            context = {
                'entities': Entity.objects.filter(is_active=True),
                'error': 'Invalid entity selected'
            }
            return render(request, self.template_name, context)
