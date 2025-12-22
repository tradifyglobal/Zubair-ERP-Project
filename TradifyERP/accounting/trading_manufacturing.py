"""
Trading & Manufacturing Account Generator
Calculates gross profit from sales, purchases, and direct manufacturing expenses.
"""

from decimal import Decimal
from django.db.models import Sum, Q
from accounting.models import Account, LedgerEntry


def calculate_trading_manufacturing_account(entity, period_start, period_end):
    """
    Calculate Trading & Manufacturing Account showing:
    - Sales Revenue
    - Less: Purchases & Direct Manufacturing Costs
    - = Gross Profit
    
    Args:
        entity: Entity object
        period_start: Start date
        period_end: End date
        
    Returns:
        Dictionary with trading & manufacturing account data
    """
    
    try:
        tm_data = {
            'entity': entity,
            'period_start': period_start,
            'period_end': period_end,
            'revenue_section': [],
            'cost_section': [],
            'total_sales': Decimal('0.00'),
            'sales_returns': Decimal('0.00'),
            'net_sales': Decimal('0.00'),
            'total_purchases': Decimal('0.00'),
            'purchase_returns': Decimal('0.00'),
            'net_purchases': Decimal('0.00'),
            'total_costs': Decimal('0.00'),
            'gross_profit': Decimal('0.00'),
            'gross_profit_percentage': Decimal('0.00'),
        }
        
        # Get all posted GL entries for the period
        gl_entries = LedgerEntry.objects.filter(
            entity=entity,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            is_posted=True
        )
        
        # ===== SALES REVENUE SECTION =====
        # Get INCOME accounts (4000-4999) excluding sales returns
        sales_accounts = Account.objects.filter(
            entity=entity,
            account_type='INCOME',
            is_active=True
        ).exclude(name__icontains='return').order_by('account_number')
        
        for account in sales_accounts:
            # Calculate net sales (Credits - Debits for INCOME accounts)
            credits = gl_entries.filter(
                account=account,
                entry_type='CREDIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            debits = gl_entries.filter(
                account=account,
                entry_type='DEBIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            net_amount = credits - debits
            
            if net_amount > Decimal('0.00'):
                tm_data['revenue_section'].append({
                    'account_number': account.account_number,
                    'account_name': account.name,
                    'amount': net_amount,
                })
                tm_data['total_sales'] += net_amount
        
        # ===== SALES RETURNS =====
        # Get sales return accounts (contra revenue accounts)
        sales_return_accounts = Account.objects.filter(
            entity=entity,
            account_type='INCOME',
            name__icontains='return',
            is_active=True
        ).order_by('account_number')
        
        for account in sales_return_accounts:
            # For sales returns (contra revenue), debits reduce revenue
            debits = gl_entries.filter(
                account=account,
                entry_type='DEBIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            credits = gl_entries.filter(
                account=account,
                entry_type='CREDIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            net_returns = debits - credits
            
            if net_returns > Decimal('0.00'):
                tm_data['sales_returns'] += net_returns
        
        # Calculate Net Sales
        tm_data['net_sales'] = tm_data['total_sales'] - tm_data['sales_returns']
        
        # ===== COST OF SALES SECTION =====
        # Get EXPENSE accounts for purchases (excluding purchase returns)
        purchase_accounts = Account.objects.filter(
            entity=entity,
            account_type='EXPENSE',
            is_active=True
        ).filter(
            Q(name__icontains='purchase') | Q(name__icontains='cost of goods')
        ).exclude(name__icontains='return').order_by('account_number')
        
        for account in purchase_accounts:
            # Calculate net expense (Debits - Credits for EXPENSE accounts)
            debits = gl_entries.filter(
                account=account,
                entry_type='DEBIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            credits = gl_entries.filter(
                account=account,
                entry_type='CREDIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            net_purchase = debits - credits
            
            if net_purchase > Decimal('0.00'):
                tm_data['cost_section'].append({
                    'account_number': account.account_number,
                    'account_name': account.name,
                    'category': 'Purchases',
                    'amount': net_purchase,
                })
                tm_data['total_purchases'] += net_purchase
        
        # ===== PURCHASE RETURNS =====
        # Get purchase return accounts (contra expense accounts)
        purchase_return_accounts = Account.objects.filter(
            entity=entity,
            account_type='EXPENSE',
            name__icontains='return',
            is_active=True
        ).filter(
            Q(name__icontains='purchase')
        ).order_by('account_number')
        
        for account in purchase_return_accounts:
            # For purchase returns (contra expense), credits reduce purchases
            credits = gl_entries.filter(
                account=account,
                entry_type='CREDIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            debits = gl_entries.filter(
                account=account,
                entry_type='DEBIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            net_returns = credits - debits
            
            if net_returns > Decimal('0.00'):
                tm_data['purchase_returns'] += net_returns
        
        # Calculate Net Purchases
        tm_data['net_purchases'] = tm_data['total_purchases'] - tm_data['purchase_returns']
        
        # Get other manufacturing/trading expense accounts
        cost_keywords = [
            'salary', 'salaries', 
            'wage', 'wages',
            'transportation', 'inward freight',
            'factory rent', 'manufacturing rent',
            'factory electricity', 'factory power',
            'factory expense', 'manufacturing expense',
            'miscellaneous', 'misc'
        ]
        
        # Get other EXPENSE accounts (excluding purchases and returns already processed)
        other_expense_accounts = Account.objects.filter(
            entity=entity,
            account_type='EXPENSE',
            is_active=True
        ).exclude(
            Q(name__icontains='purchase') | Q(name__icontains='return')
        ).order_by('account_number')
        
        for account in other_expense_accounts:
            # Check if account is for direct manufacturing/trading costs
            # Include all expense accounts since user wants GL codes
            
            # Calculate net expense (Debits - Credits for EXPENSE accounts)
            debits = gl_entries.filter(
                account=account,
                entry_type='DEBIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            credits = gl_entries.filter(
                account=account,
                entry_type='CREDIT'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            net_expense = debits - credits
            
            if net_expense > Decimal('0.00'):
                # Categorize the expense
                account_name_lower = account.name.lower()
                category = 'Other Direct Costs'
                
                if any(kw in account_name_lower for kw in ['salary', 'salaries']):
                    category = 'Salaries'
                elif any(kw in account_name_lower for kw in ['wage', 'wages']):
                    category = 'Wages'
                elif any(kw in account_name_lower for kw in ['transport', 'freight', 'inward']):
                    category = 'Transportation (Inward)'
                elif any(kw in account_name_lower for kw in ['factory rent', 'manufacturing rent']):
                    category = 'Factory Rent'
                elif any(kw in account_name_lower for kw in ['factory electricity', 'factory power', 'factory utilities']):
                    category = 'Factory Electricity'
                elif any(kw in account_name_lower for kw in ['miscellaneous', 'misc', 'sundry']):
                    category = 'Miscellaneous'
                
                tm_data['cost_section'].append({
                    'account_number': account.account_number,
                    'account_name': account.name,
                    'category': category,
                    'amount': net_expense,
                })
                tm_data['total_costs'] += net_expense
        
        # Add net purchases to total costs
        tm_data['total_costs'] += tm_data['net_purchases']
        
        # Sort cost section by category
        tm_data['cost_section'].sort(key=lambda x: (x['category'], x['account_number']))
        
        # ===== CALCULATE GROSS PROFIT =====
        tm_data['gross_profit'] = tm_data['net_sales'] - tm_data['total_costs']
        
        # Calculate gross profit percentage based on net sales
        if tm_data['net_sales'] > Decimal('0.00'):
            tm_data['gross_profit_percentage'] = (
                tm_data['gross_profit'] / tm_data['net_sales'] * 100
            )
        
        return tm_data
        
    except Exception as e:
        print(f"Error calculating Trading & Manufacturing Account: {str(e)}")
        return {
            'error': str(e),
            'entity': entity,
            'period_start': period_start,
            'period_end': period_end,
        }


def get_manufacturing_metrics(entity, period_start, period_end):
    """
    Get additional manufacturing metrics.
    
    Returns:
        Dictionary with manufacturing KPIs
    """
    tm_data = calculate_trading_manufacturing_account(entity, period_start, period_end)
    
    if 'error' in tm_data:
        return {}
    
    metrics = {
        'gross_profit_margin': tm_data['gross_profit_percentage'],
        'cost_of_sales_ratio': Decimal('0.00'),
        'revenue_per_category': {},
    }
    
    # Calculate cost of sales ratio
    if tm_data['total_sales'] > Decimal('0.00'):
        metrics['cost_of_sales_ratio'] = (
            tm_data['total_costs'] / tm_data['total_sales'] * 100
        )
    
    # Group costs by category
    for cost_item in tm_data['cost_section']:
        category = cost_item['category']
        if category not in metrics['revenue_per_category']:
            metrics['revenue_per_category'][category] = Decimal('0.00')
        metrics['revenue_per_category'][category] += cost_item['amount']
    
    return metrics
