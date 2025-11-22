"""
Manufacturing Module Signals
Handles automatic GL posting when manufacturing transactions occur.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import ProductionOrder, QualityInspection, DistributorOrder


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


# ==================== DISTRIBUTOR PERFORMANCE SIGNALS ====================

@receiver(post_save, sender=DistributorOrder)
def update_distributor_ytd_sales(sender, instance, created, **kwargs):
    """
    When an order is created or updated, update the distributor's YTD sales.
    This keeps the ytd_sales field current with all posted orders.
    """
    try:
        from django.db.models import Sum
        
        distributor = instance.distributor
        
        # Calculate total sales for current year (only posted orders)
        current_year = timezone.now().year
        
        ytd_total = DistributorOrder.objects.filter(
            distributor=distributor,
            order_date__year=current_year,
            is_posted=True
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        
        # Update distributor's YTD sales
        distributor.ytd_sales = ytd_total
        distributor.save(update_fields=['ytd_sales', 'updated_at'])
        
        import logging
        logger = logging.getLogger(__name__)
        action = "created" if created else "updated"
        logger.info(
            f'Updated YTD sales for {distributor.distributor_name} after order {action}. '
            f'New YTD: ${ytd_total}'
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error updating distributor YTD sales: {str(e)}')


@receiver(post_delete, sender=DistributorOrder)
def recalculate_distributor_ytd_sales_on_delete(sender, instance, **kwargs):
    """
    When an order is deleted, recalculate the distributor's YTD sales.
    Ensures accuracy of YTD metrics.
    """
    try:
        from django.db.models import Sum
        
        distributor = instance.distributor
        
        # Recalculate total sales for current year
        current_year = timezone.now().year
        
        ytd_total = DistributorOrder.objects.filter(
            distributor=distributor,
            order_date__year=current_year,
            is_posted=True
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        
        # Update distributor's YTD sales
        distributor.ytd_sales = ytd_total
        distributor.save(update_fields=['ytd_sales', 'updated_at'])
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f'Recalculated YTD sales for {distributor.distributor_name} after order deletion. '
            f'New YTD: ${ytd_total}'
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error recalculating distributor YTD sales: {str(e)}')
