"""
Forms for Cash Management Module
Handles Cash Receipts, Cash Payments, Bank Receipts, and Bank Payments
"""
from django import forms
from django.forms.models import ModelForm
from .models import CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine, Account, Currency, Entity
from accounting.models import Stakeholder
from decimal import Decimal


class CashReceiptLineForm(ModelForm):
    """Form for cash receipts from shareholders or other sources."""
    
    # Additional fields for cascading dropdowns
    main_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Cash Main Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Cash Main Account',
            'id': 'id_main_account',
        }),
        label='Main Cash Account (will be DEBITED)',
        help_text='Select the main cash account category'
    )
    
    main_credit_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Source Main Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Source Main Account (Capital/Revenue)',
            'id': 'id_main_credit_account',
        }),
        label='Main Source Account (will be CREDITED)',
        help_text='Select where the money is coming from (e.g., Capital, Revenue)'
    )
    
    # Stakeholder field for creating capital contributions
    stakeholder = forms.ModelChoiceField(
        queryset=Stakeholder.objects.none(),
        required=False,
        empty_label='-- Select Stakeholder (Optional) --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Stakeholder',
            'id': 'id_stakeholder',
        }),
        label='Stakeholder (for investment tracking)',
        help_text='Select if this cash is from a shareholder/investor'
    )
    
    # Exchange rate field for currency conversion
    exchange_rate = forms.DecimalField(
        required=False,
        max_digits=18,
        decimal_places=6,
        initial=1.000000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000001',
            'placeholder': '1.000000',
            'min': '0.000001',
            'id': 'id_exchange_rate',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Exchange Rate',
        help_text='Rate to convert from selected currency to entity currency'
    )
    
    # Converted amounts (calculated fields)
    converted_debit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_debit_amount',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Debit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    converted_credit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_credit_amount',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Credit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    class Meta:
        model = CashReceiptLine
        fields = ['date', 'account', 'credit_account', 'currency', 'stakeholder', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes', 'exchange_rate', 'converted_debit_amount', 'converted_credit_amount']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Cash Account (to be DEBITED)',
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
            }),
            'stakeholder': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Stakeholder (Optional)',
                'id': 'id_stakeholder',
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
            'notes': 'Notes',
            'exchange_rate': 'Exchange Rate',
            'converted_debit_amount': 'Converted Amount',
            'converted_credit_amount': 'Converted Amount'
        }
    
    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if entity:
            # Get ALL accounts (including both parent and sub-accounts)
            all_accounts = Account.objects.filter(
                entity=entity,
                is_active=True
            ).order_by('account_number')
            
            # Main account dropdown shows ALL accounts (not just parent accounts)
            self.fields['main_account'].queryset = all_accounts
            self.fields['main_credit_account'].queryset = all_accounts
            
            # Set stakeholder field to only active stakeholders from the current entity
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                entity=entity,
                status='ACTIVE'
            ).order_by('first_name', 'last_name')
            
            # Set sub-accounts queryset to ALL accounts for validation to work
            # JavaScript will filter/populate based on selected main account
            
            # Set credit_account queryset for the form field
            self.fields['credit_account'].queryset = all_accounts
            
            if self.instance and self.instance.pk and self.instance.account:
                # For edit mode, get all related sub-accounts for the parent (debit account)
                current_account = self.instance.account
                parent = current_account.parent_account or current_account
                self.fields['account'].queryset = Account.objects.filter(
                    entity=entity,
                    is_active=True,
                    parent_account=parent
                ).order_by('account_number')
                # Set the main account to the parent
                self.initial['main_account'] = parent.id
                
                # If credit_account is set, set main_credit_account to its parent
                if self.instance.credit_account:
                    credit_account = self.instance.credit_account
                    credit_parent = credit_account.parent_account or credit_account
                    self.initial['main_credit_account'] = credit_parent.id
                    # Also set credit_account queryset to the parent's sub-accounts
                    self.fields['credit_account'].queryset = Account.objects.filter(
                        entity=entity,
                        is_active=True,
                        parent_account=credit_parent
                    ).order_by('account_number')
            else:
                # For create mode, set to all accounts for form validation
                self.fields['account'].queryset = all_accounts
            
            # Ensure account field is not disabled
            if 'disabled' in self.fields['account'].widget.attrs:
                del self.fields['account'].widget.attrs['disabled']
            
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        
        # Ensure both amounts are provided and match
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit amount is required')
        if credit_amount is None:
            self.add_error('credit_amount', 'Credit amount is required')
        
        currency = cleaned_data.get('currency')
        exchange_rate = cleaned_data.get('exchange_rate')
        
        if debit_amount and credit_amount:
            if Decimal(str(debit_amount)) != Decimal(str(credit_amount)):
                self.add_error('credit_amount', 'Credit amount must equal debit amount')
            if Decimal(str(debit_amount)) <= 0:
                self.add_error('debit_amount', 'Amount must be greater than zero')
        
        # Validate exchange rate for non-entity currencies
        if currency and hasattr(self, 'entity') and self.entity:
            entity_currency = getattr(self.entity, 'company_currency', None)
            if entity_currency and currency != entity_currency:
                if not exchange_rate or exchange_rate <= 0:
                    self.add_error('exchange_rate', 'Exchange rate is required when using a different currency')
                else:
                    # Calculate converted amounts
                    if debit_amount and exchange_rate:
                        cleaned_data['converted_debit_amount'] = Decimal(str(debit_amount)) * Decimal(str(exchange_rate))
                    if credit_amount and exchange_rate:
                        cleaned_data['converted_credit_amount'] = Decimal(str(credit_amount)) * Decimal(str(exchange_rate))
            else:
                # Same currency, no conversion needed
                cleaned_data['exchange_rate'] = Decimal('1.000000')
                cleaned_data['converted_debit_amount'] = debit_amount
                cleaned_data['converted_credit_amount'] = credit_amount
        
        return cleaned_data
    
    def save(self, commit=True):
        """Override save to automatically assign stakeholder based on selected account."""
        instance = super().save(commit=False)
        
        # Auto-assign stakeholder if not manually selected
        if not instance.stakeholder_id and instance.account:
            stakeholder = self._find_stakeholder_for_account(instance.account)
            if stakeholder:
                instance.stakeholder = stakeholder
        
        if commit:
            instance.save()
        return instance
    
    def _find_stakeholder_for_account(self, account):
        """Find stakeholder that matches the account name pattern."""
        if not account or not account.name:
            return None
            
        account_name = account.name.strip()
        
        # Extract stakeholder name from account name patterns like:
        # "Dr. Irfan Mohammed - Capital" -> "Dr. Irfan Mohammed"
        # "Sajaz Ahmed - Capital" -> "Sajaz Ahmed"
        if ' - Capital' in account_name:
            stakeholder_name = account_name.replace(' - Capital', '').strip()
        else:
            return None
        
        # Try to find matching stakeholder by name
        # First, try exact match by full name
        stakeholders = Stakeholder.objects.filter(entity=account.entity)
        
        for stakeholder in stakeholders:
            if stakeholder.full_name == stakeholder_name:
                return stakeholder
        
        # If no exact match, try partial matching
        # Split the name and try to match first/last name combinations
        name_parts = stakeholder_name.split()
        if len(name_parts) >= 2:
            first_part = name_parts[0]
            last_part = name_parts[-1]
            
            # Try to match by first and last name
            for stakeholder in stakeholders:
                if (stakeholder.first_name and stakeholder.last_name and 
                    first_part.lower() in stakeholder.first_name.lower() and 
                    last_part.lower() in stakeholder.last_name.lower()):
                    return stakeholder
        
        return None


class CashPaymentLineForm(ModelForm):
    """Form for cash payments to shareholders or other entities."""
    
    # Additional fields for cascading dropdowns
    main_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Main Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Main Account',
            'id': 'id_main_account',
        }),
        label='Main Account'
    )
    
    main_credit_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Main Credit Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Main Credit Account',
            'id': 'id_main_credit_account',
        }),
        label='Main Credit Account'
    )
    
    # Exchange rate field for currency conversion
    exchange_rate = forms.DecimalField(
        required=False,
        max_digits=18,
        decimal_places=6,
        initial=1.000000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000001',
            'placeholder': '1.000000',
            'min': '0.000001',
            'id': 'id_exchange_rate',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Exchange Rate',
        help_text='Rate to convert from selected currency to entity currency'
    )
    
    # Converted amounts (calculated fields)
    converted_debit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_debit_amount',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Debit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    converted_credit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_credit_amount',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Credit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    class Meta:
        model = CashPaymentLine
        fields = ['date', 'account', 'credit_account', 'currency', 'payment_purpose', 'stakeholder', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes', 'exchange_rate', 'converted_debit_amount', 'converted_credit_amount']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Sub-Account',
                'id': 'id_account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Credit Account (Default: Cash 100001)',
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
                'data-placeholder': 'Select Stakeholder',
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
            'account': 'Sub-Account (Debit)',
            'credit_account': 'Sub-Account (Credit)',
            'currency': 'Currency',
            'payment_purpose': 'Payment Purpose',
            'stakeholder': 'Stakeholder (for Capital Withdrawal/Profit Distribution)',
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
            # Filter accounts to show only parent accounts (main accounts) with no parent
            parent_accounts = Account.objects.filter(
                entity=entity,
                is_active=True,
                parent_account__isnull=True
            ).order_by('account_number')
            
            self.fields['main_account'].queryset = parent_accounts
            self.fields['main_credit_account'].queryset = parent_accounts
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['credit_account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            
            # Use full_name for stakeholder display
            self.fields['stakeholder'].label_from_instance = lambda obj: obj.full_name
            
            # Store entity for currency comparison
            self.entity = entity
            
            # Set initial currency to entity's currency if available
            if hasattr(entity, 'currency') and entity.currency:
                self.fields['currency'].initial = entity.currency.id
            
            # Set default credit_account to Cash account (100001) for new payments
            if not self.instance.pk:  # Only for new payments, not edits
                try:
                    cash_account = Account.objects.get(entity=entity, account_number='100001')
                    self.fields['credit_account'].initial = cash_account.id
                except Account.DoesNotExist:
                    pass  # Cash account doesn't exist, user must select manually
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        currency = cleaned_data.get('currency')
        exchange_rate = cleaned_data.get('exchange_rate')
        payment_purpose = cleaned_data.get('payment_purpose')
        stakeholder = cleaned_data.get('stakeholder')
        debit_account = cleaned_data.get('account')
        credit_account = cleaned_data.get('credit_account')
        
        # Ensure credit_account is set, default to Cash (100001) if not provided
        if not credit_account and hasattr(self, 'entity'):
            try:
                cash_account = Account.objects.get(entity=self.entity, account_number='100001')
                cleaned_data['credit_account'] = cash_account
            except Account.DoesNotExist:
                self.add_error('credit_account', 'Credit account is required. Cash account (100001) not found.')
        
        # Validate that debit and credit accounts are different
        if debit_account and credit_account:
            if debit_account.id == credit_account.id:
                self.add_error('credit_account', 'Credit account must be different from debit account to avoid duplicate entries in the same ledger.')
        
        # Validate stakeholder requirement for capital withdrawal and profit distribution
        if payment_purpose in ['CAPITAL_WITHDRAWAL', 'PROFIT_DISTRIBUTION']:
            if not stakeholder:
                self.add_error('stakeholder', f'Stakeholder is required when payment purpose is {payment_purpose.replace("_", " ").title()}')
        
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
        
        # Validate exchange rate for non-entity currencies
        if currency and hasattr(self, 'entity') and self.entity:
            entity_currency = getattr(self.entity, 'company_currency', None)
            if entity_currency and currency != entity_currency:
                if not exchange_rate or exchange_rate <= 0:
                    self.add_error('exchange_rate', 'Exchange rate is required when using a different currency')
                else:
                    # Calculate converted amounts
                    if debit_amount and exchange_rate:
                        cleaned_data['converted_debit_amount'] = Decimal(str(debit_amount)) * Decimal(str(exchange_rate))
                    if credit_amount and exchange_rate:
                        cleaned_data['converted_credit_amount'] = Decimal(str(credit_amount)) * Decimal(str(exchange_rate))
            else:
                # Same currency, no conversion needed
                cleaned_data['exchange_rate'] = Decimal('1.000000')
                cleaned_data['converted_debit_amount'] = debit_amount
                cleaned_data['converted_credit_amount'] = credit_amount
        
        return cleaned_data


class BankReceiptLineForm(ModelForm):
    """Form for bank deposits/receipts."""
    
    # Additional fields for cascading dropdowns
    main_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Main Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Main Account',
            'id': 'id_main_account',
        }),
        label='Main Account'
    )
    
    # Stakeholder field for creating capital contributions
    stakeholder = forms.ModelChoiceField(
        queryset=Stakeholder.objects.none(),
        required=False,
        empty_label='-- Select Stakeholder (Optional) --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Stakeholder',
            'id': 'id_stakeholder_bank',
        }),
        label='Stakeholder (for investment tracking)',
        help_text='Select if this bank receipt is from a shareholder/investor'
    )
    
    # Exchange rate field for currency conversion
    exchange_rate = forms.DecimalField(
        required=False,
        max_digits=18,
        decimal_places=6,
        initial=1.000000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000001',
            'placeholder': '1.000000',
            'min': '0.000001',
            'id': 'id_exchange_rate_bank',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Exchange Rate',
        help_text='Rate to convert from selected currency to entity currency'
    )
    
    # Converted amounts (calculated fields)
    converted_debit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_debit_amount_bank',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Debit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    converted_credit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_credit_amount_bank',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Credit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    class Meta:
        model = BankReceiptLine
        fields = ['date', 'account', 'currency', 'stakeholder', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Sub-Account',
                'id': 'id_account',
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
            'account': 'Sub-Account (Debit)',
            'credit_account': 'Sub-Account (Credit)',
            'currency': 'Currency',
            'stakeholder': 'Stakeholder (for investment tracking)',
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
            # Filter accounts to show only parent accounts (main accounts) with no parent
            parent_accounts = Account.objects.filter(
                entity=entity,
                is_active=True,
                parent_account__isnull=True
            ).order_by('account_number')
            
            self.fields['main_account'].queryset = parent_accounts
            
            # Set stakeholder field to all stakeholders
            self.fields['stakeholder'].queryset = Stakeholder.objects.all().order_by('first_name', 'last_name')
            
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            
            # Store entity for currency comparison
            self.entity = entity
            
            # Set initial currency to entity's currency if available
            if hasattr(entity, 'currency') and entity.currency:
                self.fields['currency'].initial = entity.currency.id
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        currency = cleaned_data.get('currency')
        exchange_rate = cleaned_data.get('exchange_rate')
        
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit Amount is required')
        elif Decimal(str(debit_amount)) <= 0:
            self.add_error('debit_amount', 'Debit Amount must be greater than zero')
        
        # Validate exchange rate for non-entity currencies
        if currency and hasattr(self, 'entity') and self.entity:
            entity_currency = getattr(self.entity, 'company_currency', None)
            if entity_currency and currency != entity_currency:
                if not exchange_rate or exchange_rate <= 0:
                    self.add_error('exchange_rate', 'Exchange rate is required when using a different currency')
                else:
                    # Calculate converted amounts
                    if debit_amount and exchange_rate:
                        cleaned_data['converted_debit_amount'] = Decimal(str(debit_amount)) * Decimal(str(exchange_rate))
                    if credit_amount and exchange_rate:
                        cleaned_data['converted_credit_amount'] = Decimal(str(credit_amount)) * Decimal(str(exchange_rate))
            else:
                # Same currency, no conversion needed
                cleaned_data['exchange_rate'] = Decimal('1.000000')
                cleaned_data['converted_debit_amount'] = debit_amount
                cleaned_data['converted_credit_amount'] = credit_amount
        
        return cleaned_data
    
    def save(self, commit=True):
        """Override save to automatically assign stakeholder based on selected account."""
        instance = super().save(commit=False)
        
        # Auto-assign stakeholder if not manually selected
        if not instance.stakeholder_id and instance.account:
            stakeholder = self._find_stakeholder_for_account(instance.account)
            if stakeholder:
                instance.stakeholder = stakeholder
        
        if commit:
            instance.save()
        return instance
    
    def _find_stakeholder_for_account(self, account):
        """Find stakeholder that matches the account name pattern."""
        if not account or not account.name:
            return None
            
        account_name = account.name.strip()
        
        # Extract stakeholder name from account name patterns like:
        # "Dr. Irfan Mohammed - Capital" -> "Dr. Irfan Mohammed"
        # "Sajaz Ahmed - Capital" -> "Sajaz Ahmed"
        if ' - Capital' in account_name:
            stakeholder_name = account_name.replace(' - Capital', '').strip()
        else:
            return None
        
        # Try to find matching stakeholder by name
        # First, try exact match by full name
        stakeholders = Stakeholder.objects.filter(entity=account.entity)
        
        for stakeholder in stakeholders:
            if stakeholder.full_name == stakeholder_name:
                return stakeholder
        
        # If no exact match, try partial matching
        # Split the name and try to match first/last name combinations
        name_parts = stakeholder_name.split()
        if len(name_parts) >= 2:
            first_part = name_parts[0]
            last_part = name_parts[-1]
            
            # Try to match by first and last name
            for stakeholder in stakeholders:
                if (stakeholder.first_name and stakeholder.last_name and 
                    first_part.lower() in stakeholder.first_name.lower() and 
                    last_part.lower() in stakeholder.last_name.lower()):
                    return stakeholder
        
        return None


class BankPaymentLineForm(ModelForm):
    """Form for bank payments/withdrawals."""
    
    # Additional fields for cascading dropdowns
    main_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Main Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Main Account',
            'id': 'id_main_account',
        }),
        label='Main Account'
    )
    
    main_credit_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='-- Select Main Credit Account --',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select Main Credit Account',
            'id': 'id_main_credit_account',
        }),
        label='Main Credit Account'
    )
    
    # Exchange rate field for currency conversion
    exchange_rate = forms.DecimalField(
        required=False,
        max_digits=18,
        decimal_places=6,
        initial=1.000000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000001',
            'placeholder': '1.000000',
            'min': '0.000001',
            'id': 'id_exchange_rate_bank_payment',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Exchange Rate',
        help_text='Rate to convert from selected currency to entity currency'
    )
    
    # Converted amounts (calculated fields)
    converted_debit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_debit_amount_bank_payment',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Debit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    converted_credit_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': '0.00',
            'id': 'id_converted_credit_amount_bank_payment',
            'style': 'display: none;'  # Hidden by default
        }),
        label='Converted Credit Amount (Entity Currency)',
        help_text='Amount in entity currency'
    )
    
    class Meta:
        model = BankPaymentLine
        fields = ['date', 'account', 'credit_account', 'currency', 'payment_purpose', 'stakeholder', 'description', 'debit_amount', 'credit_amount', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Sub-Account',
                'id': 'id_account',
            }),
            'credit_account': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select Sub-Credit Account',
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
                'data-placeholder': 'Select Stakeholder',
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
            'account': 'Sub-Account (Debit)',
            'credit_account': 'Sub-Account (Credit)',
            'currency': 'Currency',
            'payment_purpose': 'Payment Purpose',
            'stakeholder': 'Stakeholder (for Capital Withdrawal/Profit Distribution)',
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
            # Filter accounts to show only parent accounts (main accounts) with no parent
            parent_accounts = Account.objects.filter(
                entity=entity,
                is_active=True,
                parent_account__isnull=True
            ).order_by('account_number')
            
            self.fields['main_account'].queryset = parent_accounts
            self.fields['main_credit_account'].queryset = parent_accounts
            self.fields['account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['credit_account'].queryset = Account.objects.filter(entity=entity, is_active=True)
            self.fields['currency'].queryset = Currency.objects.filter(is_active=True)
            self.fields['stakeholder'].queryset = Stakeholder.objects.filter(entity=entity)
            
            # Use full_name for stakeholder display
            self.fields['stakeholder'].label_from_instance = lambda obj: obj.full_name
            
            # Store entity for currency comparison
            self.entity = entity
            
            # Set initial currency to entity's currency if available
            if hasattr(entity, 'currency') and entity.currency:
                self.fields['currency'].initial = entity.currency.id
    
    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        currency = cleaned_data.get('currency')
        exchange_rate = cleaned_data.get('exchange_rate')
        payment_purpose = cleaned_data.get('payment_purpose')
        stakeholder = cleaned_data.get('stakeholder')
        
        # Validate stakeholder requirement for capital withdrawal and profit distribution
        if payment_purpose in ['CAPITAL_WITHDRAWAL', 'PROFIT_DISTRIBUTION']:
            if not stakeholder:
                self.add_error('stakeholder', f'Stakeholder is required when payment purpose is {payment_purpose.replace("_", " ").title()}')
        
        if debit_amount is None:
            self.add_error('debit_amount', 'Debit Amount is required')
        elif Decimal(str(debit_amount)) <= 0:
            self.add_error('debit_amount', 'Debit Amount must be greater than zero')
        
        # Validate exchange rate for non-entity currencies
        if currency and hasattr(self, 'entity') and self.entity:
            entity_currency = getattr(self.entity, 'company_currency', None)
            if entity_currency and currency != entity_currency:
                if not exchange_rate or exchange_rate <= 0:
                    self.add_error('exchange_rate', 'Exchange rate is required when using a different currency')
                else:
                    # Calculate converted amounts
                    if debit_amount and exchange_rate:
                        cleaned_data['converted_debit_amount'] = Decimal(str(debit_amount)) * Decimal(str(exchange_rate))
                    if credit_amount and exchange_rate:
                        cleaned_data['converted_credit_amount'] = Decimal(str(credit_amount)) * Decimal(str(exchange_rate))
            else:
                # Same currency, no conversion needed
                cleaned_data['exchange_rate'] = Decimal('1.000000')
                cleaned_data['converted_debit_amount'] = debit_amount
                cleaned_data['converted_credit_amount'] = credit_amount
        
        return cleaned_data
