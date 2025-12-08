"""
Notification system for expense reviews and approvals
"""
from django.db.models import Q
from accounting.module_permissions import ModulePermission
from .models import EmployeeExpenseReport


def get_pending_reviews_for_user(user, entity=None):
    """
    Get pending expense reports awaiting review by the user
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        QuerySet of EmployeeExpenseReport objects awaiting review by this user
    """
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


def get_pending_approvals_for_user(user, entity=None):
    """
    Get pending expense reports awaiting approval by this specific user
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        QuerySet of EmployeeExpenseReport objects awaiting approval by this user
    """
    # Check if user is a staff member (fallback if ModulePermission not set)
    if not user.is_staff:
        return EmployeeExpenseReport.objects.none()
    
    # Check if user has expense approval permission in ModulePermission
    has_approval_perm = ModulePermission.objects.filter(
        user=user,
        module='expenses',
        can_approve=True
    ).exists()
    
    if not has_approval_perm:
        # If no explicit permission, check if user is_staff (legacy fallback)
        # This allows staff users to see approvals even without ModulePermission
        if not user.is_staff:
            return EmployeeExpenseReport.objects.none()
    
    # Get expense reports assigned to this user for approval
    # Includes both awaiting assignment and awaiting final approval
    pending = EmployeeExpenseReport.objects.filter(
        status='PENDING_APPROVAL'
    ).distinct()
    
    if entity:
        pending = pending.filter(entity=entity)
    
    return pending


def get_pending_final_approvals_for_user(user, entity=None):
    """
    Get pending expense reports awaiting FINAL approval (already assigned to user)
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        QuerySet of EmployeeExpenseReport objects assigned to this user for final approval
    """
    # Check if user is a staff member (fallback if ModulePermission not set)
    if not user.is_staff:
        return EmployeeExpenseReport.objects.none()
    
    # Check if user has expense approval permission in ModulePermission
    has_approval_perm = ModulePermission.objects.filter(
        user=user,
        module='expenses',
        can_approve=True
    ).exists()
    
    if not has_approval_perm:
        # If no explicit permission, check if user is_staff (legacy fallback)
        if not user.is_staff:
            return EmployeeExpenseReport.objects.none()
    
    # Get reports where user is assigned as finance_approver and not yet approved
    from .models import ExpenseApprovalWorkflow
    
    pending = EmployeeExpenseReport.objects.filter(
        status='PENDING_APPROVAL',
        approval_workflow__finance_approver=user,
        approval_workflow__finance_approved=False
    ).distinct()
    
    if entity:
        pending = pending.filter(entity=entity)
    
    return pending


def get_all_pending_for_user(user, entity=None):
    """
    Get all pending expense reports (reviews + approvals) for the user
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        Dictionary with pending reviews and approvals counts and QuerySets
    """
    reviews = get_pending_reviews_for_user(user, entity)
    approvals = get_pending_approvals_for_user(user, entity)
    final_approvals = get_pending_final_approvals_for_user(user, entity)
    
    return {
        'pending_reviews': reviews,
        'pending_reviews_count': reviews.count(),
        'pending_approvals': approvals,
        'pending_approvals_count': approvals.count(),
        'pending_final_approvals': final_approvals,
        'pending_final_approvals_count': final_approvals.count(),
        'total_pending': reviews.count() + approvals.count() + final_approvals.count(),
    }
