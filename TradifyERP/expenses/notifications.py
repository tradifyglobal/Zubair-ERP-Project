"""
Notification system for expense reviews and approvals
"""
import logging
from django.db.models import Q
from accounting.module_permissions import ModulePermission
from .models import EmployeeExpenseReport

logger = logging.getLogger(__name__)


def get_pending_reviews_for_user(user, entity=None):
    """
    Get pending expense reports awaiting review by the user
    """
    try:
        # If not staff, return empty
        if not user.is_staff and not user.is_superuser:
            # Check if user has reviewer permission
            has_reviewer_perm = ModulePermission.objects.filter(
                user=user,
                module='reviewer',
                can_view=True
            ).exists()
            if not has_reviewer_perm:
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
    """
    try:
        # Staff users and superusers can see all pending approvals
        if not (user.is_staff or user.is_superuser):
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
    """
    try:
        # Staff users and superusers can see approvals
        if not (user.is_staff or user.is_superuser):
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

