"""
Sales Module Forms
CRUD forms for sales orders, customers, and invoices.
"""

from django import forms
from django.utils import timezone
from .models import Customer, SalesOrder, SalesOrderLine, Invoice


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_code', 'customer_name', 'customer_type',
            'email', 'phone', 'website',
            'billing_address', 'shipping_address', 'city', 'state', 'postal_code', 'country',
            'credit_limit', 'tax_id', 'is_tax_exempt',
            'status', 'notes'
        ]
        widgets = {
            'customer_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CUST-001'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'is_tax_exempt': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = [
            'so_number', 'customer', 'order_date', 'required_date',
            'shipping_method', 'po_reference',
            'subtotal', 'tax_amount', 'shipping_cost', 'total_amount',
            'status', 'payment_status', 'notes'
        ]
        widgets = {
            'so_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SO-001'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'required_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shipping_method': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., FedEx, DHL'}),
            'po_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer PO number'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_subtotal'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_tax_amount'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_shipping_cost'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'readonly': True, 'id': 'id_total_amount'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make total_amount readonly
        self.fields['total_amount'].widget.attrs['readonly'] = True
        self.fields['total_amount'].widget.attrs['title'] = 'Auto-calculated from Subtotal + Tax Amount + Shipping Cost'


class SalesOrderLineForm(forms.ModelForm):
    class Meta:
        model = SalesOrderLine
        fields = ['product', 'quantity', 'unit_price', 'discount_percent', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'sales_order', 'customer', 'invoice_date', 'due_date', 
                  'subtotal', 'tax_amount', 'total_amount', 'amount_paid', 'status', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., INV-001'}),
            'sales_order': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_subtotal', 'placeholder': 'Enter subtotal amount'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_tax_percentage', 'placeholder': 'Enter tax % (e.g., 18 for 18% GST)'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_total_amount'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_amount_paid'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Auto-generate invoice number for new invoices
        if not self.instance.pk:  # Only for new invoices
            next_invoice_number = self.generate_next_invoice_number()
            self.fields['invoice_number'].initial = next_invoice_number
            self.fields['invoice_number'].widget.attrs['readonly'] = True
            self.fields['invoice_number'].widget.attrs['title'] = 'Auto-generated invoice number'
        
        # total_amount will be auto-calculated via JavaScript - keep writable for calculation
        self.fields['total_amount'].widget.attrs['title'] = 'Auto-calculated from Subtotal + Tax Amount'
        # Make total_amount not required since it will be calculated by JavaScript
        self.fields['total_amount'].required = False
    
    def clean(self):
        """Convert tax percentage to actual tax amount before saving."""
        cleaned_data = super().clean()
        subtotal = cleaned_data.get('subtotal')
        tax_percentage = cleaned_data.get('tax_amount')
        total_amount = cleaned_data.get('total_amount')
        
        # If subtotal is provided, ensure tax_amount and total_amount are set
        if subtotal:
            # Convert tax_percentage to actual amount
            if tax_percentage is not None:
                tax_amount = subtotal * (tax_percentage / 100)
                cleaned_data['tax_amount'] = tax_amount
            else:
                tax_amount = 0
                cleaned_data['tax_amount'] = 0
            
            # Calculate total_amount if not provided
            if not total_amount:
                cleaned_data['total_amount'] = subtotal + tax_amount
        
        return cleaned_data
    
    @staticmethod
    def generate_next_invoice_number():
        """Generate the next invoice number in format INV-YYYY-XXX"""
        current_year = timezone.now().year
        prefix = f'INV-{current_year}-'
        
        # Get all invoices for current year
        invoices_this_year = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('invoice_number')
        
        if not invoices_this_year.exists():
            next_number = 1
        else:
            # Extract the numeric part from the last invoice
            last_invoice_number = invoices_this_year.last().invoice_number
            try:
                last_number = int(last_invoice_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        
        return f'{prefix}{next_number:03d}'
