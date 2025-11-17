from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    LedgerEntry, Account, Entity, Customer, Vendor, Currency, VendorInvoice,
    VendorPayment, FixedAsset, DeferredExpense, DeferredRevenue, CashTransaction,
    BankProfile, TaxRate, ReconciliationRecord
)


class DoubleEntryJournalForm(forms.Form):
    """Form for creating double-entry journal entries (Debit and Credit simultaneously)."""
    
    entry_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': 'required'
        }),
        label='Entry Date'
    )
    
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter transaction description'
        }),
        label='Description'
    )
    
    reference_number = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., INV-001, CHK-001'
        }),
        label='Reference Number (Optional)'
    )
    
    # Debit side
    debit_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Debit Account'
    )
    
    debit_amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'min': '0.01',
            'step': '0.01',
            'required': 'required'
        }),
        label='Debit Amount'
    )
    
    # Credit side
    credit_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Credit Account'
    )
    
    credit_amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'min': '0.01',
            'step': '0.01',
            'required': 'required'
        }),
        label='Credit Amount'
    )
    
    is_posted = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Post Entry Immediately',
        initial=True
    )
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the queryset for account fields based on entity
        if entity:
            accounts = Account.objects.filter(entity=entity, is_active=True).order_by('account_number')
            self.fields['debit_account'].queryset = accounts
            self.fields['credit_account'].queryset = accounts
        else:
            self.fields['debit_account'].queryset = Account.objects.filter(is_active=True)
            self.fields['credit_account'].queryset = Account.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        
        debit_amount = cleaned_data.get('debit_amount')
        credit_amount = cleaned_data.get('credit_amount')
        debit_account = cleaned_data.get('debit_account')
        credit_account = cleaned_data.get('credit_account')
        
        # Validate that debit and credit amounts are equal
        if debit_amount and credit_amount:
            if debit_amount != credit_amount:
                raise ValidationError(
                    'Debits (%(debit)s) must equal Credits (%(credit)s) for double-entry bookkeeping.',
                    code='unbalanced',
                    params={'debit': debit_amount, 'credit': credit_amount}
                )
        
        # Validate that debit and credit accounts are different
        if debit_account and credit_account:
            if debit_account.id == credit_account.id:
                raise ValidationError(
                    'Debit and Credit accounts must be different.',
                    code='same_account'
                )
        
        return cleaned_data


class SimpleLedgerEntryForm(forms.ModelForm):
    """Simple form for creating individual ledger entries."""
    
    class Meta:
        model = LedgerEntry
        fields = ['account', 'entry_date', 'entry_type', 'amount', 'description', 'reference_number', 'is_posted']
        widgets = {
            'account': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'entry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'entry_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., INV-001'
            }),
            'is_posted': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the queryset for account field based on entity
        if entity:
            self.fields['account'].queryset = Account.objects.filter(
                entity=entity, 
                is_active=True
            ).order_by('account_number')
        else:
            self.fields['account'].queryset = Account.objects.filter(is_active=True)


class QuickAddCustomerForm(forms.ModelForm):
    """Quick add form for creating customers from dashboard."""
    
    class Meta:
        model = Customer
        fields = ['customer_code', 'name', 'email', 'phone', 'address', 'tax_id', 'currency', 'credit_limit']
        widgets = {
            'customer_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CUST-001',
                'required': 'required'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1-555-0000'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Customer address'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tax/VAT ID'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
    
    def clean_customer_code(self):
        """Validate customer code is unique within the entity."""
        customer_code = self.cleaned_data.get('customer_code')
        
        if self.entity and customer_code:
            existing = Customer.objects.filter(
                entity=self.entity,
                customer_code=customer_code
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Customer code "{customer_code}" already exists for this entity.'
                )
        
        return customer_code


class QuickAddVendorForm(forms.ModelForm):
    """Quick add form for creating vendors from dashboard."""
    
    class Meta:
        model = Vendor
        fields = ['vendor_code', 'name', 'email', 'phone', 'address', 'tax_id', 'currency', 'payment_terms']
        widgets = {
            'vendor_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., VEND-001',
                'required': 'required'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vendor/Supplier name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1-555-0000'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Vendor address'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tax/VAT ID'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Net 30, Net 60'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
    
    def clean_vendor_code(self):
        """Validate vendor code is unique within the entity."""
        vendor_code = self.cleaned_data.get('vendor_code')
        
        if self.entity and vendor_code:
            existing = Vendor.objects.filter(
                entity=self.entity,
                vendor_code=vendor_code
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Vendor code "{vendor_code}" already exists for this entity.'
                )
        
        return vendor_code


class QuickAddAccountForm(forms.ModelForm):
    """Quick add form for creating chart of accounts from dashboard."""
    
    class Meta:
        model = Account
        fields = ['account_number', 'name', 'account_type', 'description', 'currency', 'opening_balance']
        widgets = {
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1000, 1010',
                'required': 'required'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account name',
                'required': 'required'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Account description'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
    
    def clean_account_number(self):
        """Validate account number is unique within the entity."""
        account_number = self.cleaned_data.get('account_number')
        
        if self.entity and account_number:
            existing = Account.objects.filter(
                entity=self.entity,
                account_number=account_number
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Account number "{account_number}" already exists for this entity.'
                )
        
        return account_number


class QuickAddVendorInvoiceForm(forms.ModelForm):
    """Quick add form for creating vendor invoices from dashboard."""
    
    class Meta:
        model = VendorInvoice
        fields = ['vendor', 'invoice_number', 'invoice_date', 'due_date', 'amount', 'tax_amount', 'total_amount', 'description']
        widgets = {
            'vendor': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., INV-2025-001',
                'required': 'required'
            }),
            'invoice_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Invoice description/notes'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter vendors by entity
        if entity:
            self.fields['vendor'].queryset = Vendor.objects.filter(entity=entity, is_active=True).order_by('name')
        else:
            self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)


class QuickAddVendorPaymentForm(forms.ModelForm):
    """Quick add form for vendor payments."""
    
    class Meta:
        model = VendorPayment
        fields = ['vendor_invoice', 'payment_date', 'amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'vendor_invoice': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CHK-001, TRF-001'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Payment notes'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if entity:
            self.fields['vendor_invoice'].queryset = VendorInvoice.objects.filter(entity=entity).order_by('-invoice_date')
        else:
            self.fields['vendor_invoice'].queryset = VendorInvoice.objects.all()


class QuickAddFixedAssetForm(forms.ModelForm):
    """Quick add form for fixed assets."""
    
    class Meta:
        model = FixedAsset
        fields = ['asset_code', 'name', 'category', 'purchase_date', 'purchase_cost', 'useful_life_years', 'book_value']
        widgets = {
            'asset_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., FA-001',
                'required': 'required'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Asset name',
                'required': 'required'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Building, Vehicle, Equipment',
                'required': 'required'
            }),
            'purchase_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'purchase_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'useful_life_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Years',
                'min': '1',
                'required': 'required'
            }),
            'book_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


class QuickAddCashTransactionForm(forms.ModelForm):
    """Quick add form for cash transactions."""
    
    class Meta:
        model = CashTransaction
        fields = ['transaction_date', 'transaction_type', 'amount', 'description', 'reference_number']
        widgets = {
            'transaction_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Transaction description',
                'required': 'required'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


class QuickAddBankProfileForm(forms.ModelForm):
    """Quick add form for bank profiles."""
    
    class Meta:
        model = BankProfile
        fields = ['bank_name', 'account_number', 'account_holder', 'currency']
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
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


class QuickAddTaxRateForm(forms.ModelForm):
    """Quick add form for tax rates."""
    
    class Meta:
        model = TaxRate
        fields = ['tax_type', 'rate_percentage', 'effective_from', 'effective_to']
        widgets = {
            'tax_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., VAT, Sales Tax',
                'required': 'required'
            }),
            'rate_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'required': 'required'
            }),
            'effective_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'effective_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


class QuickAddDeferredExpenseForm(forms.ModelForm):
    """Quick add form for deferred expenses."""
    
    class Meta:
        model = DeferredExpense
        fields = ['description', 'amount', 'deferral_date', 'expiry_date', 'expense_type']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'deferral_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'expense_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Insurance, Rent',
                'required': 'required'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


class QuickAddDeferredRevenueForm(forms.ModelForm):
    """Quick add form for deferred revenues."""
    
    class Meta:
        model = DeferredRevenue
        fields = ['description', 'amount', 'deferral_date', 'recognition_date', 'revenue_type']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': 'required'
            }),
            'deferral_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'recognition_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'revenue_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Subscription, Advance Payment',
                'required': 'required'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


class QuickAddReconciliationRecordForm(forms.ModelForm):
    """Quick add form for reconciliation records."""
    
    class Meta:
        model = ReconciliationRecord
        fields = ['reconciliation_date']
        widgets = {
            'reconciliation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            })
        }
    
    def __init__(self, entity=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
