from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q, F, Case, When, DecimalField
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import timedelta, date
from django.contrib import messages

from .models import (
    CashPosition, PaymentSchedule, LiquidityForecast, TreasuryAccount,
    CashFlowForecastDetail, FXExposure
)
from .forms import PaymentScheduleForm, CashPositionForm, LiquidityForecastForm, TreasuryAccountForm, FXExposureForm
from accounting.models import BankProfile, LedgerEntry, Account, Entity, Currency
from sales.models import Invoice
from ap.models import VendorBill as Bill
from accounting.mixins import SessionEntityMixin


class CashManagementDashboardView(LoginRequiredMixin, TemplateView):
    """Cash Management Dashboard."""
    template_name = 'cash_management/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current cash position
        today = timezone.now().date()
        latest_positions = CashPosition.objects.filter(
            position_date=today
        ).select_related('bank_account')
        
        total_cash = latest_positions.aggregate(
            total=Sum('closing_balance')
        )['total'] or Decimal('0')
        
        # Upcoming payments
        upcoming_payments = PaymentSchedule.objects.filter(
            status__in=['SCHEDULED', 'APPROVED'],
            scheduled_date__lte=today + timedelta(days=30)
        ).order_by('scheduled_date')
        
        total_scheduled = upcoming_payments.aggregate(
            total=Sum('payment_amount')
        )['total'] or Decimal('0')
        
        # Overdue payments
        overdue_payments = PaymentSchedule.objects.filter(
            status__in=['SCHEDULED', 'APPROVED'],
            due_date__lt=today
        )
        
        # Liquidity forecast
        latest_forecast = LiquidityForecast.objects.filter(
            forecast_start_date__lte=today,
            forecast_end_date__gte=today
        ).first()
        
        # Treasury accounts
        treasury_accounts = TreasuryAccount.objects.filter(is_active=True)
        
        context.update({
            'cash_positions': latest_positions,
            'total_cash': total_cash,
            'upcoming_payments': upcoming_payments[:10],
            'total_scheduled': total_scheduled,
            'overdue_payments': overdue_payments,
            'liquidity_forecast': latest_forecast,
            'treasury_accounts': treasury_accounts,
        })
        
        return context


class PaymentScheduleListView(LoginRequiredMixin, ListView):
    """List all payment schedules."""
    model = PaymentSchedule
    template_name = 'cash_management/paymentschedule_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = PaymentSchedule.objects.select_related('currency', 'from_account').order_by('-scheduled_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class PaymentScheduleDetailView(LoginRequiredMixin, DetailView):
    """Detail view for payment schedule."""
    model = PaymentSchedule
    template_name = 'cash_management/paymentschedule_detail.html'


class CashPositionDetailView(LoginRequiredMixin, DetailView):
    """Detail view for cash position."""
    model = CashPosition
    template_name = 'cash_management/cashposition_detail.html'


class CashPositionListView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Comprehensive cash position view showing real-time liquidity snapshot."""
    template_name = 'cash_management/cash_position_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        today = date.today()
        
        # Get all cash and bank accounts for this entity
        cash_accounts = Account.objects.filter(
            entity=entity
        ).filter(
            Q(account_number__startswith='100') |
            Q(account_number__startswith='101') |
            Q(account_number__startswith='110')  # Cash/Bank accounts (1000-1199)
        )
        
        # ===== OPENING BALANCE =====
        # Get GL entries up to yesterday to calculate opening balance
        opening_gl_entries = LedgerEntry.objects.filter(
            entity=entity,
            account__in=cash_accounts,
            entry_date__lt=today
        )
        
        opening_balance = Decimal('0')
        for entry in opening_gl_entries:
            if entry.entry_type == 'DEBIT':
                opening_balance += entry.amount
            else:  # CREDIT
                opening_balance -= entry.amount
        
        # ===== TODAY'S ACTUAL MOVEMENTS =====
        today_entries = LedgerEntry.objects.filter(
            entity=entity,
            account__in=cash_accounts,
            entry_date=today
        )
        
        actual_receipts = Decimal('0')
        actual_payments = Decimal('0')
        
        for entry in today_entries:
            if entry.entry_type == 'DEBIT':
                actual_receipts += entry.amount
            else:  # CREDIT
                actual_payments += entry.amount
        
        # Calculate current balance
        current_balance = opening_balance + actual_receipts - actual_payments
        
        # ===== EXPECTED CASH FLOWS (DUE TODAY) =====
        # Customer invoices due today (expected inflow)
        try:
            customer_invoices_due = Invoice.objects.filter(
                entity=entity,
                due_date=today,
                status__in=['OPEN', 'PARTIAL']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        except:
            customer_invoices_due = Decimal('0')
        
        # Vendor bills due today (expected outflow)
        try:
            vendor_bills_due = Bill.objects.filter(
                entity=entity,
                due_date=today,
                status__in=['OPEN', 'PARTIAL']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        except:
            vendor_bills_due = Decimal('0')
        
        # Scheduled payments due today
        scheduled_today = PaymentSchedule.objects.filter(
            entity=entity,
            scheduled_date=today,
            status__in=['SCHEDULED', 'APPROVED']
        ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0')
        
        # ===== FORECAST POSITION (INCLUDING TODAY'S EXPECTED FLOWS) =====
        forecast_position = current_balance + customer_invoices_due - vendor_bills_due - scheduled_today
        
        # ===== LIQUIDITY STATUS =====
        if forecast_position > opening_balance * Decimal('0.2'):  # More than 20% of opening
            liquidity_status = 'HEALTHY'
            status_color = 'green'
        elif forecast_position > 0:
            liquidity_status = 'TIGHT'
            status_color = 'yellow'
        else:
            liquidity_status = 'CRITICAL'
            status_color = 'red'
        
        # ===== BY ACCOUNT BREAKDOWN =====
        account_breakdown = []
        for account in cash_accounts:
            acc_entries = LedgerEntry.objects.filter(account=account, entry_date__lte=today)
            acc_balance = Decimal('0')
            for entry in acc_entries:
                if entry.entry_type == 'DEBIT':
                    acc_balance += entry.amount
                else:
                    acc_balance -= entry.amount
            
            if acc_balance != 0:
                account_breakdown.append({
                    'account_number': account.account_number,
                    'account_name': account.name,
                    'balance': acc_balance,
                    'balance_display': f"₹{acc_balance:,.2f}"
                })
        
        # ===== BY CURRENCY BREAKDOWN =====
        # Get default currency (INR) for the company
        currency_breakdown = {}
        try:
            # Try to get INR as the default company currency
            try:
                default_currency = Currency.objects.get(code='INR')
            except Currency.DoesNotExist:
                # If INR doesn't exist, get from entity or create default
                default_currency = entity.currency if hasattr(entity, 'currency') and entity.currency else None
                if not default_currency:
                    default_currency = Currency.objects.first()
            
            if default_currency:
                total_balance = Decimal('0')
                for entry in LedgerEntry.objects.filter(
                    entity=entity,
                    account__in=cash_accounts,
                    entry_date__lte=today
                ):
                    if entry.entry_type == 'DEBIT':
                        total_balance += entry.amount
                    else:
                        total_balance -= entry.amount
                
                currency_breakdown[default_currency.code] = {
                    'code': default_currency.code,
                    'name': default_currency.name,
                    'symbol': '₹' if default_currency.code == 'INR' else (default_currency.symbol or default_currency.code),
                    'balance': total_balance
                }
        except:
            # Fallback if currency data not available
            pass
        
        # ===== UPCOMING MOVEMENTS (NEXT 7 DAYS) =====
        upcoming_threshold = today + timedelta(days=7)
        
        upcoming_invoices = Invoice.objects.filter(
            entity=entity,
            due_date__gt=today,
            due_date__lte=upcoming_threshold,
            status__in=['OPEN', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        upcoming_bills = Bill.objects.filter(
            entity=entity,
            due_date__gt=today,
            due_date__lte=upcoming_threshold,
            status__in=['OPEN', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        upcoming_scheduled = PaymentSchedule.objects.filter(
            entity=entity,
            scheduled_date__gt=today,
            scheduled_date__lte=upcoming_threshold,
            status__in=['SCHEDULED', 'APPROVED']
        ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0')
        
        # ===== OPERATIONAL DECISION-MAKING =====
        # A. Payment Release Feasibility
        pending_payments = PaymentSchedule.objects.filter(
            entity=entity,
            status='APPROVED',
            scheduled_date__lte=today + timedelta(days=1)
        ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0')
        
        can_release_payments = forecast_position >= pending_payments
        payment_shortfall = max(Decimal('0'), pending_payments - forecast_position)
        
        # B. Fund Transfer Recommendations
        # Check if there's excess cash in operating vs investment accounts
        operating_accounts = Account.objects.filter(
            entity=entity,
            account_number__startswith='100'  # Current assets
        )
        
        investment_accounts = Account.objects.filter(
            entity=entity,
            account_number__startswith='110'  # Investments
        )
        
        operating_balance = Decimal('0')
        for account in operating_accounts:
            entries = LedgerEntry.objects.filter(account=account, entry_date__lte=today)
            for entry in entries:
                if entry.entry_type == 'DEBIT':
                    operating_balance += entry.amount
                else:
                    operating_balance -= entry.amount
        
        investment_balance = Decimal('0')
        for account in investment_accounts:
            entries = LedgerEntry.objects.filter(account=account, entry_date__lte=today)
            for entry in entries:
                if entry.entry_type == 'DEBIT':
                    investment_balance += entry.amount
                else:
                    investment_balance -= entry.amount
        
        # Minimum operating balance threshold (3 days of avg expenses)
        avg_daily_expense = vendor_bills_due / 1 if vendor_bills_due > 0 else Decimal('10000')
        min_operating_balance = avg_daily_expense * Decimal('3')
        
        excess_operating_cash = max(Decimal('0'), operating_balance - min_operating_balance)
        transfer_to_investment = excess_operating_cash * Decimal('0.5')  # Move 50% of excess
        
        fund_transfer_recommended = transfer_to_investment > Decimal('0')
        
        # C. Borrowing/Repayment Decision Indicators
        # Get any outstanding loans (mock - you might need real loan accounts)
        borrow_recommended = forecast_position < (opening_balance * Decimal('0.1'))  # Below 10% of opening
        repay_recommended = forecast_position > (opening_balance * Decimal('0.5'))   # Above 50% of opening
        
        # D. Payroll Coverage Check
        # Estimate monthly payroll (mock - adjust based on your data)
        estimated_monthly_payroll = opening_balance * Decimal('0.15')  # 15% of opening balance
        estimated_daily_payroll = estimated_monthly_payroll / Decimal('30')
        
        payroll_coverage_days = (forecast_position / estimated_daily_payroll).to_integral_value() if estimated_daily_payroll > 0 else Decimal('0')
        can_cover_payroll = payroll_coverage_days >= Decimal('3')  # At least 3 days
        
        # ===== CASH FORECASTING & LIQUIDITY PLANNING =====
        # 7-DAY FORECAST
        forecast_7day_threshold = today + timedelta(days=7)
        
        invoices_7day = Invoice.objects.filter(
            entity=entity,
            due_date__lte=forecast_7day_threshold,
            due_date__gt=today,
            status__in=['OPEN', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        bills_7day = Bill.objects.filter(
            entity=entity,
            due_date__lte=forecast_7day_threshold,
            due_date__gt=today,
            status__in=['OPEN', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        scheduled_7day = PaymentSchedule.objects.filter(
            entity=entity,
            scheduled_date__lte=forecast_7day_threshold,
            scheduled_date__gt=today,
            status__in=['SCHEDULED', 'APPROVED']
        ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0')
        
        forecast_7day_inflow = invoices_7day
        forecast_7day_outflow = bills_7day + scheduled_7day
        forecast_7day_position = forecast_position + forecast_7day_inflow - forecast_7day_outflow
        
        # 30-DAY FORECAST
        forecast_30day_threshold = today + timedelta(days=30)
        
        invoices_30day = Invoice.objects.filter(
            entity=entity,
            due_date__lte=forecast_30day_threshold,
            due_date__gt=today,
            status__in=['OPEN', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        bills_30day = Bill.objects.filter(
            entity=entity,
            due_date__lte=forecast_30day_threshold,
            due_date__gt=today,
            status__in=['OPEN', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        scheduled_30day = PaymentSchedule.objects.filter(
            entity=entity,
            scheduled_date__lte=forecast_30day_threshold,
            scheduled_date__gt=today,
            status__in=['SCHEDULED', 'APPROVED']
        ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0')
        
        forecast_30day_inflow = invoices_30day
        forecast_30day_outflow = bills_30day + scheduled_30day
        forecast_30day_position = forecast_position + forecast_30day_inflow - forecast_30day_outflow
        
        # ===== COMPLIANCE & INTERNAL CONTROLS =====
        compliance_checks = {
            'no_negative_balance': current_balance >= 0,
            'adequate_operating_cash': operating_balance >= min_operating_balance,
            'payroll_coverage': can_cover_payroll,
            'approved_payments_scheduled': pending_payments <= forecast_position,
            'forecast_positive': forecast_position >= 0,
            'diversified_accounts': len(account_breakdown) > 1,
        }
        
        compliance_score = sum(1 for v in compliance_checks.values() if v) * 100 // len(compliance_checks)
        
        # ===== AUTOMATION & WORKFLOW TRIGGERS =====
        automation_actions = []
        
        if can_release_payments:
            automation_actions.append({
                'action': 'APPROVE_PAYMENTS',
                'title': 'Release Approved Payments',
                'description': f'₹{pending_payments:,.2f} in approved payments can be released',
                'icon': '✓',
                'color': 'green'
            })
        else:
            automation_actions.append({
                'action': 'DELAY_PAYMENTS',
                'title': 'Hold Payments',
                'description': f'Insufficient cash (shortfall: ₹{payment_shortfall:,.2f})',
                'icon': '⏸',
                'color': 'orange'
            })
        
        if fund_transfer_recommended:
            automation_actions.append({
                'action': 'TRANSFER_FUNDS',
                'title': 'Transfer Excess Cash',
                'description': f'Move ₹{transfer_to_investment:,.2f} to investment account',
                'icon': '↗',
                'color': 'blue'
            })
        
        if borrow_recommended:
            automation_actions.append({
                'action': 'DRAW_CREDIT',
                'title': 'Consider Credit Line Draw',
                'description': 'Cash position below safe threshold - consider drawing from credit line',
                'icon': '⚠',
                'color': 'red'
            })
        elif repay_recommended:
            automation_actions.append({
                'action': 'REPAY_LOANS',
                'title': 'Repay Short-term Loans',
                'description': 'Cash position strong - consider repaying short-term loans',
                'icon': '→',
                'color': 'green'
            })
        
        if forecast_7day_position < Decimal('0'):
            automation_actions.append({
                'action': 'ALERT_7DAY',
                'title': '⚠ 7-Day Negative Forecast',
                'description': f'Projected deficit in 7 days: ₹{abs(forecast_7day_position):,.2f}',
                'icon': '⚠',
                'color': 'red'
            })
        
        # ===== DAILY TREASURY WORKFLOW CHECKLIST =====
        treasury_checklist = [
            {
                'item': 'Check Opening Cash Position',
                'status': 'completed' if current_balance >= 0 else 'attention',
                'value': f"₹{current_balance:,.2f}"
            },
            {
                'item': 'Review Expected Inflows/Outflows',
                'status': 'completed' if forecast_position >= 0 else 'attention',
                'inflows': f"₹{customer_invoices_due:,.2f}",
                'outflows': f"₹{vendor_bills_due + scheduled_today:,.2f}"
            },
            {
                'item': 'Decide Payment Releases',
                'status': 'completed' if can_release_payments else 'attention',
                'value': f"₹{pending_payments:,.2f}" if pending_payments > 0 else 'No pending'
            },
            {
                'item': 'Fund Transfer Assessment',
                'status': 'completed' if fund_transfer_recommended else 'completed',
                'value': f"Transfer ₹{transfer_to_investment:,.2f}" if transfer_to_investment > 0 else 'No action needed'
            },
            {
                'item': 'Liquidity Forecast Check',
                'status': 'attention' if forecast_7day_position < 0 else 'completed',
                '7day': f"₹{forecast_7day_position:,.2f}",
                '30day': f"₹{forecast_30day_position:,.2f}"
            },
            {
                'item': 'Payroll Coverage Verification',
                'status': 'completed' if can_cover_payroll else 'attention',
                'coverage_days': f"{payroll_coverage_days} days"
            },
            {
                'item': 'Compliance Review',
                'status': 'completed' if compliance_score >= 80 else 'attention',
                'score': f"{compliance_score}%"
            },
            {
                'item': 'Monitor Intraday Statements',
                'status': 'pending',
                'accounts': len(account_breakdown)
            }
        ]
        
        # ===== CONTEXT DATA =====
        context.update({
            'entity': entity,
            'today': today,
            'opening_balance': opening_balance,
            'opening_balance_display': f"₹{opening_balance:,.2f}",
            
            'actual_receipts': actual_receipts,
            'actual_receipts_display': f"₹{actual_receipts:,.2f}",
            
            'actual_payments': actual_payments,
            'actual_payments_display': f"₹{actual_payments:,.2f}",
            
            'current_balance': current_balance,
            'current_balance_display': f"₹{current_balance:,.2f}",
            'current_balance_positive': current_balance >= 0,
            
            'expected_receipts_today': customer_invoices_due,
            'expected_receipts_today_display': f"₹{customer_invoices_due:,.2f}",
            
            'expected_payments_today': vendor_bills_due + scheduled_today,
            'expected_payments_today_display': f"₹{vendor_bills_due + scheduled_today:,.2f}",
            
            'forecast_position': forecast_position,
            'forecast_position_display': f"₹{forecast_position:,.2f}",
            'forecast_position_positive': forecast_position >= 0,
            
            'liquidity_status': liquidity_status,
            'status_color': status_color,
            
            'account_breakdown': account_breakdown,
            'currency_breakdown': list(currency_breakdown.values()),
            
            'upcoming_invoices': upcoming_invoices,
            'upcoming_invoices_display': f"₹{upcoming_invoices:,.2f}",
            
            'upcoming_bills': upcoming_bills,
            'upcoming_bills_display': f"₹{upcoming_bills:,.2f}",
            
            'upcoming_scheduled': upcoming_scheduled,
            'upcoming_scheduled_display': f"₹{upcoming_scheduled:,.2f}",
            
            # Operational Decision-Making
            'pending_payments': pending_payments,
            'pending_payments_display': f"₹{pending_payments:,.2f}",
            'can_release_payments': can_release_payments,
            'payment_shortfall': payment_shortfall,
            'payment_shortfall_display': f"₹{payment_shortfall:,.2f}",
            
            'operating_balance': operating_balance,
            'operating_balance_display': f"₹{operating_balance:,.2f}",
            'investment_balance': investment_balance,
            'investment_balance_display': f"₹{investment_balance:,.2f}",
            'min_operating_balance': min_operating_balance,
            'min_operating_balance_display': f"₹{min_operating_balance:,.2f}",
            'excess_operating_cash': excess_operating_cash,
            'excess_operating_cash_display': f"₹{excess_operating_cash:,.2f}",
            'transfer_to_investment': transfer_to_investment,
            'transfer_to_investment_display': f"₹{transfer_to_investment:,.2f}",
            'fund_transfer_recommended': fund_transfer_recommended,
            
            'borrow_recommended': borrow_recommended,
            'repay_recommended': repay_recommended,
            
            'payroll_coverage_days': payroll_coverage_days,
            'can_cover_payroll': can_cover_payroll,
            'estimated_daily_payroll': estimated_daily_payroll,
            'estimated_daily_payroll_display': f"₹{estimated_daily_payroll:,.2f}",
            
            # Cash Forecasting
            'forecast_7day_inflow': forecast_7day_inflow,
            'forecast_7day_inflow_display': f"₹{forecast_7day_inflow:,.2f}",
            'forecast_7day_outflow': forecast_7day_outflow,
            'forecast_7day_outflow_display': f"₹{forecast_7day_outflow:,.2f}",
            'forecast_7day_position': forecast_7day_position,
            'forecast_7day_position_display': f"₹{forecast_7day_position:,.2f}",
            'forecast_7day_positive': forecast_7day_position >= 0,
            
            'forecast_30day_inflow': forecast_30day_inflow,
            'forecast_30day_inflow_display': f"₹{forecast_30day_inflow:,.2f}",
            'forecast_30day_outflow': forecast_30day_outflow,
            'forecast_30day_outflow_display': f"₹{forecast_30day_outflow:,.2f}",
            'forecast_30day_position': forecast_30day_position,
            'forecast_30day_position_display': f"₹{forecast_30day_position:,.2f}",
            'forecast_30day_positive': forecast_30day_position >= 0,
            
            # Compliance & Controls
            'compliance_checks': compliance_checks,
            'compliance_score': compliance_score,
            
            # Automation & Workflow Triggers
            'automation_actions': automation_actions,
            
            # Daily Treasury Workflow
            'treasury_checklist': treasury_checklist,
        })
        
        return context


class LiquidityForecastListView(LoginRequiredMixin, ListView):
    """List liquidity forecasts."""
    model = LiquidityForecast
    template_name = 'cash_management/liquidityforecast_list.html'
    context_object_name = 'forecasts'
    paginate_by = 20
    
    def get_queryset(self):
        return LiquidityForecast.objects.order_by('-forecast_start_date')


class LiquidityForecastDetailView(LoginRequiredMixin, DetailView):
    """Detail view for liquidity forecast."""
    model = LiquidityForecast
    template_name = 'cash_management/liquidityforecast_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forecast_lines'] = self.object.lines.all().order_by('forecast_date')
        return context


class TreasuryAccountListView(LoginRequiredMixin, ListView):
    """List treasury accounts."""
    model = TreasuryAccount
    template_name = 'cash_management/treasuryaccount_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return TreasuryAccount.objects.filter(is_active=True).order_by('account_code')


class TreasuryAccountDetailView(LoginRequiredMixin, DetailView):
    """Detail view for treasury account."""
    model = TreasuryAccount
    template_name = 'cash_management/treasuryaccount_detail.html'


class FXExposureListView(LoginRequiredMixin, ListView):
    """List FX exposures."""
    model = FXExposure
    template_name = 'cash_management/fxexposure_list.html'
    context_object_name = 'exposures'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = FXExposure.objects.select_related(
            'home_currency', 'foreign_currency'
        ).order_by('-exposure_date')
        hedged = self.request.GET.get('hedged')
        if hedged:
            queryset = queryset.filter(is_hedged=hedged == 'true')
        return queryset


class FXExposureDetailView(LoginRequiredMixin, DetailView):
    """Detail view for FX exposure."""
    model = FXExposure
    template_name = 'cash_management/fxexposure_detail.html'


# CREATE VIEWS
class PaymentScheduleCreateView(LoginRequiredMixin, CreateView):
    """Create payment schedule."""
    model = PaymentSchedule
    form_class = PaymentScheduleForm
    template_name = 'cash_management/paymentschedule_form.html'
    success_url = reverse_lazy('cash_management:payment_list')
    
    def form_valid(self, form):
        # Ensure entity is set - it can be set explicitly or derived from from_account
        if not form.cleaned_data.get('entity') and form.cleaned_data.get('from_account'):
            # Auto-set entity from the selected bank account
            from_account = form.cleaned_data.get('from_account')
            form.instance.entity = from_account.entity
        
        messages.success(self.request, 'Payment schedule created successfully.')
        return super().form_valid(form)


class PaymentScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Update payment schedule."""
    model = PaymentSchedule
    form_class = PaymentScheduleForm
    template_name = 'cash_management/paymentschedule_form.html'
    success_url = reverse_lazy('cash_management:payment_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Payment schedule updated successfully.')
        return super().form_valid(form)


class CashPositionCreateView(LoginRequiredMixin, CreateView):
    """Create cash position."""
    model = CashPosition
    form_class = CashPositionForm
    template_name = 'cash_management/cashposition_form.html'
    success_url = reverse_lazy('cash_management:position_list')
    
    def form_valid(self, form):
        # Ensure entity is set - it can be set explicitly or derived from bank_account
        if not form.cleaned_data.get('entity') and form.cleaned_data.get('bank_account'):
            # Auto-set entity from the selected bank account
            bank_account = form.cleaned_data.get('bank_account')
            form.instance.entity = bank_account.entity
        
        messages.success(self.request, 'Cash position created successfully.')
        return super().form_valid(form)


class CashPositionUpdateView(LoginRequiredMixin, UpdateView):
    """Update cash position."""
    model = CashPosition
    form_class = CashPositionForm
    template_name = 'cash_management/cashposition_form.html'
    success_url = reverse_lazy('cash_management:position_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cash position updated successfully.')
        return super().form_valid(form)


class LiquidityForecastCreateView(LoginRequiredMixin, CreateView):
    """Create liquidity forecast."""
    model = LiquidityForecast
    form_class = LiquidityForecastForm
    template_name = 'cash_management/liquidityforecast_form.html'
    success_url = reverse_lazy('cash_management:forecast_list')
    
    def form_valid(self, form):
        # Ensure entity is set - must be explicitly selected by user
        if not form.cleaned_data.get('entity'):
            # Entity is required, form validation should prevent this
            # but this ensures the entity is properly set if provided
            pass
        
        messages.success(self.request, 'Liquidity forecast created successfully.')
        return super().form_valid(form)


class LiquidityForecastUpdateView(LoginRequiredMixin, UpdateView):
    """Update liquidity forecast."""
    model = LiquidityForecast
    form_class = LiquidityForecastForm
    template_name = 'cash_management/liquidityforecast_form.html'
    success_url = reverse_lazy('cash_management:forecast_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Liquidity forecast updated successfully.')
        return super().form_valid(form)


class TreasuryAccountCreateView(LoginRequiredMixin, CreateView):
    """Create treasury account."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm
    template_name = 'cash_management/treasuryaccount_form.html'
    success_url = reverse_lazy('cash_management:treasury_list')
    
    def form_valid(self, form):
        # Ensure entity is set - must be explicitly selected by user
        if not form.cleaned_data.get('entity'):
            # Entity is required, form validation should prevent this
            # but this ensures the entity is properly set if provided
            pass
        
        messages.success(self.request, 'Treasury account created successfully.')
        return super().form_valid(form)


class TreasuryAccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update treasury account."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm
    template_name = 'cash_management/treasuryaccount_form.html'
    success_url = reverse_lazy('cash_management:treasury_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Treasury account updated successfully.')
        return super().form_valid(form)


class FXExposureCreateView(LoginRequiredMixin, CreateView):
    """Create FX exposure."""
    model = FXExposure
    form_class = FXExposureForm
    template_name = 'cash_management/fxexposure_form.html'
    success_url = reverse_lazy('cash_management:fx_list')
    
    def form_valid(self, form):
        # Ensure entity is set - must be explicitly selected by user
        if not form.cleaned_data.get('entity'):
            # Entity is required, form validation should prevent this
            # but this ensures the entity is properly set if provided
            pass
        
        messages.success(self.request, 'FX exposure created successfully.')
        return super().form_valid(form)


class FXExposureUpdateView(LoginRequiredMixin, UpdateView):
    """Update FX exposure."""
    model = FXExposure
    form_class = FXExposureForm
    template_name = 'cash_management/fxexposure_form.html'
    success_url = reverse_lazy('cash_management:fx_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'FX exposure updated successfully.')
        return super().form_valid(form)


# API Endpoints
@require_GET
@csrf_exempt
def bank_account_currency(request, bank_account_id):
    """API endpoint to get currency for a bank account."""
    try:
        bank_account = BankProfile.objects.select_related('currency').get(pk=bank_account_id)
        return JsonResponse({
            'currency_id': bank_account.currency.id,
            'currency_code': bank_account.currency.code,
            'currency_symbol': bank_account.currency.symbol,
        })
    except BankProfile.DoesNotExist:
        return JsonResponse({'error': 'Bank account not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    def form_valid(self, form):
        messages.success(self.request, 'FX exposure updated successfully.')
        return super().form_valid(form)
