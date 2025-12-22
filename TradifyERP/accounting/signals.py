"""
Accounting Module Signals
Auto-create UserRole entries for new users.
Auto-delete shareholder capital accounts when shareholder is deleted.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Entity
from .role_models import UserRole, Role


@receiver(post_save, sender=User)
def create_user_role_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically assign new users to the default entity with Admin role.
    This ensures new users can see entities and employees immediately upon login.
    """
    if not created:
        return  # Only process new users
    
    # Don't create roles for superusers or staff automatically
    # They should be assigned manually
    if instance.is_superuser or instance.is_staff:
        return
    
    try:
        # Get or create the default entity (usually the first one)
        entity = Entity.objects.first()
        if not entity:
            return  # No entity exists yet
        
        # Get or create Admin role
        admin_role, _ = Role.objects.get_or_create(
            name='Admin',
            defaults={'description': 'Administrator role'}
        )
        
        # Check if user already has a role for this entity
        existing_role = UserRole.objects.filter(
            user=instance,
            entity=entity
        ).exists()
        
        if not existing_role:
            # Create UserRole for the new user
            UserRole.objects.create(
                user=instance,
                entity=entity,
                role=admin_role,
                is_active=True
            )
    except Exception as e:
        # Silently fail - don't break user creation if role assignment fails
        pass


# DISABLED: Auto-account creation to prevent duplicates
# @receiver(post_save, sender='accounting.Stakeholder')
def auto_create_capital_subaccounts_DISABLED(sender, instance, created, **kwargs):
    """
    DISABLED: When a shareholder/stakeholder is added, automatically create sub-accounts
    under all capital accounts for that entity.
    This was causing duplicate account creation.
    """
    if not created:
        return  # Only for new stakeholders
    
    from .models import Account
    
    try:
        # DISABLED: Find all capital accounts for this entity
        capital_accounts = Account.objects.filter(
            entity=instance.entity,
            account_type='EQUITY',
            is_active=True
        ).filter(name__icontains='capital')
        
        # DISABLED: Create sub-accounts for this stakeholder under each capital account
        for capital_account in capital_accounts:
            pass  # capital_account.get_shareholder_subaccount(instance)
            
    except Exception as e:
        # Silently fail - don't break stakeholder creation
        pass


def deactivate_shareholder_capital_accounts(sender, instance, **kwargs):
    """
    When a shareholder/stakeholder is deleted or made inactive, automatically
    deactivate their capital sub-accounts to preserve historical transactions.
    """
    from .models import Account
    
    try:
        # Find capital parent account for this entity
        capital_account = Account.objects.filter(
            entity=instance.entity,
            account_number='3000'
        ).first()
        
        if not capital_account:
            return
        
        # Find all child accounts under capital that belong to this stakeholder
        stakeholder_name = instance.full_name
        capital_subaccounts = Account.objects.filter(
            entity=instance.entity,
            parent_account=capital_account,
            name__startswith=stakeholder_name
        )
        
        # Deactivate the sub-accounts (preserve history)
        for account in capital_subaccounts:
            account.is_active = False
            account.save()
            
    except Exception as e:
        # Silently fail - don't break stakeholder deletion
        pass


# Manual signal connection after models are loaded
def register_signals():
    """Connect signals when apps are ready"""
    from django.db.models.signals import pre_delete, post_save
    from .models import Stakeholder
    
    # Connect deactivation on delete
    pre_delete.connect(
        deactivate_shareholder_capital_accounts, 
        sender=Stakeholder, 
        dispatch_uid='stakeholder_deactivate_on_delete'
    )
    
    # Connect deactivation on status change
    post_save.connect(
        handle_stakeholder_status_change,
        sender=Stakeholder,
        dispatch_uid='stakeholder_deactivate_on_status_change'
    )




def handle_stakeholder_status_change(sender, instance, created, **kwargs):
    """
    Handle stakeholder status changes - deactivate accounts if status changes to INACTIVE/SUSPENDED/WITHDRAWN
    """
    if created:
        return  # Only handle updates, not creation
    
    # Check if status is one of the inactive statuses
    INACTIVE_STATUSES = ['INACTIVE', 'SUSPENDED', 'WITHDRAWN']
    
    if instance.status in INACTIVE_STATUSES:
        deactivate_shareholder_capital_accounts(sender, instance)


# ==================== Capital Contribution Auto-Posting Signal ====================

@receiver(post_save, sender='accounting.CashReceiptLine')
def auto_create_capital_contribution_from_cash_receipt(sender, instance, created, **kwargs):
    """
    Auto-create a capital contribution when a CashReceiptLine (shareholder capital) is authorized.
    Links the contribution to the source transaction.
    """
    # Only process on update, not on creation
    if created:
        return
    
    # Check if this receipt was just authorized (GL posted)
    from .models import CashReceiptLine, CapitalContribution, Stakeholder
    
    try:
        # Only process if marked as capital receipt and authorized (GL posted)
        if instance.workflow_status != 'AUTHORIZED' or instance.is_capital_contribution_posted:
            return
        
        # Get stakeholder from the receipt (if linked)
        stakeholder = getattr(instance, 'stakeholder', None)
        if not stakeholder:
            return
        
        # Check if capital contribution already exists for this receipt
        existing_contribution = CapitalContribution.objects.filter(
            source_cash_receipt_id=instance.id
        ).first()
        if existing_contribution:
            # Mark as posted and return (contribution already exists)
            instance.is_capital_contribution_posted = True
            instance.save(update_fields=['is_capital_contribution_posted'])
            return
        
        # Get entity's company currency for currency_destination
        company_currency = instance.entity.company_currency
        
        # Create capital contribution record using instance fields directly
        contribution = CapitalContribution.objects.create(
            entity=instance.entity,
            stakeholder=stakeholder,
            contribution_date=instance.date,
            amount=instance.debit_amount,
            currency=instance.currency,
            currency_destination=company_currency,
            status='COMPLETED',
            payment_mode='CASH',
            reference_number=instance.reference_number,
            # NEW: Link to source transaction
            source_cash_receipt_id=instance.id,
            is_auto_posted=True,  # Prevents duplicate ledger entries in save()
            workflow_status='CONTRIBUTION',  # Use proper workflow status
            equity_account=instance.account  # Link to capital account from receipt
        )
        
        # NOTE: GL entries already created by receipt authorization
        # Do NOT call post_capital_contribution_to_ledger() to avoid duplicates
        
        # Mark that contribution was posted
        instance.is_capital_contribution_posted = True
        instance.save(update_fields=['is_capital_contribution_posted'])
        
    except Exception as e:
        # Log but don't break the receipt save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error auto-creating capital contribution from cash receipt: {str(e)}", exc_info=True)


@receiver(post_save, sender='accounting.BankReceiptLine')
def auto_create_capital_contribution_from_bank_receipt(sender, instance, created, **kwargs):
    """
    Auto-create a capital contribution when a BankReceiptLine (shareholder capital) is approved.
    Links the contribution to the source transaction.
    """
    # Only process on update, not on creation
    if created:
        return
    
    # Check if this receipt was just authorized (GL posted)
    from .models import BankReceiptLine, CapitalContribution, Stakeholder
    
    try:
        # Only process if marked as capital receipt and authorized (GL posted)
        if instance.workflow_status != 'AUTHORIZED' or instance.is_capital_contribution_posted:
            return
        
        # Get stakeholder from the receipt (if linked)
        stakeholder = getattr(instance, 'stakeholder', None)
        if not stakeholder:
            return
        
        # Check if capital contribution already exists for this receipt
        existing_contribution = CapitalContribution.objects.filter(
            source_bank_receipt_id=instance.id
        ).first()
        if existing_contribution:
            # Mark as posted and return (contribution already exists)
            instance.is_capital_contribution_posted = True
            instance.save(update_fields=['is_capital_contribution_posted'])
            return
        
        # Get entity's company currency for currency_destination
        company_currency = instance.entity.company_currency
        
        # Create capital contribution record using instance fields directly
        contribution = CapitalContribution.objects.create(
            entity=instance.entity,
            stakeholder=stakeholder,
            contribution_date=instance.date,
            amount=instance.debit_amount,
            currency=instance.currency,
            currency_destination=company_currency,
            status='COMPLETED',
            payment_mode='BANK',
            reference_number=instance.reference_number,
            # NEW: Link to source transaction
            source_bank_receipt_id=instance.id,
            is_auto_posted=True,  # Prevents duplicate ledger entries in save()
            workflow_status='CONTRIBUTION',  # Use proper workflow status
            equity_account=instance.account  # Link to capital account from receipt
        )
        
        # NOTE: GL entries already created by receipt authorization
        # Do NOT call post_capital_contribution_to_ledger() to avoid duplicates
        
        # Mark that contribution was posted
        instance.is_capital_contribution_posted = True
        instance.save(update_fields=['is_capital_contribution_posted'])
        
    except Exception as e:
        # Log but don't break the receipt save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error auto-creating capital contribution from bank receipt: {str(e)}", exc_info=True)


def post_capital_contribution_to_ledger(contribution):
    """
    Post a capital contribution to the general ledger.
    Creates GL entries for the contribution (cash debit, equity credit).
    """
    from .models import GLEntry, Account, JournalEntry
    from decimal import Decimal
    from django.utils import timezone
    
    try:
        # Get or create equity account for shareholder
        equity_account = contribution.equity_account
        cash_account = contribution.cash_account
        
        if not equity_account or not cash_account:
            # Try to find default accounts
            equity_account = Account.objects.filter(
                entity=contribution.entity,
                account_type='EQUITY',
                name__icontains='Capital'
            ).first()
            
            cash_account = Account.objects.filter(
                entity=contribution.entity,
                account_type='ASSET',
                name__icontains='Cash'
            ).first()
        
        if not equity_account or not cash_account:
            return  # Can't post without accounts
        
        # Create journal entry for the contribution
        journal_entry = JournalEntry.objects.create(
            entity=contribution.entity,
            date=contribution.contribution_date,
            description=f"Capital Contribution from {contribution.stakeholder.full_name}",
            reference_type='CAPITAL_CONTRIBUTION',
            reference_id=contribution.id,
            posted_date=timezone.now()
        )
        
        # Debit cash account
        GLEntry.objects.create(
            journal_entry=journal_entry,
            account=cash_account,
            debit_amount=contribution.amount_company_currency,
            credit_amount=Decimal('0.00'),
            description=f"Cash received - {contribution.stakeholder.full_name}"
        )
        
        # Credit equity account
        GLEntry.objects.create(
            journal_entry=journal_entry,
            account=equity_account,
            debit_amount=Decimal('0.00'),
            credit_amount=contribution.amount_company_currency,
            description=f"Capital contribution - {contribution.stakeholder.full_name}"
        )
        
        # Link ledger entry to contribution
        contribution.ledger_entry = journal_entry
        contribution.save(update_fields=['ledger_entry'])
        
    except Exception as e:
        # Log but don't break
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error posting capital contribution to ledger: {str(e)}")


@receiver(post_save, sender='accounting.CashPaymentLine')
def auto_create_capital_withdrawal_from_cash_payment(sender, instance, created, **kwargs):
    """
    Auto-create a capital contribution (withdrawal/distribution) when a CashPaymentLine is authorized.
    Only triggers if payment_purpose='CAPITAL_WITHDRAWAL' or 'PROFIT_DISTRIBUTION' and stakeholder is set.
    Links the withdrawal to the source transaction.
    """
    # Only process on update, not on creation
    if created:
        return
    
    from .models import CashPaymentLine, CapitalContribution, Stakeholder
    
    try:
        # Only process if authorized (GL posted) and not already posted
        if instance.workflow_status != 'AUTHORIZED' or instance.is_capital_contribution_posted:
            return
        
        # Check if this is a capital withdrawal or profit distribution
        if instance.payment_purpose not in ['CAPITAL_WITHDRAWAL', 'PROFIT_DISTRIBUTION']:
            return
        
        # Get stakeholder from the payment (required for capital withdrawals and profit distributions)
        stakeholder = getattr(instance, 'stakeholder', None)
        if not stakeholder:
            # Log warning - capital withdrawal/profit distribution without stakeholder
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cash Payment {instance.id} marked as {instance.payment_purpose} but no stakeholder set")
            return
        
        # Determine workflow status based on payment purpose
        if instance.payment_purpose == 'CAPITAL_WITHDRAWAL':
            workflow_status = 'WITHDRAWAL'
            reference_prefix = 'WITHDRAW'
        else:  # PROFIT_DISTRIBUTION
            workflow_status = 'PROFIT_DISTRIBUTION'
            reference_prefix = 'PROFIT'
        
        # Check if capital contribution already exists for this payment
        existing_contribution = CapitalContribution.objects.filter(
            reference_number=f'{reference_prefix}-CP-{instance.id}'
        ).first()
        if existing_contribution:
            # Mark as posted and return
            instance.is_capital_contribution_posted = True
            instance.save(update_fields=['is_capital_contribution_posted'])
            return
        
        # Get entity's company currency
        company_currency = instance.entity.company_currency
        
        # Determine the correct account based on payment purpose
        if instance.payment_purpose == 'CAPITAL_WITHDRAWAL':
            # For capital withdrawals, use capital account (3100-XX)
            equity_account = instance.credit_account
        else:  # PROFIT_DISTRIBUTION
            # For profit distributions, use dividend account (4100-XX)
            from .stakeholder_account_helpers import get_or_create_stakeholder_dividend_account
            equity_account = get_or_create_stakeholder_dividend_account(stakeholder)
            
            # If dividend account creation failed, fall back to credit_account
            if not equity_account:
                equity_account = instance.credit_account
        
        # Create capital contribution (withdrawal/distribution) record
        contribution = CapitalContribution.objects.create(
            entity=instance.entity,
            stakeholder=stakeholder,
            contribution_date=instance.date,
            amount=instance.credit_amount,
            currency=instance.currency,
            currency_destination=company_currency,
            status='COMPLETED',
            payment_mode='CASH',
            reference_number=f'{reference_prefix}-CP-{instance.id}',
            is_auto_posted=True,  # Prevents duplicate ledger entries in save()
            workflow_status=workflow_status,  # WITHDRAWAL or PROFIT_DISTRIBUTION
            equity_account=equity_account,  # Link to drawings account (3200-XX) or capital account (3100-XX)
            cash_account=instance.account  # Cash account being debited
        )
        
        # NOTE: GL entries already created by payment authorization
        # Do NOT create additional ledger entries to avoid duplicates
        
        # Mark that contribution was posted
        instance.is_capital_contribution_posted = True
        instance.save(update_fields=['is_capital_contribution_posted'])
        
    except Exception as e:
        # Log but don't break the payment save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error auto-creating withdrawal/distribution from cash payment: {str(e)}", exc_info=True)


@receiver(post_save, sender='accounting.BankPaymentLine')
def auto_create_capital_withdrawal_from_bank_payment(sender, instance, created, **kwargs):
    """
    Auto-create a capital contribution (withdrawal/distribution) when a BankPaymentLine is authorized.
    Only triggers if payment_purpose='CAPITAL_WITHDRAWAL' or 'PROFIT_DISTRIBUTION' and stakeholder is set.
    Links the withdrawal to the source transaction.
    """
    # Only process on update, not on creation
    if created:
        return
    
    from .models import BankPaymentLine, CapitalContribution, Stakeholder, BankProfile
    
    try:
        # Only process if authorized (GL posted) and not already posted
        if instance.workflow_status != 'AUTHORIZED' or instance.is_capital_contribution_posted:
            return
        
        # Check if this is a capital withdrawal or profit distribution
        if instance.payment_purpose not in ['CAPITAL_WITHDRAWAL', 'PROFIT_DISTRIBUTION']:
            return
        
        # Get stakeholder from the payment (required for capital withdrawals and profit distributions)
        stakeholder = getattr(instance, 'stakeholder', None)
        if not stakeholder:
            # Log warning - capital withdrawal/profit distribution without stakeholder
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Bank Payment {instance.id} marked as {instance.payment_purpose} but no stakeholder set")
            return
        
        # Determine workflow status based on payment purpose
        if instance.payment_purpose == 'CAPITAL_WITHDRAWAL':
            workflow_status = 'WITHDRAWAL'
            reference_prefix = 'WITHDRAW'
        else:  # PROFIT_DISTRIBUTION
            workflow_status = 'PROFIT_DISTRIBUTION'
            reference_prefix = 'PROFIT'
        
        # Check if capital contribution already exists for this payment
        existing_contribution = CapitalContribution.objects.filter(
            reference_number=f'{reference_prefix}-BP-{instance.id}'
        ).first()
        if existing_contribution:
            # Mark as posted and return
            instance.is_capital_contribution_posted = True
            instance.save(update_fields=['is_capital_contribution_posted'])
            return
        
        # Get entity's company currency
        company_currency = instance.entity.company_currency
        
        # Determine the correct account based on payment purpose
        if instance.payment_purpose == 'CAPITAL_WITHDRAWAL':
            # For capital withdrawals, use capital account (3100-XX)
            equity_account = instance.credit_account
        else:  # PROFIT_DISTRIBUTION
            # For profit distributions, use dividend account (4100-XX)
            from .stakeholder_account_helpers import get_or_create_stakeholder_dividend_account
            equity_account = get_or_create_stakeholder_dividend_account(stakeholder)
            
            # If dividend account creation failed, fall back to credit_account
            if not equity_account:
                equity_account = instance.credit_account
        
        # Try to get bank profile for the entity
        bank_profile = BankProfile.objects.filter(entity=instance.entity).first()
        
        # Create capital contribution (withdrawal/distribution) record
        contribution = CapitalContribution.objects.create(
            entity=instance.entity,
            stakeholder=stakeholder,
            contribution_date=instance.date,
            amount=instance.credit_amount,
            currency=instance.currency,
            currency_destination=company_currency,
            status='COMPLETED',
            payment_mode='BANK',
            reference_number=f'{reference_prefix}-BP-{instance.id}',
            is_auto_posted=True,  # Prevents duplicate ledger entries in save()
            workflow_status=workflow_status,  # WITHDRAWAL or PROFIT_DISTRIBUTION
            equity_account=equity_account,  # Link to drawings account (3200-XX) or capital account (3100-XX)
            cash_account=instance.account,  # Bank account being debited
            payment_bank_account=bank_profile  # Link to bank profile if available
        )
        
        # NOTE: GL entries already created by payment authorization
        # Do NOT create additional ledger entries to avoid duplicates
        
        # Mark that contribution was posted
        instance.is_capital_contribution_posted = True
        instance.save(update_fields=['is_capital_contribution_posted'])
        
    except Exception as e:
        # Log but don't break the payment save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error auto-creating withdrawal/distribution from bank payment: {str(e)}", exc_info=True)
