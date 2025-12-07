"""
Context processor for expense notifications
Makes expense notification data available in all templates
"""
from .notifications import get_all_pending_for_user


def pending_expense_notifications(request):
    """
    Add pending expense notifications to template context
    
    Available in templates as:
    - expense_notifications (dict with pending counts and querysets)
    - expense_pending_reviews_count
    - expense_pending_approvals_count
    - expense_pending_final_approvals_count
    - expense_pending_reviews (QuerySet)
    - expense_pending_approvals (QuerySet)
    - expense_pending_final_approvals (QuerySet)
    - expense_total_pending
    """
    if not request.user.is_authenticated:
        return {
            'expense_notifications': {},
            'expense_pending_reviews_count': 0,
            'expense_pending_approvals_count': 0,
            'expense_pending_final_approvals_count': 0,
            'expense_pending_reviews': [],
            'expense_pending_approvals': [],
            'expense_pending_final_approvals': [],
            'expense_total_pending': 0,
        }
    
    # Get entity from session if available
    entity = getattr(request, 'entity', None)
    
    # Get all pending items for this user
    notifications = get_all_pending_for_user(request.user, entity)
    
    return {
        'expense_notifications': notifications,
        'expense_pending_reviews_count': notifications.get('pending_reviews_count', 0),
        'expense_pending_approvals_count': notifications.get('pending_approvals_count', 0),
        'expense_pending_final_approvals_count': notifications.get('pending_final_approvals_count', 0),
        'expense_pending_reviews': notifications.get('pending_reviews', []),
        'expense_pending_approvals': notifications.get('pending_approvals', []),
        'expense_pending_final_approvals': notifications.get('pending_final_approvals', []),
        'expense_total_pending': notifications.get('total_pending', 0),
    }
