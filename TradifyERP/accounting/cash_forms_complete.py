"""
Forms for Cash Management Module
Handles Cash Receipts, Cash Payments, Bank Receipts, and Bank Payments
"""
from django import forms
from django.forms.models import ModelForm
from .models import CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine, Account, Currency
from accounting.models import Stakeholder
from decimal import Decimal


class CashReceiptLineForm(ModelForm):
    """Form for cash receipts from shareholders or other sources."""

    class Meta:
        model = CashReceiptLine
        fields = ['date', 'account', 'currency', 'stakeholder', 'description', 
                 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
                'id': 'id_account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'stakeholder': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Stakeholder (Optional)',
                'id': 'id_stakeholder',
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
                'placeholder': 'Auto-generated',
                'readonly': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
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
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity

    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')

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
        fields = ['date', 'account', 'credit_account', 'currency', 'payment_purpose', 'stakeholder', 'description', 
                 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
                'id': 'id_account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Credit Account',
                'id': 'id_credit_account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'payment_purpose': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_payment_purpose',
            }),
            'stakeholder': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Stakeholder (Optional)',
                'id': 'id_stakeholder',
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
                'placeholder': 'Auto-generated',
                'readonly': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Payment Date',
            'account': 'Account (Debit)',
            'credit_account': 'Credit Account',
            'currency': 'Currency',
            'payment_purpose': 'Payment Purpose',
            'stakeholder': 'Stakeholder (Optional)',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['credit_account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity
            
            # Set default credit_account to Cash account (100001) for new payments
            if not self.instance.pk:
                try:
                    cash_account = Account.objects.get(entity=entity, account_number='100001')
                    self.fields['credit_account'].initial = cash_account.id
                except Account.DoesNotExist:
                    pass

    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        payment_purpose = cleaned_data.get('payment_purpose')
        stakeholder = cleaned_data.get('stakeholder')
        
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit amount is required')
        if credit_amount is None:
            self.add_error('credit_amount', 'Credit amount is required')

        if debit_amount and credit_amount:
            if Decimal(str(debit_amount)) != Decimal(str(credit_amount)):
                self.add_error('credit_amount', 'Credit amount must equal debit amount')
            if Decimal(str(debit_amount)) <= 0:
                self.add_error('debit_amount', 'Amount must be greater than zero')
        
        # Validate stakeholder requirement for capital withdrawal and profit distribution
        if payment_purpose in ['CAPITAL_WITHDRAWAL', 'PROFIT_DISTRIBUTION']:
            if not stakeholder:
                self.add_error('stakeholder', f'Stakeholder is required when payment purpose is {payment_purpose.replace("_", " ").title()}')

        return cleaned_data


class BankReceiptLineForm(ModelForm):
    """Form for bank deposits/receipts."""

    class Meta:
        model = BankReceiptLine
        fields = ['date', 'account', 'currency', 'stakeholder', 'description', 
                 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
                'id': 'id_account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'stakeholder': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Stakeholder (Optional)',
                'id': 'id_stakeholder_bank',
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
                'placeholder': 'Auto-generated',
                'readonly': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Receipt Date',
            'account': 'Account',
            'currency': 'Currency',
            'stakeholder': 'Stakeholder (Optional)',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity

    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')

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


class BankPaymentLineForm(ModelForm):
    """Form for bank payments/withdrawals."""

    class Meta:
        model = BankPaymentLine
        fields = ['date', 'account', 'credit_account', 'currency', 'payment_purpose', 'stakeholder', 'description', 
                 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Account',
                'id': 'id_account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Credit Account',
                'id': 'id_credit_account',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Currency',
            }),
            'payment_purpose': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_payment_purpose_bank',
            }),
            'stakeholder': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Stakeholder (Optional)',
                'id': 'id_stakeholder_bank',
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
                'placeholder': 'Auto-generated',
                'readonly': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }
        labels = {
            'date': 'Payment Date',
            'account': 'Account (Debit)',
            'credit_account': 'Credit Account',
            'currency': 'Currency',
            'payment_purpose': 'Payment Purpose',
            'stakeholder': 'Stakeholder (Optional)',
            'description': 'Description',
            'debit_amount': 'Debit Amount',
            'credit_amount': 'Credit Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['credit_account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity

    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        payment_purpose = cleaned_data.get('payment_purpose')
        stakeholder = cleaned_data.get('stakeholder')
        
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit amount is required')
        if credit_amount is None:
            self.add_error('credit_amount', 'Credit amount is required')

        if debit_amount and credit_amount:
            if Decimal(str(debit_amount)) != Decimal(str(credit_amount)):
                self.add_error('credit_amount', 'Credit amount must equal debit amount')
            if Decimal(str(debit_amount)) <= 0:
                self.add_error('debit_amount', 'Amount must be greater than zero')
        
        # Validate stakeholder requirement for capital withdrawal and profit distribution
        if payment_purpose in ['CAPITAL_WITHDRAWAL', 'PROFIT_DISTRIBUTION']:
            if not stakeholder:
                self.add_error('stakeholder', f'Stakeholder is required when payment purpose is {payment_purpose.replace("_", " ").title()}')

        return cleaned_data
