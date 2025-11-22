from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models, transaction
from django.urls import reverse_lazy
from django.contrib import messages
from decimal import Decimal
from .models import (
    Entity, Account, LedgerEntry, TrialBalance, ProfitLossReport, BalanceSheet,
    CashFlowForecast, CashTransaction, BankStatement, BankProfile, Customer, Vendor,
    VendorInvoice, VendorPayment, FixedAsset, AuditLog, Currency,
    ReconciliationEntry, ReconciliationRecord, ReconciliationMatch,
    TaxRate, TaxTransaction, TaxSummary,
    DeferredExpense, DeferredRevenue, PeriodLock
)
from .forms import DoubleEntryJournalForm, SimpleLedgerEntryForm


class PermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to check if user has add permission for a specific model."""
    permission_codename = None
    
    def test_func(self):
        """Check if user has permission to add the model."""
        if not self.permission_codename:
            return True
        return self.request.user.has_perm(f'accounting.add_{self.permission_codename}')
    
    def handle_no_permission(self):
        """Redirect if user doesn't have permission."""
        messages.error(self.request, 'You do not have permission to add this item.')
        return redirect('accounting:dashboard')


class DashboardView(LoginRequiredMixin, TemplateView):
    """General Ledger Dashboard - overview of accounting data."""
    template_name = 'accounting/dashboard_new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get primary entity (first active entity)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            context['total_accounts'] = entity.accounts.count()
            context['total_customers'] = entity.customers.count()
            context['total_vendors'] = entity.vendors.count()
            context['recent_ledger_entries'] = entity.ledger_entries.order_by('-entry_date')[:10]
            context['recent_invoices'] = entity.vendor_invoices.order_by('-invoice_date')[:5]
            context['recent_trial_balances'] = entity.trial_balances.order_by('-as_of_date')[:3]
            context['recent_audit_logs'] = entity.audit_logs.order_by('-timestamp')[:10]
            
            # Shareholder module statistics
            from accounting.models import Stakeholder, CapitalContribution, Shareholding
            context['total_stakeholders'] = Stakeholder.objects.filter(entity=entity).count()
            context['total_contributions'] = CapitalContribution.objects.filter(entity=entity).count()
            context['total_shareholdings'] = Shareholding.objects.filter(entity=entity).count()
            
            # HR module statistics
            try:
                from hr.models import Employee, Payroll, LeaveRequest
                context['total_employees'] = Employee.objects.filter(entity=entity, status='ACTIVE').count()
                context['employees_on_leave'] = Employee.objects.filter(entity=entity, status='ON_LEAVE').count()
                context['pending_payrolls'] = Payroll.objects.filter(entity=entity, status='DRAFT').count()
                context['pending_leave_requests'] = LeaveRequest.objects.filter(
                    employee__entity=entity,
                    status='SUBMITTED'
                ).count()
            except:
                # HR module not available or not configured
                context['total_employees'] = 0
                context['employees_on_leave'] = 0
                context['pending_payrolls'] = 0
                context['pending_leave_requests'] = 0
            
            # Chart data: Account Type Distribution
            account_types = entity.accounts.values('account_type').annotate(count=models.Count('id'))
            account_type_labels = [at['account_type'] for at in account_types]
            account_type_counts = [at['count'] for at in account_types]
            context['account_type_labels'] = account_type_labels
            context['account_type_counts'] = account_type_counts
            
            # Chart data: Debit vs Credit by Month (last 6 months)
            from django.utils import timezone
            from datetime import timedelta
            import json
            from calendar import monthrange
            
            # Get current date and calculate 6 months back
            end_date = timezone.now().date()
            current_year = end_date.year
            current_month = end_date.month
            
            # Calculate start month (6 months ago)
            start_month = current_month - 5
            start_year = current_year
            if start_month < 1:
                start_month += 12
                start_year -= 1
            
            # Create monthly entries for the last 6 months
            monthly_data = {}
            
            year = start_year
            month = start_month
            for _ in range(6):
                month_key = f'{year:04d}-{month:02d}'
                monthly_data[month_key] = {'debits': 0, 'credits': 0}
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            
            # Calculate the actual start date
            start_date = timezone.datetime(start_year, start_month, 1).date()
            
            # Aggregate debit/credit amounts by month
            entries = entity.ledger_entries.filter(entry_date__gte=start_date, entry_date__lte=end_date)
            for entry in entries:
                month_key = entry.entry_date.strftime('%Y-%m')
                if month_key in monthly_data:
                    if entry.entry_type == 'DEBIT':
                        monthly_data[month_key]['debits'] += float(entry.amount)
                    else:
                        monthly_data[month_key]['credits'] += float(entry.amount)
            
            # Sort by month and extract data
            sorted_months = sorted(monthly_data.keys())
            context['chart_months'] = sorted_months
            context['chart_debits'] = [int(monthly_data[m]['debits']) for m in sorted_months]
            context['chart_credits'] = [int(monthly_data[m]['credits']) for m in sorted_months]
            
            # Chart data: Customer and Vendor counts by month (created_at)
            monthly_customers = {}
            monthly_vendors = {}
            
            for month_key in sorted_months:
                year, month = month_key.split('-')
                customers = entity.customers.filter(
                    created_at__year=int(year),
                    created_at__month=int(month)
                ).count()
                vendors = entity.vendors.filter(
                    created_at__year=int(year),
                    created_at__month=int(month)
                ).count()
                monthly_customers[month_key] = customers
                monthly_vendors[month_key] = vendors
            
            context['chart_customers'] = [monthly_customers.get(m, 0) for m in sorted_months]
            context['chart_vendors'] = [monthly_vendors.get(m, 0) for m in sorted_months]
            
            # Sales by Country data
            from sales.models import SalesOrder, Customer
            from django.db.models import Sum
            
            # Define target countries
            target_countries = ['India', 'Oman', 'UAE', 'KSA', 'Canada']
            country_sales = []
            
            # Calculate total sales to get percentages
            total_sales = SalesOrder.objects.filter(
                entity=entity,
                status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'INVOICED']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            for country in target_countries:
                # Get sales for this country
                sales_amount = SalesOrder.objects.filter(
                    entity=entity,
                    customer__country__iexact=country,
                    status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'INVOICED']
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
                
                # Calculate percentage
                if total_sales > 0:
                    percentage = int((sales_amount / total_sales) * 100)
                else:
                    percentage = 0
                
                country_sales.append({
                    'country': country,
                    'percentage': percentage,
                    'amount': float(sales_amount)
                })
            
            context['country_sales'] = country_sales
            
            # Sales by India State data
            india_states = [
                'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat',
                'Uttar Pradesh', 'West Bengal', 'Rajasthan', 'Kerala', 'Punjab'
            ]
            state_sales = []
            
            # Calculate total India sales to get percentages
            total_india_sales = SalesOrder.objects.filter(
                entity=entity,
                customer__country__iexact='India',
                status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'INVOICED']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            for state in india_states:
                # Get sales for this state
                sales_amount = SalesOrder.objects.filter(
                    entity=entity,
                    customer__country__iexact='India',
                    customer__state__iexact=state,
                    status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'INVOICED']
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
                
                # Calculate percentage
                if total_india_sales > 0:
                    percentage = int((sales_amount / total_india_sales) * 100)
                else:
                    percentage = 0
                
                state_sales.append({
                    'state': state,
                    'percentage': percentage,
                    'amount': float(sales_amount)
                })
            
            context['state_sales'] = state_sales
        else:
            # Provide default empty data if no entity
            context['total_stakeholders'] = 0
            context['total_contributions'] = 0
            context['total_shareholdings'] = 0
            context['total_employees'] = 0
            context['employees_on_leave'] = 0
            context['pending_payrolls'] = 0
            context['pending_leave_requests'] = 0
            context['account_type_labels'] = []
            context['account_type_counts'] = []
            context['chart_months'] = []
            context['chart_debits'] = []
            context['chart_credits'] = []
            context['chart_customers'] = []
            context['chart_vendors'] = []
            context['country_sales'] = []
            context['state_sales'] = []
        
        return context


class GLDashboardView(LoginRequiredMixin, TemplateView):
    """Detailed GL Dashboard with financial metrics."""
    template_name = 'accounting/gl_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            # Summary metrics - calculate total assets from debit balances
            asset_accounts = entity.accounts.filter(account_type='ASSET')
            total_assets = Decimal('0.00')
            for acc in asset_accounts:
                debits = acc.ledger_entries.filter(entry_type='DEBIT').aggregate(
                    total=models.Sum('amount')
                )['total'] or Decimal('0.00')
                credits = acc.ledger_entries.filter(entry_type='CREDIT').aggregate(
                    total=models.Sum('amount')
                )['total'] or Decimal('0.00')
                total_assets += (debits - credits)
            
            context['total_assets'] = total_assets
            
            context['latest_trial_balance'] = entity.trial_balances.order_by('-as_of_date').first()
            context['latest_pl_report'] = entity.pl_reports.order_by('-period_end').first()
            context['latest_balance_sheet'] = entity.balance_sheets.order_by('-as_of_date').first()
            context['accounts'] = entity.accounts.all()
        
        return context


class AccountListView(LoginRequiredMixin, ListView):
    """List all accounts."""
    model = Account
    template_name = 'accounting/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.accounts.all()
        return Account.objects.none()


class AccountDetailView(LoginRequiredMixin, DetailView):
    """Account detail view with ledger entries and running balance."""
    model = Account
    template_name = 'accounting/account_detail.html'
    context_object_name = 'account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all ledger entries for this account, ordered by date
        entries = self.object.ledger_entries.order_by('entry_date', 'created_at')
        
        # Calculate running balance (debit positive, credit negative for assets)
        running_balance = Decimal('0.00')
        entries_with_balance = []
        
        for entry in entries:
            if entry.entry_type == 'DEBIT':
                running_balance += entry.amount
            else:  # CREDIT
                running_balance -= entry.amount
            
            entries_with_balance.append({
                'entry': entry,
                'balance': running_balance
            })
        
        # Reverse to show most recent first
        entries_with_balance.reverse()
        
        # Calculate totals
        debits = entries.filter(entry_type='DEBIT').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        credits = entries.filter(entry_type='CREDIT').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        context['ledger_entries'] = entries_with_balance
        context['total_debits'] = debits
        context['total_credits'] = credits
        context['current_balance'] = running_balance
        context['entry_count'] = entries.count()
        
        return context


class LedgerEntryListView(LoginRequiredMixin, ListView):
    """List ledger entries."""
    model = LedgerEntry
    template_name = 'accounting/ledger_entry_list.html'
    context_object_name = 'entries'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.ledger_entries.order_by('-entry_date')
        return LedgerEntry.objects.none()


class TrialBalanceListView(LoginRequiredMixin, ListView):
    """List trial balances."""
    model = TrialBalance
    template_name = 'accounting/trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 20

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.trial_balances.order_by('-as_of_date')
        return TrialBalance.objects.none()


class ProfitLossListView(LoginRequiredMixin, ListView):
    """List P&L reports."""
    model = ProfitLossReport
    template_name = 'accounting/profit_loss_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.pl_reports.order_by('-period_end')
        return ProfitLossReport.objects.none()


class BalanceSheetListView(LoginRequiredMixin, ListView):
    """List balance sheets."""
    model = BalanceSheet
    template_name = 'accounting/balance_sheet_list.html'
    context_object_name = 'balance_sheets'
    paginate_by = 20

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.balance_sheets.order_by('-as_of_date')
        return BalanceSheet.objects.none()


class CustomerListView(LoginRequiredMixin, ListView):
    """List customers."""
    model = Customer
    template_name = 'accounting/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.customers.all()
        return Customer.objects.none()


class VendorListView(LoginRequiredMixin, ListView):
    """List vendors."""
    model = Vendor
    template_name = 'accounting/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.vendors.all()
        return Vendor.objects.none()


class VendorInvoiceListView(LoginRequiredMixin, ListView):
    """List vendor invoices."""
    model = VendorInvoice
    template_name = 'accounting/vendor_invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.vendor_invoices.order_by('-invoice_date')
        return VendorInvoice.objects.none()


class VendorInvoiceDetailView(LoginRequiredMixin, DetailView):
    """Vendor invoice detail view."""
    model = VendorInvoice
    template_name = 'accounting/vendor_invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        return context


class VendorInvoiceUpdateView(LoginRequiredMixin, FormView):
    """Update vendor invoice."""
    from .forms import QuickAddVendorInvoiceForm
    form_class = QuickAddVendorInvoiceForm
    template_name = 'accounting/vendor_invoice_form.html'

    def get_object(self):
        return get_object_or_404(VendorInvoice, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        kwargs['instance'] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = self.get_object()
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        invoice = self.get_object()
        
        if invoice.status not in ['DRAFT', 'SUBMITTED']:
            messages.error(self.request, 'Cannot edit invoice in current status.')
            return redirect('accounting:vendor_invoice_detail', pk=invoice.pk)
        
        try:
            updated_invoice = form.save(commit=False)
            updated_invoice.entity = entity
            updated_invoice.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='UPDATE',
                model_name='VendorInvoice',
                object_id=str(updated_invoice.id),
                description=f'Updated invoice: {updated_invoice.invoice_number}'
            )
            
            messages.success(self.request, f'Vendor invoice {updated_invoice.invoice_number} updated successfully.')
            return redirect('accounting:vendor_invoice_detail', pk=updated_invoice.pk)
        except Exception as e:
            messages.error(self.request, f'Error updating invoice: {str(e)}')
            return self.form_invalid(form)


class RecordVendorPaymentView(LoginRequiredMixin, FormView):
    """Record payment for vendor invoice."""
    from .forms import QuickAddVendorPaymentForm
    form_class = QuickAddVendorPaymentForm
    template_name = 'accounting/record_vendor_payment.html'

    def get_invoice(self):
        return get_object_or_404(VendorInvoice, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        kwargs['initial'] = {'vendor_invoice': self.get_invoice()}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = self.get_invoice()
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        invoice = self.get_invoice()
        
        try:
            payment = form.save(commit=False)
            payment.entity = entity
            payment.vendor_invoice = invoice
            payment.save()
            
            # Check if invoice is fully paid
            if invoice.outstanding_amount <= 0:
                invoice.status = 'PAID'
                invoice.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='VendorPayment',
                object_id=str(payment.id),
                description=f'Recorded payment of ${payment.amount} for invoice {invoice.invoice_number}'
            )
            
            messages.success(self.request, f'Payment of ${payment.amount} recorded successfully.')
            return redirect('accounting:vendor_invoice_detail', pk=invoice.pk)
        except Exception as e:
            messages.error(self.request, f'Error recording payment: {str(e)}')
            return self.form_invalid(form)


class VendorInvoiceStatusUpdateView(LoginRequiredMixin, FormView):
    """Update vendor invoice status."""
    
    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(VendorInvoice, pk=kwargs['pk'])
        new_status = request.POST.get('status')
        entity = Entity.objects.filter(is_active=True).first()
        
        valid_transitions = {
            'DRAFT': ['SUBMITTED', 'CANCELLED'],
            'SUBMITTED': ['APPROVED', 'DRAFT', 'CANCELLED'],
            'APPROVED': ['CANCELLED'],
        }
        
        current_status = invoice.status
        
        if new_status not in valid_transitions.get(current_status, []):
            messages.error(request, f'Cannot change status from {current_status} to {new_status}.')
            return redirect('accounting:vendor_invoice_detail', pk=invoice.pk)
        
        try:
            old_status = invoice.status
            invoice.status = new_status
            invoice.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(request.user),
                action='UPDATE',
                model_name='VendorInvoice',
                object_id=str(invoice.id),
                description=f'Changed status from {old_status} to {new_status} for invoice {invoice.invoice_number}'
            )
            
            messages.success(request, f'Invoice status updated to {new_status}.')
        except Exception as e:
            messages.error(request, f'Error updating status: {str(e)}')
        
        return redirect('accounting:vendor_invoice_detail', pk=invoice.pk)


class FixedAssetListView(LoginRequiredMixin, ListView):
    """List fixed assets."""
    model = FixedAsset
    template_name = 'accounting/fixed_asset_list.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.fixed_assets.all()
        return FixedAsset.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = self.get_queryset()
        
        # Calculate totals
        total_gross_value = sum(asset.purchase_cost for asset in assets)
        total_accumulated_depreciation = sum(asset.accumulated_depreciation for asset in assets)
        total_net_book_value = sum(asset.book_value for asset in assets)
        
        context['total_gross_value'] = total_gross_value
        context['total_accumulated_depreciation'] = total_accumulated_depreciation
        context['total_net_book_value'] = total_net_book_value
        
        return context


class AuditLogListView(LoginRequiredMixin, ListView):
    """List audit logs."""
    model = AuditLog
    template_name = 'accounting/audit_log_list.html'
    context_object_name = 'logs'
    paginate_by = 100

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.audit_logs.order_by('-timestamp')
        return AuditLog.objects.none()


class DoubleEntryJournalView(LoginRequiredMixin, FormView):
    """Create double-entry journal entries (Debit and Credit simultaneously)."""
    template_name = 'accounting/journal_entry_create.html'
    form_class = DoubleEntryJournalForm
    success_url = reverse_lazy('accounting:dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            messages.error(self.request, 'No active entity found. Please create one in the admin panel.')
            return redirect('accounting:dashboard')
        
        try:
            with transaction.atomic():
                # Create debit entry
                debit_entry = LedgerEntry.objects.create(
                    entity=entity,
                    account=form.cleaned_data['debit_account'],
                    entry_type='DEBIT',
                    amount=form.cleaned_data['debit_amount'],
                    entry_date=form.cleaned_data['entry_date'],
                    description=form.cleaned_data['description'],
                    reference_number=form.cleaned_data['reference_number'],
                    is_posted=form.cleaned_data['is_posted']
                )
                
                # Create credit entry
                credit_entry = LedgerEntry.objects.create(
                    entity=entity,
                    account=form.cleaned_data['credit_account'],
                    entry_type='CREDIT',
                    amount=form.cleaned_data['credit_amount'],
                    entry_date=form.cleaned_data['entry_date'],
                    description=form.cleaned_data['description'],
                    reference_number=form.cleaned_data['reference_number'],
                    is_posted=form.cleaned_data['is_posted']
                )
                
                # Create audit log
                AuditLog.objects.create(
                    entity=entity,
                    entity_type='LedgerEntry',
                    action='CREATE',
                    reference_id=debit_entry.id,
                    user=self.request.user,
                    old_values={},
                    new_values={
                        'debit_account': form.cleaned_data['debit_account'].name,
                        'debit_amount': str(form.cleaned_data['debit_amount']),
                        'credit_account': form.cleaned_data['credit_account'].name,
                        'credit_amount': str(form.cleaned_data['credit_amount']),
                        'description': form.cleaned_data['description'],
                    }
                )
                
                messages.success(
                    self.request,
                    f'Journal entry created successfully. Debit: {form.cleaned_data["debit_amount"]} | Credit: {form.cleaned_data["credit_amount"]}'
                )
        except Exception as e:
            messages.error(self.request, f'Error creating journal entry: {str(e)}')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


class LedgerEntryCreateView(LoginRequiredMixin, FormView):
    """Create individual ledger entries (simple form)."""
    template_name = 'accounting/ledger_entry_form.html'
    form_class = SimpleLedgerEntryForm
    success_url = reverse_lazy('accounting:dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            messages.error(self.request, 'No active entity found.')
            return redirect('accounting:dashboard')
        
        try:
            entry = form.save(commit=False)
            entry.entity = entity
            entry.save()
            
            # Create audit log
            AuditLog.objects.create(
                entity=entity,
                entity_type='LedgerEntry',
                action='CREATE',
                reference_id=entry.id,
                user=self.request.user,
                old_values={},
                new_values={
                    'account': entry.account.name,
                    'entry_type': entry.entry_type,
                    'amount': str(entry.amount),
                    'description': entry.description,
                }
            )
            
            messages.success(self.request, 'Ledger entry created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating ledger entry: {str(e)}')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ VENDOR PAYMENTS ============
class VendorPaymentListView(LoginRequiredMixin, ListView):
    """List vendor payments."""
    from .models import VendorPayment
    model = VendorPayment
    template_name = 'accounting/vendor_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.vendor_payments.order_by('-payment_date')
        return VendorPayment.objects.none()


# ============ BANK PROFILES ============
class BankProfileListView(LoginRequiredMixin, ListView):
    """List bank profiles."""
    model = BankProfile
    template_name = 'accounting/bank_profile_list.html'
    context_object_name = 'profiles'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.bank_profiles.all()
        return BankProfile.objects.none()


# ============ BANK STATEMENTS ============
class BankStatementListView(LoginRequiredMixin, ListView):
    """List bank statements."""
    model = BankStatement
    template_name = 'accounting/bank_statement_list.html'
    context_object_name = 'statements'
    paginate_by = 50

    def get_queryset(self):
        return BankStatement.objects.order_by('-statement_date')


# ============ CASH TRANSACTIONS ============
class CashTransactionListView(LoginRequiredMixin, ListView):
    """List cash transactions."""
    model = CashTransaction
    template_name = 'accounting/cash_transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.cash_transactions.order_by('-transaction_date')
        return CashTransaction.objects.none()


# ============ CASH FLOW FORECAST ============
class CashFlowForecastListView(LoginRequiredMixin, ListView):
    """List cash flow forecasts."""
    model = CashFlowForecast
    template_name = 'accounting/cash_flow_forecast_list.html'
    context_object_name = 'forecasts'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.cash_flow_forecasts.order_by('-created_at')
        return CashFlowForecast.objects.none()


# ============ RECONCILIATION ENTRIES ============
class ReconciliationEntryListView(LoginRequiredMixin, ListView):
    """List reconciliation entries."""
    model = ReconciliationEntry
    template_name = 'accounting/reconciliation_entry_list.html'
    context_object_name = 'entries'
    paginate_by = 50

    def get_queryset(self):
        return ReconciliationEntry.objects.order_by('-matched_date')


# ============ RECONCILIATION RECORDS ============
class ReconciliationRecordListView(LoginRequiredMixin, ListView):
    """List reconciliation records."""
    model = ReconciliationRecord
    template_name = 'accounting/reconciliation_record_list.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.reconciliation_records.order_by('-reconciliation_date')
        return ReconciliationRecord.objects.none()


# ============ RECONCILIATION MATCHES ============
class ReconciliationMatchListView(LoginRequiredMixin, ListView):
    """List reconciliation matches."""
    model = ReconciliationMatch
    template_name = 'accounting/reconciliation_match_list.html'
    context_object_name = 'matches'
    paginate_by = 50

    def get_queryset(self):
        return ReconciliationMatch.objects.order_by('-matched_at')


# ============ TAX RATES ============
class TaxRateListView(LoginRequiredMixin, ListView):
    """List tax rates."""
    model = TaxRate
    template_name = 'accounting/tax_rate_list.html'
    context_object_name = 'rates'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.tax_rates.all()
        return TaxRate.objects.none()


# ============ TAX TRANSACTIONS ============
class TaxTransactionListView(LoginRequiredMixin, ListView):
    """List tax transactions."""
    model = TaxTransaction
    template_name = 'accounting/tax_transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.tax_transactions.order_by('-transaction_date')
        return TaxTransaction.objects.none()


# ============ TAX SUMMARIES ============
class TaxSummaryListView(LoginRequiredMixin, ListView):
    """List tax summaries."""
    model = TaxSummary
    template_name = 'accounting/tax_summary_list.html'
    context_object_name = 'summaries'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.tax_summaries.order_by('-period_end')
        return TaxSummary.objects.none()


# ============ DEFERRED EXPENSES ============
class DeferredExpenseListView(LoginRequiredMixin, ListView):
    """List deferred expenses."""
    model = DeferredExpense
    template_name = 'accounting/deferred_expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.deferred_expenses.order_by('expiry_date')
        return DeferredExpense.objects.none()


# ============ DEFERRED REVENUES ============
class DeferredRevenueListView(LoginRequiredMixin, ListView):
    """List deferred revenues."""
    model = DeferredRevenue
    template_name = 'accounting/deferred_revenue_list.html'
    context_object_name = 'revenues'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.deferred_revenues.order_by('recognition_date')
        return DeferredRevenue.objects.none()


# ============ ENTITIES ============
class EntityListView(LoginRequiredMixin, ListView):
    """List entities."""
    model = Entity
    template_name = 'accounting/entity_list.html'
    context_object_name = 'entities'
    paginate_by = 50

    def get_queryset(self):
        return Entity.objects.all()


# ============ CURRENCIES ============
class CurrencyListView(LoginRequiredMixin, ListView):
    """List currencies."""
    model = Currency
    template_name = 'accounting/currency_list.html'
    context_object_name = 'currencies'
    paginate_by = 50

    def get_queryset(self):
        return Currency.objects.all()


# ============ PERIOD LOCKS ============
class PeriodLockListView(LoginRequiredMixin, ListView):
    """List period locks."""
    model = PeriodLock
    template_name = 'accounting/period_lock_list.html'
    context_object_name = 'locks'
    paginate_by = 50

    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            return entity.period_locks.order_by('-period_end')
        return PeriodLock.objects.none()


# ============ QUICK ADD VIEWS FOR DASHBOARD ============
class QuickAddLedgerEntryView(LoginRequiredMixin, FormView):
    """Quick add ledger entry from dashboard."""
    form_class = DoubleEntryJournalForm
    template_name = 'accounting/quick_add_ledger_entry.html'
    success_url = reverse_lazy('accounting:dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                # Create debit entry
                debit_entry = LedgerEntry.objects.create(
                    entity=entity,
                    account=form.cleaned_data['debit_account'],
                    entry_date=form.cleaned_data['entry_date'],
                    entry_type='DEBIT',
                    amount=form.cleaned_data['debit_amount'],
                    description=form.cleaned_data['description'],
                    reference_number=form.cleaned_data['reference_number'],
                    is_posted=form.cleaned_data['is_posted']
                )
                
                # Create credit entry
                credit_entry = LedgerEntry.objects.create(
                    entity=entity,
                    account=form.cleaned_data['credit_account'],
                    entry_date=form.cleaned_data['entry_date'],
                    entry_type='CREDIT',
                    amount=form.cleaned_data['credit_amount'],
                    description=form.cleaned_data['description'],
                    reference_number=form.cleaned_data['reference_number'],
                    is_posted=form.cleaned_data['is_posted']
                )
                
                # Log the action
                AuditLog.objects.create(
                    entity=entity,
                    user=str(self.request.user),
                    action='CREATE',
                    model_name='LedgerEntry',
                    object_id=f'{debit_entry.id}, {credit_entry.id}',
                    description=f'Created double-entry: Debit {debit_entry.account} {debit_entry.amount}, Credit {credit_entry.account} {credit_entry.amount}'
                )
                
                messages.success(
                    self.request, 
                    f'Ledger entries created successfully. Amount: {form.cleaned_data["debit_amount"]}'
                )
        except Exception as e:
            messages.error(self.request, f'Error creating entries: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR CUSTOMERS ============
class QuickAddCustomerView(PermissionRequiredMixin, FormView):
    """Quick add customer from dashboard."""
    from .forms import QuickAddCustomerForm
    form_class = QuickAddCustomerForm
    template_name = 'accounting/quick_add_customer.html'
    success_url = reverse_lazy('accounting:customer_list')
    permission_codename = 'customer'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        customer = form.save(commit=False)
        customer.entity = entity
        customer.save()
        
        AuditLog.objects.create(
            entity=entity,
            user=self.request.user.username,
            action='CREATE',
            model_name='Customer',
            object_id=customer.id,
            description=f'Created customer: {customer.name}'
        )
        
        messages.success(self.request, f'Customer {customer.name} created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR VENDORS ============
class QuickAddVendorView(PermissionRequiredMixin, FormView):
    """Quick add vendor from dashboard."""
    from .forms import QuickAddVendorForm
    form_class = QuickAddVendorForm
    template_name = 'accounting/quick_add_vendor.html'
    success_url = reverse_lazy('accounting:vendor_list')
    permission_codename = 'vendor'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        vendor = form.save(commit=False)
        vendor.entity = entity
        vendor.save()
        
        AuditLog.objects.create(
            entity=entity,
            user=self.request.user.username,
            action='CREATE',
            model_name='Vendor',
            object_id=vendor.id,
            description=f'Created vendor: {vendor.name}'
        )
        
        messages.success(self.request, f'Vendor {vendor.name} created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR ACCOUNTS ============
class QuickAddAccountView(PermissionRequiredMixin, FormView):
    """Quick add account from dashboard."""
    from .forms import QuickAddAccountForm
    form_class = QuickAddAccountForm
    template_name = 'accounting/quick_add_account.html'
    success_url = reverse_lazy('accounting:account_list')
    permission_codename = 'account'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        account = form.save(commit=False)
        account.entity = entity
        account.save()
        
        AuditLog.objects.create(
            entity=entity,
            user=self.request.user.username,
            action='CREATE',
            model_name='Account',
            object_id=account.id,
            description=f'Created account: {account.name}'
        )
        
        messages.success(self.request, f'Account {account.name} created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR VENDOR INVOICES ============
class QuickAddVendorInvoiceView(LoginRequiredMixin, FormView):
    """Quick add vendor invoice from dashboard."""
    from .forms import QuickAddVendorInvoiceForm
    form_class = QuickAddVendorInvoiceForm
    template_name = 'accounting/quick_add_vendor_invoice.html'
    success_url = reverse_lazy('accounting:vendor_invoice_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            invoice = form.save(commit=False)
            invoice.entity = entity
            invoice.status = 'DRAFT'
            invoice.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='VendorInvoice',
                object_id=str(invoice.id),
                description=f'Created invoice: {invoice.invoice_number} for {invoice.vendor.name}'
            )
            
            messages.success(self.request, f'Vendor invoice {invoice.invoice_number} created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating invoice: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR VENDOR PAYMENTS ============
class QuickAddVendorPaymentView(LoginRequiredMixin, FormView):
    """Quick add vendor payment from dashboard."""
    from .forms import QuickAddVendorPaymentForm
    form_class = QuickAddVendorPaymentForm
    template_name = 'accounting/quick_add_vendor_payment.html'
    success_url = reverse_lazy('accounting:vendor_payments_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            payment = form.save(commit=False)
            payment.entity = entity
            payment.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='VendorPayment',
                object_id=str(payment.id),
                description=f'Created payment: {payment.amount} for {payment.vendor_invoice.vendor.name}'
            )
            
            messages.success(self.request, f'Vendor payment created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating payment: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR FIXED ASSETS ============
class QuickAddFixedAssetView(LoginRequiredMixin, FormView):
    """Quick add fixed asset from dashboard."""
    from .forms import QuickAddFixedAssetForm
    form_class = QuickAddFixedAssetForm
    template_name = 'accounting/quick_add_fixed_asset.html'
    success_url = reverse_lazy('accounting:fixed_asset_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            asset = form.save(commit=False)
            asset.entity = entity
            asset.save()
            
            # Auto-create ledger entry for the fixed asset purchase
            self._create_purchase_ledger_entry(asset, entity)
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='FixedAsset',
                object_id=str(asset.id),
                description=f'Created fixed asset: {asset.name} with purchase amount {asset.purchase_cost}'
            )
            
            messages.success(self.request, f'Fixed asset {asset.name} created successfully with ledger entry.')
        except Exception as e:
            messages.error(self.request, f'Error creating fixed asset: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def _create_purchase_ledger_entry(self, asset, entity):
        """Create ledger entries for fixed asset purchase.
        
        Debit: Fixed Asset Account
        Credit: Cash/Bank Account (defaults to first active account)
        """
        # Find Fixed Asset account (should be an ASSET type account)
        fixed_asset_account = Account.objects.filter(
            entity=entity,
            account_type='ASSET',
            name__icontains='fixed asset'
        ).first()
        
        if not fixed_asset_account:
            # Create a default Fixed Assets account if it doesn't exist
            currency = Currency.objects.filter(is_active=True).first()
            if not currency:
                currency = Currency.objects.create(code='USD', name='US Dollar', symbol='$')
            fixed_asset_account = Account.objects.create(
                entity=entity,
                account_number='1500',
                name='Fixed Assets',
                account_type='ASSET',
                currency=currency,
                description='Capitalized Fixed Assets Account'
            )
        
        # Find Cash account (defaults to first ASSET account for simplicity)
        cash_account = Account.objects.filter(
            entity=entity,
            account_type='ASSET',
            name__icontains='cash'
        ).first()
        
        if not cash_account:
            cash_account = Account.objects.filter(entity=entity, account_type='ASSET').first()
        
        if not cash_account:
            return  # Skip if no cash account found
        
        # Create debit entry (Fixed Asset Account)
        debit_entry = LedgerEntry.objects.create(
            account=fixed_asset_account,
            entity=entity,
            entry_date=asset.purchase_date,
            entry_type='DEBIT',
            amount=asset.purchase_cost,
            description=f'Purchase of {asset.name} ({asset.asset_code})',
            reference_number=f'FA-{asset.asset_code}',
            is_posted=True
        )
        
        # Create credit entry (Cash Account)
        LedgerEntry.objects.create(
            account=cash_account,
            entity=entity,
            entry_date=asset.purchase_date,
            entry_type='CREDIT',
            amount=asset.purchase_cost,
            description=f'Payment for {asset.name} ({asset.asset_code})',
            reference_number=f'FA-{asset.asset_code}',
            is_posted=True
        )
        
        # Link the debit entry to the asset
        asset.purchase_ledger_entry = debit_entry
        asset.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR CASH TRANSACTIONS ============
class QuickAddCashTransactionView(LoginRequiredMixin, FormView):
    """Quick add cash transaction from dashboard."""
    from .forms import QuickAddCashTransactionForm
    form_class = QuickAddCashTransactionForm
    template_name = 'accounting/quick_add_cash_transaction.html'
    success_url = reverse_lazy('accounting:cash_transactions_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            transaction_record = form.save(commit=False)
            transaction_record.entity = entity
            transaction_record.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='CashTransaction',
                object_id=str(transaction_record.id),
                description=f'Created cash transaction: {transaction_record.amount}'
            )
            
            messages.success(self.request, f'Cash transaction created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating cash transaction: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR BANK PROFILES ============
class QuickAddBankProfileView(LoginRequiredMixin, FormView):
    """Quick add bank profile from dashboard."""
    from .forms import QuickAddBankProfileForm
    form_class = QuickAddBankProfileForm
    template_name = 'accounting/quick_add_bank_profile.html'
    success_url = reverse_lazy('accounting:bank_profiles_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            profile = form.save(commit=False)
            profile.entity = entity
            profile.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='BankProfile',
                object_id=str(profile.id),
                description=f'Created bank profile: {profile.bank_name}'
            )
            
            messages.success(self.request, f'Bank profile {profile.bank_name} created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating bank profile: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR TAX RATES ============
class QuickAddTaxRateView(LoginRequiredMixin, FormView):
    """Quick add tax rate from dashboard."""
    from .forms import QuickAddTaxRateForm
    form_class = QuickAddTaxRateForm
    template_name = 'accounting/quick_add_tax_rate.html'
    success_url = reverse_lazy('accounting:tax_rates_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            tax_rate = form.save(commit=False)
            tax_rate.entity = entity
            tax_rate.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='TaxRate',
                object_id=str(tax_rate.id),
                description=f'Created tax rate: {tax_rate.name} - {tax_rate.rate}%'
            )
            
            messages.success(self.request, f'Tax rate {tax_rate.name} created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating tax rate: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR DEFERRED EXPENSES ============
class QuickAddDeferredExpenseView(LoginRequiredMixin, FormView):
    """Quick add deferred expense from dashboard."""
    from .forms import QuickAddDeferredExpenseForm
    form_class = QuickAddDeferredExpenseForm
    template_name = 'accounting/quick_add_deferred_expense.html'
    success_url = reverse_lazy('accounting:deferred_expenses_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            expense = form.save(commit=False)
            expense.entity = entity
            expense.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='DeferredExpense',
                object_id=str(expense.id),
                description=f'Created deferred expense: {expense.description}'
            )
            
            messages.success(self.request, f'Deferred expense created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating deferred expense: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR DEFERRED REVENUES ============
class QuickAddDeferredRevenueView(LoginRequiredMixin, FormView):
    """Quick add deferred revenue from dashboard."""
    from .forms import QuickAddDeferredRevenueForm
    form_class = QuickAddDeferredRevenueForm
    template_name = 'accounting/quick_add_deferred_revenue.html'
    success_url = reverse_lazy('accounting:deferred_revenues_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            revenue = form.save(commit=False)
            revenue.entity = entity
            revenue.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=str(self.request.user),
                action='CREATE',
                model_name='DeferredRevenue',
                object_id=str(revenue.id),
                description=f'Created deferred revenue: {revenue.description}'
            )
            
            messages.success(self.request, f'Deferred revenue created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating deferred revenue: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context


# ============ QUICK ADD VIEWS FOR RECONCILIATION RECORDS ============
class QuickAddReconciliationRecordView(LoginRequiredMixin, FormView):
    """Quick add reconciliation record from dashboard."""
    from .forms import QuickAddReconciliationRecordForm
    form_class = QuickAddReconciliationRecordForm
    template_name = 'accounting/quick_add_reconciliation_record.html'
    success_url = reverse_lazy('accounting:reconciliation_records_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        kwargs['entity'] = entity
        return kwargs

    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            messages.error(self.request, 'No entity configured. Please contact administrator.')
            return self.form_invalid(form)
        
        try:
            record = form.save(commit=False)
            record.entity = entity
            record.save()
            
            AuditLog.objects.create(
                entity=entity,
                user=self.request.user,
                action='CREATE',
                model_name='ReconciliationRecord',
                object_id=record.id,
                changes=f'Created reconciliation record: {record.bank_balance}'
            )
            
            messages.success(self.request, f'Reconciliation record created successfully.')
        except Exception as e:
            messages.error(self.request, f'Error creating reconciliation record: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = Entity.objects.filter(is_active=True).first()
        return context
