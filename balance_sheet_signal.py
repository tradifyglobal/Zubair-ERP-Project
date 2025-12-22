
@receiver(post_save, sender='accounting.CashReceiptLine')
@receiver(post_save, sender='accounting.CashPaymentLine')
def auto_generate_balance_sheet(sender, instance, created, **kwargs):
    """
    Automatically generate/update Balance Sheet when cash receipts or payments are authorized.
    This keeps Balance Sheets up-to-date without manual regeneration.
    """
    from accounting.models import BalanceSheet, LedgerEntry
    from datetime import date
    from decimal import Decimal
    
    # Only proceed if status is AUTHORIZED
    if instance.workflow_status != 'AUTHORIZED':
        return
    
    try:
        entity = instance.entity
        
        # Find the latest entry date or use today
        latest_entry = LedgerEntry.objects.filter(entity=entity).order_by('-entry_date').first()
        if latest_entry:
            calc_date = max(latest_entry.entry_date, date.today())
        else:
            calc_date = date.today()
        
        # Calculate balance sheet data
        balance_sheet_data = calculate_balance_sheet_for_entity(entity, calc_date)
        
        if balance_sheet_data:
            # Save or update balance sheet
            BalanceSheet.objects.update_or_create(
                entity=entity,
                as_of_date=calc_date,
                defaults={
                    'total_assets': balance_sheet_data['total_assets'],
                    'total_liabilities': balance_sheet_data['total_liabilities'],
                    'total_equity': balance_sheet_data['total_equity']
                }
            )
            print(f"Auto-generated Balance Sheet for {entity.code} as of {calc_date}")
            
    except Exception as e:
        print(f"Error auto-generating Balance Sheet: {str(e)}")
        pass


def calculate_balance_sheet_for_entity(entity, as_of_date):
    """
    Calculate balance sheet from ledger entries.
    Extracted from views.py for reuse in signals.
    """
    from accounting.models import LedgerEntry
    from decimal import Decimal
    
    # Get all ledger entries up to the date (exclude DRAFT and REJECTED)
    entries = LedgerEntry.objects.filter(
        entity=entity,
        entry_date__lte=as_of_date
    ).exclude(workflow_status__in=['DRAFT', 'REJECTED'])
    
    if entries.count() == 0:
        return None
    
    # Calculate balances by account
    accounts = {}
    for entry in entries:
        acc_key = entry.account.id
        if acc_key not in accounts:
            accounts[acc_key] = {
                'account': entry.account,
                'debit_total': Decimal('0'),
                'credit_total': Decimal('0')
            }
        
        if entry.entry_type == 'DEBIT':
            accounts[acc_key]['debit_total'] += entry.amount
        else:
            accounts[acc_key]['credit_total'] += entry.amount
    
    # Calculate totals by account type
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    total_equity = Decimal('0')
    
    for acc_data in accounts.values():
        account = acc_data['account']
        net_balance = acc_data['debit_total'] - acc_data['credit_total']
        
        if account.account_type == 'ASSET' and net_balance > 0:
            total_assets += net_balance
        elif account.account_type == 'LIABILITY' and net_balance < 0:
            total_liabilities += abs(net_balance)
        elif account.account_type == 'EQUITY' and net_balance < 0:
            total_equity += abs(net_balance)
    
    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity
    }
