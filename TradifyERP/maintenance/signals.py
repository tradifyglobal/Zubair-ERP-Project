"""
Maintenance Module - GL Integration Signals
Auto-posts completed work orders to General Ledger
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from .models import WorkOrder, MaintenanceCost, MaintenanceAsset


@receiver(post_save, sender=WorkOrder)
def post_work_order_to_gl(sender, instance, created, **kwargs):
    """
    Auto-post completed work orders to GL.
    Creates maintenance expense entry when work order is completed.
    """
    # Only process if work order is completed and not already posted
    if instance.status != 'COMPLETED':
        return
    
    # Check if already posted
    if hasattr(instance, 'is_posted_to_gl') and instance.is_posted_to_gl:
        return
    
    try:
        from accounting.models import LedgerEntry, Account
        
        # Calculate total maintenance cost
        total_cost = instance.costs.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Skip if no costs
        if total_cost <= 0:
            return
        
        # Get maintenance expense account
        try:
            expense_account = Account.objects.get(
                entity=instance.entity,
                account_type='EXPENSE',
                name__icontains='Maintenance'
            )
        except Account.DoesNotExist:
            # Try to get any expense account as fallback
            expense_account = Account.objects.filter(
                entity=instance.entity,
                account_type='EXPENSE'
            ).first()
            
            if not expense_account:
                print(f"WARNING: No expense account found for maintenance WO {instance.work_order_number}")
                return
        
        # Get Accounts Payable account
        try:
            ap_account = Account.objects.get(
                entity=instance.entity,
                account_type='LIABILITY',
                name__icontains='Accounts Payable'
            )
        except Account.DoesNotExist:
            # Try to get any liability account as fallback
            ap_account = Account.objects.filter(
                entity=instance.entity,
                account_type='LIABILITY'
            ).first()
            
            if not ap_account:
                print(f"WARNING: No liability account found for maintenance WO {instance.work_order_number}")
                return
        
        # Create GL entries
        reference = f"WO-{instance.id}"
        
        # Check if entries already exist (idempotent check)
        existing = LedgerEntry.objects.filter(
            reference_number=reference,
            entity=instance.entity
        ).exists()
        
        if existing:
            return  # Already posted
        
        # DEBIT: Maintenance Expense
        LedgerEntry.objects.create(
            account=expense_account,
            entity=instance.entity,
            entry_date=instance.completion_date or instance.scheduled_date,
            entry_type='DEBIT',
            amount=total_cost,
            description=f"Maintenance - {instance.work_order_number}: {instance.description[:100]}",
            reference_number=reference,
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        # CREDIT: Accounts Payable
        LedgerEntry.objects.create(
            account=ap_account,
            entity=instance.entity,
            entry_date=instance.completion_date or instance.scheduled_date,
            entry_type='CREDIT',
            amount=total_cost,
            description=f"AP - Maintenance {instance.work_order_number}",
            reference_number=reference,
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        # Mark as posted (if field exists)
        if hasattr(instance, 'is_posted_to_gl'):
            instance.is_posted_to_gl = True
            instance.save(update_fields=['is_posted_to_gl'])
        
        print(f"✓ Posted maintenance WO {instance.work_order_number} to GL: ${total_cost}")
        
    except Exception as e:
        # Don't break work order saving if GL posting fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error posting maintenance WO {instance.work_order_number} to GL: {e}")
        print(f"ERROR posting WO to GL: {e}")


@receiver(post_save, sender=MaintenanceCost)
def update_work_order_gl_on_cost_change(sender, instance, created, **kwargs):
    """
    When maintenance costs are added/updated, recalculate GL entries if WO is completed.
    This ensures GL stays in sync with maintenance costs.
    """
    if instance.work_order.status == 'COMPLETED':
        # Trigger re-posting by temporarily setting is_posted_to_gl to False
        wo = instance.work_order
        if hasattr(wo, 'is_posted_to_gl'):
            wo.is_posted_to_gl = False
            wo.save()


@receiver(post_save, sender=MaintenanceAsset)
def post_asset_purchase_to_gl(sender, instance, created, **kwargs):
    """
    Auto-post asset purchase to GL when a new asset is created with a purchase_account.
    Creates GL entries:
      DEBIT: Asset account
      CREDIT: Purchase account (e.g., Capital Investment)
    """
    # Only process on creation AND if a purchase account is specified
    if not created or not instance.purchase_account or not instance.entity:
        return
    
    try:
        from accounting.models import LedgerEntry, Account
        
        # Get or create the Fixed Assets account
        try:
            asset_account = Account.objects.get(
                entity=instance.entity,
                account_type='ASSET',
                name__icontains='Fixed Assets'
            )
        except Account.DoesNotExist:
            # Try to get any asset account
            asset_account = Account.objects.filter(
                entity=instance.entity,
                account_type='ASSET'
            ).order_by('account_number').first()
            
            if not asset_account:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"No asset account found for equipment {instance.asset_code}")
                return
        
        # Reference for GL entries
        reference = f"ASSET-{instance.id}"
        
        # Check if entries already exist (idempotent check)
        existing = LedgerEntry.objects.filter(
            reference_number=reference,
            entity=instance.entity
        ).exists()
        
        if existing:
            return  # Already posted
        
        # DEBIT: Fixed Assets Account
        LedgerEntry.objects.create(
            account=asset_account,
            entity=instance.entity,
            entry_date=instance.purchase_date,
            entry_type='DEBIT',
            amount=instance.acquisition_cost,
            description=f"Asset Purchase - {instance.asset_code} ({instance.asset_name})",
            reference_number=reference,
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        # CREDIT: Purchase Account (e.g., Capital Investment)
        LedgerEntry.objects.create(
            account=instance.purchase_account,
            entity=instance.entity,
            entry_date=instance.purchase_date,
            entry_type='CREDIT',
            amount=instance.acquisition_cost,
            description=f"Asset Purchase - {instance.asset_code} ({instance.asset_name})",
            reference_number=reference,
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        print(f"✓ Posted asset purchase {instance.asset_code} to GL: {instance.acquisition_cost}")
        
    except Exception as e:
        # Don't break asset saving if GL posting fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error posting asset {instance.asset_code} purchase to GL: {e}")
        print(f"ERROR posting asset to GL: {e}")
