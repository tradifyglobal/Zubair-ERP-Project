"""
Manufacturing Module Signals
Handles automatic GL posting when manufacturing transactions occur.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import ProductionOrder, QualityInspection


@receiver(post_save, sender=ProductionOrder)
def production_order_post_save(sender, instance, created, **kwargs):
    """
    Handle GL posting when production order status changes.
    Posts manufacturing costs to GL.
    """
    try:
        from accounting.models import JournalEntry, JournalEntryLine, Account
        
        # Only post GL entries for specific status transitions
        if instance.status == 'COMPLETE' and instance.completion_date:
            # Check if GL entry already exists for this PO
            if JournalEntry.objects.filter(
                reference=f"MFG-{instance.po_number}"
            ).exists():
                return
            
            # Get required GL accounts
            if not instance.bom or not instance.bom.product.inventory_account:
                return
            
            inventory_account = instance.bom.product.inventory_account
            wip_account = Account.objects.filter(
                entity=instance.entity,
                account_type='CURRENT_ASSET',
                name__icontains='WIP'
            ).first()
            
            if not wip_account:
                return
            
            # Create GL entry for completed production
            je = JournalEntry.objects.create(
                entity=instance.entity,
                date=timezone.now().date(),
                reference=f"MFG-{instance.po_number}",
                description=f"Manufacturing Cost for {instance.product.name}",
                status='POSTED',
                created_by=instance.created_by or None
            )
            
            # Debit inventory account (finished goods)
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=inventory_account,
                debit=instance.total_actual_cost or instance.total_estimated_cost,
                credit=Decimal('0.00')
            )
            
            # Credit WIP account
            JournalEntryLine.objects.create(
                journal_entry=je,
                account=wip_account,
                debit=Decimal('0.00'),
                credit=instance.total_actual_cost or instance.total_estimated_cost
            )
            
    except ImportError:
        # Accounting module not available, skip GL posting
        pass
    except Exception as e:
        # Log error but don't break production order saving
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error posting GL entry for PO {instance.po_number}: {str(e)}")


@receiver(post_save, sender=QualityInspection)
def quality_inspection_post_save(sender, instance, created, **kwargs):
    """
    Handle quality inspection status changes.
    Could trigger rework orders or scrap tracking.
    """
    if created and instance.status == 'FAIL':
        # Track failed inspection
        # Could create rework production order or notify supervisor
        pass
