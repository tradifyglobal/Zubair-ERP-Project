"""
Stakeholder Account Management Helpers
Auto-create Capital and Dividend accounts for stakeholders
"""

from decimal import Decimal
from .models import Account, Stakeholder
import logging

logger = logging.getLogger(__name__)


def get_or_create_stakeholder_capital_account(stakeholder):
    """
    Get or create Capital Account (3100-XX) for stakeholder.
    
    This account tracks the stakeholder's investment in the company.
    Account Type: EQUITY
    Account Number Pattern: 3100-01, 3100-02, etc.
    
    Args:
        stakeholder: Stakeholder instance
        
    Returns:
        Account instance for stakeholder's capital account
    """
    from .models import Account
    
    try:
        entity = stakeholder.entity
        stakeholder_name = stakeholder.full_name
        
        # Check if capital account already exists
        existing_account = Account.objects.filter(
            entity=entity,
            account_type='EQUITY',
            name__icontains=f"{stakeholder_name} - Capital"
        ).first()
        
        if existing_account:
            logger.info(f"Found existing capital account: {existing_account.account_number} for {stakeholder_name}")
            return existing_account
        
        # Find parent capital account (3100)
        parent_capital = Account.objects.filter(
            entity=entity,
            account_type='EQUITY',
            account_number='3100'
        ).first()
        
        if not parent_capital:
            logger.error(f"Parent Capital Account 3100 not found for entity {entity.name}")
            return None
        
        # Find next available sub-account number
        existing_sub_accounts = Account.objects.filter(
            entity=entity,
            parent_account=parent_capital,
            account_number__startswith='3100-'
        ).order_by('-account_number')
        
        if existing_sub_accounts.exists():
            last_number = existing_sub_accounts.first().account_number
            sub_num = int(last_number.split('-')[-1])
            next_sub_num = sub_num + 1
        else:
            next_sub_num = 1
        
        new_account_number = f"3100-{next_sub_num:02d}"
        
        # Create capital account
        capital_account = Account.objects.create(
            entity=entity,
            account_number=new_account_number,
            name=f"{stakeholder_name} - Capital",
            account_type='EQUITY',
            currency=entity.company_currency,
            parent_account=parent_capital,
            is_active=True,
            description=f"Capital/Investment account for {stakeholder_name}"
        )
        
        logger.info(f"Created capital account: {capital_account.account_number} for {stakeholder_name}")
        return capital_account
        
    except Exception as e:
        logger.error(f"Error creating capital account for stakeholder {stakeholder.id}: {str(e)}")
        return None


def get_or_create_stakeholder_dividend_account(stakeholder):
    """
    Get or create Drawings/Distribution Account (3200-XX) for stakeholder.
    
    This account tracks profit distributions/drawings to the stakeholder.
    Account Type: EQUITY (contra-equity - reduces owner's equity)
    Account Number Pattern: 3200-01, 3200-02, etc.
    
    Args:
        stakeholder: Stakeholder instance
        
    Returns:
        Account instance for stakeholder's drawings/distribution account
    """
    from .models import Account
    
    try:
        entity = stakeholder.entity
        stakeholder_name = stakeholder.full_name
        
        # Check if drawings account already exists
        existing_account = Account.objects.filter(
            entity=entity,
            account_type='EQUITY',
            name__icontains=f"{stakeholder_name} - Drawings"
        ).first()
        
        if existing_account:
            logger.info(f"Found existing drawings account: {existing_account.account_number} for {stakeholder_name}")
            return existing_account
        
        # Find parent drawings account (3200)
        parent_drawings = Account.objects.filter(
            entity=entity,
            account_type='EQUITY',
            account_number='3200'
        ).first()
        
        if not parent_drawings:
            # Create parent drawings account if it doesn't exist
            logger.warning(f"Parent Drawings Account 3200 not found, creating it for entity {entity.name}")
            parent_drawings = Account.objects.create(
                entity=entity,
                account_number='3200',
                name='Drawings / Distributions',
                account_type='EQUITY',
                currency=entity.company_currency,
                is_active=True,
                description='Parent account for all shareholder profit distributions and drawings (contra-equity)'
            )
        
        # Find next available sub-account number
        existing_sub_accounts = Account.objects.filter(
            entity=entity,
            parent_account=parent_drawings,
            account_number__startswith='3200-'
        ).order_by('-account_number')
        
        if existing_sub_accounts.exists():
            last_number = existing_sub_accounts.first().account_number
            sub_num = int(last_number.split('-')[-1])
            next_sub_num = sub_num + 1
        else:
            next_sub_num = 1
        
        new_account_number = f"3200-{next_sub_num:02d}"
        
        # Create drawings account
        drawings_account = Account.objects.create(
            entity=entity,
            account_number=new_account_number,
            name=f"{stakeholder_name} - Drawings",
            account_type='EQUITY',
            currency=entity.company_currency,
            parent_account=parent_drawings,
            is_active=True,
            description=f"Profit distribution/drawings account for {stakeholder_name} (contra-equity)"
        )
        
        logger.info(f"Created drawings account: {drawings_account.account_number} for {stakeholder_name}")
        return drawings_account
        
    except Exception as e:
        logger.error(f"Error creating drawings account for stakeholder {stakeholder.id}: {str(e)}")
        return None


def setup_stakeholder_accounts(stakeholder):
    """
    Setup both Capital and Dividend accounts for a stakeholder.
    
    Call this when:
    - A new stakeholder is created
    - Migrating existing stakeholders
    - Manual account setup
    
    Args:
        stakeholder: Stakeholder instance
        
    Returns:
        tuple: (capital_account, dividend_account)
    """
    capital_account = get_or_create_stakeholder_capital_account(stakeholder)
    dividend_account = get_or_create_stakeholder_dividend_account(stakeholder)
    
    return capital_account, dividend_account


def bulk_setup_stakeholder_accounts(entity=None):
    """
    Setup accounts for all stakeholders in an entity (or all entities).
    
    Useful for:
    - Initial migration
    - Fixing missing accounts
    - Batch account creation
    
    Args:
        entity: Entity instance (optional). If None, processes all entities.
        
    Returns:
        dict: Summary of accounts created
    """
    from .models import Entity, Stakeholder
    
    summary = {
        'total_stakeholders': 0,
        'capital_accounts_created': 0,
        'drawings_accounts_created': 0,
        'errors': []
    }
    
    if entity:
        entities = [entity]
    else:
        entities = Entity.objects.filter(is_active=True)
    
    for ent in entities:
        stakeholders = Stakeholder.objects.filter(entity=ent, status='ACTIVE')
        
        for stakeholder in stakeholders:
            summary['total_stakeholders'] += 1
            
            try:
                # Get or create capital account
                capital_account = get_or_create_stakeholder_capital_account(stakeholder)
                if capital_account:
                    # Check if it was just created
                    if not Account.objects.filter(
                        entity=ent,
                        account_number=capital_account.account_number
                    ).exclude(pk=capital_account.pk).exists():
                        summary['capital_accounts_created'] += 1
                
                # Get or create dividend account
                dividend_account = get_or_create_stakeholder_dividend_account(stakeholder)
                if dividend_account:
                    # Check if it was just created
                    if not Account.objects.filter(
                        entity=ent,
                        account_number=dividend_account.account_number
                    ).exclude(pk=dividend_account.pk).exists():
                        summary['dividend_accounts_created'] += 1
                        
            except Exception as e:
                error_msg = f"Error setting up accounts for {stakeholder.full_name}: {str(e)}"
                summary['errors'].append(error_msg)
                logger.error(error_msg)
    
    return summary
