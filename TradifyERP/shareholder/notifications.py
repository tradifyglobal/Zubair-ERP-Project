"""
Notification system for capital contribution reviews and approvals
"""
from django.db.models import Q
from accounting.models import CapitalContribution


def get_pending_reviews_for_user(user, entity=None):
    """
    Get pending capital contributions awaiting review by the user
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        QuerySet of CapitalContribution objects awaiting review
    """
    # Check if user has reviewer permission
    if not user.has_perm('accounting.review_capitalcontribution'):
        return CapitalContribution.objects.none()
    
    # Get contributions awaiting first review (assigned to this user as reviewer)
    query = Q(
        workflow_status__in=['SUBMITTED', 'FIRST_REVIEW_COMPLETED'],
        reviewed_by__isnull=True
    ) | Q(
        workflow_status='FIRST_REVIEW_COMPLETED',
        reviewed_by_2__isnull=True
    )
    
    pending = CapitalContribution.objects.filter(query).distinct()
    
    if entity:
        pending = pending.filter(entity=entity)
    
    return pending


def get_pending_approvals_for_user(user, entity=None):
    """
    Get pending capital contributions awaiting approval by the user
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        QuerySet of CapitalContribution objects awaiting approval
    """
    # Check if user has approver permission
    if not user.has_perm('accounting.approve_capitalcontribution'):
        return CapitalContribution.objects.none()
    
    # Get contributions awaiting approval (both reviews completed)
    pending = CapitalContribution.objects.filter(
        workflow_status='REVIEWED',
        approved_by__isnull=True
    )
    
    if entity:
        pending = pending.filter(entity=entity)
    
    return pending


def get_all_pending_for_user(user, entity=None):
    """
    Get all pending contributions (reviews + approvals) for the user
    
    Args:
        user: The user object
        entity: Optional entity to filter by
        
    Returns:
        Dictionary with pending reviews and approvals counts and QuerySets
    """
    reviews = get_pending_reviews_for_user(user, entity)
    approvals = get_pending_approvals_for_user(user, entity)
    
    return {
        'pending_reviews': reviews,
        'pending_reviews_count': reviews.count(),
        'pending_approvals': approvals,
        'pending_approvals_count': approvals.count(),
        'total_pending': reviews.count() + approvals.count(),
    }
