"""
Cash Management Module Forms
Forms for payment scheduling, liquidity forecasting, FX management, etc.
"""

from django import forms
from django.forms import ModelChoiceField
from .models import CashPosition, PaymentSchedule, LiquidityForecast, TreasuryAccount, FXExposure
from accounting.models import Currency, BankProfile


class CashPositionForm(forms.ModelForm):
    """Form for updating cash position and balances."""
    
    currency = ModelChoiceField(
        queryset=Currency.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Currency',
        help_text='Currency will be auto-populated based on selected bank account',
        required=False
    )
    
    class Meta:
        model = CashPosition
        fields = ['entity', 'bank_account', 'position_date', 'opening_balance', 'closing_balance', 'is_reconciled']
        widgets = {
            'entity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Select the entity for this cash position'
            }),
            'bank_account': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Select the bank account to record position for'
            }),
            'position_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required',
                'title': 'Date of the cash position snapshot'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required',
                'title': 'Opening balance at the start of the period'
            }),
            'closing_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required',
                'title': 'Closing balance at the end of the period'
            }),
            'is_reconciled': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'title': 'Check if this position has been reconciled with bank statement'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        bank_account = cleaned_data.get('bank_account')
        
        # Auto-populate currency from bank account if not explicitly set
        if bank_account and not cleaned_data.get('currency'):
            cleaned_data['currency'] = bank_account.currency
        
        return cleaned_data


class PaymentScheduleForm(forms.ModelForm):
    """Form for scheduling payments and payment approvals."""
    
    class Meta:
        model = PaymentSchedule
        fields = ['entity', 'reference_document', 'reference_type', 'payment_amount', 'currency', 'scheduled_date', 
                  'due_date', 'from_account', 'to_account_details', 'status']
        widgets = {
            'entity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Entity making the payment'
            }),
            'reference_document': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bill/PO number',
                'required': 'required',
                'title': 'Reference number (e.g., Bill #, PO #)'
            }),
            'reference_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'choices': [('BILL', 'Bill'), ('PO', 'PO'), ('LOAN', 'Loan'), ('OTHER', 'Other')],
                'title': 'Type of payment (Bill, PO, Loan, etc.)'
            }),
            'payment_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': 'required',
                'title': 'Amount to be paid'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'from_account': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'to_account_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payee account information',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class LiquidityForecastForm(forms.ModelForm):
    """Form for creating liquidity forecast scenarios."""
    
    class Meta:
        model = LiquidityForecast
        fields = ['entity', 'forecast_period', 'scenario_type', 'is_active', 
                  'forecast_start_date', 'forecast_end_date', 'forecast_horizon_days', 
                  'opening_balance', 'forecasted_inflows', 'forecasted_outflows', 
                  'minimum_cash_level']
        widgets = {
            'entity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'forecast_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Q1 2025, Jan-Mar 2025',
                'required': 'required'
            }),
            'scenario_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'forecast_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'forecast_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'forecast_horizon_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': '1',
                'max': '365',
                'required': 'required'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'forecasted_inflows': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'forecasted_outflows': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'minimum_cash_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
        }
    
    def save(self, commit=True):
        """
        Calculate surplus_deficit, closing balance, and risk level before saving.
        
        Risk Level Calculation (Industry Best Practices):
        - LOW: Surplus >= 30% of minimum (strong cash position)
        - MEDIUM: -30% to +30% of minimum (adequate but needs monitoring)
        - HIGH: Deficit < -30% of minimum (concerning cash shortage)
        """
        instance = super().save(commit=False)
        
        # Calculate forecasted_closing_balance = opening + inflows - outflows
        if instance.opening_balance is not None and instance.forecasted_inflows is not None and instance.forecasted_outflows is not None:
            instance.forecasted_closing_balance = instance.opening_balance + instance.forecasted_inflows - instance.forecasted_outflows
        
        # Calculate surplus_deficit = closing_balance - minimum_cash_level
        if instance.forecasted_closing_balance and instance.minimum_cash_level:
            instance.surplus_deficit = instance.forecasted_closing_balance - instance.minimum_cash_level
            
            # Auto-calculate risk level based on surplus/deficit percentage
            # Risk level is determined by comparing surplus/deficit to minimum cash level
            if instance.minimum_cash_level > 0:
                surplus_percentage = (instance.surplus_deficit / instance.minimum_cash_level) * 100
                
                if surplus_percentage >= 30:
                    # Strong surplus: >= 30% of minimum cash level
                    instance.risk_level = 'LOW'
                elif surplus_percentage < -30:
                    # Significant deficit: < -30% of minimum cash level
                    instance.risk_level = 'HIGH'
                else:
                    # Between -30% and +30%: adequate but monitoring needed
                    instance.risk_level = 'MEDIUM'
        
        if commit:
            instance.save()
        return instance


class TreasuryAccountForm(forms.ModelForm):
    """Form for managing treasury accounts."""
    
    class Meta:
        model = TreasuryAccount
        fields = ['entity', 'account_code', 'account_name', 'account_type', 'currency', 'gl_account',
                  'opening_balance', 'current_balance', 'interest_rate', 'maturity_date', 'credit_limit', 'is_active']
        widgets = {
            'entity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Entity owning this treasury account'
            }),
            'account_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account code',
                'required': 'required',
                'title': 'Unique code for this treasury account'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account name',
                'required': 'required',
                'title': 'Descriptive name for the account'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Type: Investment, Loan, Credit Line, or Operating'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Currency for this treasury account'
            }),
            'gl_account': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Link to general ledger account for accounting integration'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required',
                'title': 'Initial balance when account was opened'
            }),
            'current_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required',
                'title': 'Current account balance as of today'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0',
                'title': 'Annual interest rate percentage (for loans/investments)'
            }),
            'maturity_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'title': 'When the loan/investment matures'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'title': 'Maximum credit available (for credit lines)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class FXExposureForm(forms.ModelForm):
    """Form for tracking and hedging FX exposure."""
    
    class Meta:
        model = FXExposure
        fields = ['entity', 'home_currency', 'foreign_currency', 'exposure_type', 'foreign_amount', 
                  'exchange_rate', 'home_currency_amount', 'exposure_date', 'maturity_date', 'is_hedged']
        widgets = {
            'entity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Entity with FX exposure'
            }),
            'home_currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Your company\'s base currency'
            }),
            'foreign_currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Foreign currency in which you have exposure'
            }),
            'exposure_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Type of exposure: AR, AP, Investment, or Cash'
            }),
            'foreign_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required',
                'title': 'Amount in foreign currency'
            }),
            'exchange_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.000000',
                'step': '0.000001',
                'min': '0',
                'required': 'required',
                'title': 'Current exchange rate (foreign / home currency)'
            }),
            'home_currency_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'readonly': 'readonly',
                'id': 'home_currency_amount_display',
                'title': 'Automatically calculated: Foreign Amount × Exchange Rate'
            }),
            'exposure_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required',
                'title': 'Date when exposure originated'
            }),
            'maturity_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'title': 'Date when exposure will settle or mature'
            }),
            'is_hedged': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'title': 'Check if this exposure has been hedged'
            }),
        }


class BulkPaymentScheduleForm(forms.Form):
    """Form for bulk scheduling multiple payments via CSV/Excel."""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'required': 'required'
        }),
        label='Upload CSV/Excel file',
        help_text='File should contain: Vendor, Amount, ScheduledDate, PaymentMethod'
    )
    
    payment_type = forms.ChoiceField(
        choices=[
            ('BILL_PAYMENT', 'Bill Payment'),
            ('LOAN_REPAYMENT', 'Loan Repayment'),
            ('DIVIDEND_PAYMENT', 'Dividend Payment'),
            ('OTHER', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Payment Type'
    )
    
    priority = forms.ChoiceField(
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('CRITICAL', 'Critical'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Default Priority'
    )
