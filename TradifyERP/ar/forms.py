"""
Accounts Receivable (AR) Module Forms
Forms for customer invoices, payments, and reconciliation
"""

from django import forms
from .models import CustomerInvoice, InvoiceLineItem, CustomerPayment, ARDiscount, ARReconciliation


class CustomerInvoiceForm(forms.ModelForm):
    """Form for creating/editing customer invoices."""
    
    class Meta:
        model = CustomerInvoice
        fields = ['customer', 'invoice_number', 'invoice_date', 'due_date', 'total_amount', 
                  'reference_number', 'currency', 'subject', 'notes', 'status']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated invoice number',
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
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': 'required'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference number'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Invoice subject'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes/terms'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make status field not required for form
        self.fields['status'].required = False
    
    def clean(self):
        """Validate the form."""
        cleaned_data = super().clean()
        invoice_date = cleaned_data.get('invoice_date')
        due_date = cleaned_data.get('due_date')
        
        # Validate due_date is after invoice_date
        if invoice_date and due_date:
            if due_date < invoice_date:
                self.add_error('due_date', 'Due date must be after or equal to invoice date.')
        
        print(f"Form clean called - cleaned_data: {cleaned_data}")
        print(f"Form errors after validation: {self.errors}")
        return cleaned_data


class InvoiceLineItemForm(forms.ModelForm):
    """Form for adding line items to invoices."""
    
    class Meta:
        model = InvoiceLineItem
        fields = ['invoice', 'description', 'quantity', 'unit_price', 'revenue_account', 'tax_rate', 'amount']
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Item description',
                'required': 'required'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1',
                'step': '0.01',
                'min': '0.01',
                'required': 'required'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'revenue_account': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'readonly': 'readonly'
            }),
        }


class CustomerPaymentForm(forms.ModelForm):
    """Form for recording customer payments against invoices."""
    
    class Meta:
        model = CustomerPayment
        fields = ['customer', 'invoice', 'payment_date', 'amount', 'payment_method', 
                  'reference_number', 'bank_account_id', 'currency', 'notes']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'invoice': forms.Select(attrs={
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
                'step': '0.01',
                'min': '0.01',
                'required': 'required'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Check/Reference number'
            }),
            'bank_account_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank account'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Payment notes'
            }),
        }


class ARDiscountForm(forms.ModelForm):
    """Form for managing early payment discounts."""
    
    class Meta:
        model = ARDiscount
        fields = ['invoice', 'discount_percentage', 'discount_amount', 'discount_due_date', 
                  'reason', 'status']
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': 'required'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'readonly': 'readonly'
            }),
            'discount_due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Discount reason'
            }),
            'status': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class ARReconciliationForm(forms.ModelForm):
    """Form for reconciling invoices and payments."""
    
    class Meta:
        model = ARReconciliation
        fields = ['invoice', 'payment', 'reconciliation_date', 'reconciliation_amount', 'notes']
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'payment': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'reconciliation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'reconciliation_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Reconciliation notes'
            }),
        }


class BulkInvoiceForm(forms.Form):
    """Form for bulk creating invoices via CSV/Excel."""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'required': 'required'
        }),
        label='Upload CSV/Excel file',
        help_text='File should contain: CustomerID, InvoiceDate, Amount, Description'
    )
    
    currency = forms.ChoiceField(
        choices=[
            ('USD', 'USD'),
            ('EUR', 'EUR'),
            ('GBP', 'GBP'),
            ('INR', 'INR'),
            ('AED', 'AED'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Default Currency'
    )
    
    post_to_gl = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Automatically post to General Ledger',
        initial=True
    )


class BulkPaymentForm(forms.Form):
    """Form for bulk recording payments via CSV/Excel."""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'required': 'required'
        }),
        label='Upload CSV/Excel file',
        help_text='File should contain: InvoiceID, PaymentDate, Amount, PaymentMethod'
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('CASH', 'Cash'),
            ('CHEQUE', 'Cheque'),
            ('BANK_TRANSFER', 'Bank Transfer'),
            ('CREDIT_CARD', 'Credit Card'),
            ('ONLINE', 'Online Payment'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Default Payment Method'
    )
    
    post_to_gl = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Automatically post to General Ledger',
        initial=True
    )
