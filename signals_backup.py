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
            is_auto_posted=True,
            workflow_status='APPROVED'  # Auto-approved from receipt
        )
        
        # Post GL entries
        post_capital_contribution_to_ledger(contribution)
        
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
            payment_mode='BANK_TRANSFER',
            reference_number=instance.reference_number,
            # NEW: Link to source transaction
            source_bank_receipt_id=instance.id,
            is_auto_posted=True,
            workflow_status='APPROVED'  # Auto-approved from receipt
        )
        
        # Post GL entries
        post_capital_contribution_to_ledger(contribution)
        
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

 
 @ r e c e i v e r ( p o s t _ s a v e ,   s e n d e r = ' a c c o u n t i n g . C a s h R e c e i p t L i n e ' )  
 @ r e c e i v e r ( p o s t _ s a v e ,   s e n d e r = ' a c c o u n t i n g . C a s h P a y m e n t L i n e ' )  
 d e f   a u t o _ g e n e r a t e _ b a l a n c e _ s h e e t ( s e n d e r ,   i n s t a n c e ,   c r e a t e d ,   * * k w a r g s ) :  
         " " "  
         A u t o m a t i c a l l y   g e n e r a t e / u p d a t e   B a l a n c e   S h e e t   w h e n   c a s h   r e c e i p t s   o r   p a y m e n t s   a r e   a u t h o r i z e d .  
         T h i s   k e e p s   B a l a n c e   S h e e t s   u p - t o - d a t e   w i t h o u t   m a n u a l   r e g e n e r a t i o n .  
         " " "  
         f r o m   a c c o u n t i n g . m o d e l s   i m p o r t   B a l a n c e S h e e t ,   L e d g e r E n t r y  
         f r o m   d a t e t i m e   i m p o r t   d a t e  
         f r o m   d e c i m a l   i m p o r t   D e c i m a l  
          
         #   O n l y   p r o c e e d   i f   s t a t u s   i s   A U T H O R I Z E D  
         i f   i n s t a n c e . w o r k f l o w _ s t a t u s   ! =   ' A U T H O R I Z E D ' :  
                 r e t u r n  
 