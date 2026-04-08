"""
Trial Balance Calculation Module
===============================

This module provides functions to calculate trial balances from general ledger entries.
"""

from decimal import Decimal
from django.db.models import Sum, Q
from datetime import date
from .models import LedgerEntry, Account, TrialBalance


def calculate_trial_balance(entity, as_of_date=None):
    """
    Calculate trial balance for an entity as of a specific date.
    
    Args:
        entity: Entity object
        as_of_date: Date to calculate trial balance as of (default: today)
    
    Returns:
        dict: {
            'total_debits': Decimal,
            'total_credits': Decimal,
            'is_balanced': bool,
            'account_balances': list of dicts,
            'trial_balance': TrialBalance object (if saved)
        }
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    # Get GL entries up to the specified date (exclude DRAFT and REJECTED)
    gl_entries = LedgerEntry.objects.filter(
        entity=entity,
        entry_date__lte=as_of_date
    ).exclude(workflow_status__in=['DRAFT', 'REJECTED'])
    
    if not gl_entries.exists():
        return {
            'total_debits': Decimal('0.00'),
            'total_credits': Decimal('0.00'),
            'is_balanced': True,
            'account_balances': [],
            'trial_balance': None
        }
    
    # Calculate account balances
    account_balances = gl_entries.values(
        'account__id',
        'account__account_number', 
        'account__name',
        'account__account_type'
    ).annotate(
        debit_balance=Sum('amount', filter=Q(entry_type='DEBIT')),
        credit_balance=Sum('amount', filter=Q(entry_type='CREDIT'))
    ).order_by('account__account_number')
    
    # Convert to list and calculate NET balances based on account type
    balances_list = []
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')
    
    for balance in account_balances:
        debit_sum = balance['debit_balance'] or Decimal('0.00')
        credit_sum = balance['credit_balance'] or Decimal('0.00')
        account_type = balance['account__account_type']
        
        # Calculate NET balance based on normal balance for account type
        # ASSET/EXPENSE/PURCHASES accounts have DEBIT normal balance (debit - credit)
        # LIABILITY/EQUITY/INCOME/SALES accounts have CREDIT normal balance (credit - debit)
        
        if account_type in ['ASSET', 'EXPENSE', 'PURCHASES']:
            # Debit normal balance
            net_balance = debit_sum - credit_sum
            if net_balance > 0:
                debit_balance = net_balance
                credit_balance = Decimal('0.00')
                total_debits += net_balance
            elif net_balance < 0:
                # Asset/Expense with credit balance (unusual but possible)
                debit_balance = Decimal('0.00')
                credit_balance = abs(net_balance)
                total_credits += abs(net_balance)
            else:
                # Zero balance - skip this account
                continue
                
        elif account_type in ['LIABILITY', 'EQUITY', 'INCOME', 'SALES']:
            # Credit normal balance
            net_balance = credit_sum - debit_sum
            if net_balance > 0:
                debit_balance = Decimal('0.00')
                credit_balance = net_balance
                total_credits += net_balance
            elif net_balance < 0:
                # Liability/Equity/Income with debit balance (unusual but possible)
                debit_balance = abs(net_balance)
                credit_balance = Decimal('0.00')
                total_debits += abs(net_balance)
            else:
                # Zero balance - skip this account
                continue
        else:
            # Unknown account type - use old logic
            net_balance = debit_sum - credit_sum
            if net_balance > 0:
                debit_balance = net_balance
                credit_balance = Decimal('0.00')
                total_debits += net_balance
            elif net_balance < 0:
                debit_balance = Decimal('0.00')
                credit_balance = abs(net_balance)
                total_credits += abs(net_balance)
            else:
                continue
        
        # Create balance record with NET balances
        balance_record = {
            'account_id': balance['account__id'],
            'account_number': balance['account__account_number'],
            'account_name': balance['account__name'],
            'account_type': balance['account__account_type'],
            'debit_balance': debit_balance,
            'credit_balance': credit_balance,
        }
        
        balances_list.append(balance_record)
    
    # Check if balanced
    is_balanced = abs(total_debits - total_credits) < Decimal('0.01')
    
    return {
        'total_debits': total_debits,
        'total_credits': total_credits,
        'is_balanced': is_balanced,
        'account_balances': balances_list,
        'as_of_date': as_of_date,
        'trial_balance': None
    }


def save_trial_balance(entity, as_of_date=None, force_update=False):
    """
    Calculate and save trial balance to database.
    
    Args:
        entity: Entity object
        as_of_date: Date to calculate trial balance as of (default: today)
        force_update: If True, update existing record (default: False)
    
    Returns:
        TrialBalance: The saved trial balance object
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    # Check if trial balance already exists
    existing_tb = TrialBalance.objects.filter(
        entity=entity,
        as_of_date=as_of_date
    ).first()
    
    if existing_tb and not force_update:
        return existing_tb
    
    # Calculate trial balance
    tb_data = calculate_trial_balance(entity, as_of_date)
    
    # Create or update trial balance record
    if existing_tb:
        trial_balance = existing_tb
        trial_balance.total_debits = tb_data['total_debits']
        trial_balance.total_credits = tb_data['total_credits']
        trial_balance.is_balanced = tb_data['is_balanced']
        trial_balance.save()
    else:
        trial_balance = TrialBalance.objects.create(
            entity=entity,
            as_of_date=as_of_date,
            total_debits=tb_data['total_debits'],
            total_credits=tb_data['total_credits'],
            is_balanced=tb_data['is_balanced']
        )
    
    return trial_balance


def generate_trial_balance_report(entity, as_of_date=None):
    """
    Generate a formatted trial balance report.
    
    Args:
        entity: Entity object
        as_of_date: Date to generate report as of (default: today)
    
    Returns:
        str: Formatted trial balance report
    """
    tb_data = calculate_trial_balance(entity, as_of_date)
    
    if not tb_data['account_balances']:
        return f"No GL entries found for {entity.name} as of {tb_data['as_of_date']}"
    
    report = []
    report.append(f"TRIAL BALANCE - {entity.name}")
    report.append(f"As of {tb_data['as_of_date'].strftime('%B %d, %Y')}")
    report.append("=" * 80)
    report.append(f"{'Account':<50} {'Debits':>12} {'Credits':>12}")
    report.append("-" * 80)
    
    for balance in tb_data['account_balances']:
        account_name = f"{balance['account_number']} - {balance['account_name']}"
        report.append(
            f"{account_name[:48]:<50} "
            f"{balance['debit_balance']:>12.2f} "
            f"{balance['credit_balance']:>12.2f}"
        )
    
    report.append("-" * 80)
    report.append(
        f"{'TOTALS':<50} "
        f"{tb_data['total_debits']:>12.2f} "
        f"{tb_data['total_credits']:>12.2f}"
    )
    report.append("=" * 80)
    
    status = "BALANCED" if tb_data['is_balanced'] else "OUT OF BALANCE"
    report.append(f"Status: {status}")
    
    return "\n".join(report)
