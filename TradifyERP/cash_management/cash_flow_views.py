"""Cash Flow Statement Views - Generate, display, and analyze cash flow reports"""

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime, timedelta
import json

from accounting.models import (
    Entity, LedgerEntry, Account, Invoice, VendorBill, 
    PaymentSchedule, Currency, BankStatement, CashTransaction
)
from sales.models import Customer
from ap.models import Vendor
from .cash_flow_models import (
    CashFlowStatement, CashFlowCategory, CashFlowLineItem,
    CashFlowVarianceAnalysis, CashFlowComparison, CashFlowForecastDetail
)


class SessionEntityMixin:
    """Ensures user's selected entity is used for all queries"""
    def get_entity(self):
        return getattr(self.request, 'entity', None)


class CashFlowStatementListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """Display list of all cash flow statements for entity"""
    
    model = CashFlowStatement
    template_name = 'cash_management/cash_flow_statements_list.html'
    context_object_name = 'statements'
    paginate_by = 20
    
    def get_queryset(self):
        entity = self.get_entity()
        return CashFlowStatement.objects.filter(entity=entity).order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.get_entity()
        
        # Summary statistics
        statements = self.get_queryset()[:12]
        if statements.exists():
            context['latest_statement'] = statements.first()
            context['total_recent_inflows'] = sum(s.operating_inflows + s.investing_inflows + s.financing_inflows for s in statements)
            context['total_recent_outflows'] = sum(s.operating_outflows + s.investing_outflows + s.financing_outflows for s in statements)
            context['avg_net_monthly_flow'] = context['total_recent_inflows'] - context['total_recent_outflows']
        
        context['entity'] = entity
        return context


class CashFlowStatementDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detailed view of a single cash flow statement"""
    
    model = CashFlowStatement
    template_name = 'cash_management/cash_flow_statement_detail.html'
    context_object_name = 'statement'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statement = self.get_object()
        
        # Get line items by category
        line_items = statement.line_items.all()
        
        context['line_items_by_category'] = {}
        for activity_type in ['OPERATING', 'INVESTING', 'FINANCING']:
            items = line_items.filter(category__activity_type=activity_type).order_by('line_number')
            context['line_items_by_category'][activity_type] = list(items)
        
        # Get variance analysis if exists
        try:
            context['variance_analysis'] = statement.variance_analysis
        except:
            context['variance_analysis'] = None
        
        # Get comparisons
        context['prior_comparison'] = CashFlowComparison.objects.filter(
            current_period_statement=statement
        ).first()
        
        # Bank reconciliation details
        if statement.bank_closing_balance:
            context['reconciliation_difference'] = abs(
                statement.closing_balance - statement.bank_closing_balance
            )
        
        # Calculate key metrics
        context['total_inflows'] = (
            statement.operating_inflows + 
            statement.investing_inflows + 
            statement.financing_inflows
        )
        context['total_outflows'] = (
            statement.operating_outflows + 
            statement.investing_outflows + 
            statement.financing_outflows
        )
        
        return context


class CashFlowStatementGenerateView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Generate/regenerate cash flow statement from GL entries"""
    
    template_name = 'cash_management/cash_flow_generate.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.get_entity()
        
        # Get date range for generation
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        
        context['entity'] = entity
        context['generation_period'] = {
            'start_date': start_of_month,
            'end_date': today
        }
        
        # Pre-calculate summary for preview
        context['preview_data'] = self._calculate_cash_flows(
            entity, start_of_month, today
        )
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Generate or regenerate statement"""
        entity = self.get_entity()
        
        period_type = request.POST.get('period_type', 'MONTHLY')
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        
        # Generate statement
        statement = self._generate_statement(entity, period_type, start_date, end_date)
        
        return JsonResponse({
            'success': True,
            'message': f'Statement generated for {start_date} to {end_date}',
            'statement_id': statement.id,
            'statement_url': f'/cash/statements/{statement.id}/'
        })
    
    def _calculate_cash_flows(self, entity, start_date, end_date):
        """Calculate cash flows by category"""
        
        # Initialize categories
        categories = CashFlowCategory.objects.all()
        flows = {
            'OPERATING': {'inflows': Decimal('0'), 'outflows': Decimal('0')},
            'INVESTING': {'inflows': Decimal('0'), 'outflows': Decimal('0')},
            'FINANCING': {'inflows': Decimal('0'), 'outflows': Decimal('0')},
        }
        
        # Get ledger entries for period
        ledger_entries = LedgerEntry.objects.filter(
            entity=entity,
            entry_date__gte=start_date,
            entry_date__lte=end_date,
            account__number__in=[100, 101, 102]  # Cash/bank accounts
        )
        
        # Categorize based on opposing account
        for entry in ledger_entries:
            category_match = None
            
            # Match against category patterns
            for cat in categories:
                if self._matches_account_pattern(entry.opposing_account, cat.account_patterns):
                    category_match = cat
                    break
            
            if not category_match:
                # Default categorization based on account type
                category_match = self._default_categorize(entry)
            
            if category_match:
                if entry.debit_amount > 0:  # Inflow
                    flows[category_match.activity_type]['inflows'] += entry.debit_amount
                else:  # Outflow
                    flows[category_match.activity_type]['outflows'] += entry.credit_amount
        
        return flows
    
    def _generate_statement(self, entity, period_type, start_date, end_date):
        """Create or update cash flow statement"""
        
        # Calculate opening balance
        opening_ledger = LedgerEntry.objects.filter(
            entity=entity,
            entry_date__lt=start_date,
            account__number__in=[100, 101, 102]  # Cash accounts
        ).aggregate(
            balance=Coalesce(Sum('debit_amount'), Decimal('0')) - 
                   Coalesce(Sum('credit_amount'), Decimal('0'))
        )['balance']
        
        # Calculate closing balance
        closing_ledger = LedgerEntry.objects.filter(
            entity=entity,
            entry_date__lte=end_date,
            account__number__in=[100, 101, 102]
        ).aggregate(
            balance=Coalesce(Sum('debit_amount'), Decimal('0')) - 
                   Coalesce(Sum('credit_amount'), Decimal('0'))
        )['balance']
        
        # Get or create statement
        statement, created = CashFlowStatement.objects.update_or_create(
            entity=entity,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'opening_balance': opening_ledger,
                'closing_balance': closing_ledger,
                'generated_by': 'SYSTEM',
            }
        )
        
        # Recalculate flows
        flows = self._calculate_cash_flows(entity, start_date, end_date)
        
        statement.operating_inflows = flows['OPERATING']['inflows']
        statement.operating_outflows = flows['OPERATING']['outflows']
        statement.net_operating_cash_flow = statement.operating_inflows - statement.operating_outflows
        
        statement.investing_inflows = flows['INVESTING']['inflows']
        statement.investing_outflows = flows['INVESTING']['outflows']
        statement.net_investing_cash_flow = statement.investing_inflows - statement.investing_outflows
        
        statement.financing_inflows = flows['FINANCING']['inflows']
        statement.financing_outflows = flows['FINANCING']['outflows']
        statement.net_financing_cash_flow = statement.financing_inflows - statement.financing_outflows
        
        statement.total_net_cash_flow = (
            statement.net_operating_cash_flow +
            statement.net_investing_cash_flow +
            statement.net_financing_cash_flow
        )
        
        statement.save()
        
        # Generate line items
        self._generate_line_items(statement, start_date, end_date)
        
        return statement
    
    def _generate_line_items(self, statement, start_date, end_date):
        """Create detailed line items for statement"""
        
        CashFlowLineItem.objects.filter(cash_flow_statement=statement).delete()
        
        line_number = 1
        
        # Operating Activities
        operating_items = self._get_operating_items(statement.entity, start_date, end_date)
        for desc, amount in operating_items.items():
            CashFlowLineItem.objects.create(
                cash_flow_statement=statement,
                line_number=line_number,
                description=desc,
                amount=abs(amount),
                is_inflow=amount > 0,
                source_type='OPERATING'
            )
            line_number += 1
        
        # Investing Activities
        investing_items = self._get_investing_items(statement.entity, start_date, end_date)
        for desc, amount in investing_items.items():
            CashFlowLineItem.objects.create(
                cash_flow_statement=statement,
                line_number=line_number,
                description=desc,
                amount=abs(amount),
                is_inflow=amount > 0,
                source_type='INVESTING'
            )
            line_number += 1
        
        # Financing Activities
        financing_items = self._get_financing_items(statement.entity, start_date, end_date)
        for desc, amount in financing_items.items():
            CashFlowLineItem.objects.create(
                cash_flow_statement=statement,
                line_number=line_number,
                description=desc,
                amount=abs(amount),
                is_inflow=amount > 0,
                source_type='FINANCING'
            )
            line_number += 1
    
    def _get_operating_items(self, entity, start_date, end_date):
        """Calculate operating cash flows"""
        items = {}
        
        # Collections from customers (Invoices paid)
        collections = Invoice.objects.filter(
            entity=entity,
            paid_date__range=[start_date, end_date]
        ).aggregate(total=Coalesce(Sum('amount_paid'), Decimal('0')))['total']
        if collections:
            items['Collections from Customers'] = collections
        
        # Payments to vendors (Vendor bills paid)
        payments = VendorBill.objects.filter(
            entity=entity,
            paid_date__range=[start_date, end_date]
        ).aggregate(total=Coalesce(Sum('amount_paid'), Decimal('0')))['total']
        if payments:
            items['Payments to Suppliers'] = -payments
        
        return items
    
    def _get_investing_items(self, entity, start_date, end_date):
        """Calculate investing cash flows"""
        items = {}
        
        # Asset acquisitions, sales, investments
        # (Can be extended with actual asset models)
        transfers_out = LedgerEntry.objects.filter(
            entity=entity,
            entry_date__range=[start_date, end_date],
            account__account_type='INVESTMENT'
        ).aggregate(total=Coalesce(Sum('credit_amount'), Decimal('0')))['total']
        
        if transfers_out:
            items['Investment Purchases'] = -transfers_out
        
        return items
    
    def _get_financing_items(self, entity, start_date, end_date):
        """Calculate financing cash flows"""
        items = {}
        
        # Loan proceeds, repayments
        # (Can be extended with loan payment models)
        financing = LedgerEntry.objects.filter(
            entity=entity,
            entry_date__range=[start_date, end_date],
            account__account_type__in=['LIABILITY', 'EQUITY']
        ).aggregate(
            inflows=Coalesce(Sum('debit_amount'), Decimal('0')),
            outflows=Coalesce(Sum('credit_amount'), Decimal('0'))
        )
        
        if financing['inflows']:
            items['Financing Proceeds'] = financing['inflows']
        if financing['outflows']:
            items['Financing Repayments'] = -financing['outflows']
        
        return items
    
    def _matches_account_pattern(self, account_number, pattern_string):
        """Check if account matches comma-separated patterns"""
        patterns = [p.strip() for p in pattern_string.split(',')]
        for pattern in patterns:
            if pattern and str(account_number).startswith(pattern):
                return True
        return False
    
    def _default_categorize(self, entry):
        """Default categorization based on account type"""
        # AR collections = Operating
        # AP payments = Operating
        # Asset sales = Investing
        # Loan repayments = Financing
        return None


class CashFlowVarianceAnalysisView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Analyze actual vs. forecasted cash flows"""
    
    model = CashFlowStatement
    template_name = 'cash_management/cash_flow_variance_analysis.html'
    context_object_name = 'statement'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statement = self.get_object()
        
        # Get forecasts for comparison
        forecast_details = CashFlowForecastDetail.objects.filter(
            entity=statement.entity,
            forecast_date__range=[statement.start_date, statement.end_date]
        )
        
        # Summarize forecasts by category
        context['forecast_summary'] = {}
        for cat_type in ['OPERATING', 'INVESTING', 'FINANCING']:
            cat_forecast = forecast_details.filter(
                category__activity_type=cat_type
            ).aggregate(
                inflows=Coalesce(Sum('forecasted_inflow'), Decimal('0')),
                outflows=Coalesce(Sum('forecasted_outflow'), Decimal('0'))
            )
            
            if cat_type == 'OPERATING':
                actual = statement.net_operating_cash_flow
            elif cat_type == 'INVESTING':
                actual = statement.net_investing_cash_flow
            else:
                actual = statement.net_financing_cash_flow
            
            forecast_net = cat_forecast['inflows'] - cat_forecast['outflows']
            variance = actual - forecast_net
            variance_pct = (variance / forecast_net * 100) if forecast_net != 0 else 0
            
            context['forecast_summary'][cat_type] = {
                'forecast': forecast_net,
                'actual': actual,
                'variance': variance,
                'variance_pct': variance_pct,
            }
        
        # Get variance analysis record
        try:
            context['variance_analysis'] = statement.variance_analysis
        except:
            context['variance_analysis'] = None
        
        return context


class CashFlowComparisonView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Compare multiple periods side-by-side"""
    
    template_name = 'cash_management/cash_flow_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.get_entity()
        
        # Get last 12 monthly statements
        statements = CashFlowStatement.objects.filter(
            entity=entity,
            period_type='MONTHLY'
        ).order_by('-start_date')[:12]
        
        context['statements'] = list(reversed(statements))
        
        # Calculate trends
        if statements.count() >= 2:
            context['operating_trend'] = [s.net_operating_cash_flow for s in reversed(statements)]
            context['investing_trend'] = [s.net_investing_cash_flow for s in reversed(statements)]
            context['financing_trend'] = [s.net_financing_cash_flow for s in reversed(statements)]
            
            # YoY comparison if available
            first_stmt = statements.last()
            year_ago = first_stmt.start_date.replace(year=first_stmt.start_date.year - 1)
            
            year_ago_stmt = CashFlowStatement.objects.filter(
                entity=entity,
                start_date__year=year_ago.year,
                start_date__month=year_ago.month
            ).first()
            
            if year_ago_stmt:
                context['yoy_comparison'] = {
                    'current_period': first_stmt,
                    'year_ago': year_ago_stmt,
                    'operating_change': (
                        first_stmt.net_operating_cash_flow - 
                        year_ago_stmt.net_operating_cash_flow
                    ),
                    'investing_change': (
                        first_stmt.net_investing_cash_flow - 
                        year_ago_stmt.net_investing_cash_flow
                    ),
                    'financing_change': (
                        first_stmt.net_financing_cash_flow - 
                        year_ago_stmt.net_financing_cash_flow
                    ),
                }
        
        context['entity'] = entity
        return context
