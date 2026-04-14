"""
Forms for Cash Management Module - Cash Receipt Form
Clean, simplified form without cascading dropdown complexity
"""
from django import forms
from django.forms.models import ModelForm
from .models import CashReceiptLine, Account, Currency
from accounting.models import Stakeholder
from decimal import Decimal


class CashReceiptLineForm(ModelForm):
    """Form for creating cash receipts from shareholders or other sources."""
    
    class Meta:
        model = CashReceiptLine
        fields = ['date', 'account', 'currency', 'stakeholder', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True,
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account (Debit)',
                'id': 'id_account',
                'required': True,
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
                'id': 'id_currency',
                'required': True,
            }),
            'stakeholder': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Stakeholder (Optional)',
                'id': 'id_stakeholder',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description',
                'required': True,
            }),
            'debit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0',
                'required': True,
            }),
            'credit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0',
                'required': True,
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated',
                'readonly': True,
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes (Optional)',
            }),
        }
        labels = {
            'date': 'Receipt Date',
            'account': 'Account (Debit)',
            'currency': 'Currency',
            'stakeholder': 'Stakeholder (Optional)',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with entity-specific querysets."""
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            self.entity = entity
            
            # Populate account dropdown with all active accounts
            self.fields['account'].queryset = Account.objects.filter(
                entity=entity,
                is_active=True
            ).order_by('account_number')
            
            # Populate currency dropdown
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            
            # Populate stakeholder dropdown (optional field)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                entity=entity
            ).order_by('first_name', 'last_name')
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        
        # Validate amounts are provided
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit amount is required')
        if credit_amount is None:
            self.add_error('credit_amount', 'Credit amount is required')
        
        # Validate amounts match
        if debit_amount and credit_amount:
            if Decimal(str(debit_amount)) != Decimal(str(credit_amount)):
                self.add_error('credit_amount', 'Credit amount must equal debit amount')
            if Decimal(str(debit_amount)) <= 0:
                self.add_error('debit_amount', 'Amount must be greater than zero')
        
        return cleaned_data
