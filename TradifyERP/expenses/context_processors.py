"""
Context processor for expense notifications
Makes expense notification data available in all templates
"""
import logging
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

# Default empty context
DEFAULT_CONTEXT = {
    'expense_notifications': {},
    'expense_pending_reviews_count': 0,
    'expense_pending_approvals_count': 0,
    'expense_pending_final_approvals_count': 0,
    'expense_pending_reviews': [],
    'expense_pending_approvals': [],
    'expense_pending_final_approvals': [],
    'expense_total_pending': 0,
}


def pending_expense_notifications(request):
    """
    Add pending expense notifications to template context
    
    Provides:
    - expense_pending_reviews_count
    - expense_pending_approvals_count
    - expense_pending_final_approvals_count
    - expense_total_pending
    - expense_pending_reviews (QuerySet)
    - expense_pending_approvals (QuerySet)
    - expense_pending_final_approvals (QuerySet)
    """
    
    # Return defaults if user not authenticated
    if not request.user.is_authenticated:
        return DEFAULT_CONTEXT.copy()
    
    try:
        # Check database is accessible
        connection.ensure_connection()
        
        # Import here to avoid circular imports
        from .notifications import get_all_pending_for_user
        
        # Get entity from session if available
        entity = getattr(request, 'entity', None)
        
        # Get all pending items for this user
        notifications = get_all_pending_for_user(request.user, entity)
        
        # Log for debugging
        logger.debug(
            f"Expense notifications for {request.user.username}: "
            f"reviews={notifications.get('pending_reviews_count', 0)}, "
            f"approvals={notifications.get('pending_approvals_count', 0)}, "
            f"final={notifications.get('pending_final_approvals_count', 0)}"
        )
        
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
        
    except (OperationalError, ProgrammingError) as e:
        # Database not ready
        logger.warning(f"Database error in expense notifications: {str(e)}")
        return DEFAULT_CONTEXT.copy()
    except Exception as e:
        # Log any other errors but don't crash
        logger.error(
            f"Error in expense notifications for {request.user.username}: {str(e)}",
            exc_info=True
        )
        return DEFAULT_CONTEXT.copy()
