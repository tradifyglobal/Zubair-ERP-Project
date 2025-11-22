"""
Main Dashboard View
Comprehensive dashboard with metrics, charts, and activity feed
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from decimal import Decimal
from datetime import datetime, timedelta
import json


@login_required
def main_dashboard(request):
    """
    Main dashboard view with comprehensive metrics and visualizations.
    """
    
    # Calculate date ranges
    today = datetime.now()
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    
    # Import models dynamically to avoid circular imports
    from accounting.models import Entity, LedgerEntry, Account
    
    try:
        from sales.models import SalesOrder, Invoice
        has_sales = True
    except:
        has_sales = False
    
    try:
        from manufacturing.models import Product
        has_manufacturing = True
    except:
        has_manufacturing = False
    
    # Get primary entity
    entity = Entity.objects.filter(is_active=True).first()
    
    # Initialize context with default values
    context = {
        'total_revenue': Decimal('0.00'),
        'total_profit': Decimal('0.00'),
        'revenue_growth': 0,
        'profit_margin': 0,
        'active_orders': 0,
        'pending_orders': 0,
        'wallet_balance': Decimal('0.00'),
        'monthly_income': Decimal('0.00'),
        'monthly_expenses': Decimal('0.00'),
        'revenue_data': json.dumps([]),
        'revenue_labels': json.dumps([]),
        'sales_breakdown_data': json.dumps([]),
        'sales_breakdown_labels': json.dumps([]),
        'sales_categories': [],
        'top_locations': [],
        'recent_activities': [],
        'top_products': [],
    }
    
    if entity:
        # Calculate revenue from sales if available
        if has_sales:
            try:
                # Current month revenue
                current_revenue = Invoice.objects.filter(
                    customer__entity=entity,
                    invoice_date__gte=current_month_start
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                
                # Last month revenue
                last_revenue = Invoice.objects.filter(
                    customer__entity=entity,
                    invoice_date__gte=last_month_start,
                    invoice_date__lte=last_month_end
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                
                # Calculate growth
                if last_revenue > 0:
                    revenue_growth = ((current_revenue - last_revenue) / last_revenue * 100)
                else:
                    revenue_growth = 0
                
                context['total_revenue'] = current_revenue
                context['revenue_growth'] = round(revenue_growth, 1)
                
                # Active orders
                context['active_orders'] = SalesOrder.objects.filter(
                    customer__entity=entity,
                    status__in=['DRAFT', 'CONFIRMED']
                ).count()
                
                context['pending_orders'] = SalesOrder.objects.filter(
                    customer__entity=entity,
                    status='DRAFT'
                ).count()
                
                # Get revenue data for last 12 months
                revenue_by_month = []
                month_labels = []
                for i in range(11, -1, -1):
                    month_date = today - timedelta(days=30*i)
                    month_start = month_date.replace(day=1)
                    if i > 0:
                        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    else:
                        month_end = today
                    
                    month_revenue = Invoice.objects.filter(
                        customer__entity=entity,
                        invoice_date__gte=month_start,
                        invoice_date__lte=month_end
                    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                    
                    revenue_by_month.append(float(month_revenue))
                    month_labels.append(month_start.strftime('%b'))
                
                context['revenue_data'] = json.dumps(revenue_by_month)
                context['revenue_labels'] = json.dumps(month_labels)
                
                # Sales breakdown by customer - Get top 5 customers
                customer_sales = Invoice.objects.filter(
                    customer__entity=entity,
                    invoice_date__gte=current_month_start
                ).values('customer__name').annotate(
                    total=Sum('total_amount')
                ).order_by('-total')[:5]
                
                total_sales = sum([cs['total'] for cs in customer_sales]) if customer_sales else Decimal('0.00')
                
                colors = ['#556ee6', '#34c38f', '#f46a6a', '#50a5f1', '#f1b44c']
                
                if total_sales > 0:
                    sales_breakdown_data = []
                    sales_breakdown_labels = []
                    sales_categories = []
                    
                    for idx, cs in enumerate(customer_sales):
                        percentage = round(float(cs['total'] / total_sales * 100), 1)
                        sales_breakdown_data.append(percentage)
                        sales_breakdown_labels.append(cs['customer__name'])
                        sales_categories.append({
                            'name': cs['customer__name'],
                            'percentage': percentage,
                            'color': colors[idx % len(colors)]
                        })
                    
                    context['sales_breakdown_data'] = json.dumps(sales_breakdown_data)
                    context['sales_breakdown_labels'] = json.dumps(sales_breakdown_labels)
                    context['sales_categories'] = sales_categories
                
            except Exception as e:
                print(f"Error calculating sales metrics: {e}")
        
        # Calculate profit (simplified - revenue minus cost of goods sold)
        context['total_profit'] = context['total_revenue'] * Decimal('0.35')  # Assuming 35% margin
        if context['total_revenue'] > 0:
            context['profit_margin'] = round(float(context['total_profit'] / context['total_revenue'] * 100), 1)
        
        # Get wallet balance from cash accounts
        try:
            cash_accounts = Account.objects.filter(
                entity=entity,
                account_type='ASSET',
                name__icontains='cash'
            )
            
            wallet_balance = Decimal('0.00')
            for account in cash_accounts:
                balance = LedgerEntry.objects.filter(
                    account=account
                ).aggregate(
                    total=Sum('debit_amount') - Sum('credit_amount')
                )['total'] or Decimal('0.00')
                wallet_balance += balance
            
            context['wallet_balance'] = wallet_balance
        except Exception as e:
            print(f"Error calculating wallet balance: {e}")
        
        # Monthly income/expenses
        try:
            income_accounts = Account.objects.filter(
                entity=entity,
                account_type='REVENUE'
            )
            
            monthly_income = LedgerEntry.objects.filter(
                account__in=income_accounts,
                entry_date__gte=current_month_start
            ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
            
            expense_accounts = Account.objects.filter(
                entity=entity,
                account_type='EXPENSE'
            )
            
            monthly_expenses = LedgerEntry.objects.filter(
                account__in=expense_accounts,
                entry_date__gte=current_month_start
            ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
            
            context['monthly_income'] = monthly_income
            context['monthly_expenses'] = monthly_expenses
        except Exception as e:
            print(f"Error calculating income/expenses: {e}")
        
        # Top products
        if has_manufacturing:
            try:
                from manufacturing.models import Product
                products = Product.objects.filter(entity=entity)[:5]
                
                context['top_products'] = [{
                    'name': p.name,
                    'category': p.category.name if hasattr(p, 'category') and p.category else 'General',
                    'stock': 100,  # Placeholder
                    'price': p.unit_price if hasattr(p, 'unit_price') else Decimal('0.00'),
                    'sales': 50,  # Placeholder
                    'revenue': Decimal('5000.00'),  # Placeholder
                } for p in products]
            except Exception as e:
                print(f"Error fetching products: {e}")
        
        # Recent activities from audit log
        try:
            from accounting.models import AuditLog
            recent_logs = AuditLog.objects.filter(
                entity=entity
            ).order_by('-created_at')[:5]
            
            activity_icons = {
                'CREATE': 'plus-circle',
                'UPDATE': 'pencil',
                'DELETE': 'delete',
                'APPROVE': 'check-circle',
            }
            
            activity_types = {
                'CREATE': 'success',
                'UPDATE': 'info',
                'DELETE': 'danger',
                'APPROVE': 'primary',
            }
            
            context['recent_activities'] = [{
                'title': log.action,
                'description': log.description[:100] if log.description else 'No description',
                'time': log.created_at.strftime('%b %d, %I:%M %p'),
                'icon': activity_icons.get(log.action, 'information'),
                'type': activity_types.get(log.action, 'secondary'),
            } for log in recent_logs]
        except Exception as e:
            print(f"Error fetching activities: {e}")
    
    return render(request, 'dashboard_main.html', context)
