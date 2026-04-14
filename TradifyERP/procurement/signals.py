"""
Django Signals for Procure-to-Pay GL Integration

Auto-posts GL entries when:
- GRN status changes to ACCEPTED
- VendorBill status changes to APPROVED/MATCHED
- VendorPayment status changes to PAID
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from procurement.models import GoodsReceipt
from ap.models import VendorBill, VendorPayment
from procurement.gl_posting import P2PGLPosting
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=GoodsReceipt)
def post_gl_on_grn_accepted(sender, instance, created, update_fields=None, **kwargs):
    """
    Post GL entry when GRN is ACCEPTED
    
    GL Entry:
    DR: Raw Material Inventory
    CR: GR/IR Clearing Account
    """
    # Only process if status changed to ACCEPTED and GL not already posted
    if hasattr(instance, '_status_changed') and instance.status == 'ACCEPTED' and not instance.gl_entry:
        gl_entry = P2PGLPosting.post_goods_receipt(instance)
        if gl_entry:
            instance.gl_entry = gl_entry
            instance.save(update_fields=['gl_entry'])
            logger.info(f"GL Entry auto-posted for GRN {instance.receipt_number}")


@receiver(pre_save, sender=GoodsReceipt)
def track_grn_status_change(sender, instance, **kwargs):
    """Track if GRN status is changing to ACCEPTED"""
    if instance.pk:
        try:
            old_instance = GoodsReceipt.objects.get(pk=instance.pk)
            if old_instance.status != instance.status and instance.status == 'ACCEPTED':
                instance._status_changed = True
        except GoodsReceipt.DoesNotExist:
            pass


@receiver(post_save, sender=VendorBill)
def post_gl_on_invoice_approved(sender, instance, created, update_fields=None, **kwargs):
    """
    Post GL entry when VendorBill is APPROVED (after 3-way match)
    
    GL Entry:
    DR: GR/IR Clearing Account
    CR: Accounts Payable
    """
    if hasattr(instance, '_status_changed') and instance.status in ['APPROVED', 'MATCHED'] and not instance.gl_entry:
        gl_entry = P2PGLPosting.post_vendor_invoice(instance)
        if gl_entry:
            instance.gl_entry = gl_entry
            instance.save(update_fields=['gl_entry'])
            logger.info(f"GL Entry auto-posted for Invoice {instance.bill_number}")


@receiver(pre_save, sender=VendorBill)
def track_invoice_status_change(sender, instance, **kwargs):
    """Track if Invoice status is changing to APPROVED/MATCHED"""
    if instance.pk:
        try:
            old_instance = VendorBill.objects.get(pk=instance.pk)
            if old_instance.status != instance.status and instance.status in ['APPROVED', 'MATCHED']:
                instance._status_changed = True
        except VendorBill.DoesNotExist:
            pass


@receiver(post_save, sender=VendorPayment)
def post_gl_on_payment_made(sender, instance, created, update_fields=None, **kwargs):
    """
    Post GL entry when VendorPayment is PAID
    
    GL Entry:
    DR: Accounts Payable
    CR: Bank Account
    """
    if hasattr(instance, '_status_changed') and instance.status == 'PAID' and not instance.gl_entry:
        gl_entry = P2PGLPosting.post_vendor_payment(instance)
        if gl_entry:
            instance.gl_entry = gl_entry
            instance.save(update_fields=['gl_entry'])
            logger.info(f"GL Entry auto-posted for Payment {instance.payment_number}")


@receiver(pre_save, sender=VendorPayment)
def track_payment_status_change(sender, instance, **kwargs):
    """Track if Payment status is changing to PAID"""
    if instance.pk:
        try:
            old_instance = VendorPayment.objects.get(pk=instance.pk)
            if old_instance.status != instance.status and instance.status == 'PAID':
                instance._status_changed = True
        except VendorPayment.DoesNotExist:
            pass


def ready():
    """Called when app is ready - signals are registered here in apps.py"""
    pass
