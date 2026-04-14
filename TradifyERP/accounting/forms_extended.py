"""Extended quick-add forms for all accounting modules."""
from django import forms
from .models import (
    Account, Entity, Currency, BankProfile, BankStatement, CashTransaction,
    TaxRate, DeferredExpense, DeferredRevenue, FixedAsset, ReconciliationRecord,
    Customer, Vendor, VendorInvoice, VendorPayment, CashFlowForecast,
    TrialBalance, ProfitLossReport, BalanceSheet, TaxTransaction, TaxSummary,
    PeriodLock, ReconciliationEntry, ReconciliationMatch, AuditLog, InternationalTransferTracking
)


# Currency, Entity, Account, and related forms
class QuickAddCurrencyForm(forms.ModelForm):
    """Quick add form for Currencies."""
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol', 'exchange_rate', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD, EUR, GBP, etc.'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'US Dollar'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1.0', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuickAddEntityForm(forms.ModelForm):
    """Quick add form for Entities."""
    class Meta:
        model = Entity
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entity name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., ENTITY01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuickAddAccountForm(forms.ModelForm):
    """Quick add form for Chart of Accounts."""
    class Meta:
        model = Account
        fields = ['account_number', 'name', 'account_type', 'description', 'entity', 'currency', 'opening_balance', 'is_active']
        widgets = {
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1000'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cash'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


# Bank-related forms
class QuickAddBankProfileForm(forms.ModelForm):
    """Quick add form for Bank Profiles."""
    class Meta:
        model = BankProfile
        fields = ['bank_name', 'account_number', 'account_holder', 'entity', 'currency', 'is_active']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account number'}),
            'account_holder': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account holder name'}),
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddBankStatementForm(forms.ModelForm):
    """Quick add form for Bank Statements."""
    class Meta:
        model = BankStatement
        fields = ['bank_profile', 'statement_date', 'opening_balance', 'closing_balance', 'total_debits', 'total_credits']
        widgets = {
            'bank_profile': forms.Select(attrs={'class': 'form-select'}),
            'statement_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'closing_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_debits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }


# Cash and transaction forms
class QuickAddCashTransactionForm(forms.ModelForm):
    """Quick add form for Cash Transactions."""
    class Meta:
        model = CashTransaction
        fields = ['entity', 'transaction_date', 'transaction_type', 'amount', 'description', 'reference_number', 'is_reconciled']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'transaction_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference'}),
            'is_reconciled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddCashFlowForecastForm(forms.ModelForm):
    """Quick add form for Cash Flow Forecasts."""
    class Meta:
        model = CashFlowForecast
        fields = ['entity', 'forecast_period', 'opening_cash', 'inflows', 'outflows', 'closing_cash', 'notes']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'forecast_period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Q1 2025, Jan 2025, etc.'}),
            'opening_cash': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'inflows': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'outflows': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'closing_cash': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


# Tax-related forms
class QuickAddTaxRateForm(forms.ModelForm):
    """Quick add form for Tax Rates."""
    class Meta:
        model = TaxRate
        fields = ['entity', 'tax_type', 'rate_percentage', 'effective_from', 'effective_to', 'is_active']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'tax_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VAT, Sales Tax, etc.'}),
            'rate_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'effective_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'effective_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddTaxTransactionForm(forms.ModelForm):
    """Quick add form for Tax Transactions."""
    class Meta:
        model = TaxTransaction
        fields = ['entity', 'tax_rate', 'transaction_date', 'gross_amount', 'tax_amount', 'net_amount', 'reference_number']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'tax_rate': forms.Select(attrs={'class': 'form-select'}),
            'transaction_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gross_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'net_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)
            self.fields['tax_rate'].queryset = TaxRate.objects.filter(entity=entity, is_active=True)


class QuickAddTaxSummaryForm(forms.ModelForm):
    """Quick add form for Tax Summaries."""
    class Meta:
        model = TaxSummary
        fields = ['entity', 'period_start', 'period_end', 'tax_type', 'total_tax', 'total_taxable']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tax_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tax type'}),
            'total_tax': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_taxable': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


# Deferred items forms
class QuickAddDeferredExpenseForm(forms.ModelForm):
    """Quick add form for Deferred Expenses."""
    class Meta:
        model = DeferredExpense
        fields = ['entity', 'description', 'amount', 'deferral_date', 'expiry_date', 'expense_type']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'deferral_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expense_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insurance, Rent, etc.'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddDeferredRevenueForm(forms.ModelForm):
    """Quick add form for Deferred Revenues."""
    class Meta:
        model = DeferredRevenue
        fields = ['entity', 'description', 'amount', 'deferral_date', 'recognition_date', 'revenue_type']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'deferral_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'recognition_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'revenue_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subscription, etc.'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


# Asset and period forms
class QuickAddFixedAssetForm(forms.ModelForm):
    """Quick add form for Fixed Assets."""
    class Meta:
        model = FixedAsset
        fields = ['entity', 'asset_code', 'name', 'category', 'purchase_date', 'purchase_cost', 'book_value', 'useful_life_years', 'annual_depreciation', 'is_active']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'asset_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asset code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asset name'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building, Vehicle, etc.'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'book_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'annual_depreciation': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddPeriodLockForm(forms.ModelForm):
    """Quick add form for Period Locks."""
    class Meta:
        model = PeriodLock
        fields = ['entity', 'period_start', 'period_end', 'is_locked', 'locked_by']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_locked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'locked_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lock reason'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


# Report forms
class QuickAddTrialBalanceForm(forms.ModelForm):
    """Quick add form for Trial Balances."""
    class Meta:
        model = TrialBalance
        fields = ['entity', 'as_of_date', 'total_debits', 'total_credits', 'is_balanced']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'as_of_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_debits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'is_balanced': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddProfitLossReportForm(forms.ModelForm):
    """Quick add form for Profit & Loss Reports."""
    class Meta:
        model = ProfitLossReport
        fields = ['entity', 'period_start', 'period_end', 'total_income', 'total_expenses', 'net_profit']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_income': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_expenses': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'net_profit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddBalanceSheetForm(forms.ModelForm):
    """Quick add form for Balance Sheets."""
    class Meta:
        model = BalanceSheet
        fields = ['entity', 'as_of_date', 'total_assets', 'total_liabilities', 'total_equity']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'as_of_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_assets': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_liabilities': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_equity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


# Reconciliation forms
class QuickAddReconciliationRecordForm(forms.ModelForm):
    """Quick add form for Reconciliation Records."""
    class Meta:
        model = ReconciliationRecord
        fields = ['entity', 'reconciliation_date', 'total_items_reconciled', 'discrepancies_found', 'status']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'reconciliation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_items_reconciled': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'discrepancies_found': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['entity'].initial = entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity.id)


class QuickAddReconciliationEntryForm(forms.ModelForm):
    """Quick add form for Reconciliation Entries."""
    class Meta:
        model = ReconciliationEntry
        fields = ['bank_statement', 'ledger_entry', 'notes']
        widgets = {
            'bank_statement': forms.Select(attrs={'class': 'form-select'}),
            'ledger_entry': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class QuickAddReconciliationMatchForm(forms.ModelForm):
    """Quick add form for Reconciliation Matches."""
    class Meta:
        model = ReconciliationMatch
        fields = ['reconciliation_record', 'bank_entry_amount', 'ledger_entry_amount', 'variance']
        widgets = {
            'reconciliation_record': forms.Select(attrs={'class': 'form-select'}),
            'bank_entry_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'ledger_entry_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'variance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }


class InternationalTransferForm(forms.ModelForm):
    """Form for managing international capital transfer tracking."""
    class Meta:
        model = InternationalTransferTracking
        fields = [
            'source_country', 'source_bank_name', 'source_bank_account', 'source_currency_code', 'source_amount',
            'destination_country', 'destination_bank_name', 'destination_bank_account', 'destination_currency_code', 'destination_amount',
            'exchange_rate_used', 'conversion_date', 'date_sent_from_shareholder', 'date_received_in_foreign_bank',
            'date_transferred_to_local_bank', 'date_posted_to_gl', 'transfer_status', 'transfer_reference',
            'intermediary_bank_name', 'intermediary_reference', 'remittance_proof', 'conversion_receipt', 'notes'
        ]
        widgets = {
            # Source Country Section
            'source_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Canada, USA, UAE, Oman, Saudi Arabia'}),
            'source_bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank name in source country'}),
            'source_bank_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account number'}),
            'source_currency_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CAD, USD, AED, OMR, SAR, etc.', 'maxlength': '3'}),
            'source_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            
            # Destination Country Section (India)
            'destination_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., India', 'readonly': 'readonly'}),
            'destination_bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank name in India'}),
            'destination_bank_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account number'}),
            'destination_currency_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INR', 'maxlength': '3', 'readonly': 'readonly'}),
            'destination_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            
            # Exchange Rate
            'exchange_rate_used': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 65.4800', 'step': '0.0001', 'min': '0'}),
            'conversion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Transfer Dates
            'date_sent_from_shareholder': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_received_in_foreign_bank': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_transferred_to_local_bank': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_posted_to_gl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Transfer Status
            'transfer_status': forms.Select(attrs={'class': 'form-select'}),
            
            # Reference Numbers
            'transfer_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wire transfer reference or transaction ID'}),
            'intermediary_bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If transfer involved multiple banks'}),
            'intermediary_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Intermediary bank reference'}),
            
            # File Uploads
            'remittance_proof': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'conversion_receipt': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            
            # Notes
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes or comments about the transfer'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set India as default destination
        self.fields['destination_country'].initial = 'India'
        self.fields['destination_currency_code'].initial = 'INR'
        # Make destination fields read-only
        self.fields['destination_country'].disabled = True
        self.fields['destination_currency_code'].disabled = True
