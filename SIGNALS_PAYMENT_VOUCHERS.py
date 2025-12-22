"""
PAYMENT SIGNAL HANDLERS
Automatic GL posting when cash/bank payment vouchers are authorized
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import datetime

from accounting.models import (
    CashPaymentVoucher, CashPaymentLine,
    BankPaymentVoucher, BankPaymentLine,
    JournalEntry, GLEntry, GLAccount, CashAccount, BankAccount
)


@receiver(post_save, sender=CashPaymentVoucher)
@transaction.atomic
def post_cash_payment_gl_entries(sender, instance, created, update_fields, **kwargs):
    """
    Signal handler: When a CashPaymentVoucher is authorized,
    automatically create GL entries and update cash account
    
    GL Entry Pattern:
    Dr. Expense Account (600, 605, etc.)
    Cr. Cash Account (100)
    """
    
    # Only process when status changes to AUTHORIZED
    if instance.status != 'AUTHORIZED' or not instance.approver:
        return
    
    # Don't re-process if already has GL entry
    if instance.journal_entry_id:
        return
    
    try:
        # Get or create GL accounts
        cash_account = GLAccount.objects.get(code='100-CASH')
        
        # Create Journal Entry header
        journal_entry = JournalEntry.objects.create(
            entity=instance.entity,
            journal_date=instance.voucher_date,
            reference_type='CASH_PAYMENT',
            reference_number=instance.voucher_number,
            description=f'Cash Payment Voucher {instance.voucher_number} - {instance.payee_name}',
            posted_by=instance.approver,
            posted_date=timezone.now(),
            status='POSTED'
        )
        
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        # Create GL entries for each line item (debits)
        for line in instance.lines.all():
            gl_entry = GLEntry.objects.create(
                journal_entry=journal_entry,
                account=line.expense_account,
                debit_amount=line.amount,
                credit_amount=Decimal('0.00'),
                description=line.description,
                reference=instance.voucher_number
            )
            
            total_debit += line.amount
            
            # Link GL entry to payment line
            line.gl_entry = gl_entry
            line.save()
            
            # Update GL account balance
            line.expense_account.balance += line.amount
            line.expense_account.save()
        
        # Create GL entry for cash account (credit)
        cash_gl_entry = GLEntry.objects.create(
            journal_entry=journal_entry,
            account=cash_account,
            debit_amount=Decimal('0.00'),
            credit_amount=instance.total_amount,
            description=f'Cash Payment to {instance.payee_name}',
            reference=instance.voucher_number
        )
        
        total_credit = instance.total_amount
        
        # Update cash account balance (reduce)
        cash_account.balance -= instance.total_amount
        cash_account.save()
        
        # Validate GL entry (Dr = Cr)
        if total_debit != total_credit:
            raise ValueError(f"GL Entry unbalanced: Dr={total_debit}, Cr={total_credit}")
        
        # Update voucher with GL entry reference
        instance.journal_entry = journal_entry
        instance.gl_posting_date = timezone.now()
        instance.status = 'GL_POSTED'
        instance.save(update_fields=['journal_entry', 'gl_posting_date', 'status'])
        
        # Update cash account summary
        update_cash_account_summary(instance.entity, cash_account)
        
        print(f"✅ GL entries posted for {instance.voucher_number}")
        
    except Exception as e:
        print(f"❌ Error posting GL entries for {instance.voucher_number}: {str(e)}")
        raise


@receiver(post_save, sender=BankPaymentVoucher)
@transaction.atomic
def post_bank_payment_gl_entries(sender, instance, created, update_fields, **kwargs):
    """
    Signal handler: When a BankPaymentVoucher is authorized,
    automatically create GL entries and update bank account
    
    GL Entry Pattern:
    Dr. Payable Account / Expense Account (201, 600, etc.)
    Cr. Bank Account (110)
    """
    
    # Only process when status changes to AUTHORIZED
    if instance.status != 'AUTHORIZED' or not instance.approver:
        return
    
    # Don't re-process if already has GL entry
    if instance.journal_entry_id:
        return
    
    try:
        # Get bank account GL
        bank_gl_account = instance.bank_account.gl_account
        
        # Create Journal Entry header
        journal_entry = JournalEntry.objects.create(
            entity=instance.entity,
            journal_date=instance.voucher_date,
            reference_type='BANK_PAYMENT',
            reference_number=instance.voucher_number,
            description=f'Bank Payment Voucher {instance.voucher_number} - {instance.payee_name}',
            posted_by=instance.approver,
            posted_date=timezone.now(),
            status='POSTED'
        )
        
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        # Create GL entries for each line item (debits)
        for line in instance.lines.all():
            # Use payable account if available, otherwise expense account
            account = line.payable_account or line.expense_account
            
            gl_entry = GLEntry.objects.create(
                journal_entry=journal_entry,
                account=account,
                debit_amount=line.amount,
                credit_amount=Decimal('0.00'),
                description=line.description,
                reference=instance.voucher_number
            )
            
            total_debit += line.amount
            
            # Link GL entry to payment line
            line.gl_entry = gl_entry
            line.save()
            
            # Update GL account balance (increase liability/expense)
            account.balance += line.amount
            account.save()
        
        # Create GL entry for bank account (credit)
        bank_gl_entry = GLEntry.objects.create(
            journal_entry=journal_entry,
            account=bank_gl_account,
            debit_amount=Decimal('0.00'),
            credit_amount=instance.total_amount,
            description=f'Bank Payment to {instance.payee_name}',
            reference=instance.voucher_number
        )
        
        total_credit = instance.total_amount
        
        # Update bank account balance (reduce)
        bank_gl_account.balance -= instance.total_amount
        bank_gl_account.save()
        
        # Update bank account status
        instance.bank_account.available_balance -= instance.total_amount
        instance.bank_account.save()
        
        # Validate GL entry (Dr = Cr)
        if total_debit != total_credit:
            raise ValueError(f"GL Entry unbalanced: Dr={total_debit}, Cr={total_credit}")
        
        # Update voucher with GL entry reference
        instance.journal_entry = journal_entry
        instance.gl_posting_date = timezone.now()
        instance.status = 'GL_POSTED'
        instance.save(update_fields=['journal_entry', 'gl_posting_date', 'status'])
        
        # Update bank account summary
        update_bank_account_summary(instance.entity, instance.bank_account)
        
        print(f"✅ GL entries posted for {instance.voucher_number}")
        
    except Exception as e:
        print(f"❌ Error posting GL entries for {instance.voucher_number}: {str(e)}")
        raise


def update_cash_account_summary(entity, cash_account):
    """
    Update cash account summary statistics
    Called after GL posting to recalculate balances
    """
    try:
        # This would typically update a CashAccountSummary model
        # For now, just ensure account balance is correct
        pass
    except Exception as e:
        print(f"❌ Error updating cash summary: {str(e)}")


def update_bank_account_summary(entity, bank_account):
    """
    Update bank account summary statistics
    Called after GL posting to recalculate balances
    """
    try:
        # Update available balance
        # Update pending transactions
        # Update reconciliation status
        pass
    except Exception as e:
        print(f"❌ Error updating bank summary: {str(e)}")


# ============================================================================
# SIGNAL REGISTRATION
# These would be called in accounting/apps.py ready() method
# ============================================================================

def register_payment_signals():
    """
    Register all payment signal handlers
    Call this in accounting/apps.py AccountingConfig.ready()
    """
    # Signals are auto-registered via @receiver decorators
    # This function is for documentation and can be called explicitly
    pass
