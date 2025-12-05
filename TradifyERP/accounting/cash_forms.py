"""
Forms for Cash Management Module
Handles Cash Receipts, Cash Payments, Bank Receipts, and Bank Payments
"""
from django import forms
from django.forms.models import ModelForm
from .models import CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine, Account, Currency
from decimal import Decimal


class CashReceiptLineForm(ModelForm):
    """Form for cash receipts from shareholders or other sources."""
    
    class Meta:
        model = CashReceiptLine
        fields = ['date', 'account', 'credit_account', 'currency', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Credit Account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description'
            }),
            'debit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'credit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Receipt Date',
            'account': 'Debit Account (e.g., Capital - Shareholder)',
            'credit_account': 'Credit Account (e.g., Cash Account)',
            'currency': 'Currency',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        
        # Ensure both amounts are provided and match
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit amount is required')
        if credit_amount is None:
            self.add_error('credit_amount', 'Credit amount is required')
        
        if debit_amount and credit_amount:
            if Decimal(str(debit_amount)) != Decimal(str(credit_amount)):
                self.add_error('credit_amount', 'Credit amount must equal debit amount')
            if Decimal(str(debit_amount)) <= 0:
                self.add_error('debit_amount', 'Amount must be greater than zero')
        
        return cleaned_data


class CashPaymentLineForm(ModelForm):
    """Form for cash payments to shareholders or other entities."""
    
    class Meta:
        model = CashPaymentLine
        fields = ['date', 'account', 'credit_account', 'currency', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Credit Account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description'
            }),
            'debit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'credit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Payment Date',
            'account': 'Debit Account (e.g., Capital - Shareholder)',
            'credit_account': 'Credit Account (e.g., Cash Account)',
            'currency': 'Currency',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        
        # Ensure both amounts are provided and match
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit amount is required')
        if credit_amount is None:
            self.add_error('credit_amount', 'Credit amount is required')
        
        if debit_amount and credit_amount:
            if Decimal(str(debit_amount)) != Decimal(str(credit_amount)):
                self.add_error('credit_amount', 'Credit amount must equal debit amount')
            if Decimal(str(debit_amount)) <= 0:
                self.add_error('debit_amount', 'Amount must be greater than zero')
        
        return cleaned_data


class BankReceiptLineForm(ModelForm):
    """Form for bank deposits/receipts."""
    
    class Meta:
        model = BankReceiptLine
        fields = ['date', 'account', 'credit_account', 'currency', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description'
            }),
            'debit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'credit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Receipt Date',
            'account': 'Debit Account',
            'credit_account': 'Credit Account',
            'currency': 'Currency',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit Amount is required')
        elif Decimal(str(debit_amount)) <= 0:
            self.add_error('debit_amount', 'Debit Amount must be greater than zero')
        
        return cleaned_data


class BankPaymentLineForm(ModelForm):
    """Form for bank payments/withdrawals."""
    
    class Meta:
        model = BankPaymentLine
        fields = ['date', 'account', 'credit_account', 'currency', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description'
            }),
            'debit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'credit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Payment Date',
            'account': 'Debit Account',
            'credit_account': 'Credit Account',
            'currency': 'Currency',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit Amount is required')
        elif Decimal(str(debit_amount)) <= 0:
            self.add_error('debit_amount', 'Debit Amount must be greater than zero')
        
        return cleaned_data
