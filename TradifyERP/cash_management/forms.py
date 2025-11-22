"""
Cash Management Module Forms
Forms for payment scheduling, liquidity forecasting, FX management, etc.
"""

from django import forms
from .models import CashPosition, PaymentSchedule, LiquidityForecast, TreasuryAccount, FXExposure


class CashPositionForm(forms.ModelForm):
    """Form for updating cash position and balances."""
    
    class Meta:
        model = CashPosition
        fields = ['bank_account', 'position_date', 'opening_balance', 'closing_balance', 'is_reconciled']
        widgets = {
            'bank_account': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'position_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'closing_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'is_reconciled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class PaymentScheduleForm(forms.ModelForm):
    """Form for scheduling payments and payment approvals."""
    
    class Meta:
        model = PaymentSchedule
        fields = ['payment_type', 'vendor', 'amount', 'scheduled_date', 'payment_method', 
                  'priority', 'reference_number', 'notes']
        widgets = {
            'payment_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'vendor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': 'required'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Invoice/Bill number'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Payment notes'
            }),
        }


class LiquidityForecastForm(forms.ModelForm):
    """Form for creating liquidity forecast scenarios."""
    
    class Meta:
        model = LiquidityForecast
        fields = ['forecast_date', 'currency', 'forecast_days', 'scenario_name', 
                  'description', 'base_case', 'optimistic_case', 'pessimistic_case']
        widgets = {
            'forecast_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'forecast_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': '1',
                'max': '365',
                'required': 'required'
            }),
            'scenario_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Base Case, Optimistic, etc.',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Forecast assumptions and details'
            }),
            'base_case': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'optimistic_case': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'pessimistic_case': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }


class TreasuryAccountForm(forms.ModelForm):
    """Form for managing treasury accounts."""
    
    class Meta:
        model = TreasuryAccount
        fields = ['bank_name', 'account_number', 'account_holder', 'currency', 
                  'account_type', 'is_active', 'is_sweep_account', 'sweep_target']
        widgets = {
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank name',
                'required': 'required'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account number',
                'required': 'required'
            }),
            'account_holder': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account holder name',
                'required': 'required'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_sweep_account': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sweep_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
        }


class FXExposureForm(forms.ModelForm):
    """Form for tracking and hedging FX exposure."""
    
    class Meta:
        model = FXExposure
        fields = ['currency_pair', 'exposure_amount', 'direction', 'maturity_date', 
                  'hedge_status', 'hedge_rate', 'notional_amount', 'counterparty', 'notes']
        widgets = {
            'currency_pair': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., EUR/USD',
                'required': 'required'
            }),
            'exposure_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'direction': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'maturity_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'hedge_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'hedge_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.0001',
                'min': '0'
            }),
            'notional_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'counterparty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Counterparty bank/broker'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'FX exposure notes'
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
