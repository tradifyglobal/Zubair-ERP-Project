"""
Context processors for adding notification data to all templates
"""
from shareholder.notifications import get_all_pending_for_user


def pending_notifications(request):
    """
    Add pending notifications to template context
    """
    context = {
        'pending_notifications': {
            'pending_reviews_count': 0,
            'pending_approvals_count': 0,
            'total_pending': 0,
        }
    }
    
    # Only process authenticated users
    if request.user.is_authenticated:
        # Get entity from session if available
        entity = None
        if 'selected_entity_id' in request.session:
            try:
                from accounting.models import Entity
                entity = Entity.objects.get(id=request.session['selected_entity_id'])
            except Entity.DoesNotExist:
                pass
        
        # Get pending notifications
        pending = get_all_pending_for_user(request.user, entity)
        context['pending_notifications'] = {
            'pending_reviews_count': pending['pending_reviews_count'],
            'pending_approvals_count': pending['pending_approvals_count'],
            'total_pending': pending['total_pending'],
        }
    
    return context
