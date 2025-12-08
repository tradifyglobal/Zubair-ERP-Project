"""
Context processor for expense notifications
Makes expense notification data available in all templates
"""
import logging

logger = logging.getLogger(__name__)

# Default empty context that is ALWAYS returned
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
    
    This context processor makes expense notification counts available
    to all templates for display in the bell icon and dashboard.
    """
    
    # Always return a dict - never fail
    try:
        # Return defaults if user not authenticated
        if not request.user.is_authenticated:
            return DEFAULT_CONTEXT.copy()
        
        # Import here to avoid circular imports
        from .notifications import get_all_pending_for_user
        
        # Get entity from session if available
        entity = getattr(request, 'entity', None)
        
        # Get pending notifications for this user
        notifications = get_all_pending_for_user(request.user, entity)
        
        # Prepare context
        context = {
            'expense_notifications': notifications,
            'expense_pending_reviews_count': notifications.get('pending_reviews_count', 0),
            'expense_pending_approvals_count': notifications.get('pending_approvals_count', 0),
            'expense_pending_final_approvals_count': notifications.get('pending_final_approvals_count', 0),
            'expense_pending_reviews': list(notifications.get('pending_reviews', [])),
            'expense_pending_approvals': list(notifications.get('pending_approvals', [])),
            'expense_pending_final_approvals': list(notifications.get('pending_final_approvals', [])),
            'expense_total_pending': notifications.get('total_pending', 0),
        }
        
        # Log the results
        if context['expense_total_pending'] > 0:
            logger.info(
                f"Expense notifications for {request.user.username}: "
                f"total={context['expense_total_pending']}"
            )
        
        return context
        
    except ImportError as e:
        logger.error(f"Import error in expense context processor: {str(e)}", exc_info=True)
        return DEFAULT_CONTEXT.copy()
    except AttributeError as e:
        logger.error(f"Attribute error in expense context processor: {str(e)}", exc_info=True)
        return DEFAULT_CONTEXT.copy()
    except Exception as e:
        logger.error(
            f"Unexpected error in expense context processor for user {request.user.username if hasattr(request, 'user') else 'unknown'}: {str(e)}",
            exc_info=True
        )
        return DEFAULT_CONTEXT.copy()
