"""
Signal handlers for Cash/Bank Receipt workflow
Updates ShareholderInvestmentRegister when receipts are authorized

Place this in: TradifyERP/accounting/signals.py (add to existing signals)
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal


@receiver(post_save, sender='accounting.CashReceiptLine')
def update_investment_register_on_cash_receipt_authorization(sender, instance, **kwargs):
    """
    When a CashReceiptLine is authorized and posted, create/update the
    ShareholderInvestmentRegister (sub-ledger) entry.
    
    Triggered when:
    - workflow_status changes to 'AUTHORIZED'
    - status changes to 'POSTED'
    - GL entries have been created
    """
    
    # Only process if status is AUTHORIZED
    if instance.workflow_status != 'AUTHORIZED':
        return
    
    from accounting.models import ShareholderInvestmentRegister, Stakeholder
    
    try:
        # Get stakeholder
        stakeholder = instance.stakeholder
        if not stakeholder:
            return
        
        # Check if investment register entry already exists for this receipt
        existing = ShareholderInvestmentRegister.objects.filter(
            source_cash_receipt=instance
        ).first()
        
        if existing:
            # Update if exists
            existing.status = 'COMPLETED'
            existing.gl_reference = f'CASH-RECEIPT-{instance.id}'
            existing.save()
        else:
            # Create new investment register entry
            with transaction.atomic():
                register_entry = ShareholderInvestmentRegister.objects.create(
                    entity=instance.entity,
                    stakeholder=stakeholder,
                    investment_date=instance.date,
                    investment_type='CAPITAL',  # Default for capital contributions
                    amount_company_currency=instance.debit_amount,
                    original_amount=instance.debit_amount,
                    currency=instance.currency,
                    exchange_rate=instance.exchange_rate or Decimal('1.0'),
                    source_cash_receipt=instance,
                    gl_reference=f'CASH-RECEIPT-{instance.id}',
                    status='COMPLETED',
                    created_by=None,  # Can be enhanced to track who authorized
                    notes=f"Auto-created from {instance.description}"
                )
                
                # Update shareholder summary cache
                from accounting.models import ShareholderInvestmentSummary
                ShareholderInvestmentSummary.refresh_for_entity(instance.entity)
                
    except Exception as e:
        print(f"Error updating investment register for CashReceiptLine {instance.id}: {str(e)}")
        # Don't fail the whole transaction, just log the error
        pass


@receiver(post_save, sender='accounting.BankReceiptLine')
def update_investment_register_on_bank_receipt_authorization(sender, instance, **kwargs):
    """
    When a BankReceiptLine is authorized and posted, create/update the
    ShareholderInvestmentRegister (sub-ledger) entry.
    """
    
    # Only process if status is AUTHORIZED
    if instance.workflow_status != 'AUTHORIZED':
        return
    
    from accounting.models import ShareholderInvestmentRegister, Stakeholder
    
    try:
        # Get stakeholder
        stakeholder = instance.stakeholder
        if not stakeholder:
            return
        
        # Check if investment register entry already exists for this receipt
        existing = ShareholderInvestmentRegister.objects.filter(
            source_bank_receipt=instance
        ).first()
        
        if existing:
            # Update if exists
            existing.status = 'COMPLETED'
            existing.gl_reference = f'BANK-RECEIPT-{instance.id}'
            existing.save()
        else:
            # Create new investment register entry
            with transaction.atomic():
                register_entry = ShareholderInvestmentRegister.objects.create(
                    entity=instance.entity,
                    stakeholder=stakeholder,
                    investment_date=instance.date,
                    investment_type='CAPITAL',  # Default for capital contributions
                    amount_company_currency=instance.debit_amount,
                    original_amount=instance.debit_amount,
                    currency=instance.currency,
                    exchange_rate=instance.exchange_rate or Decimal('1.0'),
                    source_bank_receipt=instance,
                    gl_reference=f'BANK-RECEIPT-{instance.id}',
                    status='COMPLETED',
                    created_by=None,
                    notes=f"Auto-created from {instance.description}"
                )
                
                # Update shareholder summary cache
                from accounting.models import ShareholderInvestmentSummary
                ShareholderInvestmentSummary.refresh_for_entity(instance.entity)
                
    except Exception as e:
        print(f"Error updating investment register for BankReceiptLine {instance.id}: {str(e)}")
        pass


@receiver(post_save, sender='accounting.CapitalContribution')
def update_investment_register_from_capital_contribution(sender, instance, created, **kwargs):
    """
    Alternative: If CapitalContribution is created directly,
    also create an investment register entry.
    
    This ensures consistency whether the contribution comes from
    CashReceiptLine, BankReceiptLine, or manual CapitalContribution entry.
    """
    
    if not created or instance.status != 'COMPLETED':
        return
    
    from accounting.models import ShareholderInvestmentRegister
    
    try:
        # Check if already exists
        existing = ShareholderInvestmentRegister.objects.filter(
            entity=instance.entity,
            stakeholder=instance.stakeholder,
            contribution_date=instance.contribution_date
        ).first()
        
        if not existing and instance.stakeholder:
            ShareholderInvestmentRegister.objects.create(
                entity=instance.entity,
                stakeholder=instance.stakeholder,
                investment_date=instance.contribution_date,
                investment_type='CAPITAL',
                amount_company_currency=instance.amount_company_currency,
                original_amount=instance.amount,
                currency=instance.currency,
                exchange_rate=instance.exchange_rate or Decimal('1.0'),
                status='COMPLETED',
                notes=f"From CapitalContribution ID: {instance.id}"
            )
            
    except Exception as e:
        print(f"Error creating investment register from CapitalContribution: {str(e)}")
        pass
