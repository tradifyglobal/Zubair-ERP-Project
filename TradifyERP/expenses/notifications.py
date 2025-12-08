"""
Notification system for expense reviews and approvals
Based on Django permissions for granular control
"""
import logging
from django.db.models import Q
from .models import EmployeeExpenseReport

logger = logging.getLogger(__name__)


def get_pending_reviews_for_user(user, entity=None):
    """
    Get pending expense reports awaiting review by the user
    
    User must have 'expenses.review_employeeexpensereport' permission
    """
    try:
        # Check if user has review permission
        if not user.has_perm('expenses.review_employeeexpensereport'):
            return EmployeeExpenseReport.objects.none()
        
        # Get expense reports awaiting review (PENDING_REVIEW status)
        pending = EmployeeExpenseReport.objects.filter(
            status='PENDING_REVIEW'
        ).distinct()
        
        if entity:
            pending = pending.filter(entity=entity)
        
        return pending
    except Exception as e:
        logger.error(f"Error getting pending reviews for {user.username}: {str(e)}")
        return EmployeeExpenseReport.objects.none()


def get_pending_approvals_for_user(user, entity=None):
    """
    Get pending expense reports awaiting approval by this user
    
    User must have 'expenses.approve_employeeexpensereport' permission
    """
    try:
        # Check if user has approval permission
        if not user.has_perm('expenses.approve_employeeexpensereport'):
            return EmployeeExpenseReport.objects.none()
        
        # Get ALL expense reports in PENDING_APPROVAL status
        pending = EmployeeExpenseReport.objects.filter(
            status='PENDING_APPROVAL'
        ).distinct()
        
        if entity:
            pending = pending.filter(entity=entity)
        
        return pending
    except Exception as e:
        logger.error(f"Error getting pending approvals for {user.username}: {str(e)}")
        return EmployeeExpenseReport.objects.none()


def get_pending_final_approvals_for_user(user, entity=None):
    """
    Get pending expense reports awaiting FINAL approval (assigned to this user)
    
    User must have 'expenses.approve_employeeexpensereport' permission
    """
    try:
        # Check if user has approval permission
        if not user.has_perm('expenses.approve_employeeexpensereport'):
            return EmployeeExpenseReport.objects.none()
        
        # Get reports where user is assigned as finance_approver
        from .models import ExpenseApprovalWorkflow
        
        pending = EmployeeExpenseReport.objects.filter(
            status='PENDING_APPROVAL',
            approval_workflow__finance_approver=user,
            approval_workflow__finance_approved=False
        ).distinct()
        
        if entity:
            pending = pending.filter(entity=entity)
        
        return pending
    except Exception as e:
        logger.error(f"Error getting pending final approvals for {user.username}: {str(e)}")
        return EmployeeExpenseReport.objects.none()


def get_all_pending_for_user(user, entity=None):
    """
    Get all pending expense reports (reviews + approvals) for the user
    
    Returns a dictionary with counts and querysets
    Requires appropriate permissions to see items
    """
    try:
        reviews = get_pending_reviews_for_user(user, entity)
        approvals = get_pending_approvals_for_user(user, entity)
        final_approvals = get_pending_final_approvals_for_user(user, entity)
        
        reviews_count = reviews.count() if reviews else 0
        approvals_count = approvals.count() if approvals else 0
        final_approvals_count = final_approvals.count() if final_approvals else 0
        
        return {
            'pending_reviews': reviews,
            'pending_reviews_count': reviews_count,
            'pending_approvals': approvals,
            'pending_approvals_count': approvals_count,
            'pending_final_approvals': final_approvals,
            'pending_final_approvals_count': final_approvals_count,
            'total_pending': reviews_count + approvals_count + final_approvals_count,
        }
    except Exception as e:
        logger.error(f"Error getting all pending for {user.username}: {str(e)}")
        return {
            'pending_reviews': [],
            'pending_reviews_count': 0,
            'pending_approvals': [],
            'pending_approvals_count': 0,
            'pending_final_approvals': [],
            'pending_final_approvals_count': 0,
            'total_pending': 0,
        }

