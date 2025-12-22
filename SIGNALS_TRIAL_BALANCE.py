"""
TRIAL BALANCE SIGNAL HANDLERS
Auto-generates trial balance after GL posting
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from accounting.models import (
    JournalEntry, TrialBalance, TrialBalanceLine,
    MonthlyTrialBalance, GLAccount
)


@receiver(post_save, sender=JournalEntry)
@transaction.atomic
def auto_generate_trial_balance_on_posting(sender, instance, created, update_fields, **kwargs):
    """
    Signal handler: When a JournalEntry is posted,
    automatically generate/update trial balance for that date
    """
    
    # Only process when entry is marked as POSTED
    if instance.status != 'POSTED':
        return
    
    try:
        # Get or create trial balance for the journal entry date
        tb, created = TrialBalance.objects.get_or_create(
            entity=instance.entity,
            trial_balance_date=instance.journal_date,
            defaults={'generated_by': instance.posted_by}
        )
        
        # Regenerate trial balance
        is_balanced = tb.generate()
        
        if is_balanced:
            print(f"✅ Trial Balance auto-generated for {instance.entity.name} - {instance.journal_date}")
        else:
            print(f"⚠️ Trial Balance unbalanced for {instance.entity.name} - {instance.journal_date}")
            print(f"   Difference: {tb.balance_difference}")
        
    except Exception as e:
        print(f"❌ Error generating trial balance: {str(e)}")
        raise


def generate_trial_balance_for_date(entity, date, generated_by=None):
    """
    Utility function to generate trial balance for a specific date
    """
    tb, created = TrialBalance.objects.get_or_create(
        entity=entity,
        trial_balance_date=date,
        defaults={'generated_by': generated_by}
    )
    
    return tb.generate()


def generate_monthly_trial_balance(entity, month_end_date, approved_by=None):
    """
    Generate or update monthly trial balance
    """
    # Get trial balance for month end
    tb = TrialBalance.objects.filter(
        entity=entity,
        trial_balance_date=month_end_date
    ).first()
    
    if not tb:
        # Generate if doesn't exist
        tb_generated = generate_trial_balance_for_date(entity, month_end_date)
        tb = TrialBalance.objects.get(
            entity=entity,
            trial_balance_date=month_end_date
        )
    
    # Create or update monthly trial balance
    monthly_tb, created = MonthlyTrialBalance.objects.get_or_create(
        entity=entity,
        month_end_date=month_end_date,
        defaults={
            'trial_balance': tb,
            'total_debit': tb.total_debit,
            'total_credit': tb.total_credit,
            'is_balanced': tb.is_balanced,
        }
    )
    
    # If already exists, update the totals
    if not created:
        monthly_tb.trial_balance = tb
        monthly_tb.total_debit = tb.total_debit
        monthly_tb.total_credit = tb.total_credit
        monthly_tb.is_balanced = tb.is_balanced
        monthly_tb.save()
    
    return monthly_tb


def verify_trial_balance_integrity(entity, date):
    """
    Verify trial balance integrity - check for any discrepancies
    """
    tb = TrialBalance.objects.filter(
        entity=entity,
        trial_balance_date=date
    ).first()
    
    if not tb:
        return False, "Trial balance not found"
    
    if not tb.is_balanced:
        return False, f"Trial balance unbalanced. Difference: {tb.balance_difference}"
    
    # Verify account totals match GL entries
    for line in tb.lines.all():
        account = line.account
        
        # Recalculate balance from GL entries
        gl_entries = account.entries.all()
        calculated_balance = Decimal('0.00')
        
        for entry in gl_entries:
            if entry.debit_amount:
                calculated_balance += entry.debit_amount
            if entry.credit_amount:
                calculated_balance -= entry.credit_amount
        
        # Compare with trial balance line
        expected_debit = line.debit_amount
        expected_credit = line.credit_amount
        
        if calculated_balance > 0:
            if calculated_balance != expected_debit:
                return False, f"Account {account.code} balance mismatch. Expected debit: {calculated_balance}, Found: {expected_debit}"
        elif calculated_balance < 0:
            if abs(calculated_balance) != expected_credit:
                return False, f"Account {account.code} balance mismatch. Expected credit: {abs(calculated_balance)}, Found: {expected_credit}"
    
    return True, "Trial balance verified successfully"


def detect_trial_balance_errors(entity, date):
    """
    Detect and log any trial balance errors
    """
    tb = TrialBalance.objects.filter(
        entity=entity,
        trial_balance_date=date
    ).first()
    
    if not tb:
        return []
    
    errors = []
    
    # Check if balanced
    if not tb.is_balanced:
        errors.append({
            'type': 'UNBALANCED',
            'description': f'Debits ({tb.total_debit}) != Credits ({tb.total_credit})',
            'difference': tb.balance_difference
        })
    
    # Check for duplicate entries
    from django.db.models import Count
    duplicates = tb.lines.values('account').annotate(count=Count('account')).filter(count__gt=1)
    
    if duplicates.exists():
        for dup in duplicates:
            account = GLAccount.objects.get(id=dup['account'])
            errors.append({
                'type': 'DUPLICATE',
                'description': f'Duplicate entry for account {account.code}',
            })
    
    return errors


def generate_trial_balance_audit_report(entity, start_date, end_date):
    """
    Generate audit report of all trial balances in date range
    """
    trial_balances = TrialBalance.objects.filter(
        entity=entity,
        trial_balance_date__gte=start_date,
        trial_balance_date__lte=end_date
    ).order_by('trial_balance_date')
    
    report = {
        'entity': entity.name,
        'start_date': start_date,
        'end_date': end_date,
        'total_trial_balances': trial_balances.count(),
        'balanced': trial_balances.filter(is_balanced=True).count(),
        'unbalanced': trial_balances.filter(is_balanced=False).count(),
        'trial_balances': []
    }
    
    for tb in trial_balances:
        report['trial_balances'].append({
            'date': tb.trial_balance_date,
            'status': 'BALANCED' if tb.is_balanced else 'UNBALANCED',
            'total_debit': float(tb.total_debit),
            'total_credit': float(tb.total_credit),
            'difference': float(tb.balance_difference),
        })
    
    return report
