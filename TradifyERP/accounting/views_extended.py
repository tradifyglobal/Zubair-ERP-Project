"""Extended quick-add views for all accounting modules with permission checking."""
from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from decimal import Decimal
from .models import Entity, AuditLog
from .forms_extended import (
    QuickAddCurrencyForm, QuickAddEntityForm, QuickAddAccountForm,
    QuickAddBankProfileForm, QuickAddBankStatementForm, QuickAddCashTransactionForm,
    QuickAddCashFlowForecastForm, QuickAddTaxRateForm, QuickAddTaxTransactionForm,
    QuickAddTaxSummaryForm, QuickAddDeferredExpenseForm, QuickAddDeferredRevenueForm,
    QuickAddFixedAssetForm, QuickAddPeriodLockForm, QuickAddTrialBalanceForm,
    QuickAddProfitLossReportForm, QuickAddBalanceSheetForm,
    QuickAddReconciliationRecordForm, QuickAddReconciliationEntryForm,
    QuickAddReconciliationMatchForm
)


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


class QuickAddCurrencyView(PermissionRequiredMixin, FormView):
    """Quick add view for Currencies."""
    template_name = 'accounting/quick_add_currency.html'
    form_class = QuickAddCurrencyForm
    success_url = reverse_lazy('accounting:currency_list')
    permission_codename = 'currency'
    
    def form_valid(self, form):
        """Save and log currency creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            currency = form.save()
            
            # Log audit trail
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='Currency',
                object_id=str(currency.id),
                user=self.request.user.username,
                description=f'Created currency {currency.code} - {currency.name}',
                new_values={'code': currency.code, 'name': currency.name}
            )
            
            messages.success(self.request, f'Currency {currency.code} created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating currency: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddEntityView(PermissionRequiredMixin, FormView):
    """Quick add view for Entities."""
    template_name = 'accounting/quick_add_entity.html'
    form_class = QuickAddEntityForm
    success_url = reverse_lazy('accounting:entity_list')
    permission_codename = 'entity'
    
    def form_valid(self, form):
        """Save and log entity creation."""
        try:
            entity = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='Entity',
                object_id=str(entity.id),
                user=self.request.user.username,
                description=f'Created entity {entity.code} - {entity.name}',
                new_values={'code': entity.code, 'name': entity.name}
            )
            
            messages.success(self.request, f'Entity {entity.code} created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating entity: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddBankProfileView(PermissionRequiredMixin, FormView):
    """Quick add view for Bank Profiles."""
    template_name = 'accounting/quick_add_bank_profile.html'
    form_class = QuickAddBankProfileForm
    success_url = reverse_lazy('accounting:bank_profiles_list')
    permission_codename = 'bankprofile'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log bank profile creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            profile = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='BankProfile',
                object_id=str(profile.id),
                user=self.request.user.username,
                description=f'Created bank profile {profile.bank_name} - {profile.account_number}',
                new_values={'bank_name': profile.bank_name, 'account_number': profile.account_number}
            )
            
            messages.success(self.request, f'Bank profile {profile.bank_name} created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating bank profile: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddBankStatementView(PermissionRequiredMixin, FormView):
    """Quick add view for Bank Statements."""
    template_name = 'accounting/quick_add_bank_statement.html'
    form_class = QuickAddBankStatementForm
    success_url = reverse_lazy('accounting:bank_statement_list')
    permission_codename = 'bankstatement'
    
    def form_valid(self, form):
        """Save and log bank statement creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            statement = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='BankStatement',
                object_id=str(statement.id),
                user=self.request.user.username,
                description=f'Created bank statement for {statement.bank_profile.bank_name} on {statement.statement_date}',
                new_values={'statement_date': str(statement.statement_date), 'closing_balance': str(statement.closing_balance)}
            )
            
            messages.success(self.request, 'Bank statement created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating bank statement: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddCashTransactionView(PermissionRequiredMixin, FormView):
    """Quick add view for Cash Transactions."""
    template_name = 'accounting/quick_add_cash_transaction.html'
    form_class = QuickAddCashTransactionForm
    success_url = reverse_lazy('accounting:cash_transaction_list')
    permission_codename = 'cashtransaction'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log cash transaction creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            transaction = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='CashTransaction',
                object_id=str(transaction.id),
                user=self.request.user.username,
                description=f'Created {transaction.transaction_type} of {transaction.amount} on {transaction.transaction_date}',
                new_values={'transaction_type': transaction.transaction_type, 'amount': str(transaction.amount)}
            )
            
            messages.success(self.request, 'Cash transaction created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating cash transaction: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddCashFlowForecastView(PermissionRequiredMixin, FormView):
    """Quick add view for Cash Flow Forecasts."""
    template_name = 'accounting/quick_add_cash_flow_forecast.html'
    form_class = QuickAddCashFlowForecastForm
    success_url = reverse_lazy('accounting:cash_flow_forecast_list')
    permission_codename = 'cashflowforecast'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log cash flow forecast creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            forecast = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='CashFlowForecast',
                object_id=str(forecast.id),
                user=self.request.user.username,
                description=f'Created cash flow forecast for {forecast.forecast_period}',
                new_values={'forecast_period': forecast.forecast_period}
            )
            
            messages.success(self.request, 'Cash flow forecast created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating cash flow forecast: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddTaxRateView(PermissionRequiredMixin, FormView):
    """Quick add view for Tax Rates."""
    template_name = 'accounting/quick_add_tax_rate.html'
    form_class = QuickAddTaxRateForm
    success_url = reverse_lazy('accounting:tax_rate_list')
    permission_codename = 'taxrate'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log tax rate creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            rate = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='TaxRate',
                object_id=str(rate.id),
                user=self.request.user.username,
                description=f'Created {rate.tax_type} at {rate.rate_percentage}%',
                new_values={'tax_type': rate.tax_type, 'rate_percentage': str(rate.rate_percentage)}
            )
            
            messages.success(self.request, f'Tax rate {rate.tax_type} created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating tax rate: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddTaxTransactionView(PermissionRequiredMixin, FormView):
    """Quick add view for Tax Transactions."""
    template_name = 'accounting/quick_add_tax_transaction.html'
    form_class = QuickAddTaxTransactionForm
    success_url = reverse_lazy('accounting:tax_transaction_list')
    permission_codename = 'taxtransaction'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log tax transaction creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            transaction = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='TaxTransaction',
                object_id=str(transaction.id),
                user=self.request.user.username,
                description=f'Created tax transaction for {transaction.tax_rate.tax_type}',
                new_values={'gross_amount': str(transaction.gross_amount), 'tax_amount': str(transaction.tax_amount)}
            )
            
            messages.success(self.request, 'Tax transaction created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating tax transaction: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddTaxSummaryView(PermissionRequiredMixin, FormView):
    """Quick add view for Tax Summaries."""
    template_name = 'accounting/quick_add_tax_summary.html'
    form_class = QuickAddTaxSummaryForm
    success_url = reverse_lazy('accounting:tax_summary_list')
    permission_codename = 'taxsummary'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log tax summary creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            summary = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='TaxSummary',
                object_id=str(summary.id),
                user=self.request.user.username,
                description=f'Created tax summary for {summary.tax_type} ({summary.period_start} to {summary.period_end})',
                new_values={'period_start': str(summary.period_start), 'period_end': str(summary.period_end)}
            )
            
            messages.success(self.request, 'Tax summary created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating tax summary: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddDeferredExpenseView(PermissionRequiredMixin, FormView):
    """Quick add view for Deferred Expenses."""
    template_name = 'accounting/quick_add_deferred_expense.html'
    form_class = QuickAddDeferredExpenseForm
    success_url = reverse_lazy('accounting:deferred_expense_list')
    permission_codename = 'deferredexpense'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log deferred expense creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            expense = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='DeferredExpense',
                object_id=str(expense.id),
                user=self.request.user.username,
                description=f'Created deferred {expense.expense_type}: {expense.description}',
                new_values={'amount': str(expense.amount), 'expiry_date': str(expense.expiry_date)}
            )
            
            messages.success(self.request, 'Deferred expense created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating deferred expense: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddDeferredRevenueView(PermissionRequiredMixin, FormView):
    """Quick add view for Deferred Revenues."""
    template_name = 'accounting/quick_add_deferred_revenue.html'
    form_class = QuickAddDeferredRevenueForm
    success_url = reverse_lazy('accounting:deferred_revenue_list')
    permission_codename = 'deferredrevenue'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log deferred revenue creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            revenue = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='DeferredRevenue',
                object_id=str(revenue.id),
                user=self.request.user.username,
                description=f'Created deferred {revenue.revenue_type}: {revenue.description}',
                new_values={'amount': str(revenue.amount), 'recognition_date': str(revenue.recognition_date)}
            )
            
            messages.success(self.request, 'Deferred revenue created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating deferred revenue: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddFixedAssetView(PermissionRequiredMixin, FormView):
    """Quick add view for Fixed Assets."""
    template_name = 'accounting/quick_add_fixed_asset.html'
    form_class = QuickAddFixedAssetForm
    success_url = reverse_lazy('accounting:fixed_asset_list')
    permission_codename = 'fixedasset'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log fixed asset creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            asset = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='FixedAsset',
                object_id=str(asset.id),
                user=self.request.user.username,
                description=f'Created asset {asset.asset_code}: {asset.name}',
                new_values={'asset_code': asset.asset_code, 'purchase_cost': str(asset.purchase_cost)}
            )
            
            messages.success(self.request, f'Fixed asset {asset.asset_code} created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating fixed asset: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddPeriodLockView(PermissionRequiredMixin, FormView):
    """Quick add view for Period Locks."""
    template_name = 'accounting/quick_add_period_lock.html'
    form_class = QuickAddPeriodLockForm
    success_url = reverse_lazy('accounting:period_lock_list')
    permission_codename = 'periodlock'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log period lock creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            lock = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='PeriodLock',
                object_id=str(lock.id),
                user=self.request.user.username,
                description=f'Created period lock from {lock.period_start} to {lock.period_end}',
                new_values={'period_start': str(lock.period_start), 'period_end': str(lock.period_end), 'is_locked': lock.is_locked}
            )
            
            messages.success(self.request, 'Period lock created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating period lock: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddTrialBalanceView(PermissionRequiredMixin, FormView):
    """Quick add view for Trial Balances."""
    template_name = 'accounting/quick_add_trial_balance.html'
    form_class = QuickAddTrialBalanceForm
    success_url = reverse_lazy('accounting:trial_balance_list')
    permission_codename = 'trialbalance'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log trial balance creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            tb = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='TrialBalance',
                object_id=str(tb.id),
                user=self.request.user.username,
                description=f'Created trial balance as of {tb.as_of_date}',
                new_values={'as_of_date': str(tb.as_of_date), 'is_balanced': tb.is_balanced}
            )
            
            messages.success(self.request, 'Trial balance created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating trial balance: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddProfitLossReportView(PermissionRequiredMixin, FormView):
    """Quick add view for Profit & Loss Reports."""
    template_name = 'accounting/quick_add_profit_loss_report.html'
    form_class = QuickAddProfitLossReportForm
    success_url = reverse_lazy('accounting:profit_loss_list')
    permission_codename = 'profitlossreport'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log P&L report creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            pl = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='ProfitLossReport',
                object_id=str(pl.id),
                user=self.request.user.username,
                description=f'Created P&L report from {pl.period_start} to {pl.period_end}',
                new_values={'net_profit': str(pl.net_profit), 'period_start': str(pl.period_start)}
            )
            
            messages.success(self.request, 'P&L report created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating P&L report: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddBalanceSheetView(PermissionRequiredMixin, FormView):
    """Quick add view for Balance Sheets."""
    template_name = 'accounting/quick_add_balance_sheet.html'
    form_class = QuickAddBalanceSheetForm
    success_url = reverse_lazy('accounting:balance_sheet_list')
    permission_codename = 'balancesheet'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log balance sheet creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            bs = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='BalanceSheet',
                object_id=str(bs.id),
                user=self.request.user.username,
                description=f'Created balance sheet as of {bs.as_of_date}',
                new_values={'as_of_date': str(bs.as_of_date), 'total_assets': str(bs.total_assets)}
            )
            
            messages.success(self.request, 'Balance sheet created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating balance sheet: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddReconciliationRecordView(PermissionRequiredMixin, FormView):
    """Quick add view for Reconciliation Records."""
    template_name = 'accounting/quick_add_reconciliation_record.html'
    form_class = QuickAddReconciliationRecordForm
    success_url = reverse_lazy('accounting:reconciliation_record_list')
    permission_codename = 'reconciliationrecord'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Save and log reconciliation record creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            record = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='ReconciliationRecord',
                object_id=str(record.id),
                user=self.request.user.username,
                description=f'Created reconciliation record for {record.reconciliation_date}',
                new_values={'status': record.status, 'total_items_reconciled': record.total_items_reconciled}
            )
            
            messages.success(self.request, 'Reconciliation record created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating reconciliation record: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddReconciliationEntryView(PermissionRequiredMixin, FormView):
    """Quick add view for Reconciliation Entries."""
    template_name = 'accounting/quick_add_reconciliation_entry.html'
    form_class = QuickAddReconciliationEntryForm
    success_url = reverse_lazy('accounting:reconciliation_entry_list')
    permission_codename = 'reconciliationentry'
    
    def form_valid(self, form):
        """Save and log reconciliation entry creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            entry = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='ReconciliationEntry',
                object_id=str(entry.id),
                user=self.request.user.username,
                description=f'Matched bank statement entry to ledger entry',
                new_values={}
            )
            
            messages.success(self.request, 'Reconciliation entry created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating reconciliation entry: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)


class QuickAddReconciliationMatchView(PermissionRequiredMixin, FormView):
    """Quick add view for Reconciliation Matches."""
    template_name = 'accounting/quick_add_reconciliation_match.html'
    form_class = QuickAddReconciliationMatchForm
    success_url = reverse_lazy('accounting:reconciliation_match_list')
    permission_codename = 'reconciliationmatch'
    
    def form_valid(self, form):
        """Save and log reconciliation match creation."""
        try:
            entity = Entity.objects.filter(is_active=True).first()
            match = form.save()
            
            AuditLog.objects.create(
                entity=entity,
                action='CREATE',
                model_name='ReconciliationMatch',
                object_id=str(match.id),
                user=self.request.user.username,
                description=f'Created reconciliation match with variance: {match.variance}',
                new_values={'variance': str(match.variance)}
            )
            
            messages.success(self.request, 'Reconciliation match created successfully!')
        except Exception as e:
            messages.error(self.request, f'Error creating reconciliation match: {str(e)}')
            return self.form_invalid(form)
        
        return super().form_valid(form)
