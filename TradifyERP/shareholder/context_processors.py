"""
Context processors for adding notification data to all templates
"""
from shareholder.notifications import get_all_pending_for_user as get_shareholder_pending
from expenses.notifications import get_all_pending_for_user as get_expense_pending


def pending_notifications(request):
    """
    Add pending notifications to template context (both shareholder and expense)
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
        
        # Get pending shareholder contribution notifications
        shareholder_pending = get_shareholder_pending(request.user, entity)
        
        # Get pending expense notifications
        expense_pending = get_expense_pending(request.user, entity)
        
        # Combine both
        total_reviews = shareholder_pending['pending_reviews_count'] + expense_pending['pending_reviews_count']
        total_approvals = shareholder_pending['pending_approvals_count'] + expense_pending['pending_approvals_count']
        
        context['pending_notifications'] = {
            'pending_reviews_count': total_reviews,
            'pending_approvals_count': total_approvals,
            'total_pending': total_reviews + total_approvals,
        }
    
    return context
