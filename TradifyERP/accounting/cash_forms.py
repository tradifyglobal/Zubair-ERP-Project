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
        fields = ['date', 'account', 'credit_account', 'currency', 'stakeholder', 'description', 
                 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Specific Source Account (CREDITED)',
                'id': 'id_account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Source Sub-Account (to be CREDITED)',
                'id': 'id_credit_account',
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
            'account': 'Cash Account (will be DEBITED)',
            'credit_account': 'Source Account - Capital/Revenue (will be CREDITED)',
            'currency': 'Currency',
            'stakeholder': 'Stakeholder (for investment tracking)',
            'description': 'Description',
            'debit_amount': 'Amount',
            'credit_amount': 'Amount',
            'reference_number': 'Reference #',
            'notes': 'Notes'
        }

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            # Populate form fields
            all_accounts = Account.objects.filter(entity=entity, is_active=True).order_by('account_number')
            self.fields['account'].queryset = all_accounts
            self.fields['credit_account'].queryset = all_accounts
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity
            
            # Add cash_account field dynamically (AFTER super().__init__ so fields dict exists)
            self.fields['cash_account'] = forms.ModelChoiceField(
                queryset=all_accounts,
                required=True,
                empty_label='-- Select Main Cash Account --',
                widget=forms.Select(attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Main Cash Account (DEBITED)',
                    'id': 'id_cash_account',
                }),
                label='Main Cash Account (will be DEBITED)',
                help_text='The cash account that will receive the money'
            )
            
            # Set default cash account to 10101 - Cash if available
            if not self.instance.pk:
                try:
                    default_cash = Account.objects.get(entity=entity, account_number='10101')
                    self.fields['cash_account'].initial = default_cash.id
                except Account.DoesNotExist:
                    # Try 100001 as backup
                    try:
                        default_cash = Account.objects.get(entity=entity, account_number='100001')
                        self.fields['cash_account'].initial = default_cash.id
                    except Account.DoesNotExist:
                        pass

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
            'account': 'Cash Account (will be CREDITED)',
            'credit_account': 'Destination Account - Expense/Payable (will be DEBITED)',
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
            # Populate form fields
            all_accounts = Account.objects.filter(entity=entity, is_active=True).order_by('account_number')
            self.fields['account'].queryset = all_accounts
            self.fields['credit_account'].queryset = all_accounts
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity
            
            # Add cash_account field dynamically (AFTER super().__init__ so fields dict exists)
            self.fields['cash_account'] = forms.ModelChoiceField(
                queryset=all_accounts,
                required=True,
                empty_label='-- Select Main Cash Account --',
                widget=forms.Select(attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Main Cash Account (CREDITED)',
                    'id': 'id_cash_account',
                }),
                label='Main Cash Account (will be CREDITED)',
                help_text='The cash account from which money will be withdrawn'
            )
            
            # Set default cash account to 100001 - Cash if available
            if not self.instance.pk:
                try:
                    default_cash = Account.objects.get(entity=entity, account_number='100001')
                    self.fields['cash_account'].initial = default_cash.id
                except Account.DoesNotExist:
                    # Try 10101 as backup
                    try:
                        default_cash = Account.objects.get(entity=entity, account_number='10101')
                        self.fields['cash_account'].initial = default_cash.id
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
            'account': 'Bank Account (will be DEBITED)',
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
            # Populate form fields
            all_accounts = Account.objects.filter(entity=entity, is_active=True).order_by('account_number')
            self.fields['account'].queryset = all_accounts
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            self.entity = entity
            
            # Add cash_account field dynamically (AFTER super().__init__ so fields dict exists)
            self.fields['cash_account'] = forms.ModelChoiceField(
                queryset=all_accounts,
                required=True,
                empty_label='-- Select Main Bank Account --',
                widget=forms.Select(attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Main Bank Account (DEBITED)',
                    'id': 'id_cash_account',
                }),
                label='Main Bank Account (will be DEBITED)',
                help_text='The bank account where the money will be deposited'
            )
            
            # Set default cash account to 13020 - Axis Bank if available
            if not self.instance.pk:
                try:
                    default_cash = Account.objects.get(entity=entity, account_number='13020')
                    self.fields['cash_account'].initial = default_cash.id
                except Account.DoesNotExist:
                    # Try 10101 as backup
                    try:
                        default_cash = Account.objects.get(entity=entity, account_number='10101')
                        self.fields['cash_account'].initial = default_cash.id
                    except Account.DoesNotExist:
                        pass

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
            'account': 'Bank Account (will be CREDITED)',
            'credit_account': 'Destination Account - Expense/Payable (will be DEBITED)',
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
            all_accounts = Account.objects.filter(entity=entity, is_active=True)
            self.fields['account'].queryset = all_accounts
            self.fields['credit_account'].queryset = all_accounts
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            
            # Add dynamic cash_account field for main bank account selection
            self.fields['cash_account'] = forms.ModelChoiceField(
                queryset=all_accounts,
                required=True,
                empty_label='-- Select Main Bank Account --',
                widget=forms.Select(attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Select Main Bank Account (CREDITED)',
                    'id': 'id_cash_account',
                }),
                label='Main Bank Account (will be CREDITED)',
                help_text='The bank account from which money will be withdrawn'
            )
            
            # Set default to Axis Bank (13020) or fallback to Cash (10101)
            try:
                default_account = Account.objects.get(account_number='13020', entity=entity)
                self.fields['cash_account'].initial = default_account
            except Account.DoesNotExist:
                try:
                    default_account = Account.objects.get(account_number='10101', entity=entity)
                    self.fields['cash_account'].initial = default_account
                except Account.DoesNotExist:
                    pass
            
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
