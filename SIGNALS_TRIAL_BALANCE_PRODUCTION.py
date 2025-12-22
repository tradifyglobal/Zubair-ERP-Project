"""
TRIAL BALANCE SIGNALS
Auto-generate trial balance after GL posting
Adapted for production TrialBalance model
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

from accounting.models import JournalEntry, TrialBalance, GLAccount, LedgerEntry
from django.db.models import Sum


@receiver(post_save, sender=JournalEntry)
def auto_generate_trial_balance_on_posting(sender, instance, created, **kwargs):
    """
    Auto-generate trial balance when journal entry is posted
    Fires when JournalEntry.status changes to 'POSTED'
    """
    
    # Only process when status is POSTED
    if instance.status != 'POSTED':
        return
    
    try:
        # Get posting date
        as_of_date = instance.posting_date.date() if hasattr(instance.posting_date, 'date') else instance.posting_date
        
        # Calculate total debits and credits from this posting
        ledger_entries = LedgerEntry.objects.filter(journal_entry=instance)
        debit_sum = ledger_entries.filter(entry_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        credit_sum = ledger_entries.filter(entry_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Get cumulative totals up to this date
        all_ledger_entries = LedgerEntry.objects.filter(
            journal_entry__entity=instance.entity,
            journal_entry__posting_date__lte=as_of_date,
            journal_entry__status='POSTED'
        )
        
        total_debit = all_ledger_entries.filter(entry_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_credit = all_ledger_entries.filter(entry_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Verify balance
        is_balanced = (total_debit == total_credit)
        
        # Create or update trial balance
        tb, created = TrialBalance.objects.get_or_create(
            entity=instance.entity,
            as_of_date=as_of_date,
            defaults={
                'total_debits': total_debit,
                'total_credits': total_credit,
                'is_balanced': is_balanced
            }
        )
        
        if not created:
            # Update if already exists
            tb.total_debits = total_debit
            tb.total_credits = total_credit
            tb.is_balanced = is_balanced
            tb.save(update_fields=['total_debits', 'total_credits', 'is_balanced'])
            
    except Exception as e:
        # Log error but don't fail posting
        print(f"Error generating trial balance: {str(e)}")


def ready():
    """
    Initialize signals when app is ready
    """
    pass
