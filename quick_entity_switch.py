"""Quick entity switch for testing - temporary helper"""
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def quick_switch_entity(request, entity_code):
    """Quick switch to entity by code (for testing)"""
    from accounting.models import Entity
    
    try:
        entity = Entity.objects.get(code=entity_code, is_active=True)
        request.session['selected_entity_id'] = entity.id
        request.session['selected_entity_code'] = entity.code
        request.session['selected_entity_name'] = entity.name
        request.session.modified = True
        
        from django.contrib import messages
        messages.success(request, f'Switched to entity: {entity.name} ({entity.code})')
        
        # Redirect back to where they came from or dashboard
        next_url = request.GET.get('next', '/accounting/dashboard/')
        return redirect(next_url)
        
    except Entity.DoesNotExist:
        from django.contrib import messages
        messages.error(request, f'Entity {entity_code} not found')
        return redirect('/accounting/select-entity/')
