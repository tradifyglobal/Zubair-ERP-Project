from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    VendorBill, VendorBillLineItem, VendorPayment, 
    APDiscount, APReconciliation
)


class VendorBillForm(forms.ModelForm):
    """Form for creating/updating vendor bills."""
    
    class Meta:
        model = VendorBill
        fields = ('vendor', 'entity', 'bill_number', 'bill_date', 'due_date', 'total_amount')
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'bill_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bill Number'}),
            'bill_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class VendorBillLineItemForm(forms.ModelForm):
    """Form for creating/updating vendor bill line items."""
    
    class Meta:
        model = VendorBillLineItem
        fields = ('bill', 'description', 'quantity', 'unit_price', 'expense_account', 'po_line_item')
        widgets = {
            'bill': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expense_account': forms.Select(attrs={'class': 'form-select'}),
            'po_line_item': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity and quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')
        
        if unit_price and unit_price < 0:
            raise ValidationError('Unit price cannot be negative.')
        
        return cleaned_data


class VendorPaymentForm(forms.ModelForm):
    """Form for creating/updating vendor payments."""
    
    class Meta:
        model = VendorPayment
        fields = ('vendor', 'entity', 'payment_number', 'payment_date', 'payment_amount', 'payment_method', 'check_number', 'bank_account', 'bills')
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'entity': forms.Select(attrs={'class': 'form-select'}),
            'payment_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payment Number'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'check_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Check Number (if applicable)'}),
            'bank_account': forms.Select(attrs={'class': 'form-select'}),
            'bills': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        payment_amount = cleaned_data.get('payment_amount')
        bills = cleaned_data.get('bills')
        payment_method = cleaned_data.get('payment_method')
        check_number = cleaned_data.get('check_number')
        
        if payment_amount and payment_amount <= 0:
            raise ValidationError('Payment amount must be greater than zero.')
        
        if not bills:
            raise ValidationError('At least one bill must be selected for payment.')
        
        if payment_method == 'CHECK' and not check_number:
            raise ValidationError('Check number is required when payment method is Check.')
        
        return cleaned_data


class APDiscountForm(forms.ModelForm):
    """Form for creating/updating AP discounts."""
    
    class Meta:
        model = APDiscount
        fields = ('bill', 'discount_percentage', 'discount_days', 'discount_account')
        widgets = {
            'bill': forms.Select(attrs={'class': 'form-select'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'discount_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'discount_account': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        discount_percentage = cleaned_data.get('discount_percentage')
        discount_days = cleaned_data.get('discount_days')
        
        if discount_percentage and (discount_percentage < 0 or discount_percentage > 100):
            raise ValidationError('Discount percentage must be between 0 and 100.')
        
        if discount_days and discount_days < 0:
            raise ValidationError('Discount days cannot be negative.')
        
        return cleaned_data


class APReconciliationForm(forms.ModelForm):
    """Form for reconciling AP bills to payments."""
    
    class Meta:
        model = APReconciliation
        fields = ('bill', 'payment', 'matched_amount')
        widgets = {
            'bill': forms.Select(attrs={'class': 'form-select'}),
            'payment': forms.Select(attrs={'class': 'form-select'}),
            'matched_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        bill = cleaned_data.get('bill')
        payment = cleaned_data.get('payment')
        matched_amount = cleaned_data.get('matched_amount')
        
        if bill and payment and bill.entity != payment.entity:
            raise ValidationError('Bill and payment must belong to the same entity.')
        
        if matched_amount and matched_amount <= 0:
            raise ValidationError('Matched amount must be greater than zero.')
        
        return cleaned_data


class BulkVendorBillForm(forms.Form):
    """Form for bulk uploading vendor bills (CSV/Excel)."""
    
    file = forms.FileField(
        label='Upload Bills File (CSV or Excel)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv, .xlsx'}),
        help_text='File must contain columns: vendor_name, bill_number, bill_date, due_date, total_amount'
    )
    
    entity = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Entity'
    )
    
    def __init__(self, *args, **kwargs):
        from accounting.models import Entity
        super().__init__(*args, **kwargs)
        self.fields['entity'].queryset = Entity.objects.all()
